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

def toggle_voice():
    """Toggle voice input in VRChat. Activates or deactivates voice capture."""
    pass


def set_movement(forward: float = 0.0, horizontal: float = 0.0):
    """
    Set avatar movement axes. Use precise float values (-1 to 1) for smooth movement control.
    
    Args:
        forward: Forward/backward axis (-1 to 1, negative is backward). Defaults to 0.
        horizontal: Left/right axis (-1 to 1, negative is left). Defaults to 0.
    """
    pass


def stop_movement():
    """Stop all movement and looking. Resets movement and look axes to zero."""
    pass


def toggle_crouch():
    """Toggle crouch state in VRChat by pressing the C key."""
    pass


def toggle_crawl():
    """Toggle crawl/prone state in VRChat by pressing the Z key."""
    pass


def start_move(direction: str, speed: str = "normal"):
    """
    Start moving the avatar in a specific direction with speed control.
    
    Args:
        direction: Direction to move ('forward', 'backward', 'left', 'right').
        speed: Speed of movement ('slow', 'normal', 'fast', 'sprint'). Defaults to 'normal'.
    """
    pass


def stop_all_movement():
    """Immediately stop all avatar movement, looking, and running."""
    pass


def jump():
    """Make the avatar jump."""
    pass


def look(direction: str, duration: float, speed: str = "normal"):
    """
    Smoothly turn the avatar's head left or right with ramping up/down.
    
    Args:
        direction: Look direction ('left' or 'right').
        duration: Duration in seconds to perform the look.
        speed: Look speed ('slow', 'normal', 'fast'). Defaults to 'normal'.
    """
    pass


def look_vertical(direction: str, duration: float, speed: str = "normal"):
    """
    Smoothly look up or down with ramping behavior similar to horizontal look.
    
    Args:
        direction: Look direction ('up' or 'down').
        duration: Duration in seconds to perform the look.
        speed: Look speed ('slow', 'normal', 'fast'). Defaults to 'normal'.
    """
    pass


def grab():
    """Grab and hold an item in front of the avatar. Item stays held until drop() is called."""
    pass


def drop():
    """Release the item currently held in the avatar's right hand."""
    pass


def use():
    """Use or interact with the item in front of the avatar using the right hand."""
    pass


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
    pass


def save_long_term_memory(content: str, tags: list[str] = None, importance: int = 1):
    """
    Save a long-term memory (persistent, indefinite). Use for important info to retain.

    Args:
        content: The memory content to store.
        tags: Optional list of tags for organization (e.g., ['fact', 'rule']).
        importance: Importance level 1-5 (default 1).
    """
    pass


def save_quick_note(content: str, tags: list[str] = None):
    """
    Save a quick note/reminder (1-3 days). Use for quick thoughts and reminders.

    Args:
        content: The quick note content.
        tags: Optional list of tags (e.g., ['reminder', 'todo']).
    """
    pass


def fetch_all_memories():
    """
    Fetch all stored memories across all types (short-term, long-term, quick notes).
    Returns a JSON summary of all memories for reference and context building.
    """
    pass


def fetch_short_term_memories():
    """Fetch all short-term memories. Use to recall session-specific information."""
    pass


def fetch_long_term_memories():
    """Fetch all long-term memories. Use to recall important persistent information."""
    pass


def fetch_quick_notes():
    """Fetch all quick notes. Use to recall recent quick reminders and thoughts."""
    pass


def update_memory(memory_id: int, content: str = None, tags: list[str] = None, importance: int = None):
    """
    Update an existing memory.

    Args:
        memory_id: The ID of the memory to update.
        content: New content (optional).
        tags: New tags (optional).
        importance: New importance level 1-5 (optional, only for long-term).
    """
    pass


def delete_memory(memory_id: int):
    """
    Delete a memory by ID.

    Args:
        memory_id: The ID of the memory to delete.
    """
    pass


def search_memories(query: str):
    """
    Search all memories by keyword or tag.

    Args:
        query: Search term to find in content or tags.
    """
    pass


# ==============================================================================
# Tool Definitions and Mapping
# ==============================================================================

def get_tool_definitions():
    """
    Returns the list of tool functions for Gemini Live.

    The google-genai SDK will introspect these functions to generate tool schemas
    automatically from their signatures and docstrings.

    Returns:
        list: List of tool functions to pass to Gemini
    """
    return [
        toggle_voice,
        set_movement,
        stop_movement,
        toggle_crouch,
        toggle_crawl,
        start_move,
        stop_all_movement,
        jump,
        look,
        look_vertical,
        grab,
        drop,
        use,
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

    return {
        "toggle_voice": vrchat_osc.toggle_voice,
        "set_movement": lambda forward=0.0, horizontal=0.0: vrchat_osc.set_movement(forward, horizontal),
        "stop_movement": vrchat_osc.stop_movement,
        "toggle_crouch": vrchat_osc.toggle_crouch,
        "toggle_crawl": vrchat_osc.toggle_crawl,
        "start_move": lambda direction, speed="normal": vrchat_osc.start_move(direction, speed),
        "stop_all_movement": vrchat_osc.stop_all_movement,
        "jump": vrchat_osc.jump,
        "look": lambda direction, duration, speed="normal": vrchat_osc.look(direction, duration, speed),
        "look_vertical": lambda direction, duration, speed="normal": vrchat_osc.look_vertical(direction, duration, speed),
        "grab": vrchat_osc.grab,
        "drop": vrchat_osc.drop,
        "use": vrchat_osc.use,
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
