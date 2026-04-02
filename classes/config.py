import yaml
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path("prompt")


class Config:
    def __init__(self, path="config.yaml"):
        with open(path, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f)

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
