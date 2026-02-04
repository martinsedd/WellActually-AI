"""
Workflow orchestration for watch and init modes.
"""

import asyncio
from pathlib import Path

from wellactually.cores.inference.facade import InferenceFacade
from wellactually.cores.io.facade import IOFacade
from wellactually.cores.orchestration.output import (
    print_check_result,
    print_dim,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
)


async def run_watch_mode(path: Path, foggie: bool = False) -> None:
    """
    Run the watch workflow: monitor files and provide real-time feedback.

    Args:
        path: Directory to watch
        foggie: Enable shame mode (boring feedback)
    """
    print_header("Starting watch mode...")

    io_facade = IOFacade()
    inference_facade = InferenceFacade()

    preflight = await io_facade.run_preflight_checks()

    print_check_result(preflight.gpu_available, preflight.gpu_message)
    print_check_result(preflight.compiler_available, preflight.compiler_message)
    print_check_result(preflight.ollama_available, preflight.ollama_message)

    if not preflight.all_passed:
        print_warning("Cannot proceed without required dependencies. Exiting.")
        return

    print_dim("Initializing inference engine...")
    init_ok = await inference_facade.initialize()
    if not init_ok:
        print_error("Failed to initialize inference engine. Exiting.")
        return

    print("")
    print_info(f"Watching: {path}")
    if foggie:
        print_dim("(Shame mode enabled)")

    # Callback for file changes
    def on_file_changed(file_path: Path) -> None:
        print_warning(f"File changed: {file_path}")
        # TODO: Wire to Core-Analysis and inference_facade

    io_facade.start_watching(path, on_file_changed, debounce_seconds=1.0)

    try:
        print_success("Watching for changes... (Ctrl+C to stop)")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("")
        print_warning("Stopping watch mode...")
    finally:
        io_facade.stop_watching()
        await inference_facade.close()


async def run_init_mode(path: Path) -> None:
    """
    Run the init workflow: perform Genesis Scan and build project graph.

    Args:
        path: Project directory to initialize
    """
    print_header("Initializing project...")
    print_info(f"Path: {path}")

    io_facade = IOFacade()
    preflight = await io_facade.run_preflight_checks()

    print_check_result(preflight.gpu_available, preflight.gpu_message)
    print_check_result(preflight.compiler_available, preflight.compiler_message)

    if not preflight.critical_passed:
        print_warning("Cannot proceed without required dependencies.")
        return

    print("")
    print_warning("Genesis Scan will be implemented in Phase 1")
    # TODO: Wire to Core-Structure for Genesis Scan
