import sqlite3

import yaml


def bootstrap_tui_config(input_config: str, output_config: str):
    tui_config = []
    with sqlite3.connect(input_config) as conn:
        res = conn.execute("SELECT * FROM aws_profiles").fetchall()
        for r in res:
            profile_name = r[0]
            tui_config.append(
                {"name": f"AWS ({profile_name})", "type": "aws", "profile": profile_name}
            )

        res = conn.execute("SELECT * FROM dbx_profiles").fetchall()
        for r in res:
            profile_name = r[0]
            alias = r[1]
            config_entry = {
                "name": f"Databricks ({profile_name})",
                "type": "dbx",
                "profile": profile_name,
            }
            if alias:
                config_entry["alias"] = alias
            tui_config.append(config_entry)

        res = conn.execute("SELECT kion_cli_config_file FROM config").fetchall()
        if res[0][0]:
            tui_config.append({"name": "Kion", "type": "kion-cli", "config": res[0][0]})

    with open(output_config, "w") as f:
        yaml.dump(tui_config, f)
