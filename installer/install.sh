#!/usr/bin/env sh
set -eu

SOURCE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 "$SOURCE_ROOT/installer/launcher.py" --source-root "$SOURCE_ROOT" -- "$@"
