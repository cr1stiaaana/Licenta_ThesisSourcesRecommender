"""Ingestion pipeline for the Hybrid Thesis Recommender.

Parses JSON, CSV, and BibTeX files, generates embeddings, detects article
language, and upserts articles into the ArticleStore.  After ingestion the
BM25 index is rebuilt and persisted to disk.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from app.article_store import ArticleStore
from app.config import AppConfig
from app.language_detector import LanguageDetector
from app.models import Article

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# IngestionReport
# ---------------------------------------------------------------------------


@dataclass
class IngestionReport:
    """Summary of a single ingestion run."""

    ingested: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# IngestionPipeline
# ---------------------------------------------------------------------------


class IngestionPipeline:
    """Parses article files and indexes them into the ArticleStore.

    Args:
        article_store: The target store for articles and embeddings.
        config: Application configuration (embedding model, BM25 index path, …).
        language_detector: Used to detect the language of each article's title.
    """

    def __init__(
        self,
        article_store: ArticleStore,
        config: AppConfig,
        language_detector: LanguageDetector,
    ) -> None:
        self._store = article_store
        self._config = config
        self._language_detector = language_detector
        self._model: SentenceTransformer | None = None

    # ── Embedding model (lazy-loaded, cached) ────────────────────────────────

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self._config.embedding_model)
        return self._model

    # ── Article ID computation ────────────────────────────────────────────────

    @staticmethod
    def _compute_id(doi: str | None, title: str) -> str:
        """Return SHA-256 of the DOI (preferred) or the normalized title."""
        if doi and doi.strip():
            source = doi.strip().lower()
        else:
            source = title.strip().lower()
        return hashlib.sha256(source.encode("utf-8")).hexdigest()

    # ── Embedding generation ──────────────────────────────────────────────────

    def _embed(self, text: str) -> np.ndarray:
        """Encode *text* into a 768-dimensional float32 vector."""
        model = self._get_model()
        vec = model.encode(text, convert_to_numpy=True)
        return np.array(vec, dtype=np.float32)

    # ── BM25 index rebuild ────────────────────────────────────────────────────

    def _rebuild_bm25(self) -> None:
        """Rebuild the BM25 index from the current ArticleStore corpus and persist it."""
        corpus = self._store.get_all_texts()
        if not corpus:
            logger.warning("BM25 rebuild skipped: article store is empty.")
            return
        bm25 = BM25Okapi(corpus)
        index_path = Path(self._config.bm25_index_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(index_path, "wb") as fh:
            pickle.dump(bm25, fh)
        logger.info("BM25 index rebuilt and saved to %s (%d docs).", index_path, len(corpus))

    # ── Format parsers ────────────────────────────────────────────────────────

    @staticmethod
    def _parse_json(path: str) -> list[dict[str, Any]]:
        """Parse a JSON file containing an array of article objects."""
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            raise ValueError(f"JSON file must contain a top-level array, got {type(data).__name__}")
        return data  # type: ignore[return-value]

    @staticmethod
    def _parse_csv(path: str) -> list[dict[str, Any]]:
        """Parse a CSV file with column headers matching Article fields."""
        records: list[dict[str, Any]] = []
        with open(path, encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                records.append(dict(row))
        return records

    @staticmethod
    def _parse_bibtex(path: str) -> list[dict[str, Any]]:
        """Parse a BibTeX file using bibtexparser."""
        import bibtexparser  # type: ignore[import-untyped]

        with open(path, encoding="utf-8") as fh:
            bib_database = bibtexparser.load(fh)

        records: list[dict[str, Any]] = []
        for entry in bib_database.entries:
            record: dict[str, Any] = {
                "title": entry.get("title", ""),
                "abstract": entry.get("abstract", ""),
                "doi": entry.get("doi", ""),
                "url": entry.get("url", ""),
                "year": entry.get("year", ""),
                "keywords": entry.get("keywords", ""),
            }
            # BibTeX author field is typically "Last, First and Last2, First2"
            author_raw = entry.get("author", "")
            if author_raw:
                record["authors"] = [a.strip() for a in author_raw.split(" and ") if a.strip()]
            else:
                record["authors"] = []
            records.append(record)
        return records

    # ── Record normalisation ──────────────────────────────────────────────────

    @staticmethod
    def _normalise_record(raw: dict[str, Any]) -> dict[str, Any]:
        """Coerce raw field values to the expected Python types."""
        # title / abstract — strip whitespace
        title = (raw.get("title") or "").strip()
        abstract = (raw.get("abstract") or "").strip() or None

        # authors — may be a list already (JSON) or a comma/semicolon-separated string (CSV)
        authors_raw = raw.get("authors", [])
        if isinstance(authors_raw, list):
            authors = [str(a).strip() for a in authors_raw if str(a).strip()]
        elif isinstance(authors_raw, str) and authors_raw.strip():
            # Try semicolon first, then comma
            sep = ";" if ";" in authors_raw else ","
            authors = [a.strip() for a in authors_raw.split(sep) if a.strip()]
        else:
            authors = []

        # year — coerce to int or None
        year_raw = raw.get("year")
        year: int | None = None
        if year_raw is not None and str(year_raw).strip():
            try:
                year = int(str(year_raw).strip())
            except ValueError:
                year = None

        # doi / url — strip whitespace, treat empty string as None
        doi = (raw.get("doi") or "").strip() or None
        url = (raw.get("url") or "").strip() or None

        # keywords — may be a list (JSON) or a comma/semicolon-separated string (CSV/BibTeX)
        keywords_raw = raw.get("keywords", [])
        if isinstance(keywords_raw, list):
            keywords = [str(k).strip() for k in keywords_raw if str(k).strip()]
        elif isinstance(keywords_raw, str) and keywords_raw.strip():
            sep = ";" if ";" in keywords_raw else ","
            keywords = [k.strip() for k in keywords_raw.split(sep) if k.strip()]
        else:
            keywords = []

        return {
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "year": year,
            "doi": doi,
            "url": url,
            "keywords": keywords,
        }

    # ── Core ingestion logic ──────────────────────────────────────────────────

    def _ingest_records(self, records: list[dict[str, Any]]) -> IngestionReport:
        """Process a list of raw records and upsert valid ones into the store."""
        report = IngestionReport()

        for idx, raw in enumerate(records):
            record_id = raw.get("doi") or raw.get("title") or f"record[{idx}]"
            try:
                norm = self._normalise_record(raw)

                # Requirement 7.4 — skip records missing title or abstract
                if not norm["title"]:
                    logger.warning(
                        "Skipping record %r: missing title.", record_id
                    )
                    report.skipped += 1
                    continue

                if not norm["abstract"]:
                    logger.warning(
                        "Skipping record %r: missing abstract.", record_id
                    )
                    report.skipped += 1
                    continue

                # Compute article ID (Req 7.5 — incremental upsert by stable ID)
                article_id = self._compute_id(norm["doi"], norm["title"])

                # Detect language from title (Req 7.7)
                language = self._language_detector.detect(norm["title"])

                # Build Article dataclass
                article = Article(
                    id=article_id,
                    title=norm["title"],
                    abstract=norm["abstract"],
                    authors=norm["authors"],
                    year=norm["year"],
                    doi=norm["doi"],
                    url=norm["url"],
                    keywords=norm["keywords"],
                    language=language,
                )

                # Generate embedding from title + abstract (Req 7.2)
                combined_text = f"{article.title} {article.abstract}"
                embedding = self._embed(combined_text)

                # Upsert into ArticleStore (Req 7.2, 7.3, 7.5)
                self._store.add_article(article, embedding)
                report.ingested += 1

            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Failed to ingest record %r: %s", record_id, exc, exc_info=True
                )
                report.failed += 1
                report.errors.append(f"Record {record_id!r}: {exc}")

        return report

    # ── Public API ────────────────────────────────────────────────────────────

    def ingest_file(
        self,
        path: str,
        format: Literal["json", "csv", "bibtex"],  # noqa: A002
    ) -> IngestionReport:
        """Parse *path* in the given *format* and index all valid articles.

        Args:
            path: Filesystem path to the input file.
            format: One of ``"json"``, ``"csv"``, or ``"bibtex"``.

        Returns:
            An :class:`IngestionReport` with counts of ingested, skipped, and
            failed records.

        Raises:
            ValueError: If *format* is not one of the supported values.
            FileNotFoundError: If *path* does not exist.
        """
        if format not in ("json", "csv", "bibtex"):
            raise ValueError(
                f"Unsupported format {format!r}. Must be one of: 'json', 'csv', 'bibtex'."
            )

        logger.info("Starting ingestion of %r (format=%s).", path, format)

        # Parse the file into raw records
        try:
            if format == "json":
                records = self._parse_json(path)
            elif format == "csv":
                records = self._parse_csv(path)
            else:  # bibtex
                records = self._parse_bibtex(path)
        except Exception as exc:
            logger.error("Failed to parse file %r: %s", path, exc, exc_info=True)
            report = IngestionReport()
            report.failed += 1
            report.errors.append(f"Parse error: {exc}")
            return report

        logger.info("Parsed %d records from %r.", len(records), path)

        # Ingest records
        report = self._ingest_records(records)

        # Rebuild BM25 index after ingestion (Req 7.3)
        if report.ingested > 0:
            try:
                self._rebuild_bm25()
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to rebuild BM25 index: %s", exc, exc_info=True)
                report.errors.append(f"BM25 rebuild error: {exc}")

        logger.info(
            "Ingestion complete: ingested=%d, skipped=%d, failed=%d.",
            report.ingested,
            report.skipped,
            report.failed,
        )
        return report
