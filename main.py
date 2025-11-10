import logging
import warnings

import constants as constant
import nova
from classes.osc import VRChatOSC
from classes.vision_manager import VisionManager
from classes.vrchat_api import VRChatAPIManager

# Set up logging configuration
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def initialize_osc() -> VRChatOSC | None:
    # Initialize VRChat OSC object
    print("Initializing OSC (main.py)...")
    try:
        osc = VRChatOSC(constant.Network.LOCAL_IP, constant.Network.VRC_PORT)
        osc.send_message("System Starting")
        osc.set_typing_indicator(True)
        print("\033[92mOSC Initialized Successfully (main.py).\033[0m")
        return osc
    except Exception as e:
        logging.error(f"\033[91mFailed to initialize OSC: {e}\033[0m")
        warnings.warn("\033[91mOSC initialization failed. Continuing without OSC (main.py).\033[0m")
        return None


def create_vrchat_api_manager() -> None:
    # Clear vision history and create VRChat API manager
    print("Creating VRChat API Manager (main.py)...")
    try:
        VisionManager.clear_vision_history()
        VRChatAPIManager.create_vrchat_api_manager()
        print("\033[92mVRChat API Manager Created Successfully.\033[0m")
    except Exception as e:
        logging.error(f"\033[91mFailed to create VRChat API Manager: {e}\033[0m")
        warnings.warn("\033[91mVRChat API Manager creation failed. Continuing without it (main.py).\033[0m")
        return None


def main() -> None:
    print("\033[91mProgram Starting...\033[0m")

    initialize_osc()
    create_vrchat_api_manager()

    nova.main()


if __name__ == "__main__":
    main()
