import logging

import classes.adapters as adapters
import nova

# Set up logging configuration
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> None:
    print("\033[91mProgram Starting...\033[0m")

    adapters.initialize_osc()
    adapters.create_vrchat_api_manager()

    nova.main()


if __name__ == "__main__":
    main()
