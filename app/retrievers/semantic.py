"""SemanticRetriever: dense vector search using a multilingual sentence-transformer model."""

from __future__ import annotations

import numpy as np

from app.article_store import ArticleStore
from app.config import AppConfig
from app.models import Query, RetrievalResult


class SemanticRetrieverError(Exception):
    """Raised when the semantic retriever encounters a model or index failure."""


class SemanticRetriever:
    """Retrieves articles by cosine similarity against a FAISS vector index.

    The embedding model is loaded once at construction time so that startup
    fails fast if the model is unavailable, rather than failing on the first
    query.
    """

    def __init__(self, article_store: ArticleStore, config: AppConfig) -> None:
        self._article_store = article_store
        self._config = config
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            self._model: SentenceTransformer = SentenceTransformer(config.embedding_model)
        except Exception as exc:
            raise SemanticRetrieverError(
                f"Failed to load embedding model '{config.embedding_model}': {exc}"
            ) from exc

    # ── Public API ────────────────────────────────────────────────────────────

    def encode(self, text: str) -> np.ndarray:
        """Encode *text* into a 768-dimensional embedding vector.

        The vector is normalized to unit length for cosine similarity.

        Exposed as a public method so that ``ContentVerifier`` can reuse the
        same model instance without loading a second copy.

        Raises:
            SemanticRetrieverError: if the model raises during encoding.
        """
        try:
            vector: np.ndarray = self._model.encode(text, convert_to_numpy=True)
            # Normalize to unit length for cosine similarity
            vector = vector / np.linalg.norm(vector)
            return vector
        except Exception as exc:
            raise SemanticRetrieverError(f"Encoding failed: {exc}") from exc

    def retrieve(self, query: Query, top_k: int) -> RetrievalResult:
        """Encode *query* and return the top-*k* most similar articles.

        Cosine similarity scores from the FAISS inner-product index are in
        ``[-1, 1]`` for unit-normalized vectors. Scores are returned as-is.

        Args:
            query:  The user query; ``query.combined_text()`` is encoded.
            top_k:  Maximum number of results to return.

        Returns:
            A :class:`~app.models.RetrievalResult` with ``source="semantic"``.

        Raises:
            SemanticRetrieverError: on model encoding failure or FAISS error.
        """
        try:
            query_embedding = self.encode(query.combined_text())
        except SemanticRetrieverError:
            raise
        except Exception as exc:
            raise SemanticRetrieverError(f"Failed to encode query: {exc}") from exc

        try:
            raw_results = self._article_store.search_vector(query_embedding, top_k)
        except Exception as exc:
            raise SemanticRetrieverError(f"FAISS index search failed: {exc}") from exc

        # Scores are already cosine similarities in [-1, 1], use as-is
        from app.models import ScoredArticle

        results = [
            ScoredArticle(
                article=sa.article,
                score=float(sa.score),
            )
            for sa in raw_results
        ]

        return RetrievalResult(items=results, source="semantic")
