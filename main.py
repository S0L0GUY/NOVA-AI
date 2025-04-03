"""
Main module for running the Nova AI application.
This module sets up logging, initializes the VRChatOSC class, and runs the
main loop which executes the Nova AI code. If an error occurs during execution,
it logs the error, sends an error message via OSC, and sets a typing indicator.
Functions:
    main(): Initializes VRChatOSC and runs the Nova AI code in a loop,
    handling any exceptions.
Usage:
    Run this module directly to start the Nova AI application.
"""
import time
import logging
import nova
import constants as constant
from classes.osc import VRChatOSC
import warnings

warnings.filterwarnings(
                    "ignore",
                    message="FP16 is not supported on CPU; using FP32 instead"
    )

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    """
    Main function to start the VRChatOSC and run the Nova code.
    This function initializes the VRChatOSC with the local IP and VRC port
    from the constants. It then enters an infinite loop where it attempts to
    run the Nova code. If an exception occurs, it logs the error, sends an
    error message via VRChatOSC, sets the typing indicator, waits for 5
    seconds, and continues the loop.
    Raises:
        Exception: If an error occurs during the execution of nova.run_code().
    """

    osc = VRChatOSC(constant.Network.LOCAL_IP, constant.Network.VRC_PORT)
    while True:
        try:
            print("Program Starting...")
            nova.run_code()
        except (RuntimeError, ValueError) as e:
            logging.error("An error occurred: %s", e)
            osc.send_message(f"System Error: {e}")
            osc.set_typing_indicator(True)
            time.sleep(5)


if __name__ == '__main__':
    main()
