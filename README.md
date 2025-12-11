[![](https://dcbadge.limes.pink/api/server/vSxGKpfK8j?style=flat)](https://discord.gg/vSxGKpfK8j)
# NOVA AI

/ˈnōvə/ — VRChat AI companion

NOVA is a lightweight VRChat assistant that:

* Listens via **Whisper || GenAI**
* Uses **GenAI** for language
* Speaks using **Edge TTS**
* Supports **multilingual speech, OSC integration**, and **customizable personalities** via prompt files

---

## Table of Contents

* [Quick Start](#quick-start-windows--powershell)
* [Configuration](#configuration)
* [Common Issues & Quick Fixes](#common-issues--quick-fixes)
* [Advanced Usage](#advanced-usage)
* [Troubleshooting Tips](#troubleshooting-tips)
* [Contributing](#contributing)
* [Contributors](#contributors)
* [License](#license)
* [Support](#support)

---

## Quick Start (Windows / PowerShell)

1. **Create & activate virtual environment**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. **Install dependencies**

```powershell
pip install -r requirements.txt
```

3. **Copy & edit environment file**

```powershell
copy .env.example .env
# Edit .env and set at least: LLM_API_KEY=your-genai-api-key
```

4. *(Optional)* Detect audio devices

```powershell
python list_audio_devices.py
```

5. **Run NOVA**

```powershell
python main.py
```

6. *(Optional)* Run a quick smoke test to verify core components

```powershell
python smoke_test.py
```

---

## Configuration

- **Runtime options:** `constants.py` (audio indices, `VRC_PORT`, voice, Whisper model, toggles)
- **Prompt files:**

  * `prompts/normal_system_prompt.txt`
  * `prompts/vision_prompt.txt`

  Add additional prompt files to the `prompts/` directory to create new
  personalities or system prompts. Only the files present in the `prompts/`
  folder are loaded by default.
- **Whisper model:** `WhisperSettings.MODEL_SIZE` (`tiny|base|small|medium|large`)
- **TTS voice:** `Voice.VOICE_NAME` (list available voices if needed)

---

## Common Issues & Quick Fixes

* **No module error:**

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

* **GenAI API auth error:** set `LLM_API_KEY` in `.env`

* **Mic/audio issues:**

  1. Run `python list_audio_devices.py`
  2. Update `AUDIO_INPUT_INDEX` / `AUDIO_OUTPUT_INDEX` in `constants.py`
  3. Check Windows microphone permissions

* **ffmpeg warnings:** install ffmpeg and add `ffmpeg\bin` to PATH

* **VRChat OSC not receiving messages:** enable OSC in VRChat, confirm VRChat is running, ensure `VRC_PORT` matches (default 9000)

* **TTS / language issues:** verify voice name, terminal UTF-8 encoding, try larger Whisper model, or tweak VAD/threshold

* **Vision features not working:** ensure `VisionSystem.ENABLED = True` and GenAI key is valid

---

## Advanced Usage

* **Virtual audio routing:** [use VB-Audio Virtual Cable](https://vb-audio.com/Cable/), update indices in `constants.py`
* **Multi-instance:** separate project folders & OSC ports, set unique `VRC_PORT`
* **Development:** follow PEP8, run tests, consider `flake8`. Modular code lives under `classes/`

**Branch / Feature Notes**

This repository may contain feature branches that add or change behavior
(for example, an audio-generation caching feature). If you're using a
non-main branch, review the branch/PR notes for any special runtime
requirements before filing issues.

---

## Troubleshooting Tips

1. Check console output for detailed errors
2. Verify `.env` and API keys
3. Test components individually (audio list script, minimal config)
4. Review `constants.py` for misconfig or syntax errors

---

## Contributing

1. Fork → create branch → implement → test
2. Commit & push → open a pull request
3. Follow PEP8, document changes, add tests

---

## Contributors

* **Evan Grinnell** — Project Lead & Core Developer
* **Duck Song** — Core Contributor
* **Viscrimson** — Core Contributor

---

## License

MIT — see LICENSE

---

## Support


Star the repo, report issues, suggest features, or open PRs for fixes and improvements, join the discord





