"""Multi-level memory system with SQLite backend."""

import json
import sqlite3
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional


class MemoryType(Enum):
    """Memory type classifications."""

    SHORT_TERM = "short_term"  # Temporary, session-specific (1-7 days)
    LONG_TERM = "long_term"  # Persistent, important (indefinite)
    QUICK_NOTE = "quick_note"  # Quick thoughts/reminders (1-3 days)


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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK(type IN ('short_term', 'long_term', 'quick_note')),
                    content TEXT NOT NULL,
                    tags TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    importance INTEGER DEFAULT 1
                )
            """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON memories(type)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_created ON memories(created_at)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)"
            )
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
            return cursor.lastrowid  # type: ignore

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
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")

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
            cursor = conn.execute("SELECT * FROM memories ORDER BY updated_at DESC")
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

    def delete_memory(
        self, memory_id: int, archive_db_path: Optional[str] = None
    ) -> bool:
        """Archive a memory (to the archive DB) then delete it from the main DB.

        If `archive_db_path` is None the default archive DB next to the main DB
        will be used. Returns True if the memory was removed from the main DB.
        """
        # Fetch the memory first
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
            row = cur.fetchone()

        if not row:
            return False

        # Determine archive DB path
        if not archive_db_path:
            archive_db_path = self._default_archive_path()
        else:
            p = Path(archive_db_path)
            if not p.is_absolute():
                archive_db_path = str(self.db_path.parent.joinpath(archive_db_path))

        now = datetime.now().isoformat()

        # Try to insert into archive DB, but do not fail deletion if archiving fails
        try:
            with sqlite3.connect(archive_db_path) as aconn:
                aconn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS archived_memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        orig_id INTEGER,
                        type TEXT,
                        content TEXT,
                        tags TEXT,
                        created_at TEXT,
                        updated_at TEXT,
                        importance INTEGER,
                        deleted_at TEXT
                    )
                    """
                )
                aconn.execute(
                    """
                    INSERT INTO archived_memories (
                        orig_id, type, content, tags, created_at, updated_at, importance, deleted_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["id"],
                        row["type"],
                        row["content"],
                        row["tags"],
                        row["created_at"],
                        row["updated_at"],
                        row["importance"],
                        now,
                    ),
                )
                aconn.commit()
        except Exception:
            # ignore archiving errors and proceed with deletion
            pass

        # Delete from main DB
        with sqlite3.connect(self.db_path) as conn2:
            cursor = conn2.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn2.commit()
            return cursor.rowcount > 0

    def purge_expired(
        self, ttl_days_map: Optional[dict] = None, archive_db_path: Optional[str] = None
    ) -> list[dict]:
        """Purge expired memories according to TTL map.

        ttl_days_map: mapping of memory type string to days (int). If a type maps to
        0 or a non-positive value, it is not auto-deleted.

        Returns a list of metadata for deleted memories.
        """
        # Defaults if not provided
        defaults = {
            MemoryType.QUICK_NOTE.value: 3,
            MemoryType.SHORT_TERM.value: 7,
            MemoryType.LONG_TERM.value: 0,
        }

        ttl_map = {}
        if ttl_days_map:
            # normalize keys to str and coerce values defensively
            for k, v in ttl_days_map.items():
                try:
                    ttl_map[str(k)] = int(v) if v is not None else 0
                except (TypeError, ValueError):
                    ttl_map[str(k)] = 0

        # Fill missing with defaults
        for k, v in defaults.items():
            ttl_map.setdefault(k, v)

        now = datetime.now()
        deleted = []

        # Fetch all memories and filter in Python to avoid SQL datetime format issues
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM memories")
            rows = cursor.fetchall()

        for row in rows:
            mem_type = row["type"]
            ttl_days = int(ttl_map.get(mem_type, 0))
            if ttl_days <= 0:
                continue

            try:
                created = datetime.fromisoformat(row["created_at"])
            except Exception:
                # Skip rows with invalid dates
                continue

            if created + timedelta(days=ttl_days) <= now:
                # Delegate archiving+deletion to delete_memory which will
                # archive into `archive_db_path` (or default) and then remove
                # the row from the main DB.
                try:
                    removed = False
                    if archive_db_path:
                        removed = self.delete_memory(
                            row["id"], archive_db_path=archive_db_path
                        )
                    else:
                        removed = self.delete_memory(row["id"])

                    if removed:
                        deleted.append(
                            {
                                "id": row["id"],
                                "type": mem_type,
                                "created_at": row["created_at"],
                                "content": row["content"],
                            }
                        )
                except Exception:
                    # if anything goes wrong, skip this row
                    continue

        return deleted

    def get_memory(self, memory_id: int) -> Optional[dict]:
        """Get a specific memory by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
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

    def _default_archive_path(self) -> str:
        """Return default archive DB path next to the main DB."""
        return str(self.db_path.parent.joinpath("memories_archive.db"))

    def fetch_archived_memories(
        self,
        archive_db_path: Optional[str] = None,
        limit: Optional[int] = None,
        order_by: str = "deleted_at DESC",
    ) -> list[dict]:
        """Fetch archived memories from the archive DB.

        If `archive_db_path` is None, use the default archive DB located
        next to the main DB. If a relative path is provided, resolve it
        relative to the main DB directory so the archive is found reliably
        regardless of current working directory.
        """
        if not archive_db_path:
            archive_db_path = self._default_archive_path()
        else:
            p = Path(archive_db_path)
            if not p.is_absolute():
                archive_db_path = str(self.db_path.parent.joinpath(archive_db_path))

        try:
            with sqlite3.connect(archive_db_path) as conn:
                conn.row_factory = sqlite3.Row
                query = f"SELECT * FROM archived_memories ORDER BY {order_by}"
                if limit:
                    query += f" LIMIT {limit}"
                cursor = conn.execute(query)
                rows = cursor.fetchall()
        except sqlite3.OperationalError:
            # Archive DB or table doesn't exist yet
            return []

        result = []
        for row in rows:
            rd = dict(row)
            # Normalize tags safely
            tags_raw = rd.get("tags")
            if tags_raw is None:
                tags = []
            else:
                try:
                    tags = json.loads(tags_raw)
                except Exception:
                    tags = []

            result.append(
                {
                    "archived_id": rd.get("id") or rd.get("archived_id"),
                    "orig_id": rd.get("orig_id") or rd.get("origId") or rd.get("orig"),
                    "type": rd.get("type") or rd.get("mem_type"),
                    "content": rd.get("content"),
                    "tags": tags,
                    "created_at": rd.get("created_at") or rd.get("createdAt"),
                    "updated_at": rd.get("updated_at") or rd.get("updatedAt"),
                    "importance": (
                        rd.get("importance") if rd.get("importance") is not None else 0
                    ),
                    "deleted_at": rd.get("deleted_at") or rd.get("deletedAt"),
                }
            )

        return result

    def restore_archived_memory(
        self, archived_id: int, archive_db_path: Optional[str] = None
    ) -> bool:
        """Restore an archived memory back into the main memories table."""
        if not archive_db_path:
            archive_db_path = self._default_archive_path()

        with sqlite3.connect(archive_db_path) as aconn:
            aconn.row_factory = sqlite3.Row
            cursor = aconn.execute(
                "SELECT * FROM archived_memories WHERE id = ?", (archived_id,)
            )
            row = cursor.fetchone()
            if not row:
                return False

            # Re-insert into main DB using original timestamps
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO memories (type, content, tags, created_at, updated_at, importance) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        row["type"],
                        row["content"],
                        row["tags"],
                        row["created_at"],
                        row["updated_at"],
                        row["importance"],
                    ),
                )
                conn.commit()

            # Delete from archive
            with sqlite3.connect(archive_db_path) as aconn2:
                cursor = aconn2.execute(
                    "DELETE FROM archived_memories WHERE id = ?", (archived_id,)
                )
                aconn2.commit()
                return cursor.rowcount > 0

    def delete_archived_memory(
        self, archived_id: int, archive_db_path: Optional[str] = None
    ) -> bool:
        """Permanently delete an archived memory from the archive DB."""
        if not archive_db_path:
            archive_db_path = self._default_archive_path()

        try:
            with sqlite3.connect(archive_db_path) as aconn:
                cursor = aconn.execute(
                    "DELETE FROM archived_memories WHERE id = ?", (archived_id,)
                )
                aconn.commit()
                return cursor.rowcount > 0
        except sqlite3.OperationalError:
            return False
