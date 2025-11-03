import time

from pythonosc import udp_client

import constants as constant

time.sleep(constant.NovaPlacement.INITIAL_DELAY)

# Set up OSC
osc_client = udp_client.SimpleUDPClient(constant.Network.LOCAL_IP, constant.Network.VRC_PORT)
osc_client.send_message("/chatbox/input", ["Positioning...", True])

##########################################################################
# "The Black Cat" Positions: "Downstairs Bar" "Upstairs Bar" "Front Desk"
# "Downstairs Bar Back"
WORLD = constant.NovaPlacement.DEFAULT_WORLD
POSITION = constant.NovaPlacement.DEFAULT_POSITION
##########################################################################


def move_forward(duration: float, speed=1) -> None:
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


def look_right(duration: float, speed=1) -> None:
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


def look_left(duration: float, speed=1) -> None:
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


def main() -> None:
    """
    Main function to execute the movement and look commands based on the
    """
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


if __name__ == "__main__":
    main()
