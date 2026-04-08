"""Multi-level memory system with SQLite backend."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum


class MemoryType(Enum):
    """Memory type classifications."""
    SHORT_TERM = "short_term"      # Temporary, session-specific (1-7 days)
    LONG_TERM = "long_term"        # Persistent, important (indefinite)
    QUICK_NOTE = "quick_note"      # Quick thoughts/reminders (1-3 days)


class MemoryManager:
    """Manages multi-level memories with SQLite persistence."""

    def __init__(self, db_path: str = "memories.db"):
        """Initialize memory manager with SQLite database."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK(type IN ('short_term', 'long_term', 'quick_note')),
                    content TEXT NOT NULL,
                    tags TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    importance INTEGER DEFAULT 1
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON memories(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON memories(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)")
            conn.commit()

    def store_memory(
        self,
        content: str,
        memory_type: MemoryType,
        tags: Optional[list[str]] = None,
        importance: int = 1,
    ) -> int:
        """Store a new memory. Returns memory ID."""
        now = datetime.now().isoformat()
        tags_json = json.dumps(tags or [])

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO memories (type, content, tags, created_at, updated_at, importance)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (memory_type.value, content, tags_json, now, now, importance),
            )
            conn.commit()
            return cursor.lastrowid

    def fetch_memories(
        self,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[list[str]] = None,
        limit: Optional[int] = None,
        order_by: str = "updated_at DESC",
    ) -> list[dict]:
        """Fetch memories with optional filtering. Returns list of memory dicts."""
        query = "SELECT * FROM memories WHERE 1=1"
        params = []

        if memory_type:
            query += " AND type = ?"
            params.append(memory_type.value)

        if tags:
            # Simple tag matching (any tag present)
            for tag in tags:
                query += f" AND tags LIKE ?"
                params.append(f'%{tag}%')

        query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "type": row["type"],
                "content": row["content"],
                "tags": json.loads(row["tags"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "importance": row["importance"],
            }
            for row in rows
        ]

    def fetch_all_memories(self) -> list[dict]:
        """Fetch all memories of all types."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM memories ORDER BY updated_at DESC"
            )
            rows = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "type": row["type"],
                "content": row["content"],
                "tags": json.loads(row["tags"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "importance": row["importance"],
            }
            for row in rows
        ]

    def update_memory(
        self,
        memory_id: int,
        content: Optional[str] = None,
        tags: Optional[list[str]] = None,
        importance: Optional[int] = None,
    ) -> bool:
        """Update a memory. Returns True if successful."""
        updates = []
        params = []

        if content is not None:
            updates.append("content = ?")
            params.append(content)

        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags))

        if importance is not None:
            updates.append("importance = ?")
            params.append(importance)

        if not updates:
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(memory_id)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                f"UPDATE memories SET {', '.join(updates)} WHERE id = ?",
                params,
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory. Returns True if successful."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_memory(self, memory_id: int) -> Optional[dict]:
        """Get a specific memory by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM memories WHERE id = ?", (memory_id,)
            )
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row["id"],
            "type": row["type"],
            "content": row["content"],
            "tags": json.loads(row["tags"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "importance": row["importance"],
        }

    def search_memories(self, query: str) -> list[dict]:
        """Search memories by content."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM memories
                WHERE content LIKE ? OR tags LIKE ?
                ORDER BY updated_at DESC
                """,
                (f"%{query}%", f"%{query}%"),
            )
            rows = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "type": row["type"],
                "content": row["content"],
                "tags": json.loads(row["tags"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "importance": row["importance"],
            }
            for row in rows
        ]

    def get_stats(self) -> dict:
        """Get memory statistics."""
        with sqlite3.connect(self.db_path) as conn:
            counts = {}
            for mem_type in MemoryType:
                cursor = conn.execute(
                    "SELECT COUNT(*) as count FROM memories WHERE type = ?",
                    (mem_type.value,),
                )
                counts[mem_type.value] = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) as count FROM memories")
            total = cursor.fetchone()[0]

        return {
            "total": total,
            "by_type": counts,
        }
