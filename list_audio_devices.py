import pyaudio

# optional color support on Windows via colorama; falls back to ANSI codes
try:
    from colorama import init, Fore, Style

    init()
    HIGHLIGHT = Fore.YELLOW + Style.BRIGHT
    RESET = Style.RESET_ALL
except Exception:
    HIGHLIGHT = "\033[93m"  # ANSI bright yellow
    RESET = "\033[0m"


def list_audio_devices() -> None:
    """List all of the audio devices, their indexes, and number of channels.
    Highlight devices matching the VB-Audio CABLE names.
    """
    patterns = [
        "CABLE-B Input (VB-Audio Cable B",
        "CABLE-A Output (VB-Audio Cable",
    ]

    p = pyaudio.PyAudio()
    try:
        device_count = p.get_device_count()

        print("Available Audio Devices:")
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            name = device_info.get("name", "")
            channels = device_info.get("maxInputChannels", 0)

            # case-insensitive substring match against the patterns
            match = any(pat.lower() in name.lower() for pat in patterns)
            line = f"Index {i}: {name}, Channels: {channels}"
            if match:
                print(f"{HIGHLIGHT}{line}{RESET}")
            else:
                print(line)
    finally:
        p.terminate()


if __name__ == "__main__":
    list_audio_devices()
