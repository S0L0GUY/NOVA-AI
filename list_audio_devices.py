import pyaudio


def list_audio_devices() -> None:
    """List all of the audio devices, their indexes, and number of channels."""
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()

    print("Available Audio Devices:")
    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        print(f"Index {i}: {device_info['name']}, "
              f"Channels: {device_info['maxInputChannels']}")

    p.terminate()


if __name__ == "__main__":
    list_audio_devices()
