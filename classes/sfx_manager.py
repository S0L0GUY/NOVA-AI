"""
Sound-effects (SFX) manager for NOVA-AI.

Scans the sfx/ directory for audio files, maintains a JSON cache, and
plays them on request via pygame.  Exposes Gemini function-call
declarations so the LLM can trigger sound playback directly.

Ported from Project Gabriel's sfx.py and refactored to NOVA's
class-based, constants-driven coding style.
"""

import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import constants as constant

logger = logging.getLogger(__name__)

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False


class SFXManager:
    """
    Manages local sound-effect files and handles playback via pygame.

    The manager scans the configured SFX directory on initialisation and
    maintains a lightweight JSON index so repeated startups are fast.
    Files are looked up by name, relative path, or fuzzy search term.
    """

    def __init__(self, sfx_dir: Optional[str] = None) -> None:
        """
        Initialises the SFXManager.

        Args:
            sfx_dir (Optional[str]): Override for the SFX base directory.
                                     Falls back to constant.FilePaths.SFX_DIR.
        """
        self.sfx_base_path = Path(sfx_dir or constant.FilePaths.SFX_DIR)
        self.cache_file = self.sfx_base_path / constant.SFXConfig.CACHE_FILENAME
        self.audio_cache: Dict[str, Dict[str, Any]] = {}
        self.is_playing: bool = False
        self.volume: float = constant.SFXConfig.DEFAULT_VOLUME
        self.current_playing_info: Optional[Dict[str, Any]] = None
        self.supported_formats = constant.SFXConfig.SUPPORTED_FORMATS

        self._monitor_thread: Optional[threading.Thread] = None
        self._monitor_stop = threading.Event()

        self._init_audio()
        self._load_cache()
        self._scan_files()

    def _init_audio(self) -> None:
        """
        Initialises the pygame mixer, or falls back gracefully if unavailable.
        """
        if not _PYGAME_AVAILABLE:
            logger.error("SFXManager: pygame is not installed – SFX disabled.")
            self.audio_system: Optional[str] = None
            return

        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.audio_system = "pygame"
            logger.info("SFXManager: pygame audio system initialised.")
            self._start_monitor_thread()
        except Exception as exc:
            logger.warning(f"SFXManager: failed to initialise pygame: {exc}")
            self.audio_system = None

    def _start_monitor_thread(self) -> None:
        """
        Starts the background thread that clears is_playing when music ends.
        """
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        self._monitor_stop.clear()
        t = threading.Thread(target=self._monitor_loop, daemon=True, name="sfx-monitor")
        self._monitor_thread = t
        t.start()

    def _monitor_loop(self) -> None:
        """
        Background loop that tracks when pygame music finishes.
        """
        while not self._monitor_stop.is_set():
            try:
                if self.audio_system == "pygame" and self.is_playing:
                    info = self.current_playing_info or {}
                    if str(info.get("category", "")).lower() == "music":
                        try:
                            busy = pygame.mixer.music.get_busy()
                        except Exception:
                            busy = False
                        if not busy:
                            self.is_playing = False
                            self.current_playing_info = None
                            logger.debug("SFXManager: music playback finished.")
            except Exception as exc:
                logger.debug(f"SFXManager: monitor loop error: {exc}")
            finally:
                time.sleep(0.5)

    def _load_cache(self) -> None:
        """
        Loads the audio file index from the JSON cache file.
        """
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.audio_cache = json.load(f)
                logger.info(f"SFXManager: loaded {len(self.audio_cache)} cached files.")
        except Exception as exc:
            logger.error(f"SFXManager: error loading cache: {exc}")
            self.audio_cache = {}

    def _save_cache(self) -> None:
        """
        Saves the current audio file index to the JSON cache file.
        """
        try:
            self.sfx_base_path.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.audio_cache, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            logger.error(f"SFXManager: error saving cache: {exc}")

    def _scan_files(self) -> None:
        """
        Walks the SFX directory and rebuilds the in-memory index.
        Any new or modified files trigger a cache save.
        """
        if not self.sfx_base_path.exists():
            logger.warning(f"SFXManager: SFX directory '{self.sfx_base_path}' does not exist.")
            return

        new_files = 0
        updated_files = 0

        for root, _, files in os.walk(self.sfx_base_path):
            for filename in files:
                file_path = Path(root) / filename
                if file_path.suffix.lower() not in self.supported_formats:
                    continue

                rel = str(file_path.relative_to(self.sfx_base_path)).replace("\\", "/")
                stats = file_path.stat()
                info: Dict[str, Any] = {
                    "path": str(file_path),
                    "relative_path": rel,
                    "name": file_path.stem,
                    "category": (
                        file_path.parent.name
                        if file_path.parent != self.sfx_base_path
                        else "general"
                    ),
                    "format": file_path.suffix.lower(),
                    "size": stats.st_size,
                    "modified": stats.st_mtime,
                }

                if rel not in self.audio_cache:
                    new_files += 1
                elif self.audio_cache[rel].get("modified") != stats.st_mtime:
                    updated_files += 1

                self.audio_cache[rel] = info

        logger.info(
            f"SFXManager: scanned – {new_files} new, {updated_files} updated, "
            f"{len(self.audio_cache)} total."
        )
        if new_files > 0 or updated_files > 0:
            self._save_cache()

    def get_audio_files(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns a sorted list of available audio files.

        Args:
            category (Optional[str]): If given, filter to this category only.

        Returns:
            List[Dict[str, Any]]: List of file-info dicts.
        """
        files = [
            info
            for info in self.audio_cache.values()
            if category is None or info["category"].lower() == category.lower()
        ]
        return sorted(files, key=lambda x: x["name"].lower())

    def search_audio_files(self, query: str) -> List[Dict[str, Any]]:
        """
        Searches the index by name, category, or relative path.

        Args:
            query (str): Search term.

        Returns:
            List[Dict[str, Any]]: Matching file-info dicts.
        """
        q = query.lower()
        results = [
            info
            for info in self.audio_cache.values()
            if q in info["name"].lower()
            or q in info["category"].lower()
            or q in info["relative_path"].lower()
        ]
        return sorted(results, key=lambda x: x["name"].lower())

    def get_categories(self) -> List[str]:
        """
        Returns a sorted list of unique category names present in the index.

        Returns:
            List[str]: Category names.
        """
        return sorted({info["category"] for info in self.audio_cache.values()})

    def play_audio_file(
        self, file_identifier: str, count: int = 1
    ) -> Dict[str, Any]:
        """
        Plays an audio file identified by name, path, or search term.

        Args:
            file_identifier (str): Name, relative path, or fuzzy search term.
            count (int): Number of times to play the file.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        if not self.audio_system:
            return {"success": False, "message": "No audio system available."}

        file_info = self._find_audio_file(file_identifier)
        if not file_info:
            return {"success": False, "message": f"Audio file '{file_identifier}' not found."}

        self.stop_audio()

        try:
            last_result: Dict[str, Any] = {}
            for _ in range(max(1, int(count))):
                last_result = self._play_with_pygame(file_info["path"], file_info)
                if not last_result.get("success"):
                    return last_result
            return last_result
        except Exception as exc:
            logger.error(f"SFXManager: error playing '{file_identifier}': {exc}")
            return {"success": False, "message": f"Playback error: {exc}"}

    def _find_audio_file(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Resolves a file identifier to a cache entry.

        Looks up exact path matches first, then exact name matches, then
        falls back to fuzzy token scoring.

        Args:
            identifier (str): The user-supplied identifier string.

        Returns:
            Optional[Dict[str, Any]]: Matching cache entry, or None.
        """
        id_low = identifier.strip().lower().replace("\\", "/").strip("/ ")
        if not id_low:
            return None

        # Exact relative-path match
        for info in self.audio_cache.values():
            if info["relative_path"].lower() == id_low:
                return info

        # Exact stem name match
        for info in self.audio_cache.values():
            if info["name"].lower() == id_low:
                return info

        # Fuzzy token scoring
        best: Optional[Dict[str, Any]] = None
        best_score = -1
        for info in self.audio_cache.values():
            name_norm = info["name"].lower()
            rel_norm = info["relative_path"].lower()
            if id_low == name_norm or id_low == rel_norm:
                score = 100
            elif id_low in name_norm or id_low in rel_norm:
                score = len(id_low)
            else:
                tokens = set(id_low.split())
                score = sum(1 for t in tokens if t in name_norm or t in rel_norm) if tokens else 0
            if score > best_score:
                best = info
                best_score = score

        return best if best_score > 0 else None

    def _play_with_pygame(
        self, file_path: str, file_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plays a single audio file with pygame.

        Args:
            file_path (str): Absolute path to the audio file.
            file_info (Dict[str, Any]): Metadata dict from the cache.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            self.is_playing = True
            self.current_playing_info = file_info
            return {
                "success": True,
                "message": f"Playing '{file_info['name']}' via pygame.",
                "file_info": file_info,
            }
        except Exception as exc:
            raise RuntimeError(f"pygame playback error: {exc}") from exc

    def stop_audio(self) -> Dict[str, Any]:
        """
        Stops any currently playing audio.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        try:
            if not self.is_playing:
                return {"success": True, "message": "No audio currently playing."}
            if self.audio_system == "pygame":
                pygame.mixer.music.stop()
            self.is_playing = False
            self.current_playing_info = None
            return {"success": True, "message": "Audio stopped."}
        except Exception as exc:
            logger.error(f"SFXManager: error stopping audio: {exc}")
            return {"success": False, "message": f"Stop error: {exc}"}

    def set_volume(self, volume: float) -> Dict[str, Any]:
        """
        Sets the playback volume.

        Args:
            volume (float): Volume level between 0.0 and 1.0.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        try:
            volume = max(0.0, min(1.0, volume))
            self.volume = volume
            if self.is_playing and self.audio_system == "pygame":
                pygame.mixer.music.set_volume(volume)
            return {"success": True, "message": f"Volume set to {volume:.0%}.", "volume": volume}
        except Exception as exc:
            return {"success": False, "message": f"Volume error: {exc}"}

    def get_playback_status(self) -> Dict[str, Any]:
        """
        Returns the current playback state.

        Returns:
            Dict[str, Any]: Status dict.
        """
        return {
            "is_playing": self.is_playing,
            "volume": self.volume,
            "audio_system": self.audio_system,
            "total_files": len(self.audio_cache),
            "categories": self.get_categories(),
            "current": self.current_playing_info.get("name") if self.current_playing_info else None,
        }

    def is_music_playing(self) -> bool:
        """
        Returns True if a 'music' category file is currently playing.

        Returns:
            bool: True if music is active.
        """
        if not self.is_playing:
            return False
        info = self.current_playing_info or {}
        return str(info.get("category", "")).lower() == "music"

    FUNCTION_DECLARATIONS = [
        {
            "name": "play_sfx",
            "description": "Play a sound effect or audio file from the sfx folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_identifier": {
                        "type": "string",
                        "description": "Name, relative path, or search term for the audio file.",
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of times to play (default 1).",
                        "default": 1,
                        "minimum": 1,
                    },
                },
                "required": ["file_identifier"],
            },
        },
        {
            "name": "stop_sfx",
            "description": "Stop any currently playing sound effect.",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "list_sfx",
            "description": "List available sound effects, optionally filtered by category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Category filter."},
                    "limit": {"type": "integer", "description": "Max files to return.", "default": 20},
                },
            },
        },
        {
            "name": "search_sfx",
            "description": "Search for sound effects by name or category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term."},
                    "limit": {"type": "integer", "description": "Max results.", "default": 10},
                },
                "required": ["query"],
            },
        },
        {
            "name": "set_sfx_volume",
            "description": "Set SFX playback volume (0.0 – 1.0).",
            "parameters": {
                "type": "object",
                "properties": {
                    "volume": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                },
                "required": ["volume"],
            },
        },
        {
            "name": "get_sfx_status",
            "description": "Get current SFX playback status.",
            "parameters": {"type": "object", "properties": {}},
        },
    ]

    async def handle_function_call(self, function_call) -> Any:
        """
        Dispatches a Gemini function-call object to the correct SFX action.

        Args:
            function_call: Gemini types.FunctionCall with .name and .args.

        Returns:
            types.FunctionResponse
        """
        from google.genai import types

        name = function_call.name
        args = function_call.args or {}

        try:
            if name == "play_sfx":
                result = self.play_audio_file(args["file_identifier"], args.get("count", 1))
            elif name == "stop_sfx":
                result = self.stop_audio()
            elif name == "list_sfx":
                files = self.get_audio_files(args.get("category"))
                limit = args.get("limit", 20)
                result = {
                    "success": True,
                    "files": [{"name": f["name"], "category": f["category"]} for f in files[:limit]],
                    "total": len(files),
                }
            elif name == "search_sfx":
                files = self.search_audio_files(args["query"])
                limit = args.get("limit", 10)
                result = {
                    "success": True,
                    "files": [{"name": f["name"], "category": f["category"]} for f in files[:limit]],
                    "total": len(files),
                }
            elif name == "set_sfx_volume":
                result = self.set_volume(args["volume"])
            elif name == "get_sfx_status":
                result = {"success": True, **self.get_playback_status()}
            else:
                result = {"success": False, "message": f"Unknown SFX function: {name}"}

            return types.FunctionResponse(id=function_call.id, name=name, response=result)

        except Exception as exc:
            logger.error(f"SFXManager: function '{name}' failed: {exc}")
            return types.FunctionResponse(
                id=function_call.id,
                name=name,
                response={"success": False, "message": f"Error in {name}: {exc}"},
            )

_sfx_manager: Optional[SFXManager] = None


def get_sfx_manager() -> SFXManager:
    """
    Returns the module-level SFXManager singleton.

    Returns:
        SFXManager: The shared instance.
    """
    global _sfx_manager
    if _sfx_manager is None:
        _sfx_manager = SFXManager()
    return _sfx_manager
