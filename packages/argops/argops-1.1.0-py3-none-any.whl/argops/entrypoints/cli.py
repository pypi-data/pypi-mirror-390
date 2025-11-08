"""Define the command line interface."""

import logging
import traceback
from pathlib import Path
from typing import List, Optional

import typer

from argops.adapters.argocd import ArgoCD
from argops.adapters.console import Console
from argops.adapters.git import Git
from argops.adapters.gitea import Gitea

from .. import services
from . import utils

log = logging.getLogger(__name__)
cli = typer.Typer()


@cli.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(  # noqa: W0613, M511, B008
        None, "--version", callback=utils.version_callback, is_eager=True
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    repo_path: Path = typer.Option(Path("."), "--repo_path", "-r"),
) -> None:
    """Command line tool to smoothly interact with ArgoCD."""
    ctx.ensure_object(dict)
    utils.load_logger(verbose)
    ctx.obj["repo"] = Git(repo_path=repo_path)
    ctx.obj["console"] = Console()
    ctx.obj["argo"] = ArgoCD()
    ctx.obj["gitea"] = Gitea()
    ctx.obj["verbose"] = verbose


@cli.command()
def promote(
    ctx: typer.Context,
    src_dir: Path = typer.Option(
        "staging", "--src-dir", "-s", help="Name of the source directory"
    ),
    dest_dir: Path = typer.Option(
        "production",
        "--dest-dir",
        "-d",
        help="Name of the destination directory",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help=(
            "Perform a dry run, showing the differences without changing the "
            "files or directories"
        ),
    ),
    filters: List[str] = typer.Argument(
        None, help="List of environment, application or application sets to promote"
    ),
) -> None:
    """Promote argo applications between environments.

    If no filters are specified it will promote all applications under the current
    directory.
    """
    filters = filters or []
    # Until we refactor the print from the promote function we need to change the
    # default logger level as the diff is shown with log.info instead with the
    # console
    logging.getLogger().setLevel(logging.INFO)
    try:
        services.promote_changes(ctx.obj["repo"], src_dir, dest_dir, filters, dry_run)
    except Exception as error:
        if ctx.obj["verbose"]:
            raise error
        log.error(traceback.format_exception(None, error, error.__traceback__)[-1])
        ctx.obj["console"].bell()
        raise typer.Exit(code=1)


@cli.command()
def apply(
    ctx: typer.Context,
    environment: str = typer.Option(
        "staging",
        "--environment",
        "-e",
        help="Name of the destination environment",
    ),
) -> None:
    """Push, diff and sync the changes of an argocd application."""
    try:
        services.apply(
            environment=environment,
            argocd=ctx.obj["argo"],
            repo=ctx.obj["repo"],
            git_server=ctx.obj["gitea"],
            console=ctx.obj["console"],
        )
    except Exception as error:
        if ctx.obj["verbose"]:
            raise error
        log.error(traceback.format_exception(None, error, error.__traceback__)[-1])
        ctx.obj["console"].bell()
        raise typer.Exit(code=1)


if __name__ == "__main__":
    cli()
