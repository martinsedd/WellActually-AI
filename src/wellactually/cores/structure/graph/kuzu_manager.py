"""
KuzuDB connection and graph operations
"""

from pathlib import Path
from typing import Any

import kuzu

from wellactually.cores.structure.graph.schema import SCHEMA_DDL, ClassNode, FileNode, FunctionNode


class KuzuManager:
    """
    Manages KuzuDB embedded graph database for code structure
    """

    def __init__(self, db_path: Path | None = None) -> None:
        if db_path is None:
            db_path = Path.cwd() / ".wellactually" / "graph"

        self.db_path = db_path
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.db = kuzu.Database(str(self.db_path))
        self.conn = kuzu.Connection(self.db)

        self._init_schema()

    def _init_schema(self) -> None:
        """Create graph schema if it doesn't exist."""
        # Split DDL by semicolons and execute each statement
        statements = [s.strip() for s in SCHEMA_DDL.split(";") if s.strip()]
        for statement in statements:
            try:
                self.conn.execute(statement)
            except Exception:
                # Schema might already exist, continue
                pass

    def add_file(self, file_node: FileNode) -> None:
        query = """
        MERGE (f:File {path: $path})
        SET f.language = $language, f.lines_of_code = $lines_of_code
        """

        self.conn.execute(
            query,
            {
                "path": file_node.path,
                "language": file_node.language,
                "lines_of_code": file_node.lines_of_code,
            },
        )

    def add_class(self, class_node: ClassNode) -> None:
        class_id = f"{class_node.file_path}::{class_node.name}"

        query = """
        MERGE (c:Class {id: $id})
        SET c.name = $name, c.file_path = $file_path,
            c.start_line = $start_line, c.end_line = $end_line,
            c.is_abstract = $is_abstract, c.method_count = $method_count
        """

        self.conn.execute(
            query,
            {
                "id": class_id,
                "name": class_node.name,
                "file_path": class_node.file_path,
                "start_line": class_node.start_line,
                "end_line": class_node.end_line,
                "is_abstract": class_node.is_abstract,
                "method_count": class_node.method_count,
            },
        )

        # Create DEFINES relationship from File to Class
        defines_query = """
        MATCH (f:File {path: $file_path}), (c:Class {id: $class_id})
        MERGE (f)-[:DEFINES]->(c)
        """

        self.conn.execute(defines_query, {"file_path": class_node.file_path, "class_id": class_id})

    def add_function(self, function_node: FunctionNode) -> None:
        func_id = f"{function_node.file_path}::{function_node.name}"

        query = """
        MERGE (fn:Function {id: $id})
        SET fn.name = $name, fn.file_path = $file_path,
            fn.start_line = $start_line, fn.end = $end_line,
            fn.complexity = $complexity, fn.parent_class = $parent_class
        """

        self.conn.execute(
            query,
            {
                "id": func_id,
                "name": function_node.name,
                "file_path": function_node.file_path,
                "start_line": function_node.start_line,
                "end_line": function_node.end_line,
                "complexity": function_node.complexity,
                "parent_class": function_node.parent_class or "",
            },
        )

        # If a function belongs to a class, create CONTAINS relationship
        if function_node.parent_class:
            class_id = f"{function_node.file_path}::{function_node.parent_class}"
            contains_query = """
            MATCH (c:Class {id: $class_id}), (fn:Function {id: $func_id})
            MERGE (c)-[:CONTAINS]->(fn)
            """
            self.conn.execute(contains_query, {"class_id": class_id, "func_id": func_id})

    def add_import(self, from_file: str, to_module: str, imported_names: list[str]) -> None:
        query = """
        MATCH (f1:File {path: $from_file}), (f2:File {path: $to_module})
        MERGE (f1)-[i:IMPORTS]->(f2)
        SET i.imported_names = $imported_names
        """

        self.conn.execute(
            query,
            {
                "from_file": from_file,
                "to_module": to_module,
                "imported_names": imported_names,
            },
        )

    def delete_file(self, file_path: str) -> None:
        # Delete all classes and functions in this file
        self.conn.execute("MATCH (c:Class {file_path: $path}) DETACH DELETE c", {"path": file_path})
        self.conn.execute("MATCH (fn:Function {file_path: $path}) DETACH DELETE fn", {"path": file_path})
        # Delete the file itself
        self.conn.execute("MATCH (f:File {path: $path}) DETACH DELETE f", {"file": file_path})

    def execute_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Execute a raw Cypher query.

        Args:
            query: Cypher query string
            params: Query parameters

        Returns:
            List of result records as dictionaries
        """
        result = self.conn.execute(query, params or {})
        rows: list[dict[str, Any]] = []

        if isinstance(result, list):
            for query_result in result:
                try:
                    for row in query_result:
                        rows.append(dict(row))
                except Exception:
                    pass
        else:
            try:
                for row in result:
                    rows.append(dict(row))
            except Exception:
                pass

        return rows

    def close(self) -> None:
        # KuzuDB auto-closes, but keeping it here for consistency
        pass
