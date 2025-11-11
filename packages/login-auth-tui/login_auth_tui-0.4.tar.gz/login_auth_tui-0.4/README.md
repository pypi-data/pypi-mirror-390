# login-auth-tui

[![Changelog](https://img.shields.io/pypi/v/login-auth-tui)](https://git.sr.ht/~nwgh/login-auth-tui/log)

[![builds.sr.ht status](https://builds.sr.ht/~nwgh/login-auth-tui.svg)](https://builds.sr.ht/~nwgh/login-auth-tui?)

[![License](https://img.shields.io/badge/license-CC0%201.0-blue.svg)](https://git.sr.ht/~nwgh/login-auth-tui/tree/main/item/LICENSE)

TUI for login-auth stuff

## Installation

Install this tool using `uv`:

```bash
uv tool install auth-manage --from login-auth-tui
```

## Usage

For help, run:

```bash
auth-manage --help
```

## Development

To contribute to this tool, first install `uv`. See [the uv documentation](https://docs.astral.sh/uv/getting-started/installation/) for how.

Next, checkout the code

```bash
git clone https://git.sr.ht/~nwgh/login-auth-tui
```

Then create a new virtual environment and sync the dependencies:

```bash
cd login-auth-tui
uv sync
```

To run the tests:

```bash
uv run python -m pytest
```
