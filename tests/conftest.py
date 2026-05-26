"""Shared pytest fixtures for NOVA-AI test suite."""

import shutil
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


EXAMPLE_CONFIG = ROOT / "config.yaml.example"
EXAMPLE_PROMPT = ROOT / "prompt.yaml.example"


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
def example_config_data():
    """Parsed contents of config.yaml.example."""
    with open(EXAMPLE_CONFIG, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@pytest.fixture
def example_prompt_data():
    """Parsed contents of prompt.yaml.example."""
    with open(EXAMPLE_PROMPT, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@pytest.fixture
def sample_config_files(tmp_path):
    """Copy config.yaml.example and prompt.yaml.example into a tmp dir.

    Returns (config_path, prompt_path). Tests assert against the real
    example file values so the fixture stays in sync with the project
    template rather than drifting via hardcoded duplicates.
    """
    config_path = tmp_path / "config.yaml"
    prompt_path = tmp_path / "prompt.yaml"
    shutil.copyfile(EXAMPLE_CONFIG, config_path)
    shutil.copyfile(EXAMPLE_PROMPT, prompt_path)
    return config_path, prompt_path
