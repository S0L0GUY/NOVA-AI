"""
LLM tools module for NOVA-AI.

Declares function-callable tools for the GenAI SDK, now extended with
Gabriel-style features: movement, SFX, and personality switching.

All tool registrations are done through get_generate_config() so the
nova.py main loop only needs a single import and a single config= change.
"""

import datetime
import json
import math
import os
from typing import Any, Dict, Optional

from google.genai import types

import constants


def load_memory():
    """
    Loads the memory JSON file, creating it if absent.

    Returns:
        dict: The in-memory key-value store.
    """
    if not os.path.exists(constants.FilePaths.MEMORY_FILE):
        with open(constants.FilePaths.MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(constants.FilePaths.MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(db: dict) -> None:
    """
    Saves the in-memory key-value store to disk.

    Args:
        db (dict): The memory dictionary to persist.
    """
    with open(constants.FilePaths.MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)


def get_time(location: Optional[str]) -> Dict[str, Any]:
    """Return the current time, optionally for a named location.

    Args:
        location: city or location string (optional)

    Returns:
        A dict with the current time for the location if provided, else local time.
    """
    print(f"\033[94mGetting time for location: {location}\033[0m")
    now = datetime.datetime.now()
    loc_label = location if location else "local"
    return {
        "location": loc_label,
        "iso": now.isoformat(),
        "readable": now.strftime("%Y-%m-%d %H:%M:%S"),
    }


def calculator(expression: str) -> str:
    """A simple calculator that evaluates a math expression.

    Args:
        expression: A string containing a math expression, e.g. "2 + 2 * 3"

    Returns:
        The result of the evaluated expression.
    """
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    allowed_names.update({"abs": abs, "round": round})
    print(f"\033[94mCalculating: {expression}\033[0m")
    try:
        return str(eval(expression, {"__builtins__": None}, allowed_names))
    except Exception as exc:
        return f"error: {exc}"


def memory_get(key: str):
    """Retrieve a value from the persistent memory store.

    Args:
        key: The key to look up in the memory store.

    Returns:
        The value stored for `key` if present; otherwise None.
    """
    return load_memory().get(key, None)


def memory_set(key: str, value: str):
    """Store a key-value pair in the persistent memory store.
    Only set memories you want to keep long-term.

    Args:
        key: The key to store the value under.
        value: The value to store.

    Returns:
        A confirmation string "ok" upon successful storage.
    """
    db = load_memory()
    db[key] = value
    save_memory(db)
    return "ok"


def memory_search(query: str):
    """Search the persistent memory store for keys or values matching the query.

    Args:
        query: The search query string.

    Returns:
        A dict of key-value pairs matching the query.
    """
    db = load_memory()
    q = query.lower()
    return {k: v for k, v in db.items() if q in k.lower() or q in str(v).lower()}


def move(direction: str, duration: float = 1.0, run: bool = False) -> Dict[str, Any]:
    """Move the avatar in a direction using VRChat OSC inputs.

    Args:
        direction: One of forward, backward, left, right.
        duration: How long to move in seconds.
        run: Whether to hold Run while moving.

    Returns:
        A result dict with a 'success' key.
    """
    import asyncio
    from classes.movement import get_movement_controller

    controller = get_movement_controller()
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(controller.move_direction(direction, duration, run))
    finally:
        loop.close()


def turn(direction: str, duration: float = 1.0) -> Dict[str, Any]:
    """Turn the avatar's view left or right.

    Args:
        direction: 'left' or 'right'.
        duration: How long to hold the turn in seconds.

    Returns:
        A result dict with a 'success' key.
    """
    import asyncio
    from classes.movement import get_movement_controller

    controller = get_movement_controller()
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(controller.look_turn(direction, duration))
    finally:
        loop.close()


def play_sound(file_identifier: str, count: int = 1) -> Dict[str, Any]:
    """Play a sound effect from the sfx folder.

    Args:
        file_identifier: Name, path, or search term for the audio file.
        count: Number of times to play the sound.

    Returns:
        A result dict with a 'success' key.
    """
    from classes.sfx_manager import get_sfx_manager

    return get_sfx_manager().play_audio_file(file_identifier, count)


def switch_personality(personality_id: str) -> Dict[str, Any]:
    """Switch to a different personality mode.

    Args:
        personality_id: The ID of the personality to activate.

    Returns:
        A result dict with a 'success' key and the new prompt.
    """
    from classes.personality_manager import get_personality_manager

    return get_personality_manager().switch_personality(personality_id)


def list_personalities() -> Dict[str, Any]:
    """List all available personality modes.

    Returns:
        A result dict containing the list of personalities.
    """
    from classes.personality_manager import get_personality_manager

    return get_personality_manager().list_personalities()


def get_generate_config(disable_automatic: bool = False) -> types.GenerateContentConfig:
    """Return a GenAI GenerateContentConfig with all function tools attached.

    Includes the original NOVA-AI tools (time, calculator, memory) plus the
    new Gabriel-style tools (movement, sound effects, personality switching).

    Args:
        disable_automatic: If True, disable automatic function calling.

    Returns:
        A types.GenerateContentConfig configured with all tools.
    """
    tools = [
        # Original NOVA-AI tools
        get_time,
        calculator,
        memory_get,
        memory_set,
        memory_search,
        # Gabriel-style additions
        move,
        turn,
        play_sound,
        switch_personality,
        list_personalities,
    ]

    config = types.GenerateContentConfig(tools=tools)
    if disable_automatic:
        config.automatic_function_calling = types.AutomaticFunctionCallingConfig(disable=True)

    return config
