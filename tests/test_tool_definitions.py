"""Tests for classes/tool_definitions.py: tool schema integrity and mapping wiring."""

import json
from unittest.mock import MagicMock

import pytest

from classes.memory import MemoryManager, MemoryType
from classes.tool_definitions import get_tool_definitions, get_tool_mapping


def test_tool_definitions_are_callables():
    tools = get_tool_definitions()
    assert len(tools) > 0
    for t in tools:
        assert callable(t)
        assert t.__doc__, f"{t.__name__} is missing a docstring"


def test_tool_names_unique():
    tools = get_tool_definitions()
    names = [t.__name__ for t in tools]
    assert len(names) == len(set(names))


def test_expected_tools_present():
    names = {t.__name__ for t in get_tool_definitions()}
    must_have = {
        "toggle_voice", "look_left", "look_right", "jump",
        "move_forward", "move_backward", "move_left", "move_right",
        "save_short_term_memory", "save_long_term_memory", "save_quick_note",
        "fetch_all_memories", "search_memories", "delete_memory",
        "update_memory", "capture_screenshot", "wander",
    }
    missing = must_have - names
    assert not missing, f"Missing tools: {missing}"


@pytest.fixture
def memory(tmp_path):
    return MemoryManager(db_path=str(tmp_path / "m.db"))


def test_mapping_routes_to_osc(memory):
    osc = MagicMock()
    mapping = get_tool_mapping(osc, memory_manager=memory)
    assert mapping["jump"] is osc.jump
    assert mapping["look_left"] is osc.look_left
    assert mapping["toggle_voice"] is osc.toggle_voice
    assert mapping["wander"] is osc.wander


def test_mapping_save_short_term_stores(memory):
    mapping = get_tool_mapping(MagicMock(), memory_manager=memory)
    mid = mapping["save_short_term_memory"]("note", ["t"])
    assert isinstance(mid, int)
    stored = memory.get_memory(mid)
    assert stored["content"] == "note"
    assert stored["type"] == "short_term"


def test_mapping_save_long_term_with_importance(memory):
    mapping = get_tool_mapping(MagicMock(), memory_manager=memory)
    mid = mapping["save_long_term_memory"]("fact", ["x"], 4)
    stored = memory.get_memory(mid)
    assert stored["type"] == "long_term"
    assert stored["importance"] == 4


def test_mapping_fetch_all_returns_json(memory):
    mapping = get_tool_mapping(MagicMock(), memory_manager=memory)
    memory.store_memory("hello", MemoryType.LONG_TERM, tags=["a"])
    result = mapping["fetch_all_memories"]()
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert parsed[0]["content"] == "hello"


def test_mapping_search(memory):
    mapping = get_tool_mapping(MagicMock(), memory_manager=memory)
    memory.store_memory("the answer is 42", MemoryType.LONG_TERM)
    result = json.loads(mapping["search_memories"]("answer"))
    assert len(result) == 1
    assert "42" in result[0]["content"]


def test_mapping_covers_all_declared_tools(memory):
    mapping = get_tool_mapping(MagicMock(), memory_manager=memory)
    declared = {t.__name__ for t in get_tool_definitions()}
    assert declared <= set(mapping.keys()), (
        f"Tools declared but not mapped: {declared - set(mapping.keys())}"
    )
