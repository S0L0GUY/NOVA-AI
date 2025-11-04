# NOVA AI

/ˈnōvə/ — VRChat AI companion

NOVA is a lightweight VRChat assistant that:

* Listens via **Whisper**
* Uses **Together AI** for language & vision
* Speaks using **Edge TTS**
* Supports **multilingual speech, vision features, OSC integration**, and **customizable personalities** via prompt files

---

## Table of Contents

* [Quick Start](#quick-start-windows--powershell)
* [Configuration](#configuration)
* [Common Issues & Quick Fixes](#common-issues--quick-fixes)
* [Performance Optimization](#performance-optimization)
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
# Edit .env and set at least: LLM_API_KEY=your-together-api-key
```

4. *(Optional)* Detect audio devices

```powershell
python list_audio_devices.py
```

5. **Run NOVA**

```powershell
python main.py
```

---

## Configuration

* **Runtime options:** `constants.py` (audio indices, VRC_PORT, voice, Whisper model, toggles)
* **Prompt files:**

  * `prompts/normal_system_prompt.txt`
  * `prompts/snapchat_system_prompt.txt`
  * `prompts/additional_system_prompt.txt`
  * `prompts/vision_prompt.txt`
* **Whisper model:** `WhisperSettings.MODEL_SIZE` (`tiny|base|small|medium|large`)
* **TTS voice:** `Voice.VOICE_NAME` (list available voices if needed)

---

## Common Issues & Quick Fixes

* **No module error:**

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

* **Together API auth error:** set `LLM_API_KEY` in `.env` or session (`TOGETHER_API_KEY`)

* **Mic/audio issues:**

  1. Run `python list_audio_devices.py`
  2. Update `AUDIO_INPUT_INDEX` / `AUDIO_OUTPUT_INDEX` in `constants.py`
  3. Check Windows microphone permissions

* **ffmpeg warnings:** install ffmpeg and add `ffmpeg\bin` to PATH

* **VRChat OSC not receiving messages:** enable OSC in VRChat, confirm VRChat is running, ensure `VRC_PORT` matches (default 9000)

* **TTS / language issues:** verify voice name, terminal UTF-8 encoding, try larger Whisper model, or tweak VAD/threshold

* **Vision features not working:** ensure `VisionSystem.ENABLED = True` and Together AI key is valid

---

## Performance Optimization

NOVA's response time has been optimized for minimal latency. Key settings in `constants.py`:

### Whisper Settings (Speech Recognition)

* **`MODEL_SIZE`**: Use `"tiny"` for fastest response (default), or `"base"` for better accuracy
  * `"tiny"` is 4x faster than `"base"` but slightly less accurate
  * Consider `"small"` or `"medium"` only if accuracy is critical
* **`VAD_AGGRESSIVENESS`**: Higher values (1-3) detect speech faster but may cut off beginnings

### TTS Settings (Text-to-Speech)

* **`QUEUE_SLEEP_INTERVAL`**: Set to `0.05` for faster processing (default optimized)

### Response Time Breakdown

Typical response times with optimized settings:

1. **Voice detection & recording**: 1-3 seconds (depends on speech length)
2. **Whisper transcription** (tiny model): 0.3-0.8 seconds
3. **LLM processing**: 1-3 seconds (depends on response length & API latency)
4. **TTS generation**: Parallel with LLM streaming
5. **Audio playback**: Real-time as sentences are generated

**Total typical response**: 3-7 seconds from speech end to audio start

---

## Advanced Usage

* **Virtual audio routing:** use VB-Audio Virtual Cable, update indices in `constants.py`
* **Multi-instance:** separate project folders & OSC ports, set unique `VRC_PORT`
* **Development:** follow PEP8, run tests, consider `flake8`. Modular code lives under `classes/`

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

Star the repo, report issues, suggest features, or open PRs for fixes and improvements