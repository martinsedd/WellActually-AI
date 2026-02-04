"""
Typer application definition with base commands.
"""

import asyncio
from pathlib import Path

import typer
from rich.console import Console

from wellactually.cores.io.doctor import check_compiler, check_gpu, check_ollama
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
    foggie: bool = typer.Option(
        False,
        "--foggie",
        help="Enable shame mode (boring                                                                            feedback)",
    ),
) -> None:
    """
    Watch a directory for file changes and provide real-time architectural feedback.
    """
    path_obj = Path(path).resolve()

    if not path_obj.exists():
        console.print(f"[bold red]Error:[/bold red] Path does not exist: {path}")
        raise typer.Exit(1)

    if not path_obj.is_dir():
        console.print(f"[bold red]Error:[/bold red] Path is not a directory: {path}")
        raise typer.Exit(1)

    asyncio.run(run_watch_mode(path_obj, foggie))


@app.command()
def init(
    path: str = typer.Argument(".", help="Path to initialize"),
) -> None:
    """
    Initialize WellActually for a project (runs Genesis Scan).
    """
    path_obj = Path(path).resolve()

    if not path_obj.exists():
        console.print(f"[bold red]Error:[/bold red] Path does not exist: {path}")
        raise typer.Exit(1)

    if not path_obj.is_dir():
        console.print(f"[bold red]Error:[/bold red] Path is not a directory: {path}")
        raise typer.Exit(1)

    asyncio.run(run_init_mode(path_obj))


@app.command()
def doctor() -> None:
    """
    Run pre-flight checks: GPU availability, Ollama connection, C-compiler status.
    """
    console.print("[bold cyan]Running pre-flight checks...[/bold cyan]\n")

    gpu_ok, gpu_msg = check_gpu()
    console.print(f"[bold green]✓[/bold green] {gpu_msg}" if gpu_msg else f"[bold red]x[/bold red] {gpu_msg}")

    compiler_ok, compiler_msg = check_compiler()
    console.print(
        f"[bold green]✓[/bold green] {compiler_msg}" if compiler_ok else f"[bold red]x[/bold red] {compiler_msg}"
    )

    async def check_ollama_async() -> None:
        ollama_ok, ollama_msg = await check_ollama()
        console.print(f"[bold green]✓[/bold green] {ollama_msg}" if ollama_ok else f"[bold red]x[/bold] {ollama_msg}")

    asyncio.run(check_ollama_async())

    console.print()
    if gpu_ok and compiler_ok:
        console.print("[bold green]System is ready for WellActually![/bold green]")
    else:
        console.print("[bold yellow]Some checks failed. Please resolve issues before running.[/bold yellow]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """
    Show WellActually version.
    """
    from wellactually import __version__

    console.print(f"WellActually v{__version__}")
