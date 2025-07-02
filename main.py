import subprocess
import sys
import logging
import nova
import constants as constant
from classes.osc import VRChatOSC
from classes.vrchat_api import VRChatAPIManager
from classes.vision_manager import VisionManager
import warnings

# Supresses FP16 warnings on CPU
warnings.filterwarnings(
                    "ignore",
                    message="FP16 is not supported on CPU; using FP32 instead"
    )

# Configure logging to log errors to a file
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main() -> None:
    print("\033[91mProgram Starting...\033[0m")

    # Initialize VRChat OSC object
    osc = VRChatOSC(constant.Network.LOCAL_IP, constant.Network.VRC_PORT)

    osc.send_message("System Starting")
    osc.set_typing_indicator(True)

    VisionManager.clear_vision_history()
    VRChatAPIManager.create_vrchat_api_manager()

    print("\033[91mStarting resource monitor...\033[0m")

    try:
        subprocess.Popen(
            [sys.executable, "resource_monitor.py"],
            shell=False
            )

    except Exception as e:
        print(f"\033[91mError starting resource monitor: "
              f"{e}\033[0m")

    nova.main()


if __name__ == '__main__':
    main()
