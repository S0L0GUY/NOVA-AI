import logging
import warnings

import constants as constant
import nova
from classes.osc import VRChatOSC
from classes.vision_manager import VisionManager
from classes.vrchat_api import VRChatAPIManager

# Suppresses FP16 warnings on CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Configure logging to log errors to a file
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> None:
    print("\033[91mProgram Starting...\033[0m")

    # Initialize VRChat OSC object
    osc = VRChatOSC(constant.Network.LOCAL_IP, constant.Network.VRC_PORT)

    osc.send_message("System Starting")
    osc.set_typing_indicator(True)

    VisionManager.clear_vision_history()
    VRChatAPIManager.create_vrchat_api_manager()

    nova.main()


if __name__ == "__main__":
    main()
