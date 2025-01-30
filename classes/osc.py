from pythonosc import udp_client


class VRChatOSC:
"""
Module for handling OSC (Open Sound Control) communications with VRChat.
This module provides a class for sending messages and managing typing
indicators in the VRChat chatbox through OSC protocol. It utilizes the
python-osc library for UDP client functionality.
Classes:
    VRChatOSC: A class for managing OSC communications with VRChat chatbox.
"""

from pythonosc import udp_client


class VRChatOSC:
    """
    A class for managing OSC communications with VRChat chatbox.
    Provides methods for sending messages and controlling typing indicators
    through OSC protocol.
    """
    def __init__(self, ip: str, port: int):
        """
        Initializes the OSC client with the specified IP address and port.
        Args:
            ip (str): The IP address of the OSC server.
            port (int): The port number of the OSC server.
        """

        self.client = udp_client.SimpleUDPClient(ip, port)

    def send_message(self, message: str):
        """
        Sends a message to the chatbox.
        Args:
            message (str): The message to be sent to the chatbox.
        """

        self.client.send_message("/chatbox/input", [message, True])
        self.client.send_message("/chatbox/typing", False)

    def set_typing_indicator(self, typing: bool):
        """
        Sets the typing indicator status in the chatbox.
        Args:
            typing (bool): If True, the typing indicator will be shown. If
            False, it will be hidden.
        """

        self.client.send_message("/chatbox/typing", typing)
    def __init__(self, ip: str, port: int):
        """
        Initializes the OSC client with the specified IP address and port.
        Args:
            ip (str): The IP address of the OSC server.
            port (int): The port number of the OSC server.
        """

        self.client = udp_client.SimpleUDPClient(ip, port)

    def send_message(self, message: str):
        """
        Sends a message to the chatbox.
        Args:
            message (str): The message to be sent to the chatbox.
        """

        self.client.send_message("/chatbox/input", [message, True])
        self.client.send_message("/chatbox/typing", False)

    def set_typing_indicator(self, typing: bool):
        """
        Sets the typing indicator status in the chatbox.
        Args:
            typing (bool): If True, the typing indicator will be shown. If
            False, it will be hidden.
        """

        self.client.send_message("/chatbox/typing", typing)
