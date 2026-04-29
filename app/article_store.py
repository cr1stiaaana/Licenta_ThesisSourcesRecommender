"""ArticleStore: FAISS vector index + SQLite metadata store for academic articles."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

import faiss
import numpy as np

from app.models import Article, ScoredArticle

_EMBEDDING_DIM = 768

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    abstract TEXT,
    authors TEXT,
    year INTEGER,
    doi TEXT,
    url TEXT,
    keywords TEXT,
    language TEXT,
    faiss_idx INTEGER
)
"""


class ArticleStore:
    """Stores article embeddings in a FAISS index and metadata in SQLite."""

    def __init__(self, vector_store_path: str, metadata_db_path: str) -> None:
        self._vector_store_path = vector_store_path
        self._metadata_db_path = metadata_db_path

        # ── FAISS index ──────────────────────────────────────────────────────
        if os.path.exists(vector_store_path):
            self._index: faiss.IndexFlatIP = faiss.read_index(vector_store_path)
        else:
            self._index = faiss.IndexFlatIP(_EMBEDDING_DIM)

        # ── SQLite metadata DB ───────────────────────────────────────────────
        Path(metadata_db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(metadata_db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(_CREATE_TABLE_SQL)
        self._conn.commit()

        # ── In-memory id ↔ faiss_idx mappings ───────────────────────────────
        self._id_to_faiss_idx: dict[str, int] = {}
        self._faiss_idx_to_id: dict[int, str] = {}
        self._load_mappings()

    # ── Private helpers ──────────────────────────────────────────────────────

    def _load_mappings(self) -> None:
        """Populate in-memory mappings from the database at startup."""
        cursor = self._conn.execute("SELECT id, faiss_idx FROM articles WHERE faiss_idx IS NOT NULL")
        for row in cursor:
            article_id: str = row["id"]
            faiss_idx: int = row["faiss_idx"]
            self._id_to_faiss_idx[article_id] = faiss_idx
            self._faiss_idx_to_id[faiss_idx] = article_id

    def _save_index(self) -> None:
        """Persist the FAISS index to disk."""
        Path(self._vector_store_path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, self._vector_store_path)

    @staticmethod
    def _row_to_article(row: sqlite3.Row) -> Article:
        """Convert a SQLite row to an Article dataclass."""
        authors_raw = row["authors"]
        keywords_raw = row["keywords"]
        authors: list[str] = json.loads(authors_raw) if authors_raw else []
        keywords: list[str] = json.loads(keywords_raw) if keywords_raw else []
        return Article(
            id=row["id"],
            title=row["title"],
            abstract=row["abstract"],
            authors=authors,
            year=row["year"],
            doi=row["doi"],
            url=row["url"],
            keywords=keywords,
            language=row["language"] or "en",
        )

    # ── Public API ───────────────────────────────────────────────────────────

    def add_article(self, article: Article, embedding: np.ndarray) -> None:
        """Upsert an article and its embedding.

        If the article already exists (by id), the metadata and FAISS vector
        are updated in-place.  If it is new, the embedding is appended to the
        FAISS index and a new row is inserted into SQLite.
        """
        vec = np.array(embedding, dtype=np.float32).reshape(1, _EMBEDDING_DIM)
        authors_json = json.dumps(article.authors)
        keywords_json = json.dumps(article.keywords)

        if article.id in self._id_to_faiss_idx:
            # ── Update existing ──────────────────────────────────────────────
            faiss_idx = self._id_to_faiss_idx[article.id]

            # FAISS IndexFlatIP does not support in-place replacement, so we
            # reconstruct the vector at the existing position by removing and
            # re-adding.  For a Flat index the simplest approach is to
            # reconstruct all vectors, replace the target, and rebuild.
            n = self._index.ntotal
            all_vecs = np.zeros((n, _EMBEDDING_DIM), dtype=np.float32)
            self._index.reconstruct_n(0, n, all_vecs)
            all_vecs[faiss_idx] = vec[0]
            self._index.reset()
            self._index.add(all_vecs)

            self._conn.execute(
                """
                UPDATE articles
                SET title=?, abstract=?, authors=?, year=?, doi=?, url=?,
                    keywords=?, language=?
                WHERE id=?
                """,
                (
                    article.title,
                    article.abstract,
                    authors_json,
                    article.year,
                    article.doi,
                    article.url,
                    keywords_json,
                    article.language,
                    article.id,
                ),
            )
        else:
            # ── Insert new ───────────────────────────────────────────────────
            faiss_idx = self._index.ntotal
            self._index.add(vec)

            self._conn.execute(
                """
                INSERT INTO articles
                    (id, title, abstract, authors, year, doi, url, keywords, language, faiss_idx)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    article.id,
                    article.title,
                    article.abstract,
                    authors_json,
                    article.year,
                    article.doi,
                    article.url,
                    keywords_json,
                    article.language,
                    faiss_idx,
                ),
            )
            self._id_to_faiss_idx[article.id] = faiss_idx
            self._faiss_idx_to_id[faiss_idx] = article.id

        self._conn.commit()
        self._save_index()

    def get_all_texts(self) -> list[list[str]]:
        """Return tokenized documents for BM25 index construction.

        Each document is ``title + " " + abstract + " " + keywords`` split by
        whitespace and lowercased.  Documents are returned in FAISS index order (by faiss_idx).
        """
        import re
        cursor = self._conn.execute(
            "SELECT title, abstract, keywords, faiss_idx FROM articles ORDER BY faiss_idx"
        )
        rows = cursor.fetchall()
        result: list[list[str]] = []
        for row in rows:
            title: str = row["title"] or ""
            abstract: str = row["abstract"] or ""
            keywords_raw = row["keywords"]
            keywords_list: list[str] = json.loads(keywords_raw) if keywords_raw else []
            keywords_str = " ".join(keywords_list)
            text = f"{title} {abstract} {keywords_str}"
            # Tokenize the same way as KeywordRetriever._tokenize()
            tokens = re.split(r"[\s\W]+", text.lower())
            result.append([t for t in tokens if t])
        return result

    def search_vector(self, query_embedding: np.ndarray, top_k: int) -> list[ScoredArticle]:
        """Search the FAISS index and return the top-k results.

        Returns an empty list when the index contains no vectors.
        Scores are raw FAISS inner-product values (caller normalizes).
        """
        if self._index.ntotal == 0:
            return []

        k = min(top_k, self._index.ntotal)
        vec = np.array(query_embedding, dtype=np.float32).reshape(1, _EMBEDDING_DIM)
        scores, indices = self._index.search(vec, k)

        results: list[ScoredArticle] = []
        for score, faiss_idx in zip(scores[0], indices[0]):
            if faiss_idx < 0:
                # FAISS returns -1 for padding when fewer results exist
                continue
            article_id = self._faiss_idx_to_id.get(int(faiss_idx))
            if article_id is None:
                continue
            row = self._conn.execute(
                "SELECT * FROM articles WHERE id=?", (article_id,)
            ).fetchone()
            if row is None:
                continue
            article = self._row_to_article(row)
            results.append(ScoredArticle(article=article, score=float(score)))

        return results

    def get_article_by_id(self, article_id: str) -> Article | None:
        """Look up an article by its id.  Returns None if not found."""
        row = self._conn.execute(
            "SELECT * FROM articles WHERE id=?", (article_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_article(row)

    def get_all_articles_ordered(self) -> list[Article]:
        """Return all articles ordered by faiss_idx (for BM25 corpus alignment)."""
        cursor = self._conn.execute("SELECT * FROM articles ORDER BY faiss_idx")
        return [self._row_to_article(row) for row in cursor.fetchall()]
