"""
Core-Orchestration: Workflow management and dependency wiring.

The only core allowed to import other cores.
Manages workflows (Watch vs Report) and coordinates cross-core operations.
"""

from wellactually.cores.orchestration.workflows import run_init_mode, run_watch_mode

__all__ = ["run_watch_mode", "run_init_mode"]
