"""
Small helper module that declares function-callable tools for the GenAI SDK.

This file keeps all function-declaration and implementation details out of
`nova.py` so only a tiny import and a single `config=` change are required
in the main loop. The functions here are intentionally simple and mockable.
"""

import datetime

from typing import Any, Dict, Optional

from google.genai import types


def get_time(location: Optional[str]) -> Dict[str, Any]:
    """Return the current time for a given location.

    Args:
        location: city or location string (optional)

    Returns:
        A dict with the current time for the location if provided, else UTC time.
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
    tools = [get_time]

    config = types.GenerateContentConfig(tools=tools)
    if disable_automatic:
        config.automatic_function_calling = types.AutomaticFunctionCallingConfig(disable=True)

    return config
