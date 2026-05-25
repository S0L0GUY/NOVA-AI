"""Tests for classes/memory_supervisor.py: TTL purge orchestration and dry-run."""

import sqlite3
from datetime import datetime, timedelta

from classes.memory import MemoryManager, MemoryType
from classes.memory_supervisor import MemorySupervisor


def _insert_with_date(db_path, mem_type, content, created):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO memories (type, content, tags, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (mem_type, content, "[]", created, created),
        )
        conn.commit()


def test_run_once_purges_expired(tmp_path):
    db = tmp_path / "m.db"
    mm = MemoryManager(db_path=str(db))
    old = (datetime.now() - timedelta(days=20)).isoformat()
    _insert_with_date(db, "short_term", "expired", old)
    mm.store_memory("fresh", MemoryType.SHORT_TERM)

    sup = MemorySupervisor(mm)
    result = sup.run_once()

    assert result["dry_run"] is False
    assert any(d["content"] == "expired" for d in result["deleted"])
    assert sup.last_purge is not None
    assert sup.last_purge["deleted_count"] == len(result["deleted"])

    remaining = {m["content"] for m in mm.fetch_all_memories()}
    assert "expired" not in remaining
    assert "fresh" in remaining


def test_dry_run_does_not_delete(tmp_path):
    db = tmp_path / "m.db"
    mm = MemoryManager(db_path=str(db))
    old = (datetime.now() - timedelta(days=20)).isoformat()
    _insert_with_date(db, "short_term", "expired", old)

    sup = MemorySupervisor(mm)
    result = sup.run_once(dry_run=True)

    assert result["dry_run"] is True
    assert any(c["type"] == "short_term" for c in result["deleted"])
    # Row still present
    assert len(mm.fetch_all_memories()) == 1


def test_empty_db_noop(tmp_path):
    mm = MemoryManager(db_path=str(tmp_path / "m.db"))
    sup = MemorySupervisor(mm)
    result = sup.run_once()
    assert result["deleted"] == []


def test_logger_invoked_on_success(tmp_path):
    mm = MemoryManager(db_path=str(tmp_path / "m.db"))
    calls = []

    def fake_logger(msg, level):
        calls.append((msg, level))

    sup = MemorySupervisor(mm, logger=fake_logger)
    sup.run_once()
    assert any("purged" in m for m, _ in calls)


def test_custom_ttl_map(tmp_path):
    db = tmp_path / "m.db"
    mm = MemoryManager(db_path=str(db))
    two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
    _insert_with_date(db, "short_term", "borderline", two_days_ago)

    sup = MemorySupervisor(mm)
    # With a TTL of 1 day for short_term, the 2-day-old row should be deleted
    result = sup.run_once(ttl_days_map={"short_term": 1})
    assert any(d["content"] == "borderline" for d in result["deleted"])
