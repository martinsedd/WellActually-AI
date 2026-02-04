"""
Output formatting helpers for orchestration workflows.
"""

from rich.console import Console

console = Console()


def print_check_result(passed: bool, message: str) -> None:
    """Print a preflight check result with color coding."""
    icon = "[bold green]✓[/bold green]" if passed else "[bold red]X[/bold red]"
    console.print(f"{icon} {message}")


def print_header(text: str) -> None:
    console.print(f"[bold yellow]{text}[/bold yellow]")


def print_info(text: str) -> None:
    console.print(f"[cyan]{text}[/cyan]")


def print_success(text: str) -> None:
    console.print(f"[green]{text}[/green]")


def print_warning(text: str) -> None:
    console.print(f"[yellow]{text}[/yellow]")


def print_error(text: str) -> None:
    console.print(f"[bold red]{text}[/bold red]")


def print_dim(text: str) -> None:
    console.print(f"[dim]{text}[/dim]")
