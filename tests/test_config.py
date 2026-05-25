"""Tests for classes/config.py: YAML loading and property accessors."""

from classes.config import DEFAULT_SYSTEM_PROMPT, Config


def test_loads_values(sample_config_files):
    cfg_path, prompt_path = sample_config_files
    cfg = Config(path=str(cfg_path), prompt_path=str(prompt_path))

    assert cfg.get_gemini_api_key == "test-api-key"
    assert cfg.get_gemini_model == "gemini-test-model"
    assert cfg.get_gemini_voice == "Charon"
    assert cfg.get_osc_enabled is True
    assert cfg.get_osc_ip == "192.168.1.10"
    assert cfg.get_osc_port == 9100
    assert cfg.get_osc_receive_port == 9101
    assert cfg.get_system_prompt == "You are a test assistant."


def test_nested_get_with_missing_key_returns_default(sample_config_files):
    cfg_path, prompt_path = sample_config_files
    cfg = Config(path=str(cfg_path), prompt_path=str(prompt_path))

    assert cfg.get("nonexistent", "key", default="fallback") == "fallback"
    assert cfg.get("gemini", "missing_field", default=42) == 42


def test_defaults_when_config_empty(tmp_path):
    cfg_path = tmp_path / "empty.yaml"
    cfg_path.write_text("")
    cfg = Config(path=str(cfg_path), prompt_path=str(tmp_path / "missing-prompt.yaml"))

    assert cfg.get_gemini_voice == "Puck"
    assert cfg.get_osc_enabled is False
    assert cfg.get_osc_ip == "127.0.0.1"
    assert cfg.get_osc_port == 9000
    assert cfg.get_osc_receive_port == 9001
    assert cfg.get_prompt_name == "system_instruction"


def test_missing_prompt_file_falls_back_to_default(tmp_path):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text("gemini:\n  API_key: k\n")
    cfg = Config(path=str(cfg_path), prompt_path=str(tmp_path / "absent.yaml"))

    assert cfg.get_system_prompt == DEFAULT_SYSTEM_PROMPT


def test_system_prompt_list_format(tmp_path):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text("prompt:\n  name: system_instruction\n")
    prompt_path = tmp_path / "prompt.yaml"
    prompt_path.write_text(
        "system_instruction:\n  - line one\n  - line two\n"
    )
    cfg = Config(path=str(cfg_path), prompt_path=str(prompt_path))
    assert cfg.get_system_prompt == "line one\nline two"


def test_system_prompt_dict_format(tmp_path):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text("prompt:\n  name: system_instruction\n")
    prompt_path = tmp_path / "prompt.yaml"
    prompt_path.write_text("system_instruction:\n  text: nested-text\n")
    cfg = Config(path=str(cfg_path), prompt_path=str(prompt_path))
    assert cfg.get_system_prompt == "nested-text"


def test_empty_prompt_falls_back_to_default(tmp_path):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text("prompt:\n  name: system_instruction\n")
    prompt_path = tmp_path / "prompt.yaml"
    prompt_path.write_text("system_instruction: '   '\n")
    cfg = Config(path=str(cfg_path), prompt_path=str(prompt_path))
    assert cfg.get_system_prompt == DEFAULT_SYSTEM_PROMPT
