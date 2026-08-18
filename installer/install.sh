#!/usr/bin/env sh
set -eu

SOURCE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
  exec python3 -m installer.gui --source-root "$SOURCE_ROOT" -- "$@"
fi
exec python3 -m installer.launcher --source-root "$SOURCE_ROOT" -- "$@"
