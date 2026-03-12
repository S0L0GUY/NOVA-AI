"""
NOVA-AI Supervisor entry point.

Run this instead of main.py when you want the supervisor to automatically
restart NOVA if it crashes.

Usage:
    python supervisor.py
"""

from classes.supervisor import Supervisor
import constants as constant
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(constant.SupervisorConfig.LOG_FILE),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Starts the NOVA-AI supervisor process.
    """
    logger.info("=" * 60)
    logger.info("  NOVA-AI Supervisor starting...")
    logger.info("=" * 60)

    supervisor = Supervisor()
    supervisor.run()

    logger.info("Supervisor shutdown complete.")


if __name__ == "__main__":
    main()
