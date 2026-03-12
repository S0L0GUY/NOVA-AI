"""
Supervisor module for NOVA-AI.

Watches the main nova process and automatically restarts it on crash.
Ported from Project Gabriel's supervisor.py, refactored into NOVA's
class-based style and integrated with constants.py.
"""

import logging
import subprocess
import sys
import time
from datetime import datetime
from typing import Optional

import constants as constant

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(constant.SupervisorConfig.LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class ProcessMonitor:
    """
    Monitors a single child process and handles restarts.

    Attributes:
        name (str): Human-readable name for log output.
        path (str): Path to the Python script to run.
        restart_delay (int): Seconds to wait before restarting.
        max_restart_attempts (Optional[int]): Cap on restarts (None = unlimited).
        enabled (bool): Whether this monitor is active.
    """

    def __init__(
        self,
        name: str,
        path: str,
        restart_delay: int = constant.SupervisorConfig.RESTART_DELAY,
        max_restart_attempts: Optional[int] = constant.SupervisorConfig.MAX_RESTART_ATTEMPTS,
        enabled: bool = True,
    ) -> None:
        """
        Initialises the ProcessMonitor.

        Args:
            name (str): Display name for this process.
            path (str): Path to the Python script to launch.
            restart_delay (int): Seconds to wait before restarting on crash.
            max_restart_attempts (Optional[int]): Maximum restarts before giving up.
            enabled (bool): Whether this process should be started.
        """
        self.name = name
        self.path = path
        self.restart_delay = restart_delay
        self.max_restart_attempts = max_restart_attempts
        self.enabled = enabled

        self.process: Optional[subprocess.Popen] = None
        self.restart_count: int = 0
        self.last_start_time: Optional[datetime] = None

    def start(self) -> bool:
        """
        Starts the monitored process.

        Returns:
            bool: True if the process started successfully, False otherwise.
        """
        if not self.enabled:
            logger.info(f"{self.name} is disabled, skipping.")
            return False

        try:
            logger.info(f"Starting {self.name}...")
            self.process = subprocess.Popen(
                [sys.executable, self.path],
                stdout=None,
                stderr=None,
                stdin=None,
            )
            self.last_start_time = datetime.now()
            self.restart_count += 1
            logger.info(f"{self.name} started with PID {self.process.pid}")
            return True
        except Exception as exc:
            logger.error(f"Failed to start {self.name}: {exc}")
            return False

    def is_running(self) -> bool:
        """
        Checks whether the process is currently running.

        Returns:
            bool: True if the process is alive.
        """
        if self.process is None:
            return False
        return self.process.poll() is None

    def get_exit_code(self) -> Optional[int]:
        """
        Returns the exit code of the process if it has stopped.

        Returns:
            Optional[int]: Exit code, or None if the process is still running.
        """
        if self.process:
            return self.process.poll()
        return None

    def should_restart(self) -> bool:
        """
        Determines whether the process should be restarted.

        Returns:
            bool: True if a restart attempt is allowed.
        """
        if not self.enabled:
            return False
        if (
            self.max_restart_attempts is not None
            and self.restart_count >= self.max_restart_attempts
        ):
            logger.warning(
                f"{self.name} has reached the maximum restart attempts "
                f"({self.max_restart_attempts})."
            )
            return False
        return True

    def stop(self) -> None:
        """
        Gracefully terminates the monitored process.
        """
        if self.process and self.is_running():
            logger.info(f"Stopping {self.name}...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"{self.name} did not stop gracefully – killing.")
                self.process.kill()


class Supervisor:
    """
    Manages a collection of ProcessMonitors and keeps them alive.

    This is the main entry point when running NOVA-AI via the supervisor
    rather than directly via main.py.
    """

    def __init__(self) -> None:
        """
        Initialises the supervisor with the default NOVA-AI process list.
        """
        self.monitors = [
            ProcessMonitor(
                name="NOVA-AI main.py",
                path="main.py",
                restart_delay=constant.SupervisorConfig.RESTART_DELAY,
                max_restart_attempts=constant.SupervisorConfig.MAX_RESTART_ATTEMPTS,
                enabled=True,
            )
        ]
        self.running = True

    def start_all(self) -> None:
        """
        Starts all enabled monitored processes.
        """
        logger.info("Supervisor starting all enabled processes...")
        for monitor in self.monitors:
            if monitor.enabled:
                monitor.start()
                time.sleep(1)

    def check_and_restart(self) -> None:
        """
        Checks each monitor and restarts any that have stopped unexpectedly.
        """
        for monitor in self.monitors:
            if not monitor.enabled:
                continue

            if not monitor.is_running():
                exit_code = monitor.get_exit_code()
                if exit_code is not None:
                    logger.warning(f"{monitor.name} exited with code {exit_code}.")
                else:
                    logger.warning(f"{monitor.name} is not running.")

                if monitor.should_restart():
                    logger.info(
                        f"Restarting {monitor.name} in {monitor.restart_delay}s..."
                    )
                    time.sleep(monitor.restart_delay)
                    monitor.start()
                else:
                    logger.error(f"{monitor.name} will not be restarted.")

    def stop_all(self) -> None:
        """
        Stops all monitored processes and shuts the supervisor down.
        """
        logger.info("Supervisor stopping all processes...")
        for monitor in self.monitors:
            monitor.stop()
        self.running = False

    def run(self) -> None:
        """
        Main supervisor loop. Starts all processes and watches them indefinitely.
        """
        self.start_all()

        try:
            while self.running:
                self.check_and_restart()
                time.sleep(2)
        except KeyboardInterrupt:
            logger.info("Supervisor received shutdown signal.")
            self.stop_all()
        except Exception as exc:
            logger.error(f"Supervisor error: {exc}")
            self.stop_all()
