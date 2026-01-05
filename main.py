import logging

import classes.adapters as adapters
import nova

# Set up logging configuration
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> None:
    colors = ["\033[91m", "\033[93m", "\033[92m", "\033[96m", "\033[94m", "\033[95m"]
    lines = [
        "===========================================",
        "|                NOVA-AI                  |",
        "|          Developed by N O M A           |",
        "==========================================="
    ]
    for line in lines:
        colored_line = "".join(f"{colors[i % len(colors)]}{char}\033[0m" for i, char in enumerate(line))
        print(colored_line)

    print("\033[91mProgram Starting...\033[0m")

    adapters.initialize_osc()
    adapters.create_vrchat_api_manager()

    nova.main()


if __name__ == "__main__":
    main()
