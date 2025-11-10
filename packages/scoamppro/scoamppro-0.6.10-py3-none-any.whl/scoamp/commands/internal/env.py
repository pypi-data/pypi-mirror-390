import json
import typer
from rich import print
from rich.table import Table

from ...utils.api_utils import (
    get_env_cfg,
    switch_env,
)
from ...utils.error import ExitCode

app = typer.Typer(name="env", help="scoamp context operation")


@app.command(name="list", help="show env list")
def list_env():
    try:
        env_cfg = get_env_cfg()
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        print("Error: no or invalid auth info, use 'scoamp login' first")
        raise typer.Exit(ExitCode.LoginError)

    table = Table(title="Env List", show_lines=False, show_edge=True, show_header=False)
    for env in env_cfg["envs"]:
        if env == env_cfg["use"]:
            style = "magenta bold"
        else:
            style = None
        table.add_row(env, env_cfg["envs"][env]["endpoint"], style=style)
    print(table)


@app.command(name="use", help="switch to specified env")
def use_env(
    name: str = typer.Argument(..., help="env name"),
):
    try:
        switch_env(name)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        print("Error: no or invalid auth info, use 'scoamp login' first")
        raise typer.Exit(ExitCode.LoginError)
    except Exception as exc:
        print(f"Error: {str(exc)}")
        raise typer.Exit(ExitCode.DefaultError)

    print(f"Successfully Switched to env '{name}'!")
