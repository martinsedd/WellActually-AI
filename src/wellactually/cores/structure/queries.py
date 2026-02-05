"""
Cypher queries for detecting architectural violations.
"""

from typing import Any

from wellactually.cores.structure.graph.kuzu_manager import KuzuManager


class ViolationQueries:
    """
    Pre-defined Cypher queries for detecting structural violations.
    """

    def __init__(self, kuzu: KuzuManager) -> None:
        self.kuzu = kuzu

    def find_circular_dependencies(self) -> list[dict[str, Any]]:
        """
        Detect circular import dependencies between files.

        Returns:
            List of circular dependency paths
        """
        query = """
        MATCH path = (f1:File)-[:IMPORTS*]->(f1)
        WHERE length(path) > 1
        RETURN [node IN nodes(path) | node.path] AS cycle
        """

        return self.kuzu.execute_query(query)

    def find_layer_violations(
        self, domain_pattern: str = "domain", infra_pattern: str = "infra"
    ) -> list[dict[str, Any]]:
        """
        Detect violations where domain layer imports from infrastructure layer.

        Args:
            domain_pattern: Path pattern for domain layer (e.g., "domain", "core")
            infra_pattern: Path pattern for infrastructure layer (e.g., "infra",
                "infrastructure")

        Returns:
            List of layer violation records
        """
        query = """
        MATCH (domain:File)-[i:IMPORTS]->(infra:File)
        WHERE domain.path CONTAINS $domain_pattern
            AND infra.path CONTAINS $infra_pattern
        RETURN domain.path AS violating file,
            infra.path AS imported_file,
            i.imported_names AS symbols
        """
        return self.kuzu.execute_query(query, {"domain_pattern": domain_pattern, "infra_pattern": infra_pattern})

    def find_god_classes(self, method_threshold: int = 10) -> list[dict[str, Any]]:
        """
        Find classes with excessive methods (potential God Classes).

        Args:
            method_threshold: Minimum method count to flag as God Class

        Returns:
            List of God Class candidates
        """
        query = """
        MATCH (c:Class)
        WHERE c.method_count >= $threshold
        RETURN c.name AS class_name,
            c.file_path AS file_path,
            c.method_count AS method_count
        ORDER BY c.method_count DESC
        """
        return self.kuzu.execute_query(query, {"threshold": method_threshold})

    def find_high_complexity_functions(self, complexity_threshold: int = 10) -> list[dict[str, Any]]:
        """
        Find functions with high cyclomatic complexity.

        Args:
            complexity_threshold: Minimum complexity to flag

        Returns:
            List of complex function records
        """
        query = """
        MATCH (fn:Function)
        WHERE fn.complexity >= $threshold
        RETURN fn.name AS function_name,
                fn.file_path AS file_path,
                fn.start_line AS line,
                fn.complexity AS complexity
        ORDER BY fn.complexity DESC
        """
        return self.kuzu.execute_query(query, {"threshold": complexity_threshold})

    def get_file_dependencies(self, file_path: str) -> list[dict[str, Any]]:
        """
        Get all direct dependencies for a specific file.

        Args:
            file_path: Path to the file

        Returns:
            List of imported files
        """
        query = """
        MATCH (f:File {path: $file_path})-[i:IMPORTS]->(dep:File)
        RETURN dep.path AS dependency,
                i.imported_names AS imported_symbols
        """
        return self.kuzu.execute_query(query, {"file_path": file_path})

    def get_file_dependents(self, file_path: str) -> list[dict[str, Any]]:
        """
        Get all files that depend on a specific file (reverse dependencies).

        Args:
            file_path: Path to the file

        Returns:
            List of dependent files
        """
        query = """
        MATCH (dependent:File)-[i:IMPORTS]->(f:File {path: $file_path})
        RETURN dependent.path AS dependent_file,
                i.imported_names AS imported_symbols
        """
        return self.kuzu.execute_query(query, {"file_path": file_path})

    def calculate_file_centrality(self) -> list[dict[str, Any]]:
        """
        Calculate centrality (degree) for all files to identify hub files.
        Higher centrality = more connections = higher blast radius.

        Returns:
            List of files with their centrality scores
        """
        query = """
        MATCH (f:File)
        OPTIONAL MATCH (f)-[i:IMPORTS]->()
        WITH f, count(i) AS out_degree
        OPTIONAL MATCH ()-[i2:IMPORTS]->(f)
        WITH f, out_degree, count(i2) AS in_degree
        RETURN f.path AS file_path,
            (out_degree + in_degree) AS centrality
        ORDER BY centrality DESC
        """
        return self.kuzu.execute_query(query)
