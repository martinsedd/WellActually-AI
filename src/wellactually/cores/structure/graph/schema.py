"""
KuzuDB graph schema definitions for code structure.
"""

from dataclasses import dataclass


@dataclass
class FileNode:
    """Represents a source file in the codebase."""

    path: str  # Relative path from project root
    language: str  # Python, Typescript, etc...
    lines_of_code: int


@dataclass
class ClassNode:
    """Represents a class or interface definition"""

    name: str
    file_path: str
    start_line: int
    end_line: int
    is_abstract: bool
    method_count: int


@dataclass
class FunctionNode:
    """Represents a function or method definition"""

    name: str
    file_path: str
    start_line: int
    end_line: int
    complexity: int  # Cyclomatic complexity
    parent_class: str | None  # None for module-level functions


@dataclass
class ImportNode:
    """Represents an import statement."""

    from_file: str
    to_module: str
    imported_named: list[str]


# Cypher DDL for creating the graph schema
SCHEMA_DDL = """
-- Node tables
CREATE NODE TABLE IF NOT EXISTS File(
    path STRING PRIMARY KEY,
    language STRING,
    lines_of_code INT64
);

CREATE NODE TABLE IF NOT EXISTS Class(
    id STRING PRIMARY KEY,
    name STRING,
    file_path STRING,
    start_line INT64,
    end_line INT64,
    is_abstract BOOLEAN,
    method_count INT64
);

CREATE NODE TABLE IF NOT EXISTS Function(
    id STRING PRIMARY KEY,
    name STRING,
    file_path STRING,
    start_line INT64,
    end_line INT64,
    complexity INT64,
    parent_class STRING
);

-- Relationship tables
CREATE REL TABLE IF NOT EXISTS IMPORTS(
    FROM File TO File,
    imported_names STRING[]
);

CREATE REL TABLE IF NOT EXISTS DEPENDS_ON(
    FROM Class TO Class
);

CREATE REL TABLE IF NOT EXISTS CALLS(
    FROM Function TO Function
);

CREATE REL TABLE IF NOT EXISTS DEFINES(
    FROM File TO Class
);

CREATE REL TABLE IF NOT EXISTS CONTAINS(
    FROM Class TO Function
);
"""
