"""
Single Responsibility Principle rule.
"""

from wellactually.cores.analysis.rules.base import BaseRule, Violation


class SRPRule(BaseRule):
    """
    Detects SRP violations based on file location and architectural expectations

    Different locations have different SRP tolerance:
    - domain/: String (1 concert)
    - controllers/: Moderate (2-3 concerns)
    - services/: High (3-5 concerns)
    """

    def __init__(self) -> None:
        self.tolerance_map = {
            "domain": 1,
            "entity": 1,
            "controller": 3,
            "service": 5,
            "legacy": 999,  # Feels this way far too often (Ignored)
        }

    @property
    def name(self) -> str:
        return "SRP"

    @property
    def description(self) -> str:
        return "Single Responsibility Principle - classes should have one reason to change"

    def analyze(self, file_path: str, context: dict[str, Any]) -> list[Violation]:
        """Check if classes violate SRP based on their location"""
        violations: list[Violation] = []

        tolerance = self._get_tolerance_for_path(file_path)

        if tolerance == 999:
            # Legacy code is ignored (Ha! If only...)
            return violations

        classes = context.get("classes", [])

        for cls in classes:
            method_count = cls.get("method_count", 0)

            # SRP heuristic: method count is a rough proxy for responsibility count
            if method_count > tolerance * 3:
                violations.append(
                    Violation(
                        rule_name=self.name,
                        severity="high",
                        file_path=file_path,
                        line_number=cls.get("start_line", 0),
                        code_snippet=f"class {cls.get('name', 'unknown')}:",
                        message=f"Class likely has multiple responsibilities ({method_count} in {self._get_layer_name(file_path)} layer)",
                        context=f"Expected tolerance: {tolerance} concerns, found: {method_count // 3} estimated concerns",
                    )
                )

        return violations
