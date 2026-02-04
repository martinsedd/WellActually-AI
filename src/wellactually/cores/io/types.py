"""
Type definitions for Core-IO.
"""

from dataclasses import dataclass


@dataclass
class PreflightResult:
    """
    Result of pre-flight system checks.
    """

    gpu_available: bool
    gpu_message: str

    compiler_available: bool
    compiler_message: str

    ollama_available: bool
    ollama_message: str

    @property
    def all_passed(self) -> bool:
        return self.gpu_available and self.compiler_available and self.ollama_available

    @property
    def critical_passed(self) -> bool:
        return self.gpu_available and self.compiler_available
