"""
IO facade - High-level API for file watching and system checks.
"""

from pathlib import Path
from typing import Callable

from wellactually.cores.io.doctor import check_compiler, check_gpu, check_ollama
from wellactually.cores.io.types import PreflightResult
from wellactually.cores.io.watcher import FileWatcher


class IOFacade:
    """
    High-level facade for I/O operations and system validation.

    Orchestrator interacts with this class without needing to know about Watchdog
    internals or individual check functions.
    """

    def __init__(self) -> None:
        self.watcher: FileWatcher | None = None

    @staticmethod
    async def run_preflight_checks() -> PreflightResult:
        """
        Run all pre-flight system checks.

        Returns:
            PreflightResult with all check statuses
        """
        gpu_ok, gpu_msg = check_gpu()
        compiler_ok, compiler_msg = check_compiler()
        ollama_ok, ollama_msg = await check_ollama()

        return PreflightResult(
            gpu_available=gpu_ok,
            compiler_available=compiler_ok,
            ollama_available=ollama_ok,
            gpu_message=gpu_msg,
            compiler_message=compiler_msg,
            ollama_message=ollama_msg,
        )

    def start_watching(
        self,
        path: Path,
        callback: Callable[[Path], None],
        debounce_seconds: float = 1.0,
    ) -> None:
        """
        Start watching a directory for file changes.

        Args:
            path: Directory to watch
            callback: Function to call when files change
            debounce_seconds: Debounce delay in seconds
        """
        if self.watcher is not None:
            raise RuntimeError("Watcher is already running")

        self.watcher = FileWatcher(path, callback, debounce_seconds)
        self.watcher.start()

    def stop_watching(self) -> None:
        if self.watcher is not None:
            self.watcher.stop()
            self.watcher = None
