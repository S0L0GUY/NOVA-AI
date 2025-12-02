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

    def send_message(self, message: str):
        """
        Sends a message to the chatbox.
        Args:
            message (str): The message to be sent to the chatbox.
        """

        self.client.send_message("/chatbox/input", [message, True])
        self.client.send_message("/chatbox/typing", False)

    def look_left(self, seconds: float):
        """
        Sends a command to make the avatar look left by a specified angle.
        Args:
            seconds (float): The amount of time in seconds to look left.
        """

        self.client.send_message("/input/LookLeft", 1)
        time.sleep(seconds)
        self.client.send_message("/input/LookLeft", 0)

    def look_right(self, seconds: float):
        """
        Sends a command to make the avatar look right by a specified angle.
        Args:
            seconds (float): The amount of time in seconds to look right.
        """

        self.client.send_message("/input/LookRight", 1)
        time.sleep(seconds)
        self.client.send_message("/input/LookRight", 0)

    def jump(self):
        """
        Sends a command to make the avatar jump.
        """

        self.client.send_message("/input/Jump", 1)
        time.sleep(0.1)
        self.client.send_message("/input/Jump", 0)
