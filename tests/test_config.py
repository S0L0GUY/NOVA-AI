"""Tests for classes/config.py: YAML loading and property accessors.

The `sample_config_files` fixture copies config.yaml.example and
prompt.yaml.example into a tmp dir, so these tests assert against the
real project template values rather than duplicating literals.
"""

from classes.config import DEFAULT_SYSTEM_PROMPT, Config


def test_loads_values_from_example(
    sample_config_files, example_config_data, example_prompt_data
):
    """All accessors return the exact values from config.yaml.example."""
    cfg_path, prompt_path = sample_config_files
    cfg = Config(path=str(cfg_path), prompt_path=str(prompt_path))

    gemini = example_config_data["gemini"]
    osc = example_config_data["osc"]
    prompt_name = example_config_data["prompt"]["name"]

    assert cfg.get_gemini_api_key == gemini["API_key"]
    assert cfg.get_gemini_model == gemini["model"]
    assert cfg.get_gemini_voice == gemini["voice"]
    assert cfg.get_osc_enabled is bool(osc["enabled"])
    assert cfg.get_osc_ip == osc["ip"]
    assert cfg.get_osc_port == osc["port"]
    assert cfg.get_osc_receive_port == osc["receive_port"]
    assert cfg.get_prompt_name == prompt_name

    # System prompt should come from the example prompt file under the configured name
    expected_prompt = example_prompt_data[prompt_name].strip()
    assert cfg.get_system_prompt == expected_prompt


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
    prompt_path.write_text("system_instruction:\n  - line one\n  - line two\n")
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
