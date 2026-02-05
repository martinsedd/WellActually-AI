import multiprocessing as mp
from pathlib import Path

from rich.console import Console

from wellactually.cores.structure.graph.kuzu_manager import KuzuManager
from wellactually.cores.structure.graph.schema import ClassNode, FileNode, FunctionNode
from wellactually.cores.structure.parsers.python_parser import PythonParser

console = Console()


class GenesisScanner:
    """
    Performs a full project scan using multiprocessing to build the code graph.
    """

    def __init__(self, kuzu: KuzuManager) -> None:
        self.kuzu = kuzu
        self.parsers = {
            ".py": PythonParser(),
            # TODO: Add TypeScript parser
        }

    def scan_project(self, project_path: Path, extensions: list[str] | None = None) -> None:
        """
        Scan entire project and populate the graph database.

        Args:
            project_path: Root directory of the project
            extensions: File extensions to scan (defaults to [".py", ".ts", "tsx"])
        """
        if extensions is None:
            extensions = [".py"]

        files_to_parse = self._find_files(project_path, extensions)

        console.print(f"[cyan]Found {len(files_to_parse)} files to parse[/cyan]")

        cpu_count = mp.cpu_count()
        pool_size = max(1, cpu_count - 1)  # Leave one CPU free :)

        console.print(f"[dim]Using {pool_size} worker processes[/dim]")

        with mp.Pool(pool_size) as pool:
            results = pool.starmap(
                self._parse_file_worker, [(str(file_path), str(project_path)) for file_path in files_to_parse]
            )

        # Insert results into graph db (single-threaded to avoid DB lock contention)
        console.print("[dim]Inserting results into graph database...[/dim]")

        for result in results:
            if result is None:
                continue

            file_node, classes, functions, imports = result

            self.kuzu.add_file(file_node)

            for class_node in classes:
                self.kuzu.add_class(class_node)

            for func_node in functions:
                self.kuzu.add_function(func_node)

            for module_path, imported_names in imports:
                resolved_path = self._resolve_import(module_path, file_node.path, project_path)
                if resolved_path:
                    self.kuzu.add_import(file_node.path, resolved_path, imported_names)

        console.print(f"[green]Genesis Scan complete: {len(results)} files processed[/green]")

    def _find_files(self, root: Path, extensions: list[str]) -> list[Path]:
        """
        Find all files with given extensions in the project.

        Args:
            root: Root directory to search
            extensions: File extensions to include

        Returns:
            List of file paths
        """
        files: list[Path] = []

        for ext in extensions:
            files.extend(root.rglob(f"*{ext}"))

        ignore_patterns = {".venv", "venv", "node_modules", ".git", "__pycache__", ".pytest_cache", "dist", "build"}

        filtered = [f for f in files if not any(ignored in f.parts for ignored in ignore_patterns)]

        return filtered

    @staticmethod
    def _parse_file_worker(
        file_path: str, project_root: str
    ) -> tuple[FileNode, list[ClassNode], list[FunctionNode], list[tuple[str, list[str]]]] | None:
        """
        Worker function for multiprocessing: parse a single file.

        Args:
            file_path: Absolute path to the file
            project_root: Project root directory

        Returns:
            Tuple of (FileNode, classes, functions, imports) or None on error
        """
        try:
            path = Path(file_path)
            extension = path.suffix

            if extension == ".py":
                parser = PythonParser()
            else:
                return None

            content = path.read_text(encoding="utf-8")

            relative_path = path.relative_to(project_root)

            file_node, classes, functions = parser.parse_file(relative_path, content)
            imports = parser.get_imports(content)

            return file_node, classes, functions, imports
        except Exception as e:
            console.print(f"[red]Error parsing {file_path}: {e}[/red]")
            return None

    def _resolve_import(self, module_path: str, current_file: str, project_root: Path) -> str | None:
        """
        Resolve an import statement to an actual file path.

        Args:
            module_path: The imported module name (e.g., "wellactually.cores.io")
            current_file: Current file path doing the import
            project_root: Project root directory

        Returns:
            Resolved file path or None if not found
        """
        # Convert module path to file path
        # e.g., "wellactually.cores.io" -> "wellactually/cores/io.py" or
        # "wellactually/cores/io/__init__.py"

        parts = module_path.split(".")

        candidate = project_root / Path(*parts[:-1]) / f"{parts[-1]}.py"
        if candidate.exists():
            return str(candidate.relative_to(project_root))

        # Relative import handling would go here
        # For now, return None for unresolved imports
        return None
