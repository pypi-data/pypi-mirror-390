from __future__ import annotations

import os
import subprocess
from pathlib import Path

import click
from click.exceptions import Abort, Exit
from llama_deploy.appserver.app import prepare_server, start_preflight_in_target_venv
from llama_deploy.appserver.deployment_config_parser import get_deployment_config
from llama_deploy.appserver.settings import configure_settings, settings
from llama_deploy.appserver.workflow_loader import (
    load_environment_variables,
    parse_environment_variables,
    validate_required_env_vars,
)
from llama_deploy.cli.commands.aliased_group import AliasedGroup
from llama_deploy.cli.commands.serve import (
    _maybe_inject_llama_cloud_credentials,
    _print_connection_summary,
)
from llama_deploy.cli.commands.serve import (
    serve as serve_command,
)
from llama_deploy.cli.options import global_options, interactive_option
from llama_deploy.core.config import DEFAULT_DEPLOYMENT_FILE_PATH
from llama_deploy.core.deployment_config import DeploymentConfig
from rich import print as rprint

from ..app import app


@app.group(
    name="dev",
    help="Development utilities for llama-deploy projects",
    cls=AliasedGroup,
    no_args_is_help=True,
)
@global_options
def dev() -> None:
    """Collection of development commands."""


dev.add_command(serve_command, name="serve")


@dev.command(
    "validate",
    help="Load configured workflows and run their validation hooks",
)
@click.argument(
    "deployment_file",
    required=False,
    default=DEFAULT_DEPLOYMENT_FILE_PATH,
    type=click.Path(dir_okay=True, resolve_path=True, path_type=Path),
)
@interactive_option
@global_options
def validate_command(deployment_file: Path, interactive: bool) -> None:
    """Validate workflows defined in the deployment configuration."""
    config_dir = _ensure_project_layout(
        deployment_file, command_name="llamactl dev validate"
    )
    # Ensure cloud credentials/env are available to the subprocess (if required)
    _maybe_inject_llama_cloud_credentials(
        deployment_file, interactive, require_cloud=False
    )

    prepare_server(
        deployment_file=deployment_file,
        install=True,
        build=False,
        install_ui_deps=False,
    )

    # Delegate venv-targeted invocation to the appserver helper (mirrors start_server_in_target_venv)

    try:
        start_preflight_in_target_venv(cwd=Path.cwd(), deployment_file=deployment_file)
    except subprocess.CalledProcessError as exc:
        rprint("[red]Workflow validation failed. See errors above.[/red]")
        raise Exit(exc.returncode)

    _print_connection_summary()
    rprint(f"[green]Validated workflows in {config_dir} successfully.[/green]")


@dev.command(
    "run",
    help=(
        "Load env configuration and execute a command. Use '--' before the command "
        "to avoid option parsing."
    ),
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@global_options
@click.option(
    "deployment_file",
    "--deployment-file",
    default=DEFAULT_DEPLOYMENT_FILE_PATH,
    type=click.Path(dir_okay=True, resolve_path=True, path_type=Path),
    help="The deployment file to use for the command",
)
@click.option(
    "no_auth",
    "--no-auth",
    is_flag=True,
    help="Do not inject/authenticate with Llama Cloud credentials",
)
@interactive_option
@click.argument("cmd", nargs=-1, type=click.UNPROCESSED)
def run_command(
    deployment_file: Path, no_auth: bool, interactive: bool, cmd: tuple[str, ...]
) -> None:  # type: ignore
    """Execute COMMAND with deployment environment variables applied."""
    if not cmd:
        raise click.ClickException(
            "No command provided. Use '--' before the command arguments if needed."
        )

    try:
        config, config_parent = _prepare_environment(
            deployment_file, interactive, require_cloud=not no_auth
        )
        env_overrides = parse_environment_variables(config, config_parent)
        env = os.environ.copy()
        env.update({k: v for k, v in env_overrides.items() if v is not None})

        _print_connection_summary()
        result = subprocess.run(cmd, env=env, check=False)
        if result.returncode != 0:
            raise SystemExit(result.returncode)
    except (Exit, Abort, SystemExit, click.ClickException):
        raise
    except FileNotFoundError as exc:
        rprint(f"[red]Command not found: {exc.filename}[/red]")
        raise click.Abort()
    except Exception as exc:  # pragma: no cover - unexpected errors reported to user
        rprint(f"[red]Failed to run command: {exc}[/red]")
        raise click.Abort()


def _ensure_project_layout(deployment_file: Path, *, command_name: str) -> Path:
    if not deployment_file.exists():
        rprint(f"[red]Deployment file '{deployment_file}' not found[/red]")
        raise click.Abort()

    config_dir = deployment_file if deployment_file.is_dir() else deployment_file.parent
    if not (config_dir / "pyproject.toml").exists():
        rprint(
            "[red]No pyproject.toml found at[/red] "
            f"[bold]{config_dir}[/bold].\n"
            f"Add a pyproject.toml to your project and re-run '{command_name}'."
        )
        raise click.Abort()
    return config_dir


def _prepare_environment(
    deployment_file: Path, interactive: bool, *, require_cloud: bool
) -> tuple[DeploymentConfig, Path]:
    _maybe_inject_llama_cloud_credentials(
        deployment_file, interactive, require_cloud=require_cloud
    )
    configure_settings(
        deployment_file_path=deployment_file,
        app_root=Path.cwd(),
    )
    config = get_deployment_config()
    config_parent = settings.resolved_config_parent
    load_environment_variables(config, config_parent)
    validate_required_env_vars(config)
    return config, config_parent


__all__ = ["dev", "validate_command", "run_command"]
