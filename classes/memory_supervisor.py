"""Supervisor for memory TTL enforcement and purge operations.

This module provides a small `MemorySupervisor` class that runs purges
and returns summaries. Designed to be simple and invoked at startup.
"""

from datetime import datetime
from typing import Optional


class MemorySupervisor:
    """Runs memory purge operations and reports results."""

    def __init__(self, memory_manager, logger=None):
        self.memory_manager = memory_manager
        self.logger = logger
        self.last_purge = None

    def run_once(
        self, ttl_days_map: Optional[dict] = None, dry_run: bool = False
    ) -> dict:
        """Run a single purge operation.

        ttl_days_map: mapping of memory type (string) to TTL days (int).
        dry_run: if True, does not perform deletions but returns what would be deleted.
        Returns a dict with keys: `deleted` (list), `timestamp`.
        """
        if dry_run:
            # Simulate by inspecting but not deleting: use purge_expired then restore? Simpler: run purge_expired on a copy is expensive.
            # For now, dry_run will just compute candidate IDs without deleting by inspecting DB rows.
            candidates = []
            now = datetime.now()
            defaults = {
                "quick_note": 3,
                "short_term": 7,
                "long_term": 0,
            }
            ttl_map = {}
            if ttl_days_map:
                for k, v in ttl_days_map.items():
                    ttl_map[str(k)] = int(v) if v is not None else 0
            for k, v in defaults.items():
                ttl_map.setdefault(k, v)

            # inspect rows
            import sqlite3

            conn = sqlite3.connect(self.memory_manager.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM memories")
            rows = cur.fetchall()
            for row in rows:
                mem_type = row["type"]
                ttl_days = int(ttl_map.get(mem_type, 0))
                if ttl_days <= 0:
                    continue
                try:
                    created = datetime.fromisoformat(row["created_at"])
                except Exception:
                    continue
                if (
                    created
                    and created.day
                    and (created)
                    and (
                        created + __import__("datetime").timedelta(days=ttl_days) <= now
                    )
                ):
                    candidates.append(
                        {
                            "id": row["id"],
                            "type": mem_type,
                            "created_at": row["created_at"],
                        }
                    )
            conn.close()
            return {
                "deleted": candidates,
                "timestamp": datetime.now().isoformat(),
                "dry_run": True,
            }

        # perform actual purge - archive into a secondary DB file next to the primary DB
        deleted = []
        try:
            try:
                archive_path = str(
                    self.memory_manager.db_path.parent / "memories_archive.db"
                )
            except Exception:
                archive_path = "memories_archive.db"

            deleted = self.memory_manager.purge_expired(
                ttl_days_map=ttl_days_map, archive_db_path=archive_path
            )
            self.last_purge = {
                "timestamp": datetime.now().isoformat(),
                "deleted_count": len(deleted),
                "deleted": deleted,
            }
            if self.logger:
                try:
                    self.logger(
                        f"MemorySupervisor purged {len(deleted)} memories on startup",
                        "info",
                    )
                except Exception:
                    pass
        except Exception as e:
            if self.logger:
                try:
                    self.logger(f"MemorySupervisor error: {e}", "error")
                except Exception:
                    pass
        return {
            "deleted": deleted,
            "timestamp": datetime.now().isoformat(),
            "dry_run": False,
        }
