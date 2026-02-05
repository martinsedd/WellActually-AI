"""
Cyclomatic complexity rule.
"""

from typing import Any

from wellactually.cores.analysis.rules.base import BaseRule, ThresholdRule, Violation


class ComplexityRule(ThresholdRule):
    """
    Detects functions with excessive cyclomatic complexity.
    """

    @property
    def name(self) -> str:
        return "COMPLEXITY"

    @property
    def description(self) -> str:
        return f"Functions should have cyclomatic complexity <= {self.threshold}"

    @property
    def context_key(self) -> str:
        return "functions"

    @property
    def item_name_key(self) -> str:
        return "jname"

    def format_snippet(self, item: dict[str, Any]) -> str:
        return f"def {item.get('name', 'unknown')}(...):"

    def format_message(self, item: dict[str, Any], metric_value: int) -> str:
        return f"Function has complexity {metric_value} (threshold: {self.threshold})"
