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
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return ROOT_DIR / candidate

    def get(self, *keys, default=None):
        val = self._data
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k, default)
            else:
                return default
        return val

    @property
    def get_gemini_api_key(self):
        return self.get("gemini", "API_key", default=False)

    @property
    def get_gemini_model(self):
        return self.get("gemini", "model", default=False)

    @property
    def get_gemini_voice(self):
        return self.get("gemini", "voice", default="Puck")

    @property
    def get_system_prompt(self):
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
