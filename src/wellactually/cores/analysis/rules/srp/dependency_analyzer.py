"""
Dependency analysis for SRP detection.
"""


class DependencyAnalyzer:
    """
    Analyses class dependencies to identify distinct concert domains.
    """

    # Import patterns mapped to concern domains
    CONCERN_PATTERNS = {
        "persistence": {"db", "database", "sql", "orm", "repository", "dao", "model", "entity"},
        "communication": {"http", "requests", "api", "client", "socket", "email", "smtp", "webhook"},
        "serialization": {"json", "xml", "yaml", "pickle", "serialize", "marshal"},
        "validation": {"validator", "schema", "pydantic", "marshmallow", "cerberus"},
        "logging": {"logging", "logger", "log"},
        "caching": {"cache", "redis", "memcached"},
        "file_io": {"file", "path", "io", "os.path"},
        "datetime": {"datetime", "time", "timezone"},
        "security": {"auth", "jwt", "bcrypt", "hash", "crypto", "security"},
    }

    def analyze_imports(self, imports: list[str]) -> dict[str, int]:
        """
        Categorize imports into concert domains.

        Args:
            imports: List of import module names (e.g., ["sqlalchemy", "requests.api"])

        Returns:
            Dict mapping concern domain to count
        """
        concern_counts: dict[str, int] = {}

        for import_name in imports:
            import_lower = import_name.lower()

            for concern, patterns in self.CONCERN_PATTERNS.items():
                if any(pattern in import_lower for pattern in patterns):
                    concern_counts[concern] = concern_counts.get(concern, 0) + 1
                    break
        return concern_counts

    def calculate_dependency_diversity(self, concert_counts: dict[str, int]) -> float:
        """
        Calculate diversity score based on distinct concern domains.

        Return:
            Score from 0.0 (single concert) to 1.0 (many diverse concerns)
        """
        if not concert_counts:
            return 0.0

        num_concerns = len(concert_counts)
        match num_concerns:
            case 1:
                return 0.0
            case 2:
                return 0.3
            case 3:
                return 0.6
            case _:
                return min(0.6 + (num_concerns - 3) * 0.1, 1.0)

    def check_layer_violations(self, file_path: str, imports: list[str]) -> list[str]:
        """
        Check if a class imports from architecturally forbidden layers.

        Args:
            file_path: Path to the file being analyzed
            imports: List of import module names

        Return:
            List of violation descriptions
        """
        violations: list[str] = []
        path_lower = file_path.lower()

        if "domain" in path_lower or "entity" in path_lower:
            infra_imports = [
                imp
                for imp in imports
                if any(x in imp.lower() for x in ["infra", "infrastructure", "repository", "service"])
            ]
            if infra_imports:
                violations.append(f"Domain layer imports from infrastructure: {', '}.join(infra_imports[:3]")

        if "controller" in path_lower:
            db_imports = [
                imp for imp in imports if any(x in imp.lower() for x in ["sqlalchemy", "psycopg", "pymongo", "mysql"])
            ]
            if db_imports:
                violations.append(f"Controller imports database directly: {', '.join(db_imports[:3])}")

        return violations
