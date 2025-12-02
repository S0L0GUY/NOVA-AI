"""
Small helper module that declares function-callable tools for the GenAI SDK.

This file keeps all function-declaration and implementation details out of
`nova.py` so only a tiny import and a single `config=` change are required
in the main loop. The functions here are intentionally simple and mockable.
"""

import datetime
import json
import math
import os
from typing import Any, Dict, Optional

from google.genai import types

import constants


def load_memory():
    if not os.path.exists(constants.Memory.MEMORY_FILE):
        with open(constants.Memory.MEMORY_FILE, "w") as f:
            json.dump({}, f)
    with open(constants.Memory.MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(db):
    with open(constants.Memory.MEMORY_FILE, "w") as f:
        json.dump(db, f, indent=2)


def get_time(location: Optional[str]) -> Dict[str, Any]:
    """Return the current time for a given location.

    Args:
        location: city or location string (optional)

    Returns:
        A dict with the current time for the location if provided, else local time.
    """
    print(f"\033[94mGetting time for location: {location}\033[0m")

    now = datetime.datetime.now()
    iso = now.isoformat()
    readable = now.strftime("%Y-%m-%d %H:%M:%S")
    loc_label = location if location else "local"

    return {
        "location": loc_label,
        "iso": iso,
        "readable": readable,
    }


def calculator(expression: str) -> str:
    """A simple calculator that evaluates a math expression.
    Args:
        expression: A string containing a math expression, e.g. "2 + 2 * 3"

    Returns:
        The result of the evaluated expression.
    """
    # Optional: restrict functions for safety
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}

    # Add safe things like abs(), round(), etc.
    allowed_names.update({
        "abs": abs,
        "round": round
    })

    print(f"\033[94mCalculating expression: {expression}\033[0m")

    # Evaluate safely-ish
    try:
        result = str(eval(expression, {"__builtins__": None}, allowed_names))
        return result
    except Exception as e:
        return f"error: {str(e)}"


def memory_get(key: str):
    """Retrieve a value from the persistent memory store.

    Args:
        key: The key to look up in the memory store.

    Returns:
        The value stored for `key` if present; otherwise None.
    """

    db = load_memory()
    return db.get(key, None)


def memory_set(key: str, value: str):
    """"Store a key-value pair in the persistent memory store.
    Only set memories that you want to keep long-term! This can
    be things about your personality, but not things about other
    users other than their names and what they tell you about
    themselves.

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
    query = query.lower()
    results = {k: v for k, v in db.items() if query in k.lower() or query in str(v).lower()}
    return results


def get_generate_config(disable_automatic: bool = False) -> types.GenerateContentConfig:
    """Return a GenAI GenerateContentConfig with our function tools attached.

    By passing Python callables directly, the Google GenAI Python SDK will
    automatically create function declarations from the callables' type hints
    and docstrings and (when enabled) execute them when the model requests
    a function call. This keeps integration minimal in `nova.py`.

    Args:
        disable_automatic: If True, disable automatic function calling (SDK will
                           return function_call suggestions instead of executing).

    Returns:
        A `types.GenerateContentConfig` instance configured with our tools.
    """

    # Pass the callables directly so the SDK can infer schemas and handle calls.
    tools = [get_time, calculator, memory_get, memory_set, memory_search]

    config = types.GenerateContentConfig(tools=tools)
    if disable_automatic:
        config.automatic_function_calling = types.AutomaticFunctionCallingConfig(disable=True)

    return config
