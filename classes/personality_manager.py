"""
Personality manager for NOVA-AI.

Allows the LLM to switch between different personality presets at runtime.
Personalities are stored in a JSON file (default: personalities.json) so
new ones can be added without touching code.

Ported from Project Gabriel's personalities.py and refactored to NOVA's
class-based, constants-driven coding style.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import constants as constant

logger = logging.getLogger(__name__)


class PersonalityManager:
    """
    Loads, stores, and switches between named personality presets.

    Each personality is a dict with at minimum:
        - name (str)
        - description (str)
        - prompt (str)  – injected as a system instruction on switch
        - enabled (bool)
    """

    def __init__(self, personalities_file: Optional[str] = None) -> None:
        """
        Initialises the PersonalityManager.

        Args:
            personalities_file (Optional[str]): Override the JSON file path.
                Falls back to constant.FilePaths.PERSONALITIES_FILE.
        """
        self.personalities_file = personalities_file or constant.FilePaths.PERSONALITIES_FILE
        self.personalities: Dict[str, Dict[str, Any]] = {}
        self.current_personality: Optional[str] = None
        self.personality_history: List[Dict[str, Any]] = []
        self._load_personalities()

    def _load_personalities(self) -> None:
        """
        Reads personalities from the JSON file.
        """
        try:
            if os.path.exists(self.personalities_file):
                with open(self.personalities_file, "r", encoding="utf-8") as f:
                    self.personalities = json.load(f)
                logger.info(
                    f"PersonalityManager: loaded {len(self.personalities)} personalities."
                )
            else:
                logger.warning(
                    f"PersonalityManager: '{self.personalities_file}' not found – "
                    "starting with empty personality set."
                )
                self.personalities = {}
        except Exception as exc:
            logger.error(f"PersonalityManager: error loading personalities: {exc}")
            self.personalities = {}

    def _save_personalities(self) -> bool:
        """
        Writes the in-memory personality dict back to disk.

        Returns:
            bool: True on success.
        """
        try:
            with open(self.personalities_file, "w", encoding="utf-8") as f:
                json.dump(self.personalities, f, indent=2, ensure_ascii=False)
            logger.info("PersonalityManager: personalities saved.")
            return True
        except Exception as exc:
            logger.error(f"PersonalityManager: error saving personalities: {exc}")
            return False

    def switch_personality(self, personality_id: str) -> Dict[str, Any]:
        """
        Switches to the named personality.

        Args:
            personality_id (str): Key in the personalities dict.

        Returns:
            Dict[str, Any]: Result dict with 'success' and the prompt to inject.
        """
        if personality_id not in self.personalities:
            return {
                "success": False,
                "message": f"Personality '{personality_id}' not found.",
                "available": list(self.personalities.keys()),
            }

        personality = self.personalities[personality_id]
        if not personality.get("enabled", True):
            return {
                "success": False,
                "message": "This personality is disabled.",
                "personality_id": personality_id,
            }

        self.personality_history.append(
            {
                "from": self.current_personality,
                "to": personality_id,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.current_personality = personality_id
        prompt_text = personality.get("prompt", personality.get("system_prompt", ""))

        logger.info(f"PersonalityManager: switched to '{personality_id}'.")
        return {
            "success": True,
            "message": f"Switched to '{personality['name']}'.",
            "personality_id": personality_id,
            "personality": personality,
            "prompt": prompt_text,
            "instruction": f"Now in {personality['name']} mode. {prompt_text}",
        }

    def get_current_personality(self) -> Dict[str, Any]:
        """
        Returns information about the currently active personality.

        Returns:
            Dict[str, Any]: Result dict including the current prompt.
        """
        if self.current_personality and self.current_personality in self.personalities:
            p = self.personalities[self.current_personality]
            prompt_text = p.get("prompt", p.get("system_prompt", ""))
            return {
                "success": True,
                "personality_id": self.current_personality,
                "personality": p,
                "prompt": prompt_text,
            }
        return {"success": False, "message": "No personality is currently active."}

    def list_personalities(self) -> Dict[str, Any]:
        """
        Lists all available personalities.

        Returns:
            Dict[str, Any]: Result dict with a 'personalities' list.
        """
        items: List[Dict[str, Any]] = [
            {
                "id": pid,
                "name": p["name"],
                "description": p.get("description", ""),
                "active": pid == self.current_personality,
                "enabled": p.get("enabled", True),
            }
            for pid, p in self.personalities.items()
        ]
        return {
            "success": True,
            "personalities": items,
            "count": len(items),
            "current": self.current_personality,
        }

    def add_personality(
        self,
        personality_id: str,
        name: str,
        description: str,
        prompt: str,
        enabled: bool = True,
    ) -> Dict[str, Any]:
        """
        Adds a new personality preset.

        Args:
            personality_id (str): Unique key.
            name (str): Display name.
            description (str): Short description.
            prompt (str): System instruction injected on switch.
            enabled (bool): Whether the personality is switchable.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        if personality_id in self.personalities:
            return {"success": False, "message": f"'{personality_id}' already exists."}

        new_personality = {
            "name": name,
            "description": description,
            "prompt": prompt,
            "enabled": bool(enabled),
        }
        self.personalities[personality_id] = new_personality
        self._save_personalities()
        logger.info(f"PersonalityManager: added '{personality_id}'.")
        return {
            "success": True,
            "message": f"Added personality '{name}'.",
            "personality_id": personality_id,
            "personality": new_personality,
        }

    def update_personality(
        self,
        personality_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        prompt: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Updates one or more fields of an existing personality.

        Args:
            personality_id (str): Key of the personality to update.
            name (Optional[str]): New display name.
            description (Optional[str]): New description.
            prompt (Optional[str]): New system instruction.
            enabled (Optional[bool]): Enable or disable the personality.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        if personality_id not in self.personalities:
            return {"success": False, "message": f"Personality '{personality_id}' not found."}

        p = self.personalities[personality_id]
        if name is not None:
            p["name"] = name
        if description is not None:
            p["description"] = description
        if prompt is not None:
            p["prompt"] = prompt
        if enabled is not None:
            p["enabled"] = bool(enabled)

        self._save_personalities()
        logger.info(f"PersonalityManager: updated '{personality_id}'.")
        return {"success": True, "message": f"Updated '{p['name']}'.", "personality": p}

    def delete_personality(self, personality_id: str) -> Dict[str, Any]:
        """
        Removes a personality preset.

        Args:
            personality_id (str): Key to remove.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        if personality_id not in self.personalities:
            return {"success": False, "message": f"Personality '{personality_id}' not found."}

        if personality_id == self.current_personality:
            self.current_personality = None

        deleted = self.personalities.pop(personality_id)
        self._save_personalities()
        logger.info(f"PersonalityManager: deleted '{personality_id}'.")
        return {"success": True, "message": f"Deleted '{deleted['name']}'."}

    def get_personality_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        Returns recent personality switch history.

        Args:
            limit (int): Maximum history entries to return.

        Returns:
            Dict[str, Any]: Result dict with 'history' list.
        """
        recent = self.personality_history[-limit:] if limit > 0 else self.personality_history
        return {
            "success": True,
            "history": recent,
            "count": len(recent),
            "total_switches": len(self.personality_history),
        }

    FUNCTION_DECLARATIONS = [
        {
            "name": "switch_personality",
            "description": "Switch to a different personality mode, changing behaviour and response style.",
            "parameters": {
                "type": "object",
                "properties": {
                    "personality_id": {
                        "type": "string",
                        "description": "The personality ID to switch to.",
                    }
                },
                "required": ["personality_id"],
            },
        },
        {
            "name": "get_current_personality",
            "description": "Get information about the currently active personality.",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "list_personalities",
            "description": "List all available personality modes.",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "add_personality",
            "description": "Add a new custom personality preset.",
            "parameters": {
                "type": "object",
                "properties": {
                    "personality_id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "prompt": {"type": "string"},
                    "enabled": {"type": "boolean", "default": True},
                },
                "required": ["personality_id", "name", "description", "prompt"],
            },
        },
        {
            "name": "update_personality",
            "description": "Update an existing personality's fields.",
            "parameters": {
                "type": "object",
                "properties": {
                    "personality_id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "prompt": {"type": "string"},
                    "enabled": {"type": "boolean"},
                },
                "required": ["personality_id"],
            },
        },
        {
            "name": "get_personality_history",
            "description": "Get the history of recent personality switches.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10}
                },
            },
        },
    ]

    async def handle_function_call(self, function_call) -> Any:
        """
        Dispatches a Gemini function-call object to the correct personality action.

        Args:
            function_call: Gemini types.FunctionCall with .name and .args.

        Returns:
            types.FunctionResponse
        """
        from google.genai import types

        name = function_call.name
        args = function_call.args or {}

        try:
            if name == "switch_personality":
                result = self.switch_personality(args["personality_id"])
            elif name == "get_current_personality":
                result = self.get_current_personality()
            elif name == "list_personalities":
                result = self.list_personalities()
            elif name == "add_personality":
                result = self.add_personality(
                    personality_id=args["personality_id"],
                    name=args["name"],
                    description=args["description"],
                    prompt=args["prompt"],
                    enabled=args.get("enabled", True),
                )
            elif name == "update_personality":
                result = self.update_personality(
                    personality_id=args["personality_id"],
                    name=args.get("name"),
                    description=args.get("description"),
                    prompt=args.get("prompt"),
                    enabled=args.get("enabled"),
                )
            elif name == "get_personality_history":
                result = self.get_personality_history(limit=args.get("limit", 10))
            else:
                result = {"success": False, "message": f"Unknown personality function: {name}"}

            return types.FunctionResponse(id=function_call.id, name=name, response=result)

        except Exception as exc:
            logger.error(f"PersonalityManager: function '{name}' failed: {exc}")
            return types.FunctionResponse(
                id=function_call.id,
                name=name,
                response={"success": False, "message": f"Error in {name}: {exc}"},
            )

_personality_manager: Optional[PersonalityManager] = None


def get_personality_manager() -> PersonalityManager:
    """
    Returns the module-level PersonalityManager singleton.

    Returns:
        PersonalityManager: The shared instance.
    """
    global _personality_manager
    if _personality_manager is None:
        _personality_manager = PersonalityManager()
    return _personality_manager
