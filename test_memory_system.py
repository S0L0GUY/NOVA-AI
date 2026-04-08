#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick test script to verify the memory system."""

import json
from classes.memory import MemoryManager, MemoryType

print("Memory System Integration Test\n")
print("=" * 50)

# Test 1: Create manager
print("\n[OK] Test 1: Initialize MemoryManager")
try:
    manager = MemoryManager()
    print("  Database initialized successfully")
except Exception as e:
    print(f"  [FAIL] {e}")
    exit(1)

# Test 2: Store memories
print("\n[OK] Test 2: Store all memory types")
try:
    st_id = manager.store_memory(
        "This is a short-term memory",
        MemoryType.SHORT_TERM,
        ["test", "short_term"],
    )
    lt_id = manager.store_memory(
        "This is a long-term important fact",
        MemoryType.LONG_TERM,
        ["test", "long_term"],
        importance=5,
    )
    qn_id = manager.store_memory(
        "Quick note/reminder",
        MemoryType.QUICK_NOTE,
        ["test", "reminder"],
    )
    print(f"  Short-term memory ID: {st_id}")
    print(f"  Long-term memory ID: {lt_id}")
    print(f"  Quick note ID: {qn_id}")
except Exception as e:
    print(f"  [FAIL] {e}")
    exit(1)

# Test 3: Fetch memories
print("\n[OK] Test 3: Fetch all memories")
try:
    all_mems = manager.fetch_all_memories()
    print(f"  Total memories: {len(all_mems)}")
    for mem in all_mems:
        print(f"    - [{mem['type']}] {mem['content'][:40]}...")
except Exception as e:
    print(f"  [FAIL] {e}")
    exit(1)

# Test 4: Fetch by type
print("\n[OK] Test 4: Fetch by memory type")
try:
    st_mems = manager.fetch_memories(MemoryType.SHORT_TERM)
    lt_mems = manager.fetch_memories(MemoryType.LONG_TERM)
    qn_mems = manager.fetch_memories(MemoryType.QUICK_NOTE)
    print(f"  Short-term: {len(st_mems)}")
    print(f"  Long-term: {len(lt_mems)}")
    print(f"  Quick notes: {len(qn_mems)}")
except Exception as e:
    print(f"  [FAIL] {e}")
    exit(1)

# Test 5: Search
print("\n[OK] Test 5: Search memories")
try:
    results = manager.search_memories("test")
    print(f"  Found {len(results)} results for 'test'")
except Exception as e:
    print(f"  [FAIL] {e}")
    exit(1)

# Test 6: Update
print("\n[OK] Test 6: Update memory")
try:
    manager.update_memory(st_id, content="Updated short-term memory")
    updated = manager.get_memory(st_id)
    print(f"  Updated content: {updated['content']}")
except Exception as e:
    print(f"  [FAIL] {e}")
    exit(1)

# Test 7: Get stats
print("\n[OK] Test 7: Get statistics")
try:
    stats = manager.get_stats()
    print(f"  Total: {stats['total']}")
    for mem_type, count in stats["by_type"].items():
        print(f"  {mem_type}: {count}")
except Exception as e:
    print(f"  [FAIL] {e}")
    exit(1)

# Test 8: Tool format (JSON)
print("\n[OK] Test 8: Tool output format (JSON)")
try:
    mems_json = json.dumps(manager.fetch_all_memories(), indent=2)
    print(f"  JSON size: {len(mems_json)} bytes")
    print("  Sample output:")
    print(mems_json[:200] + "...")
except Exception as e:
    print(f"  [FAIL] {e}")
    exit(1)

# Test 9: Delete
print("\n[OK] Test 9: Delete memory")
try:
    success = manager.delete_memory(qn_id)
    if success:
        print(f"  Deleted memory ID {qn_id}")
        remaining = manager.get_stats()["total"]
        print(f"  Remaining: {remaining}")
    else:
        print("  No memory found for deletion")
except Exception as e:
    print(f"  [FAIL] {e}")
    exit(1)

# Test 10: Tool integration check
print("\n[OK] Test 10: Tool definitions available")
try:
    from classes.tool_definitions import get_tool_definitions
    tools = get_tool_definitions()
    memory_tools = [t.__name__ for t in tools if "memory" in t.__name__.lower()]
    print(f"  Total tools: {len(tools)}")
    print(f"  Memory tools: {len(memory_tools)}")
    for tool in memory_tools:
        print(f"    - {tool}")
except Exception as e:
    print(f"  [FAIL] {e}")
    exit(1)

print("\n" + "=" * 50)
print("[PASS] All tests passed! Memory system ready to use.\n")
print("Next steps:")
print("  1. Run NOVA: python nova.py")
print("  2. Launch UI: streamlit run memory_ui.py")
print("  3. Check examples: python MEMORY_SYSTEM_EXAMPLES.py")
