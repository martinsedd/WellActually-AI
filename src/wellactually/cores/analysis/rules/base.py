"""
Base rule interface for architectural analysis.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class Violation:
    """
    Represents a detected code violation.
    """

    rule_name: str
    severity: str  # "low", "medium", "high", "critical"
    file_path: str
    line_number: int
    code_snippet: str
    message: str
    context: str | None = None


class BaseRule(ABC):
    """
    Abstract base class for analysis rules.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Rule name (e.g., 'SRP', 'DRY')."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the rule."""
        ...

    @abstractmethod
    def analyze(self, file_path: str, context: dict[str, Any]) -> list[Violation]:
        """
        Analyze code and detect violations.

        Args:
            code: The code to analyze
            file_path: Path to the file being analyzed
            context: Additional context (graph data, file location, etc.)

        Returns:
            List of detected violations
        """
        ...


class ThresholdRule(BaseRule):
    """
    Base class for rules that check if a metric exceeds a threshold.
    """

    def __init__(self, threshold: int) -> None:
        self.threshold = threshold

    @property
    @abstractmethod
    def context_key(self) -> str:
        """Key in context dict containing items to check (e.g., 'functions', 'classes')."""
        ...

    @property
    def metric_key(self) -> str:
        return self.name.lower()

    @property
    @abstractmethod
    def item_name_key(self) -> str:
        """Key in item dict containing the item name (e.g., 'name')."""
        ...

    @abstractmethod
    def format_snippet(self, item: dict[str, Any]) -> str:
        """Format code snippet for the violation"""
        ...

    @abstractmethod
    def format_message(self, item: dict[str, Any], metric_value: int) -> str:
        """Format violation message."""
        ...

    def calculate_severity(self, metric_value: int) -> str:
        """
        Caculate severity based on threshold multipliers.

        Override for custom severity logic.
        """
        if metric_value > self.threshold * 3:
            return "critical"
        elif metric_value > self.threshold * 2:
            return "high"
        elif metric_value > self.threshold:
            return "medium"
        else:
            return "low"

    def analyze(self, file_path: str, context: dict[str, Any]) -> list[Violation]:
        """
        Generic threshold-based analysis.
        """
        violations: list[Violation] = []
        items = context.get(self.context_key, [])

        for item in items:
            metric_value = item.get(self.metric_key, 0)

            if metric_value > self.threshold:
                violations.append(
                    Violation(
                        rule_name=self.name,
                        severity=self.calculate_severity(metric_value),
                        file_path=file_path,
                        line_number=item.get("start_line", 0),
                        code_snippet=self.format_snippet(item),
                        message=self.format_message(item, metric_value),
                        context=f"{self.item_name_key.title()}: {item.get(self.item_name_key, 'unknown')}",
                    )
                )
        return violations
