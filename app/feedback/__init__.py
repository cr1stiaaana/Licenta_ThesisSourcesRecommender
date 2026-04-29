"""Feedback package: SQLite-backed user rating store."""

from app.feedback.store import FeedbackStore, FeedbackStoreError

__all__ = ["FeedbackStore", "FeedbackStoreError"]
