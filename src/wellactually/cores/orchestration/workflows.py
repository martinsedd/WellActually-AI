"""
Workflow orchestration for watch and init modes.
"""

import asyncio
from pathlib import Path

from rich.console import Console

from wellactually.cores.inference.ollama_client import OllamaClient
from wellactually.cores.io.doctor import check_compiler, check_gpu, check_ollama
from wellactually.cores.io.watcher import FileWatcher

console = Console()


async def run_watch_mode(path: Path, foggie: bool = False) -> None:
    """
    Run the watch workflow: monitor files and provide real-time feedback.

    Args:
        path: Directory to watch
        foggie: Enable shame mode (boring feedback)
    """
    console.print("[bold yellow]Starting watch mode...[/bold yellow]")

    # Pre-flight checks
    gpu_ok, gpu_msg = check_gpu()
    if not gpu_ok:
        console.print(f"[bold red]x[/bold red] {gpu_msg}")
        console.print("[yellow]WellActually required GPU acceleration. Exiting[/yellow]")
        return
    console.print(f"[bold green]✓[/bold green] {gpu_msg}")

    compiler_ok, compiler_msg = check_compiler()
    if not compiler_ok:
        console.print(f"[bold red]x[/bold red] {compiler_msg}")
        return
    console.print(f"[bold green]✓[/bold green] {compiler_msg}")

    ollama_ok, ollama_msg = await check_ollama()
    if not ollama_ok:
        console.print(f"[bold red]x[/bold red] {ollama_msg}")
        return
    console.print(f"[bold green]✓[/bold green] {ollama_msg}")

    ollama = OllamaClient()
    warmpup_ok = await ollama.warmup()
    if not warmpup_ok:
        console.print("[bold red] Failed to warm up GPU. Exiting.[/bold red]")
        await ollama.close()
        return

    console.print(f"\n[cyan]Watching:[/cyan] {path}")
    if foggie:
        console.print("[dim](Shame mode enabled)[/dim]")

    # ---
    def on_file_changed(file_path: Path) -> None:
        console.print(f"[yellow]File changed:[/yellow] {file_path}")
        # TODO: Wire to Core-Analysis and Core-Inference

    watcher = FileWatcher(path, on_file_changed, debouce_seconds=1.0)
    watcher.start()

    try:
        console.print("[green]Watching for changes... (Ctrl+C to stop)[/green]")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yello]Stopping watch mode...[/yellow]")
    finally:
        watcher.stop()


async def run_init_mode(path: Path) -> None:
    """
    Run the init workflow: perform Genesis Scan and build project graph.

    Args:
        path: Project directory to initialize
    """
    console.print("[bold green]Initializing project...[/bold green]")
    console.print(f"[cyan]Path:[/cyan] {path}")

    # Pre-flight checks
    gpu_ok, gpu_msg = check_gpu()
    console.print(f"[bold green]✓[/bold green] {gpu_msg}" if gpu_ok else f"[bold red]x[/bold red] {gpu_msg}")

    compiler_ok, compiler_msg = check_compiler()
    console.print(
        f"[bold green]✓[/bold green] {compiler_msg}" if compiler_ok else f"[bold red]x[/bold red] {compiler_msg}"
    )

    if not gpu_ok or not compiler_ok:
        console.print("[yellow]Cannot proceed without required dependencies.[/yellow]")
        return

    console.print("\n[yellow]Genesis Scan will be implemented in Phase 1[/yellow]")
    # TODO: Wire to Core-Structure for Genesis Scan
