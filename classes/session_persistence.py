"""
Session persistence module for NOVA-AI.

Saves and loads the active conversation/session handle so that context
is preserved across unexpected shutdowns or planned restarts.

Ported from Project Gabriel's session_persistence.py and refactored to
follow NOVA's class-based, constants-driven coding style.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import constants as constant

logger = logging.getLogger(__name__)


class SessionPersistenceManager:
    """
    Manages saving and loading of session handles to/from disk.

    The handle is written periodically so the most recent context can be
    recovered after a crash.  This is especially useful for long-running
    sessions where rebuilding context from scratch would be expensive.
    """

    def __init__(
        self,
        save_interval: int = constant.SessionPersistenceConfig.SAVE_INTERVAL,
    ) -> None:
        """
        Initialises the SessionPersistenceManager.

        Args:
            save_interval (int): Seconds between automatic saves.
        """
        self.save_interval = save_interval
        self.session_file = Path(constant.FilePaths.SESSION_FILE)
        self.last_save_time: float = 0.0
        self._running: bool = False
        logger.info(
            f"SessionPersistenceManager initialised with {save_interval}s save interval."
        )

    def save_session_handle(
        self,
        handle: str,
        mode: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Writes the session handle and optional metadata to disk.

        Args:
            handle (str): The session handle string to persist.
            mode (str): Identifier for the session mode (e.g. 'v1').
            metadata (Optional[Dict[str, Any]]): Additional data to save.

        Returns:
            bool: True on success, False on failure.
        """
        try:
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "handle": handle,
                "mode": mode,
                "timestamp": time.time(),
                "metadata": metadata or {},
            }
            with open(self.session_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
            logger.info(f"Saved {mode} session handle to {self.session_file}.")
            return True
        except Exception as exc:
            logger.error(f"Failed to save session handle: {exc}")
            return False

    def load_session_handle(self) -> Optional[Dict[str, Any]]:
        """
        Reads the most recently saved session handle from disk.

        Returns:
            Optional[Dict[str, Any]]: Saved data dict, or None if unavailable.
        """
        try:
            if not self.session_file.exists():
                logger.info("No saved session handle found.")
                return None
            with open(self.session_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            logger.info(
                f"Loaded {data.get('mode', 'unknown')} session handle "
                f"(saved at {data.get('timestamp', 0):.0f})."
            )
            return data
        except Exception as exc:
            logger.error(f"Failed to load session handle: {exc}")
            return None

    def get_session_age(self) -> Optional[float]:
        """
        Returns the age of the saved session in seconds.

        Returns:
            Optional[float]: Age in seconds, or None if no session file exists.
        """
        data = self.load_session_handle()
        if data and "timestamp" in data:
            return time.time() - data["timestamp"]
        return None

    def clear_session_handle(self) -> bool:
        """
        Deletes the saved session handle file.

        Returns:
            bool: True on success or if no file existed, False on error.
        """
        try:
            if self.session_file.exists():
                self.session_file.unlink()
                logger.info("Cleared saved session handle.")
            return True
        except Exception as exc:
            logger.error(f"Failed to clear session handle: {exc}")
            return False

    async def start_periodic_save(
        self,
        handle_getter: Callable[[], Optional[str]],
        mode: str,
        metadata_getter: Optional[Callable[[], Dict[str, Any]]] = None,
    ) -> None:
        """
        Runs as an async task and saves the session handle on a fixed interval.

        Args:
            handle_getter: Zero-arg callable that returns the current handle.
            mode (str): Session mode identifier passed to save_session_handle.
            metadata_getter: Optional callable returning metadata to persist.
        """
        self._running = True
        logger.info(f"Started periodic session save for '{mode}' mode.")
        try:
            while self._running:
                await asyncio.sleep(self.save_interval)
                if not self._running:
                    break
                handle = handle_getter()
                if handle:
                    metadata = metadata_getter() if metadata_getter else None
                    self.save_session_handle(handle, mode, metadata)
                else:
                    logger.debug("No session handle available to save.")
        except asyncio.CancelledError:
            logger.info("Periodic save task cancelled.")
        finally:
            self._running = False

    def stop_periodic_save(self) -> None:
        """
        Signals the periodic save loop to stop on its next iteration.
        """
        self._running = False
        logger.info("Stopped periodic session handle saving.")

_persistence_manager: Optional[SessionPersistenceManager] = None


def get_persistence_manager(
    save_interval: int = constant.SessionPersistenceConfig.SAVE_INTERVAL,
) -> SessionPersistenceManager:
    """
    Returns the module-level SessionPersistenceManager singleton.

    Args:
        save_interval (int): Interval passed to the manager on first creation.

    Returns:
        SessionPersistenceManager: The shared instance.
    """
    global _persistence_manager
    if _persistence_manager is None:
        _persistence_manager = SessionPersistenceManager(save_interval)
    return _persistence_manager
