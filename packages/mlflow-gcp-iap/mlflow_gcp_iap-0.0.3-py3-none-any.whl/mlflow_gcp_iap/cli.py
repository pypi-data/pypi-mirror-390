"""Configuration CLI."""

import os

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.theme import Theme

from mlflow_gcp_iap import TokenRefresher
from mlflow_gcp_iap.config import Config
from mlflow_gcp_iap.test import run as run_test

console = Console(
    theme=Theme(
        {
            "success": "green bold",
            "error": "red bold",
            "warning": "yellow",
            "info": "cyan",
        }
    )
)


def get_config() -> Config:
    try:
        return Config()
    except (Exception, ValidationError) as e:
        console.print(f"[error]Unable to load configuration: {e}[/]")
        raise


cli = typer.Typer(no_args_is_help=True, add_completion=False, help="Configure IAP access.")


@cli.command(name="setup", help="Configure library to connect to MlFlow.")
def setup():
    if Config.local_file_path().exists():
        config = get_config()
        console.print("[info]Current configuration:[/]")
        console.print_json(config.model_dump_json(indent=2))
        if not Confirm.ask("[warning]Overwrite?[/]", console=console, default=True):
            console.print("[info]Kept current configuration.[/]")
            return

    mlflow_tracking_server = Prompt.ask("[info]MlFlow tracking server URL[/]", console=console)
    target_service_account = Prompt.ask("[info]Service account to impersonate[/]", console=console)
    iap_client_id = Prompt.ask("[info]IAP (OAuth 2.0) client ID[/]", console=console)
    config = Config(
        mlflow_tracking_server=mlflow_tracking_server,
        target_service_account=target_service_account,
        iap_client_id=iap_client_id,
    )

    config.save_to_file()
    console.print("[success]Configuration updated successfully:[/]")
    console.print_json(config.model_dump_json(indent=2))


@cli.command(name="show", help="Show current configuration.")
def show():
    # Tenta carregar configurações
    if Config.local_file_path().exists():
        config = get_config()
        console.print_json(config.model_dump_json(indent=2))
        return

    console.print("[warning]No configuration found.[/]")


@cli.command(name="test", help="Make a test run to MlFlow.")
def test():
    # Guarantee configuration is available
    try:
        _ = get_config()
    except:
        console.print("[warning]Confirm that the configuration has been initialized.[/]")
        return -1

    # Run test
    try:
        run_test()
    except Exception as e:
        console.print(f"[error]Test failed: {e}[/]")
        return -1

    console.print("[success]Test run successfully![/]")


@cli.command(name="cmd", help="Run authenticated CLI commands.")
def cmd(
    cmd: str = typer.Argument(
        help="Target command to run. Example: 'mlflow --help'.", allow_dash=True
    )
):
    with TokenRefresher():
        return os.system(cmd)
