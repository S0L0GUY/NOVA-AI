"""Tests for classes/memory.py: MemoryManager CRUD, filtering, TTL, archiving."""

from datetime import datetime, timedelta

import pytest

from classes.memory import MemoryManager, MemoryType


def test_store_and_get(memory_manager):
    mid = memory_manager.store_memory(
        "hello world", MemoryType.SHORT_TERM, tags=["greeting"], importance=3
    )
    assert isinstance(mid, int) and mid > 0

    mem = memory_manager.get_memory(mid)
    assert mem is not None
    assert mem["content"] == "hello world"
    assert mem["type"] == "short_term"
    assert mem["tags"] == ["greeting"]
    assert mem["importance"] == 3


def test_get_missing_returns_none(memory_manager):
    assert memory_manager.get_memory(9999) is None


def test_fetch_filters_by_type(memory_manager):
    memory_manager.store_memory("a", MemoryType.SHORT_TERM)
    memory_manager.store_memory("b", MemoryType.LONG_TERM)
    memory_manager.store_memory("c", MemoryType.QUICK_NOTE)

    short = memory_manager.fetch_memories(MemoryType.SHORT_TERM)
    long_ = memory_manager.fetch_memories(MemoryType.LONG_TERM)
    quick = memory_manager.fetch_memories(MemoryType.QUICK_NOTE)

    assert {m["content"] for m in short} == {"a"}
    assert {m["content"] for m in long_} == {"b"}
    assert {m["content"] for m in quick} == {"c"}


def test_fetch_filters_by_tags(memory_manager):
    memory_manager.store_memory("alpha", MemoryType.LONG_TERM, tags=["important"])
    memory_manager.store_memory("beta", MemoryType.LONG_TERM, tags=["trivial"])

    results = memory_manager.fetch_memories(tags=["important"])
    assert len(results) == 1
    assert results[0]["content"] == "alpha"


def test_fetch_limit(memory_manager):
    for i in range(5):
        memory_manager.store_memory(f"m{i}", MemoryType.SHORT_TERM)
    assert len(memory_manager.fetch_memories(limit=2)) == 2


def test_fetch_all(memory_manager):
    memory_manager.store_memory("a", MemoryType.SHORT_TERM)
    memory_manager.store_memory("b", MemoryType.LONG_TERM)
    assert len(memory_manager.fetch_all_memories()) == 2


def test_update_memory(memory_manager):
    mid = memory_manager.store_memory("original", MemoryType.LONG_TERM)
    assert memory_manager.update_memory(mid, content="updated", importance=5) is True
    mem = memory_manager.get_memory(mid)
    assert mem["content"] == "updated"
    assert mem["importance"] == 5


def test_update_with_no_fields_returns_false(memory_manager):
    mid = memory_manager.store_memory("x", MemoryType.SHORT_TERM)
    assert memory_manager.update_memory(mid) is False


def test_update_nonexistent_returns_false(memory_manager):
    assert memory_manager.update_memory(9999, content="x") is False


def test_delete_memory_archives_and_removes(memory_manager, tmp_path):
    mid = memory_manager.store_memory("doomed", MemoryType.SHORT_TERM, tags=["t"])
    archive = tmp_path / "archive.db"

    assert memory_manager.delete_memory(mid, archive_db_path=str(archive)) is True
    assert memory_manager.get_memory(mid) is None

    archived = memory_manager.fetch_archived_memories(archive_db_path=str(archive))
    assert len(archived) == 1
    assert archived[0]["content"] == "doomed"
    assert archived[0]["orig_id"] == mid


def test_delete_missing_returns_false(memory_manager):
    assert memory_manager.delete_memory(9999) is False


def test_invalid_type_rejected_by_check_constraint(memory_manager):
    import sqlite3

    with pytest.raises(sqlite3.IntegrityError):
        with sqlite3.connect(memory_manager.db_path) as conn:
            conn.execute(
                "INSERT INTO memories (type, content, tags, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?)",
                ("bogus_type", "x", "[]", "2025-01-01", "2025-01-01"),
            )
            conn.commit()


def test_search_memories(memory_manager):
    memory_manager.store_memory("the quick brown fox", MemoryType.LONG_TERM)
    memory_manager.store_memory("lazy dog", MemoryType.LONG_TERM)

    results = memory_manager.search_memories("quick")
    assert len(results) == 1
    assert "fox" in results[0]["content"]


def test_get_stats(memory_manager):
    memory_manager.store_memory("a", MemoryType.SHORT_TERM)
    memory_manager.store_memory("b", MemoryType.SHORT_TERM)
    memory_manager.store_memory("c", MemoryType.LONG_TERM)

    stats = memory_manager.get_stats()
    assert stats["total"] == 3
    assert stats["by_type"]["short_term"] == 2
    assert stats["by_type"]["long_term"] == 1
    assert stats["by_type"]["quick_note"] == 0


def test_purge_expired_removes_old_short_term(memory_manager, tmp_path):
    import sqlite3

    old = (datetime.now() - timedelta(days=30)).isoformat()
    recent = datetime.now().isoformat()

    with sqlite3.connect(memory_manager.db_path) as conn:
        conn.execute(
            "INSERT INTO memories (type, content, tags, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            ("short_term", "old", "[]", old, old),
        )
        conn.execute(
            "INSERT INTO memories (type, content, tags, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            ("short_term", "fresh", "[]", recent, recent),
        )
        conn.execute(
            "INSERT INTO memories (type, content, tags, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            ("long_term", "keep", "[]", old, old),
        )
        conn.commit()

    archive = tmp_path / "archive.db"
    deleted = memory_manager.purge_expired(archive_db_path=str(archive))

    contents = {d["content"] for d in deleted}
    assert "old" in contents
    assert "fresh" not in contents
    assert "keep" not in contents  # long_term TTL=0 means never expire

    remaining = {m["content"] for m in memory_manager.fetch_all_memories()}
    assert "old" not in remaining
    assert "fresh" in remaining
    assert "keep" in remaining


def test_restore_archived_memory(memory_manager, tmp_path):
    mid = memory_manager.store_memory("restore-me", MemoryType.LONG_TERM)
    archive = tmp_path / "archive.db"
    memory_manager.delete_memory(mid, archive_db_path=str(archive))

    archived = memory_manager.fetch_archived_memories(archive_db_path=str(archive))
    archived_id = archived[0]["archived_id"]

    assert (
        memory_manager.restore_archived_memory(
            archived_id, archive_db_path=str(archive)
        )
        is True
    )

    contents = {m["content"] for m in memory_manager.fetch_all_memories()}
    assert "restore-me" in contents

    # archive row removed after restore
    assert memory_manager.fetch_archived_memories(archive_db_path=str(archive)) == []


def test_delete_archived_memory(memory_manager, tmp_path):
    mid = memory_manager.store_memory("trash", MemoryType.SHORT_TERM)
    archive = tmp_path / "archive.db"
    memory_manager.delete_memory(mid, archive_db_path=str(archive))

    archived = memory_manager.fetch_archived_memories(archive_db_path=str(archive))
    archived_id = archived[0]["archived_id"]

    assert (
        memory_manager.delete_archived_memory(archived_id, archive_db_path=str(archive))
        is True
    )
    assert memory_manager.fetch_archived_memories(archive_db_path=str(archive)) == []


def test_fetch_archived_missing_db_returns_empty(memory_manager, tmp_path):
    result = memory_manager.fetch_archived_memories(
        archive_db_path=str(tmp_path / "nonexistent.db")
    )
    assert result == []
