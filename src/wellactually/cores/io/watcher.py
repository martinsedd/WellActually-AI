from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class DebouncedHandler(FileSystemEventHandler):
    """
    Watchdog event handler with deboucing and temp file filtering.
    """

    def __init__(self, callback: Callable[[Path], None], debouce_seconds: float = 1.0) -> None:
        self.callback = callback
        self.debouce_seconds = debouce_seconds
        self.pending_files: set[Path] = set()
        self.lock = asyncio.Lock()
        self.task: asyncio.Task[None] | None = None

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = Path(str(event.src_path))

        if self._is_temp_file(file_path):
            return

        if not self._is_supported_file(file_path):
            return

        asyncio.create_task(self._schedule_processing(file_path))

    def _is_temp_file(self, path: Path) -> bool:
        """Check if file is a temporary file that should be ignored."""
        temp_patterns = {".swp", ".swo", ".swn", "~", ".tmp", ".bak"}
        return any(path.name.endswith(pattern) for pattern in temp_patterns) or path.name.startswith(".")

    def _is_supported_file(self, path: Path) -> bool:
        """Check if file type is supported for analysis."""
        supported_extensions = {".py", ".ts", ".tsx", ".js", ".jsx"}
        return path.suffix in supported_extensions

    async def _schedule_processing(self, file_path: Path) -> None:
        """Schedule file processing with debouce."""
        async with self.lock:
            self.pending_files.add(file_path)

            if self.task is not None and not self.task.done():
                self.task.cancel()

            self.task = asyncio.create_task(self._process_after_delay())

    async def _process_after_delay(self) -> None:
        """Process pending files after debouce delay."""
        await asyncio.sleep(self.debouce_seconds)

        async with self.lock:
            files_to_process = self.pending_files.copy()
            self.pending_files.clear()

        for file_path in files_to_process:
            self.callback(file_path)


class FileWatcher:
    """
    Manages file system watching with debounced event handling.
    """

    def __init__(self, path: Path, callback: Callable[[Path], None], debouce_seconds: float = 1.0) -> None:
        self.path = path
        self.callback = callback
        self.debouce_seconds = debouce_seconds
        self.observer: Any | None = None
        self.handler: DebouncedHandler | None = None

    def start(self) -> None:
        """Start watching the file system."""
        self.handler = DebouncedHandler(self.callback, self.debouce_seconds)
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.path), recursive=True)
        self.observer.start()

    def stop(self) -> None:
        """Stop watching the file system."""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
