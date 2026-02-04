"""
Embedding model integration for semantic violation vectorization.
"""

from sentence_transformers import SentenceTransformer


class Vectorizer:
    """
    Manages semantic embeddings for cross-language pattern recognition.

    Uses a lightweight CPU-based embedding model to vectorize code violations
    for similarity search across projects.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize the embedding mdoel.

        Args:
            model_name: HuggingFace model name. Default is a 384-dim lightweight model.
        """
        self.model_name = model_name
        self.model: SentenceTransformer | None = None

    def _ensure_model_loaded(self) -> None:
        """Lazy-load the model on first use."""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

    def vectorize(self, text: str) -> list[float]:
        """
        Convert text to a semantic vector embedding.

        Args:
            text: The text to vectorize (code snippet + violation context)

        Returns:
            384-dimensional vector embedding
        """
        self._ensure_model_loaded()
        assert self.model is not None

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def vectorize_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Convert multiple texts to embedding in batch.

        Args:
            texts: List of texts to vectorize

        Returns:
            List of 384-dimensional vector embeddings
        """
        self._ensure_model_loaded()
        assert self.model is not None

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def get_embedding_dimension(self) -> int:
        """
        Get the dimensionality of the embedding model.

        Return:
            Embedding dimension (384 for all-MiniLM-L6-v2)
        """
        self._ensure_model_loaded()
        assert self.model is not None

        dimension = self.model.get_sentence_embedding_dimension()
        if dimension is not None:
            return dimension
        return 0
