"""
Base parser interface for Tree-sitter language parsers.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from wellactually.cores.structure.graph.schema import ClassNode, FileNode, FunctionNode


class BaseParser(ABC):
    """
    Abstract base class for language-specific parsers
    """

    @abstractmethod
    def parse_file(self, file_path: Path, content: str) -> tuple[FileNode, list[ClassNode], list[FunctionNode]]:
        """
        Parse a source file and extract structural information.

        Args:
            file_path: Path to the file being parsed
            content: File content as string

        Returns:
            Tuple of (FileNode, list of ClassNodes, list of FunctionNodes)
        """
        ...

    @abstractmethod
    def get_imports(self, content: str) -> list[tuple[str, list[str]]]:
        """
        Extract import statements from source code.

        Args:
            content: File content as string

        Returns:
            List of (module_path, imported_names) tuples
        """
        ...

    @abstractmethod
    def calculate_complexity(self, function_body: str) -> int:
        """
        Calculate cyclomatic complexity for a function.

        Args:
            function_body: Function source code

        Returns:
            Cyclomatic complexity score
        """
        ...
