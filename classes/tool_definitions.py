"""
tool_definitions.py: Tool calling definitions for Gemini Live.

Defines all available tools for Gemini to call, including VRChat avatar control
and interaction methods. Provides tool creation and function mappings.

The google-genai SDK introspects function signatures to generate tool schemas,
so we define actual Python functions with proper signatures and docstrings.
"""

import json

from classes.memory import MemoryManager, MemoryType


# ==============================================================================
# Tool Functions (Gemini will introspect these for tool schemas)
# ==============================================================================

# ==============================================================================
# VRChat Control Tools (Avatar control via OSC)
# ==============================================================================


def toggle_voice():
    """
    Toggles the voice chat state. Sends /input/Voice with value 1 to disable and 0 to enable.
    """


def look_left(seconds: float):
    """
    Sends a command to make the avatar look left for a specified duration.

    Args:
        seconds: The amount of time in seconds to look left.
    """


def look_right(seconds: float):
    """
    Sends a command to make the avatar look right for a specified duration.

    Args:
        seconds: The amount of time in seconds to look right.
    """


def jump():
    """
    Sends a command to make the avatar jump.
    """


def send_osc(address: str, value):
    """
    Sends a raw OSC message to the specified address.

    Args:
        address: The OSC address path.
        value: The value(s) to send (can be single value or list).
    """


def move_forward(seconds: float):
    """
    Sends a command to make the avatar move forward for a specified duration.

    Args:
        seconds: The amount of time in seconds to move forward.
    """


def move_backward(seconds: float):
    """
    Sends a command to make the avatar move backward for a specified duration.

    Args:
        seconds: The amount of time in seconds to move backward.
    """


def move_left(seconds: float):
    """
    Sends a command to make the avatar strafe left for a specified duration.

    Args:
        seconds: The amount of time in seconds to strafe left.
    """


def move_right(seconds: float):
    """
    Sends a command to make the avatar strafe right for a specified duration.

    Args:
        seconds: The amount of time in seconds to strafe right.
    """


# ==============================================================================
# Memory Tools (AI-controlled memory management)
# ==============================================================================

def save_short_term_memory(content: str, tags: list[str] = None):
    """
    Save a short-term memory (temporary, 1-7 days). Use for session-specific info.

    Args:
        content: The memory content to store.
        tags: Optional list of tags for organization (e.g., ['user', 'preference']).
    """


def save_long_term_memory(content: str, tags: list[str] = None, importance: int = 1):
    """
    Save a long-term memory (persistent, indefinite). Use for important info to retain.

    Args:
        content: The memory content to store.
        tags: Optional list of tags for organization (e.g., ['fact', 'rule']).
        importance: Importance level 1-5 (default 1).
    """


def save_quick_note(content: str, tags: list[str] = None):
    """
    Save a quick note/reminder (1-3 days). Use for quick thoughts and reminders.

    Args:
        content: The quick note content.
        tags: Optional list of tags (e.g., ['reminder', 'todo']).
    """


def fetch_all_memories():
    """
    Fetch all stored memories across all types (short-term, long-term, quick notes).
    Returns a JSON summary of all memories for reference and context building.
    """


def fetch_short_term_memories():
    """Fetch all short-term memories. Use to recall session-specific information."""


def fetch_long_term_memories():
    """Fetch all long-term memories. Use to recall important persistent information."""


def fetch_quick_notes():
    """Fetch all quick notes. Use to recall recent quick reminders and thoughts."""


def update_memory(memory_id: int, content: str = None, tags: list[str] = None, importance: int = None):
    """
    Update an existing memory.

    Args:
        memory_id: The ID of the memory to update.
        content: New content (optional).
        tags: New tags (optional).
        importance: New importance level 1-5 (optional, only for long-term).
    """


def delete_memory(memory_id: int):
    """
    Delete a memory by ID.

    Args:
        memory_id: The ID of the memory to delete.
    """


def search_memories(query: str):
    """
    Search all memories by keyword or tag.

    Args:
        query: Search term to find in content or tags.
    """


