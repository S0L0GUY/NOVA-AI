"""
config.py: Configuration management for NOVA-AI.

Loads and manages configuration from config.yaml (API keys, OSC settings) and prompt.yaml
(Gemini system instructions). Provides property accessors for all config values with defaults.
"""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant. Keep your responses concise. Speak in a "
    "friendly Irish accent. You can see the user's camera or screen which is "
    "shared as realtime input images with you."
)


class Config:
    """
    Manages YAML-based configuration for NOVA-AI.

    Loads config.yaml for API keys, OSC settings, and other parameters.
    Loads prompt.yaml for Gemini system instructions.
    Provides property accessors with sensible defaults.
    """

    def __init__(self, path="config.yaml", prompt_path="prompt.yaml"):
        self.path = self._resolve_path(path)
        self.prompt_path = self._resolve_path(prompt_path)

        with open(self.path, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f) or {}

        self._prompt_data = {}
        if self.prompt_path.exists():
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                self._prompt_data = yaml.safe_load(f) or {}
        else:
            logger.warning("Prompt file not found at %s; using built-in default prompt", self.prompt_path)

    @staticmethod
    def _resolve_path(path: str) -> Path:
        """Resolve path relative to project root if not absolute."""
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return ROOT_DIR / candidate

    def get(self, *keys, default=None):
        """Get nested config value by key path (e.g., cfg.get('gemini', 'API_key'))."""
        val = self._data
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k, default)
            else:
                return default
        return val

    @property
    def get_gemini_api_key(self):
        """Get Gemini API key from config."""
        return self.get("gemini", "API_key", default=False)

    @property
    def get_gemini_model(self):
        """Get Gemini model name (e.g., 'gemini-2.0-flash-exp')."""
        return self.get("gemini", "model", default=False)

    @property
    def get_gemini_voice(self):
        """Get Gemini voice name for text-to-speech (default: 'Puck')."""
        return self.get("gemini", "voice", default="Puck")

    @property
    def get_osc_enabled(self):
        """Check if VRChat OSC integration is enabled."""
        return self.get("osc", "enabled", default=False)

    @property
    def get_osc_ip(self):
        """Get OSC server IP address for VRChat (default: localhost)."""
        return self.get("osc", "ip", default="127.0.0.1")

    @property
    def get_osc_port(self):
        """Get OSC server port for outgoing messages (default: 9000)."""
        return self.get("osc", "port", default=9000)

    @property
    def get_osc_receive_port(self):
        """Get OSC server port for incoming messages from VRChat (default: 9001)."""
        return self.get("osc", "receive_port", default=9001)

    @property
    def get_system_prompt(self):
        """
        Get Gemini system instruction prompt from prompt.yaml.

        Supports multiple formats: string, list, or dict with text/prompt/content keys.
        Falls back to DEFAULT_SYSTEM_PROMPT if not configured.
        """
        prompt = self._prompt_data.get("system_instruction")

        if isinstance(prompt, str) and prompt.strip():
            return prompt.strip()

        if isinstance(prompt, list):
            lines = [str(item).strip() for item in prompt if str(item).strip()]
            if lines:
                return "\n".join(lines)

        if isinstance(prompt, dict):
            for key in ("text", "prompt", "content"):
                value = prompt.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

        logger.warning("prompt.yaml is empty or missing system_instruction; falling back to the built-in prompt")
        return DEFAULT_SYSTEM_PROMPT
