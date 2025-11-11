import enum
import io
import logging

import yaml
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import HorizontalGroup
from textual.logging import TextualHandler
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import (
    Footer,
    Label,
    ListItem,
    ListView,
    Log,
    Rule,
)

from .aws_kion import DEFAULT_AWS_CREDENTIALS, DEFAULT_KION_SOURCE_CONFIG, aws_kion
from .aws_kion_check import aws_kion_check
from .aws_mfa import aws_mfa
from .dbx_token_rotate import manage_dbx_tokens
from .kion_cli_password import DEFAULT_CONFIG_FILE, update_kion_cli_password
from .noop import run_noop

logger = logging.getLogger("tui")


class ProcessStatus(enum.Enum):
    OK = 0
    FAIL = 1
    UNKNOWN = 2
    RUNNING = 3


# Each process will write to its own io.StringIO
class AuthProcess:
    def __init__(self, process_config: dict):
        self.name = process_config["name"]
        self.type = process_config["type"]

        if self.type == "aws":
            self.profile = process_config["profile"]
        elif self.type == "dbx":
            self.profile = process_config["profile"]
            self.aliases = []
            alias = process_config.get("alias")
            if alias:
                self.aliases.append(alias)
        elif self.type == "kion-cli":
            self.config = process_config.get("config", DEFAULT_CONFIG_FILE)
        elif self.type == "aws-kion":
            self.profile = process_config["profile"]
            self.favourite = process_config.get("favourite", process_config["favorite"])
            self.credentials_file = process_config.get("credentials_file", DEFAULT_AWS_CREDENTIALS)
            self.kion_config_src = process_config.get("kion_config", DEFAULT_KION_SOURCE_CONFIG)
            self.kion_bin = process_config.get("kion_bin", "/opt/homebrew/bin/kion")
        elif self.type == "aws-kion-check":
            self.profile = process_config["profile"]
        elif self.type == "noop":
            # This is used for testing things
            pass
        else:
            raise ValueError(f"Unexpected auth process type: {self.type}")

        self.log_stream = io.StringIO()
        self.log_handler = logging.StreamHandler(self.log_stream)

    def run(self):
        logger.debug(f"Run {self.name} {self.type}")
        process_logger = logging.getLogger(self.type)
        process_logger.addHandler(self.log_handler)
        try:
            if self.type == "aws":
                aws_mfa(self.profile, False)
            elif self.type == "dbx":
                manage_dbx_tokens(self.profile, self.aliases, False)
            elif self.type == "kion-cli":
                update_kion_cli_password(self.config)
            elif self.type == "aws-kion":
                aws_kion(
                    self.profile,
                    self.credentials_file,
                    self.favourite,
                    self.kion_config_src,
                    self.kion_bin,
                )
            elif self.type == "aws-kion-check":
                aws_kion_check(self.profile)
            elif self.type == "noop":
                run_noop()
            else:
                raise ValueError(f"Unexpected auth process type: {self.type}")
        except Exception:
            process_logger.exception(f"Exception running {self.name}")
            raise
        finally:
            process_logger.removeHandler(self.log_handler)


def load_config(config_file: str) -> list[AuthProcess]:
    logger.debug(f"Loading config from {config_file}")
    processes = []
    with open(config_file) as f:
        config = yaml.safe_load(f)
    for auth_process in config:
        processes.append(AuthProcess(auth_process))
    return processes


class AuthProcessStatus(Widget):
    value = reactive(ProcessStatus.UNKNOWN)

    def render(self) -> str:
        if self.value == ProcessStatus.OK:
            return "\u2714"
        if self.value == ProcessStatus.FAIL:
            return "\u2716"
        if self.value == ProcessStatus.RUNNING:
            return "-"
        return "?"


