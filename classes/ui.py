"""
ui.py: Terminal UI and event display handling.

Provides visual feedback in the terminal about conversation events and NOVA status.
"""

_DIM = "\033[2m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_BLUE = "\033[94m"
_GREEN = "\033[92m"
_CYAN = "\033[96m"
_MAGENTA = "\033[95m"
_RST = "\033[0m"
_BOLD = "\033[1m"


def log(msg: str, level: str = "info", prefix: str = "") -> None:
    """Print colored log message with standardized formatting."""
    level_symbol = {
        "info": ("● ├────", _BLUE),
        "success": ("✓ ├────", _GREEN),
        "warning": ("⚠ ├────", _YELLOW),
        "error": ("✗ ├────", _RED),
        "user": ("╰───── ›", _CYAN),
        "gemini": ("● NOVA├─", _GREEN),
    }.get(level, ("● ├─", _DIM))

    symbol, color = level_symbol
    if prefix:
        symbol = prefix

    print(f"{color}{_BOLD}{symbol}{_RST} {color}{msg}{_RST}", flush=True)


def print_startup_logo() -> None:
    """Print the NOVA startup banner with rainbow coloring."""
    colors = [_RED, _YELLOW, _GREEN, _CYAN, _BLUE, _MAGENTA]
    lines = [
        "===========================================",
        "|                NOVA-AI                  |",
        "|          Developed by N O M A           |",
        "===========================================",
    ]

    for line in lines:
        colored_line = "".join(f"{colors[i % len(colors)]}{char}{_RST}" for i, char in enumerate(line))
        print(colored_line, flush=True)


def handle_event(event: dict) -> None:
    """Display Gemini Live events in the terminal for debugging and user feedback."""
    event_type = event.get("type")

    if event_type == "user":
        log(f"User: {event.get('text')}", "user")
    elif event_type == "gemini":
        log(f"{event.get('text')}", "gemini")
    elif event_type == "turn_complete":
        log("Turn complete", "success", prefix="├───↻")
    elif event_type == "interrupted":
        log("Response interrupted", "warning", prefix="├───⊚")
    elif event_type == "tool_call":
        log(
            f"Tool: {event.get('name')} → {event.get('result')}",
            "info",
            prefix="├───⚙"
        )
    elif event_type == "error":
        log(f"Error: {event.get('error')}", "error")
