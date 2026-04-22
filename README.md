# NOVA-AI

NOVA-AI is a local-first personal assistant framework that integrates memory, vision, audio, and simple tools to enable rapid experimentation with conversational agents. It includes components for audio I/O, SQLite-backed memory storage, screenshot capture, and simple UI utilities.

Features

- Local memory system persisted in SQLite (`memories.db`)
- Audio input and output support
- Screenshot and basic vision logging
- Simple UI and command-line entry points

Requirements

- Python 3.11.9 recomended
- Dependencies listed in `requirements.txt`

Installation

1. Clone the repository and change into the project folder.

```bash
git clone https://github.com/S0L0GUY/NOVA-AI
cd NOVA-AI
```

2. Create and activate a virtual environment.

On Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install Python dependencies.

```bash
pip install -r requirements.txt
```

Configuration

- Copy `config.yaml.example` to `config.yaml` and adjust settings as needed.
- Configure any API keys or local paths in `config.yaml`.
- Existing modules load from the `models/`, `sfx/`, and `tts_cache/` folders when applicable.
- The memory system persists data in a SQLite database file named `memories.db`, which is created in the project/runtime directory when memory is used.

Usage

- Run the main application:

```bash
python main.py
```

- Launch the alternative entry point:

```bash
python nova.py
```

- For a simple memory UI (if available):

```bash
python memory_ui.py
```

Project layout

```
.
├── classes/            # Core modules: audio, memory, UI, tools
├── json_files/         # JSON-based state and logs used by some modules
├── memories.db         # SQLite database used for persistent memory storage
├── models/             # Model files (not included)
├── sfx/                # Sound effects used by the app
├── tts_cache/          # Cached TTS audio
├── main.py             # Primary entry point
├── nova.py             # Alternate entry point
├── memory_ui.py        # Simple memory inspector UI
├── config.yaml         # Runtime configuration (not committed)
└── requirements.txt    # Python dependencies
```

Contributing

Contributions are welcome. To contribute:

1. Open an issue to discuss major changes.
2. Create a feature branch from `main`.
3. Submit a pull request with a clear description of changes.

If you add new dependencies, update `requirements.txt` and include a brief note in the PR.

License

Specify the project license in this section, for example MIT. Add a `LICENSE` file in the repository root.

Support

Report issues on the repository issue tracker or contact the maintainers listed in the project metadata.

Maintainers

- Evan Grinnell (S0L0GUY)
