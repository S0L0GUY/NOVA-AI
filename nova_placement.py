import constants as constant
from pythonosc import udp_client
import time

time.sleep(15)

# Set up OSC
osc_client = udp_client.SimpleUDPClient(constant.LOCAL_IP, constant.VRC_PORT)
osc_client.send_message("/chatbox/input", ["Positioning...", True])

################################################################################################
# "The Black Cat" Positions: "Downstairs Bar" "Upstairs Bar" "Front Desk" "Downstairs Bar Back"
world = "The Black Cat"
position = "Downstairs Bar"
################################################################################################

def move_forward(time, speed=1):
    osc_client.send_message("/input/MoveForward", speed)
    time.sleep(time)
    osc_client.send_message("/input/MoveForward", 0)

def look_right(time, speed=1):
    osc_client.send_message("/input/LookRight", speed)
    time.sleep(time)
    osc_client.send_message("/input/LookRight", 0)

def look_left(time, speed=1):
    osc_client.send_message("/input/LookLeft", speed)
    time.sleep(time)
    osc_client.send_message("/input/LookLeft", 0)

if world == "The Black Cat":
    if position == "Downstairs Bar":
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
    elif position == "Upstairs Bar":
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
    elif position == "Front Desk":
        move_forward(3)
        look_right(0.4)
        move_forward(1.3)
        look_left(0.38)
        move_forward(1.3)
        look_left(0.45)
        move_forward(1.4)
        look_left(0.48)
        move_forward(0.3)
    elif position == "Downstairs Bar Back":
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
