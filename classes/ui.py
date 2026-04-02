"""UI and display handling for NOVA."""


def print_startup_logo() -> None:
    """Print the NOVA startup logo with colors."""
    colors = ["\033[91m", "\033[93m", "\033[92m", "\033[96m", "\033[94m", "\033[95m"]
    lines = [
        "===========================================",
        "|                NOVA-AI                  |",
        "|          Developed by N O M A           |",
        "===========================================",
    ]

    for line in lines:
        colored_line = "".join(f"{colors[i % len(colors)]}{char}\033[0m" for i, char in enumerate(line))
        print(colored_line)


def handle_event(event: dict) -> None:
    """Handle and display Gemini Live events."""
    event_type = event.get("type")

    if event_type == "user":
        print(f"\n🗣️ User: {event.get('text')}")
    elif event_type == "gemini":
        print(f"🤖 Gemini: {event.get('text')}")
    elif event_type == "turn_complete":
        print("✅ Turn complete")
    elif event_type == "interrupted":
        print("⏹️ Response interrupted")
    elif event_type == "tool_call":
        print(f"🔧 Tool called: {event.get('name')} -> {event.get('result')}")
    elif event_type == "error":
        print(f"❌ Error: {event.get('error')}")
