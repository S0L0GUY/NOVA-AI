"""
This script controls the movement and orientation of an avatar in the virtual
world "The Black Cat" using OSC (Open Sound Control) messages.
Modules:
    constants: A module containing constant values such as LOCAL_IP and
    VRC_PORT.
    pythonosc.udp_client: A module for sending OSC messages over UDP.
    time: A module for handling time-related tasks.
Functions:
    move_forward(duration, speed=1):
        Moves the avatar forward for a specified duration at a given speed.
        Args:
            duration (float): The time in seconds to move forward.
            speed (int, optional): The speed of movement. Default is 1.
    look_right(duration, speed=1):
        Rotates the avatar to the right for a specified duration at a given
        speed.
        Args:
            duration (float): The time in seconds to rotate right.
            speed (int, optional): The speed of rotation. Default is 1.
    look_left(duration, speed=1):
        Rotates the avatar to the left for a specified duration at a given
        speed.
        Args:
            duration (float): The time in seconds to rotate left.
            speed (int, optional): The speed of rotation. Default is 1.
Usage:
    The script sets up an OSC client and sends a message to indicate the start
    of positioning. Depending on the specified world and position, the avatar
    will move and look around according to predefined sequences.
"""

import time
from pythonosc import udp_client
import constants as constant

time.sleep(15)

# Set up OSC
osc_client = udp_client.SimpleUDPClient(constant.LOCAL_IP, constant.VRC_PORT)
osc_client.send_message("/chatbox/input", ["Positioning...", True])

##########################################################################
# "The Black Cat" Positions: "Downstairs Bar" "Upstairs Bar" "Front Desk"
# "Downstairs Bar Back"
WORLD = "The Black Cat"
POSITION = "Downstairs Bar"
##########################################################################


def move_forward(duration, speed=1):
    """
    Moves forward for a specified duration at a given speed.
    Args:
        duration (float): The time in seconds to move forward.
        speed (int, optional): The speed at which to move forward. Default is
        1.
    Returns:
        None
    """

    osc_client.send_message("/input/MoveForward", speed)
    time.sleep(duration)
    osc_client.send_message("/input/MoveForward", 0)


def look_right(duration, speed=1):
    """
    Sends a command to look right for a specified duration and speed.
    Parameters:
    duration (float): The amount of time in seconds to look right.
    speed (int, optional): The speed at which to look right. Default is 1.
    Returns:
    None
    """

    osc_client.send_message("/input/LookRight", speed)
    time.sleep(duration)
    osc_client.send_message("/input/LookRight", 0)


def look_left(duration, speed=1):
    """
    Sends a command to look left for a specified duration and speed.
    Args:
        duration (float): The amount of time in seconds to look left.
        speed (int, optional): The speed at which to look left. Defaults to 1.
    Sends:
        OSC messages to start and stop looking left.
    """

    osc_client.send_message("/input/LookLeft", speed)
    time.sleep(duration)
    osc_client.send_message("/input/LookLeft", 0)


if WORLD == "The Black Cat":
    if POSITION == "Downstairs Bar":
        move_forward(3)
        look_right(0.4)
        move_forward(5.5)
        look_left(0.4)
        move_forward(4.5)
        look_left(0.3)
        move_forward(2.9)
        look_right(0.2)
        move_forward(0.5)
        look_right(0.3)
        move_forward(1.2)
        look_right(0.33)
        move_forward(0.3)
    elif POSITION == "Upstairs Bar":
        move_forward(3)
        look_right(0.4)
        move_forward(5.5)
        look_left(0.4)
        move_forward(3.5)
        look_right(0.45)
        move_forward(4.3)
        look_left(0.45)
        move_forward(3.55)
        look_right(0.45)
        move_forward(1.7)
        look_left(0.3)
        move_forward(4)
        look_left(0.3)
        move_forward(1.8)
        look_left(0.34)
        move_forward(3.4)
        look_right(0.5)
        move_forward(1.5)
        look_right(0.43)
        move_forward(0.3)
    elif POSITION == "Front Desk":
        move_forward(3)
        look_right(0.4)
        move_forward(1.3)
        look_left(0.38)
        move_forward(1.3)
        look_left(0.45)
        move_forward(1.4)
        look_left(0.48)
        move_forward(0.3)
    elif POSITION == "Downstairs Bar Back":
        move_forward(3)
        look_right(0.4)
        move_forward(5.5)
        look_left(0.4)
        move_forward(4.5)
        look_left(0.3)
        move_forward(3.4)
        look_left(0.15)
        move_forward(1)
        look_right(0.15)
        move_forward(1)
        look_right(0.15)
        move_forward(1)
        look_right(0.2)
        move_forward(0.5)
        look_left(0.4)
