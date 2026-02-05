"""
Method-level analysis for SRP detection
"""

import re


class MethodAnalyzer:
    """
    Analyzes methods for naming patterns and semantic grouping.
    """

    # Verb categories mapping concerns
    VERB_CATEGORIES = {
        "data": {
            "create",
            "read",
            "get",
            "fetch",
            "update",
            "delete",
            "save",
            "load",
            "insert",
            "remove",
            "find",
            "query",
        },
        "validation": {"validate", "check", "verify", "ensure", "assert", "test", "confirm"},
        "transformation": {
            "convert",
            "transform",
            "map",
            "serialize",
            "deserialize",
            "parse",
            "format",
            "encode",
            "decode",
        },
        "communication": {"send", "fetch", "notify", "publish", "subscribe", "request", "respond", "emit", "broadcast"},
        "calculation": {"calculate", "compute", "sum", "count", "average", "process", "analyze"},
        "orchestration": {"execute", "run", "perform", "handle", "manage", "coordinate", "dispatch"},
    }

    def extract_verb_categories(self, method_names: list[str]) -> dict[str, int]:
        """
        Categorize methods by their verb to identify distinct concerns.

        Args:
            method_names: List of method names

        Returns:
            Dict mapping category to count of methods in that category
        """
        category_counts: dict[str, int] = {}

        for method_name in method_names:
            verb = self._extract_verb(method_name)

            for category, verbs in self.VERB_CATEGORIES.items():
                if verb in verbs:
                    category_counts[category] = category_counts.get(category, 0) + 1
                    break

        return category_counts

    def _extract_verb(self, method_name: str) -> str:
        """
        Extract the verb from a method name;

        Examples:
            create_user -> create
            getUserById -> get
            validateEmail -> validate
        """
        # Handle snake_case
        if "_" in method_name:
            return method_name.split("_")[0].lower()

        # Handle camelCase - split on uppercase
        words = re.findall(r"^[a-z]+|[A-Z][a-z]*", method_name)
        if words:
            return words[0].lower()

        return method_name.lower()

    def calculate_concert_diversity(self, category_counts: dict[str, int]) -> float:
        """
        Calculate a diversity score for method concerns.

        Return:
            Score from 0.0 (single concern) to 1.0 (many diverse concerns)
        """
        if not category_counts:
            return 0.0

        total_methods = sum(category_counts.values())
        num_categories = len(category_counts)

        if num_categories == 1:
            return 0.0

        # Calculate Shannon entropy for diversity
        entropy = 0.0
        for count in category_counts.values():
            proportion = count / total_methods
            if proportion > 0:
                entropy -= proportion * (proportion**0.5)  # simplified

        max_entropy = 1.0
        return min(entropy / max_entropy, 1.0)