def capture_screenshot():
    """
    Captures and analyzes the current VRChat window screenshot.
    Use this to see what's currently happening in VRChat.
    """


# ==============================================================================
# Tool Definitions and Mapping
# ==============================================================================

def get_tool_definitions():
    """
    Returns the list of tool functions for Gemini Live.

    The google-genai SDK will introspect these functions to generate tool schemas
    automatically from their signatures and docstrings.

    Returns:
        list: List of tool functions t to Gemini
    """
    return [
        toggle_voice,
        look_left,
        look_right,
        jump,
        move_forward,
        move_backward,
        move_left,
        move_right,
        capture_screenshot,
        save_short_term_memory,
        save_long_term_memory,
        save_quick_note,
        fetch_all_memories,
        fetch_short_term_memories,
        fetch_long_term_memories,
        fetch_quick_notes,
        update_memory,
        delete_memory,
        search_memories,
    ]


def get_tool_mapping(vrchat_osc, memory_manager=None):
    """
    Returns a mapping of tool names to their corresponding functions.

    Creates the bridge between Gemini's tool calls and the actual
    VRChat OSC methods and memory management functions.

    Args:
        vrchat_osc (VRChatOSC): The VRChat OSC control instance
        memory_manager (MemoryManager): The memory manager instance (optional)

    Returns:
        dict: Mapping of tool name (str) to function (callable)
    """
    if memory_manager is None:
        memory_manager = MemoryManager()

    def _format_memories(memories):
        """Format memories as JSON string for Gemini."""
        if not memories:
            return json.dumps([])
        return json.dumps(
            [
                {
                    "id": m["id"],
                    "type": m["type"],
                    "content": m["content"],
                    "tags": m["tags"],
                    "importance": m.get("importance", 1),
                }
                for m in memories
            ],
            indent=2,
        )

    def _capture_screenshot_impl():
        """Implementation of screenshot capture."""
        from classes.screenshot import ScreenshotManager
        screenshot_manager = ScreenshotManager(target_window_name="VRChat")
        jpeg_data = screenshot_manager.capture_screenshot()
        if jpeg_data:
            return f"Screenshot captured: {len(jpeg_data)} bytes"
        return "Failed to capture screenshot"

    return {
        "toggle_voice": vrchat_osc.toggle_voice,
        "look_left": vrchat_osc.look_left,
        "look_right": vrchat_osc.look_right,
        "jump": vrchat_osc.jump,
        "move_forward": vrchat_osc.move_forward,
        "move_backward": vrchat_osc.move_backward,
        "move_left": vrchat_osc.move_left,
        "move_right": vrchat_osc.move_right,
        "capture_screenshot": _capture_screenshot_impl,
        "save_short_term_memory": lambda content, tags=None: memory_manager.store_memory(
            content, MemoryType.SHORT_TERM, tags
        ),
        "save_long_term_memory": lambda content, tags=None, importance=1: memory_manager.store_memory(
            content, MemoryType.LONG_TERM, tags, importance
        ),
        "save_quick_note": lambda content, tags=None: memory_manager.store_memory(
            content, MemoryType.QUICK_NOTE, tags
        ),
        "fetch_all_memories": lambda: _format_memories(memory_manager.fetch_all_memories()),
        "fetch_short_term_memories": lambda: _format_memories(
            memory_manager.fetch_memories(MemoryType.SHORT_TERM)
        ),
        "fetch_long_term_memories": lambda: _format_memories(
            memory_manager.fetch_memories(MemoryType.LONG_TERM)
        ),
        "fetch_quick_notes": lambda: _format_memories(
            memory_manager.fetch_memories(MemoryType.QUICK_NOTE)
        ),
        "update_memory": lambda memory_id, content=None, tags=None, importance=None: memory_manager.update_memory(
            memory_id, content, tags, importance
        ),
        "delete_memory": lambda memory_id: memory_manager.delete_memory(memory_id),
        "search_memories": lambda query: _format_memories(memory_manager.search_memories(query)),
    }