class AuthRunMessage(Message):
    def __init__(self, status: ProcessStatus, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = status


class AuthRunCompleteMessage(Message):
    pass


class AuthProcessItem(ListItem):
    def __init__(self, proc: AuthProcess, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process_config = proc
        self.status = AuthProcessStatus()

    def compose(self) -> ComposeResult:
        # TODO - make use of more stuff here
        yield HorizontalGroup(Label(self.process_config.name), Label(" "), self.status)

    @on(AuthRunMessage)
    def run_complete(self, msg: AuthRunMessage):
        self.status.value = msg.status
        self.post_message(AuthRunCompleteMessage())

    @work(exclusive=True, thread=True)
    def run_auth(self):
        logger.debug(f"Run auth: {self}")
        result = ProcessStatus.UNKNOWN
        try:
            self.process_config.run()
            result = ProcessStatus.OK
        except Exception:
            logger.exception("Error updating auth")
            result = ProcessStatus.FAIL
        self.post_message(AuthRunMessage(result))


class UpdateLogMessage(Message):
    def __init__(self, name: str, value: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proc_name = name
        self.log_value = value


class AuthProcessList(ListView):
    BINDINGS = [
        Binding("j, down", "cursor_down", "Cursor down"),
        Binding("k, up", "cursor_up", "Cursor up"),
        Binding("o, enter", "select_cursor", "Select"),
        Binding("r", "run_auth", "Run highlighted"),
    ]

    def __init__(self, procs: list[AuthProcess], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._auth_processes: list[AuthProcess] = procs
        self._highlighted: AuthProcessItem
        self.running = False
        self.running_all = False
        self.current_item = 0
        self.set_interval(300, self.run_all)

    def compose(self) -> ComposeResult:
        for p in self._auth_processes:
            yield AuthProcessItem(p)

    def action_run_auth(self):
        self.running = True
        self._highlighted.status.value = ProcessStatus.RUNNING
        self._highlighted.run_auth()

    def on_list_view_selected(self, event: ListView.Selected):
        logger.debug(f"Opening {event.item}")
        proc: AuthProcessItem = event.item  # type: ignore
        proc_name = proc.process_config.name
        log_value = proc.process_config.log_stream.getvalue()
        self.post_message(UpdateLogMessage(proc_name, log_value))

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        logger.debug(f"Item is {event.item}")
        self._highlighted = event.item  # type: ignore

    def run_all(self):
        self.running_all = True
        self.running = True
        self.current_item = 0
        self.run_next()

    def run_next(self):
        if self.current_item >= len(self.children):
            self.running_all = False
        else:
            self.running = True
            item: AuthProcessItem = self.children[self.current_item]  # type: ignore
            item.run_auth()

    @on(AuthRunCompleteMessage)
    def handle_auth_run_complete(self):
        self.running = False
        if self.running_all:
            self.current_item += 1
            self.run_next()


class ProcessLogHeader(Widget):
    process = reactive("none")

    def render(self):
        return f"Log for process: {self.process}"


class LogScreen(ModalScreen):
    BINDINGS = [Binding("x", "close_log", "Close")]

    def __init__(self, auth_name: str, log_value: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_name = auth_name
        self.log_value = log_value

    def compose(self) -> ComposeResult:
        yield Label(f"Log for {self.auth_name}")
        yield Rule()

        log = Log()
        yield log
        log.write(self.log_value)
        yield Footer()

    def action_close_log(self):
        self.app.pop_screen()


class AuthTUI(App):
    BINDINGS = [Binding("q", "quit", "Quit")]
    CSS_PATH = "tui.tcss"

    def __init__(self, processes: list[AuthProcess], **kwargs):
        super().__init__(**kwargs)
        self._processes = processes

    def compose(self) -> ComposeResult:
        yield AuthProcessList(self._processes, id="auth_list")
        yield Footer()

    @on(UpdateLogMessage)
    def handle_update_log(self, msg: UpdateLogMessage):
        self.push_screen(LogScreen(msg.proc_name, msg.log_value))


def run_tui(config_file: str):
    logger.addHandler(TextualHandler())
    processes = load_config(config_file)
    app = AuthTUI(processes)
    app.run()
