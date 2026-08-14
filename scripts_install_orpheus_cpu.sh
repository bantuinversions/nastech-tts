#!/usr/bin/env bash
set -euo pipefail

PROJECT="$HOME/nastech-tts"
VENV="$HOME/kokoro-tts-venv"
LOG="$PROJECT/orpheus_cpu_install.log"

exec > >(tee "$LOG") 2>&1
source "$VENV/bin/activate"
cd "$PROJECT"

python -m pip install orpheus-cpp
python -m pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
python -m pip install -e .

nastech-tts status
