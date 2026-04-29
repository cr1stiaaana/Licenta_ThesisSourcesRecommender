"""FeedbackStore: SQLite-backed persistence for user ratings."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from app.models import FeedbackQueryResult


class FeedbackStoreError(Exception):
    """Raised when the feedback database is unavailable or an operation fails."""


class FeedbackStore:
    """Persists and retrieves item ratings using a SQLite database."""

    def __init__(self, feedback_store_path: str) -> None:
        """Initialize the store, creating parent directories and the ratings table.

        Args:
            feedback_store_path: Path to the SQLite database file.

        Raises:
            FeedbackStoreError: If the database cannot be created or initialized.
        """
        self._db_path = feedback_store_path
        try:
            Path(feedback_store_path).parent.mkdir(parents=True, exist_ok=True)
            conn = self._connect()
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS ratings (
                        item_id    TEXT,
                        session_id TEXT,
                        query      TEXT,
                        rating     INTEGER,
                        updated_at TIMESTAMP,
                        UNIQUE(item_id, session_id)
                    )
                    """
                )
        except FeedbackStoreError:
            raise
        except Exception as exc:
            raise FeedbackStoreError(
                f"Failed to initialize feedback database at '{feedback_store_path}': {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        """Open a SQLite connection with check_same_thread=False for Flask."""
        try:
            return sqlite3.connect(self._db_path, check_same_thread=False)
        except Exception as exc:
            raise FeedbackStoreError(
                f"Cannot connect to feedback database '{self._db_path}': {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def upsert_rating(
        self,
        item_id: str,
        query: str,
        rating: int,
        session_id: str | None,
        timestamp: datetime,
    ) -> None:
        """Insert or replace a rating for the given (item_id, session_id) pair.

        Args:
            item_id: Identifier of the rated item.
            query: The search query associated with this rating.
            rating: Integer rating value (expected to be in [1, 5]).
            session_id: Browser/user session identifier (may be None).
            timestamp: When the rating was submitted.

        Raises:
            FeedbackStoreError: If the database operation fails.
        """
        try:
            conn = self._connect()
            with conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO ratings
                        (item_id, session_id, query, rating, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (item_id, session_id, query, rating, timestamp.isoformat()),
                )
        except FeedbackStoreError:
            raise
        except Exception as exc:
            raise FeedbackStoreError(
                f"Failed to upsert rating for item '{item_id}': {exc}"
            ) from exc

    def get_ratings(
        self,
        item_id: str,
        session_id: str | None,
    ) -> FeedbackQueryResult:
        """Return aggregated rating information for an item.

        - ``user_rating``: the rating submitted by ``session_id`` (None when
          ``session_id`` is None or no rating exists for that session).
        - ``average_rating``: mean rating across **all** sessions for the item
          (None when no ratings exist).
        - ``rating_count``: total number of ratings across all sessions.

        Returns a zero-count result (no error) when the item has no ratings.

        Args:
            item_id: Identifier of the item to query.
            session_id: Session to look up for ``user_rating`` (may be None).

        Raises:
            FeedbackStoreError: If the database operation fails.
        """
        try:
            conn = self._connect()
            conn.row_factory = sqlite3.Row

            # Aggregate stats across all sessions for this item
            agg_row = conn.execute(
                """
                SELECT COUNT(*) AS rating_count,
                       AVG(CAST(rating AS REAL)) AS average_rating
                FROM ratings
                WHERE item_id = ?
                """,
                (item_id,),
            ).fetchone()

            rating_count: int = agg_row["rating_count"] if agg_row else 0
            average_rating: float | None = (
                agg_row["average_rating"] if agg_row and agg_row["average_rating"] is not None else None
            )

            # Per-session rating (only when session_id is provided)
            user_rating: int | None = None
            if session_id is not None:
                user_row = conn.execute(
                    """
                    SELECT rating FROM ratings
                    WHERE item_id = ? AND session_id = ?
                    """,
                    (item_id, session_id),
                ).fetchone()
                if user_row is not None:
                    user_rating = int(user_row["rating"])

            return FeedbackQueryResult(
                item_id=item_id,
                user_rating=user_rating,
                average_rating=average_rating,
                rating_count=rating_count,
            )
        except FeedbackStoreError:
            raise
        except Exception as exc:
            raise FeedbackStoreError(
                f"Failed to retrieve ratings for item '{item_id}': {exc}"
            ) from exc
