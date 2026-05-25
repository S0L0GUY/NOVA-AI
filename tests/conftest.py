"""Shared pytest fixtures for NOVA-AI test suite."""

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def tmp_db(tmp_path):
    """Provide a temporary SQLite DB path for MemoryManager tests."""
    return tmp_path / "memories.db"


@pytest.fixture
def memory_manager(tmp_db):
    """A MemoryManager instance backed by a temp SQLite DB."""
    from classes.memory import MemoryManager

    return MemoryManager(db_path=str(tmp_db))


@pytest.fixture
def sample_config_files(tmp_path):
    """Create temp config.yaml and prompt.yaml files. Returns (config_path, prompt_path)."""
    config_path = tmp_path / "config.yaml"
    prompt_path = tmp_path / "prompt.yaml"

    config_data = {
        "gemini": {
            "API_key": "test-api-key",
            "model": "gemini-test-model",
            "voice": "Charon",
        },
        "osc": {
            "enabled": True,
            "ip": "192.168.1.10",
            "port": 9100,
            "receive_port": 9101,
        },
        "prompt": {"name": "system_instruction"},
    }
    prompt_data = {"system_instruction": "You are a test assistant."}

    config_path.write_text(yaml.safe_dump(config_data))
    prompt_path.write_text(yaml.safe_dump(prompt_data))
    return config_path, prompt_path
