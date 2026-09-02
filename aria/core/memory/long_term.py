"""SQLite long-term memory store with strict eviction and privacy guarantees."""

import logging
import sqlite3
from typing import Any

from aria.core.memory.schema import SCHEMA_SQL
from aria.core.pipeline.state import AssistantMode

logger = logging.getLogger(__name__)


class LongTermMemory:
    """Persistent SQLite memory store with explicit FIFO history eviction and LRU fact bounding."""

    def __init__(
        self,
        db_path: str = ":memory:",
        max_history_entries: int = 5000,
        max_facts_entries: int = 1000,
    ) -> None:
        self.db_path = db_path
        self.max_history_entries = max_history_entries
        self.max_facts_entries = max_facts_entries
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database connection, foreign keys, and schema."""
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()
        self.enforce_retention_policy()

    def save_turn(
        self,
        session_id: str,
        mode: AssistantMode,
        role: str,
        content: str,
    ) -> None:
        """Persist a conversation turn to history."""
        if not self._conn:
            return
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO conversation_history (session_id, mode, role, content)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, mode.value, role, content),
            )

    def get_recent_history(self, limit: int = 20) -> list[dict[str, Any]]:
        """Retrieve most recent conversational turns across sessions."""
        if not self._conn:
            return []
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT session_id, mode, role, content, created_at
            FROM conversation_history
            ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        # Return in chronological order
        return [dict(row) for row in reversed(rows)]

    def set_fact(
        self,
        key: str,
        value: str,
        category: str = "general",
        confidence: float = 1.0,
    ) -> None:
        """Upsert a user fact or long-term preference."""
        if not self._conn:
            return
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO user_facts (key, value, category, confidence, access_count, last_accessed_at)
                VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    category = excluded.category,
                    confidence = excluded.confidence,
                    access_count = user_facts.access_count + 1,
                    last_accessed_at = CURRENT_TIMESTAMP
                """,
                (key, value, category, confidence),
            )
        self._enforce_facts_bound()

    def get_fact(self, key: str) -> str | None:
        """Retrieve a specific fact by key and update access timestamp."""
        if not self._conn:
            return None
        cursor = self._conn.cursor()
        cursor.execute("SELECT value FROM user_facts WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            with self._conn:
                self._conn.execute(
                    """
                    UPDATE user_facts
                    SET access_count = access_count + 1, last_accessed_at = CURRENT_TIMESTAMP
                    WHERE key = ?
                    """,
                    (key,),
                )
            return str(row["value"])
        return None

    def get_all_facts(self) -> dict[str, str]:
        """Retrieve all active user facts."""
        if not self._conn:
            return {}
        cursor = self._conn.cursor()
        cursor.execute("SELECT key, value FROM user_facts")
        return {row["key"]: row["value"] for row in cursor.fetchall()}

    def set_preference(self, key: str, value: str) -> None:
        """Save a user preference key-value."""
        if not self._conn:
            return
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO user_preferences (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, value),
            )

    def get_preference(self, key: str, default: str | None = None) -> str | None:
        """Get preference by key."""
        if not self._conn:
            return default
        cursor = self._conn.cursor()
        cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
        row = cursor.fetchone()
        return str(row["value"]) if row else default

    def enforce_retention_policy(self) -> int:
        """Evict oldest conversation history rows exceeding maximum entries bound (FIFO)."""
        if not self._conn:
            return 0
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                DELETE FROM conversation_history
                WHERE id NOT IN (
                    SELECT id FROM conversation_history ORDER BY id DESC LIMIT ?
                )
                """,
                (self.max_history_entries,),
            )
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                logger.info(
                    "Evicted %d conversation history entries under retention policy.",
                    deleted_count,
                )
            return int(deleted_count)

    def _enforce_facts_bound(self) -> int:
        """Evict least recently accessed user facts exceeding maximum facts bound (LRU)."""
        if not self._conn:
            return 0
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                DELETE FROM user_facts
                WHERE key NOT IN (
                    SELECT key FROM user_facts ORDER BY last_accessed_at DESC LIMIT ?
                )
                """,
                (self.max_facts_entries,),
            )
            deleted_count = cursor.rowcount
            return int(deleted_count)

    def clear_all_memory(self) -> None:
        """Privacy purge: completely erase all conversation history, user facts, and preferences."""
        if not self._conn:
            return
        with self._conn:
            self._conn.execute("DELETE FROM conversation_history;")
            self._conn.execute("DELETE FROM user_facts;")
            self._conn.execute("DELETE FROM user_preferences;")
            self._conn.execute("DELETE FROM intent_audit_log;")
        logger.info("Executed complete privacy purge of all long-term memory.")

    def vacuum(self) -> None:
        """Reclaim unused storage space."""
        if self._conn:
            self._conn.execute("VACUUM;")

    def close(self) -> None:
        """Close SQLite database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
