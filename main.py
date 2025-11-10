import logging
import warnings

import nova
import classes.adapters as adapters
from classes.vision_manager import VisionManager
from classes.vrchat_api import VRChatAPIManager

# Set up logging configuration
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def main() -> None:
    print("\033[91mProgram Starting...\033[0m")

    adapters.initialize_osc()
    adapters.create_vrchat_api_manager()

    nova.main()


if __name__ == "__main__":
    main()
