"""Semantic embedding generation."""

from typing import Optional
import numpy as np
from csf.semantic.vectorizer import SemanticVectorizer


class SemanticEmbedding:
    """
    Generates semantic embeddings from text.
    """

    def __init__(self, vector_dim: int = 128):
        """
        Initialize semantic embedding generator.

        Args:
            vector_dim: Embedding dimension
        """
        self.vectorizer = SemanticVectorizer(vector_dim)

    def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        return self.vectorizer.text_to_vector(text)
