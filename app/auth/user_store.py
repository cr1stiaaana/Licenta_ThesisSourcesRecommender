"""User authentication and saved items store."""

from __future__ import annotations

import hashlib
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class User:
    """User account."""
    id: int
    username: str
    email: str
    created_at: datetime


@dataclass
class SavedItem:
    """A saved article or web resource."""
    id: int
    user_id: int
    item_data: dict[str, Any]  # Full article/web resource JSON
    saved_at: datetime


class UserStoreError(Exception):
    """Raised when the UserStore encounters an error."""


class UserStore:
    """Manages user accounts and saved items in SQLite."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS saved_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    item_id TEXT NOT NULL,
                    item_data TEXT NOT NULL,
                    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, item_id)
                )
            """)
            conn.commit()

    # ── User management ───────────────────────────────────────────────

    def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user account.
        
        Raises:
            UserStoreError: If username or email already exists.
        """
        password_hash = self._hash_password(password)
        
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, password_hash),
                )
                user_id = cursor.lastrowid
                conn.commit()
                
                return User(
                    id=user_id,
                    username=username,
                    email=email,
                    created_at=datetime.now(timezone.utc),
                )
        except sqlite3.IntegrityError as exc:
            if "username" in str(exc):
                raise UserStoreError("Username already exists") from exc
            if "email" in str(exc):
                raise UserStoreError("Email already exists") from exc
            raise UserStoreError("User creation failed") from exc

    def authenticate(self, username: str, password: str) -> User | None:
        """Authenticate a user by username and password.
        
        Returns:
            User if credentials are valid, None otherwise.
        """
        password_hash = self._hash_password(password)
        
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, username, email, created_at FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash),
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return User(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, username, email, created_at FROM users WHERE id = ?",
                (user_id,),
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return User(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    # ── Saved items ───────────────────────────────────────────────────

    def save_item(self, user_id: int, item_id: str, item_data: dict) -> None:
        """Save an item for a user.
        
        Uses INSERT OR REPLACE to handle duplicates.
        """
        import json
        
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO saved_items (user_id, item_id, item_data) VALUES (?, ?, ?)",
                (user_id, item_id, json.dumps(item_data)),
            )
            conn.commit()

    def unsave_item(self, user_id: int, item_id: str) -> None:
        """Remove a saved item for a user."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "DELETE FROM saved_items WHERE user_id = ? AND item_id = ?",
                (user_id, item_id),
            )
            conn.commit()

    def get_saved_items(self, user_id: int) -> list[dict]:
        """Get all saved items for a user."""
        import json
        
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT item_data, saved_at FROM saved_items WHERE user_id = ? ORDER BY saved_at DESC",
                (user_id,),
            )
            rows = cursor.fetchall()
            
            return [json.loads(row["item_data"]) for row in rows]

    def is_item_saved(self, user_id: int, item_id: str) -> bool:
        """Check if an item is saved by a user."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM saved_items WHERE user_id = ? AND item_id = ? LIMIT 1",
                (user_id, item_id),
            )
            return cursor.fetchone() is not None

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password using SHA-256.
        
        Note: In production, use bcrypt or argon2. SHA-256 is used here for simplicity.
        """
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
