import asyncio
import textwrap
import time

from pythonosc import udp_client


class VRChatOSC:
    def __init__(self, ip: str, port: int):
        """
        Initializes the OSC client with the specified IP address and port.
        Args:
            ip (str): The IP address of the OSC server.
            port (int): The port number of the OSC server.
        """

        self.client = udp_client.SimpleUDPClient(ip, port)

    def set_typing_indicator(self, typing: bool):
        """
        Sets the typing indicator status in the chatbox.
        Args:
            typing (bool): If True, the typing indicator will be shown. If
            False, it will be hidden.
        """

        self.client.send_message("/chatbox/typing", typing)

    def toggle_voice(self):
        """
        Toggles the voice chat state.
        Sends /input/Voice with value 1 to disable and 0 to enable.
        """
        self.client.send_message("/input/Voice", 1)
        time.sleep(0.1)
        self.client.send_message("/input/Voice", 0)

    def send_message(self, message: str):
        """
        Sends a message to the chatbox.
        Args:
            message (str): The message to be sent to the chatbox.
        """

        self.client.send_message("/chatbox/input", [message, True])
        self.client.send_message("/chatbox/typing", False)

    def send_chatbox_paginated(self, message: str, max_chars: int = 140) -> list[str]:
        """Split a chat message into VRChat-safe pages."""

        cleaned = " ".join(message.split())
        if not cleaned:
            return []

        return textwrap.wrap(
            cleaned,
            width=max_chars,
            break_long_words=True,
            break_on_hyphens=False,
        )

    async def display_pages(self, pages: list[str], delay_seconds: float = 0.35) -> None:
        """Send paginated chatbox pages in sequence with a short delay."""

        for page in pages:
            self.send_message(page)
            await asyncio.sleep(delay_seconds)

    async def look_left(self, seconds: float):
        """
        Sends a command to make the avatar look left by a specified angle.
        Args:
            seconds (float): The amount of time in seconds to look left.
        """

        self.client.send_message("/input/LookLeft", 1)
        await asyncio.sleep(seconds)
        self.client.send_message("/input/LookLeft", 0)

    async def look_right(self, seconds: float):
        """
        Sends a command to make the avatar look right by a specified angle.
        Args:
            seconds (float): The amount of time in seconds to look right.
        """

        self.client.send_message("/input/LookRight", 1)
        await asyncio.sleep(seconds)
        self.client.send_message("/input/LookRight", 0)

    async def jump(self):
        """
        Sends a command to make the avatar jump.
        """

        self.client.send_message("/input/Jump", 1)
        await asyncio.sleep(0.1)
        self.client.send_message("/input/Jump", 0)

    def send_osc(self, address: str, value):
        """
        Sends a raw OSC message to the specified address.
        Args:
            address (str): The OSC address path.
            value: The value(s) to send (can be single value or list).
        """
        self.client.send_message(address, value)

    async def move_forward(self, seconds: float):
        """
        Sends a command to make the avatar move forward.
        Args:
            seconds (float): The amount of time in seconds to move forward.
        """

        self.client.send_message("/input/MoveForward", 1)
        await asyncio.sleep(seconds)
        self.client.send_message("/input/MoveForward", 0)

    async def move_backward(self, seconds: float):
        """
        Sends a command to make the avatar move backward.
        Args:
            seconds (float): The amount of time in seconds to move backward.
        """

        self.client.send_message("/input/MoveBackward", 1)
        await asyncio.sleep(seconds)
        self.client.send_message("/input/MoveBackward", 0)

    def move_left(self, seconds: float):
        """
        Sends a command to make the avatar strafe left.
        Args:
            seconds (float): The amount of time in seconds to strafe left.
        """

        self.client.send_message("/input/MoveLeft", 1)
        time.sleep(seconds)
        self.client.send_message("/input/MoveLeft", 0)

    async def move_right(self, seconds: float):
        """
        Sends a command to make the avatar strafe right.
        Args:
            seconds (float): The amount of time in seconds to strafe right.
        """

        self.client.send_message("/input/MoveRight", 1)
        time.sleep(seconds)
        self.client.send_message("/input/MoveRight", 0)
