"""
Combined SRP scoring system.
"""

from dataclasses import dataclass


@dataclass
class SRPScore:
    """
    Breakdown of SRP violation score.
    """
    
    total_score: float
    semantic_score: float
    dependency_score: float
    naming_score: float
    method_count_score: float
    
    num_methods: int
    num_semantic_clusters: int
    num_dependency_concerns: int
    num_naming_categories: int
    
    layer_violations: list[str]
    
    @property
    def is_violation(self) -> bool:
        return self.total_score >= 0.7
    
    @property
    def severity(self) -> str:
        if self.total_score >= 0.9:
            return "critical"
        elif self.total_score >= 0.8:
            return "high"
        elif self.total_score >= 0.7:
            return "medium"
        else:
            return "low"
    
    def get_explanation(self) -> str:
        reasons: list[str] = []
        
        if self.semantic_score > 0.5:
            reasons.append(f"methods from {self.num_semantic_clusters} distinct semantic clusters")
        if self.dependency_score > 0.5:
            reasons.append(f"imports span {self.num_dependency_concerns} concern domains")
        if self.naming_score > 0.5:
            reasons.append(f"methods use {self.num_naming_categories} different verb categories")
        if self.layer_violations:
            reasons.append(f"violates architectural layers: {', '.join(self.layer_violations)}")
        
        if not reasons:
            return "Class appears to have a single, cohesive responsibility"
        
        return "Likely multiple responsibilities: " + "; ".join(reasons)


class SPRScorer:
    """Combines multiple signals to calculate SRP violation score."""
    
    # Signal weights
    SEMANTIC_WEIGHT = 0.4
    DEPENDENCY_WEIGHT = 0.3
    NAMING_WEIGHT = 0.2
    METHOD_COUNT_WEIGHT = 0.1
    
    def calculate_score(
            self,
            semantic_diversity: float,
            dependency_diversity: float,
            naming_diversity: float,
            method_count: int,
            expected_tolerance: int,
            num_semantic_clusters: int,
            num_dependency_concerns: int,
            num_naming_categories: int,
            layer_violations: list[str],
    ) -> SRPScore:
        """
        Calculate combined SRP score from multiple signals.

        :param semantic_diversity: Score from semantic clustering (0.0-1.0)
        :param dependency_diversity: Score from dependency clustering (0.0-1.0)
        :param naming_diversity: Score from method naming clustering (0.0-1.0)
        :param method_count: Total number of methods
        :param expected_tolerance: Expected method count for this layer
        :param num_semantic_clusters: Number of semantic clusters found
        :param num_dependency_concerns: Number of dependency concerns domains
        :param num_naming_categories: Number of distinct naming categories
        :param layer_violations: List of architectural layer violations

        :return: SRPScore with breakdown
        """
        if expected_tolerance > 0:
            ratio = method_count / expected_tolerance
            if ratio <= 1.0:
                method_count_score = 0.0
            elif ratio <= 2.0:
                method_count_score = 0.3
            else:
                method_count_score = min(0.6 + (ratio - 2.0) * 0.1, 1.0)
        else:
            method_count_score = 0.0
        
        layer_violation_boost = 0.2 if layer_violations else 0.0
        
        total_score = (
                self.SEMANTIC_WEIGHT * semantic_diversity
                + self.DEPENDENCY_WEIGHT * dependency_diversity
                + self.NAMING_WEIGHT * naming_diversity
                + self.METHOD_COUNT_WEIGHT * method_count_score
                + layer_violation_boost
        )
        
        total_score = min(max(total_score, 0.0), 1.0)
        
        return SRPScore(
            total_score=total_score,
            semantic_score=semantic_diversity,
            dependency_score=dependency_diversity,
            naming_score=naming_diversity,
            method_count_score=method_count_score,
            num_methods=method_count,
            num_semantic_clusters=num_semantic_clusters,
            num_dependency_concerns=num_dependency_concerns,
            num_naming_categories=num_naming_categories,
            layer_violations=layer_violations,
        )
