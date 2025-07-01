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
import subprocess
import sys
import time
import logging
import json
import nova
import constants as constant
from classes.osc import VRChatOSC
from classes.vrchat_api import VRChatAPIManager
import warnings

warnings.filterwarnings(
                    "ignore",
                    message="FP16 is not supported on CPU; using FP32 instead"
    )

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def clear_vision_history() -> None:
    """
    Clear the vision history log file at startup.
    This ensures that each program run starts with a clean vision history.
    """
    try:
        vision_log_path = constant.VisionSystem.LOG_FILE
        with open(vision_log_path, 'w') as f:
            json.dump([], f)
        print("\033[92mVision history cleared.\033[0m")
    except Exception as e:
        print(f"\033[91mError clearing vision history: {e}\033[0m")


def main() -> None:
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

    # Clear vision history at startup
    clear_vision_history()

    # Initialize VRChat OSC
    osc = VRChatOSC(constant.Network.LOCAL_IP, constant.Network.VRC_PORT)

    # Initialize VRChat API if enabled
    vrchat_api = None
    if VRChatAPIManager.is_api_enabled():
        vrchat_api = VRChatAPIManager()

        # Try to initialize VRChat API
        print("\033[94mInitializing VRChat API...\033[0m")
        if vrchat_api.initialize():
            print("\033[92mVRChat API initialized successfully\033[0m")
            # Start periodic checks for friend requests and notifications
            vrchat_api.start_periodic_checks()
        else:
            print("\033[91mVRChat API initialization failed, continuing "
                  "without API features\033[0m")
            vrchat_api = None
    else:
        print("\033[93mVRChat API disabled in configuration\033[0m")

    try:
        while True:
            try:
                print("\033[91mProgram Starting...\033[0m")

                print("\033[91mStarting resource monitor...\033[0m")

                try:
                    subprocess.Popen(
                        [sys.executable, "resource_monitor.py"],
                        shell=False
                        )
                except Exception as e:
                    print(f"\033[91mError starting resource monitor: "
                          f"{e}\033[0m")

                nova.run_code()
            except (RuntimeError, ValueError) as e:
                logging.error("An error occurred: %s", e)
                osc.send_message(f"System Error: {e}")
                osc.set_typing_indicator(True)
                time.sleep(constant.ErrorHandling.ERROR_RETRY_DELAY)
    finally:
        # Clean up VRChat API on exit
        if vrchat_api and vrchat_api.is_authenticated:
            print("\033[93mShutting down VRChat API...\033[0m")
            vrchat_api.disconnect()


if __name__ == '__main__':
    clear_vision_history()
    main()
