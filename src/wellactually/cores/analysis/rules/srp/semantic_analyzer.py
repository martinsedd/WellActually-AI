"""
Semantic clustering of methods using embeddings.
"""

import numpy as np
from sklearn.cluster import DBSCAN

from wellactually.cores.persistence.vectorizer import Vectorizer


class SemanticAnalyzer:
    """
    Uses embeddings to cluster methods semantically and detect unrelated concerns.
    """
    
    def __init__(self) -> None:
        self.vectorizer = Vectorizer()
    
    def cluster_methods(self, method_signatures: list[str]) -> tuple[int, float]:
        """
        Cluster methods by semantic similarity.

        Args:
            method_signatures: List of method signatures (e.g., ["def create_user(name,
            email)", "def send_email(to, subject)"])

        Returns:
            Tuple of (number_of_clusters, silhouette_score)
        """
        if len(method_signatures) < 2:
            return 1, 0.0
        
        embeddings = self.vectorizer.vectorize_batch(method_signatures)
        embeddings_array = np.array(embeddings)
        
        clustering = DBSCAN(eps=0.5, min_samples=2, metric="cosine").fit(embeddings_array)
        
        labels = clustering.labels_
        
        num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        if num_clusters <= 1:
            separation_score = 0.0
        else:
            separation_score = min(0.3 * num_clusters, 1.0)
        
        return num_clusters, separation_score
    
    def calculate_semantic_diversity(self, method_names: list[str]) -> float:
        """
        Calculate semantic diversity score for a list of method names.
        
        :return: Score from 0.0 (cohesive) to 1.0 (diverse/scattered)
        """
        if len(method_names) < 2:
            return 0.0
        
        signatures = [f"def {name}()" for name in method_names]
        
        num_clusters, separation_score = self.cluster_methods(signatures)
        
        return separation_score
