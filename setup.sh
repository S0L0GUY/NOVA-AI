#!/usr/bin/env bash
set -euo pipefail

pythonVersion="3.11.9"

echo "==============="
echo " NOVA-AI Setup"
echo "==============="

if command -v python3 >/dev/null 2>&1; then
  python_cmd=python3
elif command -v python >/dev/null 2>&1; then
  python_cmd=python
else
  echo "Python not found. Attempting to install..."
  uname_s=$(uname)
  if [ "$uname_s" = "Linux" ]; then
    if command -v apt-get >/dev/null 2>&1; then
      sudo apt-get update
      sudo apt-get install -y python3 python3-venv python3-pip
      python_cmd=python3
    else
      echo "Unsupported package manager; please install Python $pythonVersion manually."
      exit 1
    fi
  elif [ "$uname_s" = "Darwin" ]; then
    if command -v brew >/dev/null 2>&1; then
      brew install python@3.11
      python_cmd=python3
    else
      echo "Homebrew not found; please install Homebrew and rerun."
      exit 1
    fi
  else
    echo "Unsupported OS. Please install Python $pythonVersion manually."
    exit 1
  fi
fi

echo "Using Python: $($python_cmd --version 2>&1)"

$python_cmd -m venv venv

. venv/bin/activate

pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  echo "requirements.txt not found; skipping pip install."
fi

echo "Virtual environment created and activated."
echo "To activate manually, run: source venv/bin/activate"
