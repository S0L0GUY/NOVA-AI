"""
main.py — starts a script and restarts it if it dies.

Usage:
    python main.py <script.py> [--no-restart]
"""

import argparse
import ctypes
import os
import signal
import subprocess
import sys
from pathlib import Path

_DIM = "\033[2m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_BLUE = "\033[94m"
_GREEN = "\033[92m"
_RST = "\033[0m"
_BOLD = "\033[1m"

# Toggle color output (can be disabled via CLI)
_USE_COLOR = True


def _log(msg: str, color: str = _DIM, prefix: str = "●") -> None:
    """Print colored log message with standardized formatting.

    Colors are suppressed when `_USE_COLOR` is False.
    """
    if not _USE_COLOR:
        print(f"{prefix} {msg}", flush=True)
        return
    print(f"{color}{_BOLD}{prefix}{_RST} {color}{msg}{_RST}", flush=True)


def _enable_ansi_windows() -> None:
    """Enable ANSI escape codes on Windows terminals."""
    if sys.platform != "win32":
        return
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


class Supervisor:
    def __init__(self, script: str, restart: bool = True, python: Path | None = None, cwd: Path | None = None) -> None:
        self.script = script
        self.restart = restart
        self._proc: subprocess.Popen | None = None
        self._alive = True
        self._python = python
        self._cwd = cwd

    def run(self) -> None:
        """Block until the supervised process exits (and won't be restarted)."""
        _enable_ansi_windows()
        # Run the supervisor loop in the main thread so signal handlers
        # can stop it cleanly without forcing an immediate process exit.
        self._loop()

    def stop(self) -> None:
        """Gracefully stop the supervised process."""
        self._alive = False
        if self._proc and self._proc.poll() is None:
            _log("Stopping process…", _YELLOW, prefix="⊚")
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()

    def _loop(self) -> None:
        python = self._python or self._resolve_python()

        while self._alive:
            _log(f"Starting {self.script}", _BLUE, prefix="▶")
            exit_code = self._run_once(python)

            if not self._alive:
                break

            if self.restart:
                _log(f"Exited with code {exit_code} — restarting…", _YELLOW, prefix="↻")
            else:
                _log(f"Exited with code {exit_code}", _GREEN, prefix="◼")
                break

    def _run_once(self, python: Path) -> int:
        env = {
            **os.environ,
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",  # Force unbuffered output``
        }
        try:
            self._proc = subprocess.Popen(
                [str(python), self.script],
                cwd=str(self._cwd or Path(self.script).parent.resolve()),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
            )
            for line in self._proc.stdout:  # type: ignore
                sys.stdout.write(line)
                sys.stdout.flush()
            self._proc.wait()
            return self._proc.returncode
        except Exception as exc:
            _log(f"Error: {exc}", _RED)
            return -1

    @staticmethod
    def _resolve_python() -> Path:
        """Prefer the venv interpreter if one exists alongside this script."""
        root = Path(__file__).parent
        venv = root / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / "python"
        venv_exe = venv.with_suffix(".exe") if sys.platform == "win32" else venv
        if venv_exe.exists():
            return venv_exe
        return Path(sys.executable)  # fall back to whatever Python is running this


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="supervisor",
        description="Start and (optionally) restart a script when it exits.",
        epilog="Examples:\n  python main.py nova.py --no-restart\n  python main.py app.py --python C:/Python39/python.exe",
    )
    parser.add_argument("script", nargs="?", default="nova.py", help="Script to supervise (default: nova.py)")
    parser.add_argument("--no-restart", action="store_true", help="Don't restart the script after it exits")
    parser.add_argument("--python", "-p", dest="python", help="Path to the Python interpreter to run the script with")
    parser.add_argument("--cwd", dest="cwd", help="Working directory to run the script in (defaults to script's folder)")
    parser.add_argument("--no-color", action="store_true", help="Disable colored log output")

    args = parser.parse_args()

    global _USE_COLOR
    if args.no_color:
        _USE_COLOR = False

    python_path = Path(args.python) if args.python else None
    cwd = Path(args.cwd).resolve() if args.cwd else None

    sup = Supervisor(script=args.script, restart=not args.no_restart, python=python_path, cwd=cwd)

    def _on_signal(signum, frame) -> None:
        print()
        _log("Shutting down…", _RED, prefix="◆")
        # Request the supervisor to stop; return to main so it can exit normally.
        sup.stop()

    signal.signal(signal.SIGINT, _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)

    sup.run()


if __name__ == "__main__":
    main()
