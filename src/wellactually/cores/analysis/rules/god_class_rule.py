"""
God Class detection rule.
"""

from typing import Any, Dict

from wellactually.cores.analysis.rules.base import ThresholdRule


class GodClassRule(ThresholdRule):
    """
    Detects classes with excessive methods (God Classes).
    """

    @property
    def name(self) -> str:
        return "GOD_CLASS"

    @property
    def description(self) -> str:
        return f"Classes should have <= {self.threshold} methods"

    @property
    def context_key(self) -> str:
        return "classes"

    @property
    def metric_key(self) -> str:
        return "method_count"

    @property
    def item_name_key(self) -> str:
        return "name"

    def format_snippet(self, item: Dict[str, Any]) -> str:
        return f"class {item.get('name', 'unknown')}:"

    def format_message(self, item: Dict[str, Any], metric_value: int) -> str:
        return f"Class has {metric_value} methods (threshold: {self.threshold})"
