"""
Structure facade - High-level API for structural analysis and graph operations.
"""

from pathlib import Path
from typing import Any

from wellactually.cores.structure.graph.kuzu_manager import KuzuManager
from wellactually.cores.structure.parsers.python_parser import PythonParser
from wellactually.cores.structure.queries import ViolationQueries
from wellactually.cores.structure.scanner import GenesisScanner


class StructureFacade:
    """
    High-level facade for all structural analysis operations

    Orchestrator interacts wit this class without needing to know about Tree-sitter,
    KuzuDB, or parsing internals.
    """

    def __init__(self, project_root: Path, db_path: Path | None = None) -> None:
        self.project_root = project_root
        self.kuzu = KuzuManager(db_path)
        self.scanner = GenesisScanner(self.kuzu)
        self.queries = ViolationQueries(self.kuzu)
        self.parsers = {
            ".py": PythonParser(),
        }

    def run_genesis_scan(self, extensions: list[str] | None = None) -> None:
        """
        Perform a full project scan to build the code graph.

        Args:
            extensions: File extensions to scan (defaults to [".py"])
        """
        self.scanner.scan_project(self.project_root, extensions)

    def update_file(self, file_path: Path) -> None:
        """
        Update the graph for a single file (incremental update).

        Args:
            file_path: Path to changed file
        """
        if not file_path.exists():
            relative_path = str(file_path.relative_to(self.project_root))
            self.kuzu.delete_file(relative_path)
            return

        extension = file_path.suffix
        parser = self.parsers.get(extension)

        if parser is None:
            return  # Unsupported file type

        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(self.project_root)

            self.kuzu.delete_file(str(relative_path))

            file_node, classes, functions = parser.parse_file(relative_path, content)
            imports = parser.get_imports(content)

            self.kuzu.add_file(file_node)

            for class_node in classes:
                self.kuzu.add_class(class_node)
            for func_node in functions:
                self.kuzu.add_function(func_node)
            for module_path, imported_names in imports:
                # HACK: Simplified: just store the import, resolution handled elsewhere
                # TODO: In prod, would need proper module resolution
                pass

        except Exception as e:
            print(f"Error updating file {file_path}: {e}")

    def find_circular_dependencies(self) -> list[dict[str, Any]]:
        """Find circular import dependencies."""
        return self.queries.find_circular_dependencies()

    def find_layer_violations(
        self, domain_pattern: str = "domain", infra_pattern: str = "infra"
    ) -> list[dict[str, Any]]:
        """Find violations where domain imports from infrastructure."""
        return self.queries.find_layer_violations(domain_pattern, infra_pattern)

    def find_god_classes(self, threshold: int = 10) -> list[dict[str, Any]]:
        """Find classes with excessive methods."""
        return self.queries.find_god_classes(threshold)

    def find_high_complexity_functions(self, threshold: int = 10) -> list[dict[str, Any]]:
        """Find functions with high cyclomatic complexity."""
        return self.queries.find_high_complexity_functions(threshold)

    def get_file_dependencies(self, file_path: str) -> list[dict[str, Any]]:
        """Get all dependencies for a file."""
        return self.queries.get_file_dependencies(file_path)

    def get_blast_radius(self) -> list[dict[str, Any]]:
        """Calculate blast radius (centrality) for all files."""
        return self.queries.calculate_file_centrality()

    def close(self) -> None:
        self.kuzu.close()
