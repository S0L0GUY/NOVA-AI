"""
main.py — starts a script and restarts it if it dies.

Usage:
    python main.py <script.py> [--no-restart]
"""

import ctypes
import os
import signal
import subprocess
import sys
import threading
from pathlib import Path

_DIM = "\033[2m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_BLUE = "\033[94m"
_GREEN = "\033[92m"
_RST = "\033[0m"
_BOLD = "\033[1m"


def _log(msg: str, color: str = _DIM, prefix: str = "●") -> None:
    """Print colored log message with standardized formatting."""
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
    def __init__(self, script: str, restart: bool = True) -> None:
        self.script = script
        self.restart = restart
        self._proc: subprocess.Popen | None = None
        self._alive = True

    def run(self) -> None:
        """Block until the supervised process exits (and won't be restarted)."""
        _enable_ansi_windows()
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        thread.join()

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
        python = self._resolve_python()

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
            "PYTHONUNBUFFERED": "1",  # Force unbuffered output
        }
        try:
            self._proc = subprocess.Popen(
                [str(python), self.script],
                cwd=str(Path(self.script).parent.resolve()),
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
    sup = Supervisor(script="nova.py", restart=True)

    def _on_signal(signum, frame) -> None:
        print()
        _log("Shutting down…", _RED, prefix="◆")
        sup.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)

    sup.run()


if __name__ == "__main__":
    main()
