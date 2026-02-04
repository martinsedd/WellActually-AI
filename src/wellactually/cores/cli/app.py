"""
Typer application definition with base commands.
"""

import asyncio
from pathlib import Path

import typer
from rich.console import Console

from wellactually.cores.io.facade import IOFacade
from wellactually.cores.orchestration.workflows import run_init_mode, run_watch_mode

app = typer.Typer(
    name="wellactually",
    help="An intervention, not a linter - context-aware architectural feedback",
    add_completion=False,
)

console = Console()


@app.command()
def watch(
    path: str = typer.Argument(".", help="Path to watch for file changes"),
    foggie: bool = typer.Option(False, "--foggie", help="Enable shame mode (boring feedback)"),
) -> None:
    """Watch a directory for file changes and provide real-time architectural feedback."""
    path_obj = Path(path).resolve()
    _check_path_is_valid(path_obj)

    asyncio.run(run_watch_mode(path_obj, foggie))


@app.command()
def init(path: str = typer.Argument(".", help="Path to initialize")) -> None:
    """Initialize WellActually for a project (runs Genesis Scan)."""
    path_obj = Path(path).resolve()
    _check_path_is_valid(path_obj)

    asyncio.run(run_init_mode(path_obj))


@app.command()
def doctor() -> None:
    """
    Run pre-flight checks: GPU availability, Ollama connection, C-compiler status.
    """
    console.print("[bold cyan]Running pre-flight checks...[/bold cyan]\n")

    async def run_checks() -> None:
        preflight = await IOFacade.run_preflight_checks()

        _print_check_result(preflight.gpu_available, preflight.gpu_message)
        _print_check_result(preflight.compiler_available, preflight.compiler_message)
        _print_check_result(preflight.ollama_available, preflight.ollama_message)

        console.print()
        if preflight.all_passed:
            console.print("[bold green]System is ready for WellActually![/bold green]")
        else:
            console.print("[bold yellow]Some checks failed. Please resolve issues before running.[/bold yellow]")
            raise typer.Exit(1)

    asyncio.run(run_checks())


@app.command()
def version() -> None:
    from wellactually import __version__

    console.print(f"WellActually v{__version__}")


def _check_path_is_valid(path: Path) -> None:
    if not path.exists():
        _print_error(f"Path does not exist: {path}")
        raise typer.Exit(1)

    if not path.is_dir():
        _print_error(f"Path is not a directory: {path}")
        raise typer.Exit(1)


def _print_check_result(passed: bool, message: str) -> None:
    icon = "[bold green]✓[/bold green]" if passed else "[bold red]X[/bold red]"
    console.print(f"{icon} {message}")


def _print_error(text: str) -> None:
    console.print(f"[bold red]Error: [/bold red] {text}")
