"""
Core-IO: File system monitoring, event debouncing, and hardware checks

Public API for I/O operations and system validation
"""

from wellactually.cores.io.facade import IOFacade
from wellactually.cores.io.types import PreflightResult

__all__ = ["IOFacade", "PreflightResult"]
