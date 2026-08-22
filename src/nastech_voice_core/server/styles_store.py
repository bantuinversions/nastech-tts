"""On-disk store for user-imported voice styles.

Imported voice styles live alongside the bundled built-ins, **scoped per
model** so that a voice imported while serving ``supertonic-3`` is not
silently used by ``supertonic-2``:

    ~/.cache/supertonic3/custom_styles/<name>.json   # supertonic-3
    ~/.cache/supertonic2/custom_styles/<name>.json   # supertonic-2
    ~/.cache/supertonic/custom_styles/<name>.json    # supertonic v1

This matches how the bundled voices are organized (each model's
``voice_styles/`` lives under its own cache dir) and keeps custom JSONs out
of ``voice_styles/`` so the SDK's :func:`list_available_voice_style_names`
remains unchanged.

This module deliberately stays small: it never *loads* the styles itself —
that work belongs to :func:`supertonic.loader.load_voice_style_from_json_file`,
which already enforces the JSON schema via
:func:`supertonic.utils.validate_voice_style_format`. We just decide *where*
files live and how their names are sanitized.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, Iterable

from ..config import DEFAULT_MODEL
from ..loader import get_cache_dir
from ..utils import validate_voice_style_format

logger = logging.getLogger(__name__)

# Names that conflict with built-in voices are rejected to keep ``GET /v1/styles``
# unambiguous. Built-in names are discovered at runtime from the model dir, but
# we also hardcode this regex as a structural guard.
_NAME_RE = re.compile(r"[A-Za-z0-9_\-]{1,64}")


def default_custom_styles_dir(model: str = DEFAULT_MODEL) -> Path:
    """Resolve the on-disk directory for user-imported voice styles.

    Priority:

    1. ``$SUPERTONIC_CUSTOM_STYLES_DIR`` — explicit override, applies to every
       model (the user opted into a single shared location).
    2. ``<model cache dir>/custom_styles/`` — e.g. ``~/.cache/supertonic3/
       custom_styles/`` for ``supertonic-3``. Respects ``$SUPERTONIC_CACHE_DIR``
       through :func:`supertonic.loader.get_cache_dir`.
    """
    env = os.getenv("SUPERTONIC_CUSTOM_STYLES_DIR")
    if env:
        return Path(env).expanduser()
    return get_cache_dir(model) / "custom_styles"


class InvalidStyleName(ValueError):
    """Raised when an imported style name fails sanitization."""


class StyleNameConflict(ValueError):
    """Raised when an imported style would overwrite an existing one."""


def sanitize_name(name: str) -> str:
    name = (name or "").strip()
    if not _NAME_RE.fullmatch(name):
        raise InvalidStyleName(f"Invalid style name {name!r}: must match [A-Za-z0-9_-]{{1,64}}")
    return name


def scan(directory: Path) -> Dict[str, Path]:
    """Return ``{stem: path}`` for every well-formed JSON in ``directory``.

    A file that fails :func:`validate_voice_style_format` is skipped with a
    warning rather than crashing startup — the server should still come up.
    """
    out: Dict[str, Path] = {}
    if not directory.exists():
        return out
    for p in sorted(directory.glob("*.json")):
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not validate_voice_style_format(data):
                logger.warning("Skipping invalid voice style file: %s", p)
                continue
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("Skipping unreadable voice style file %s: %s", p, e)
            continue
        out[p.stem] = p
    return out


def save(
    directory: Path,
    name: str,
    payload: dict,
    *,
    builtin_names: Iterable[str] = (),
    overwrite: bool = False,
) -> Path:
    """Persist a validated style payload to ``directory / f"{name}.json"``.

    Args:
        directory: target directory (created if missing).
        name: requested style name; sanitized via :func:`sanitize_name`.
        payload: parsed JSON; must pass :func:`validate_voice_style_format`.
        builtin_names: names reserved by the bundled model; conflict → 400.
        overwrite: if False, conflict with an existing custom name → 409.

    Returns:
        The path the style was written to.
    """
    name = sanitize_name(name)
    if name in set(builtin_names):
        raise StyleNameConflict(f"Name {name!r} is a built-in voice and cannot be overwritten")
    if not validate_voice_style_format(payload):
        # Re-using the SDK error type so server handlers can map uniformly.
        raise ValueError("voice style JSON is missing required keys/fields")

    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{name}.json"
    if target.exists() and not overwrite:
        raise StyleNameConflict(f"Style {name!r} already exists")
    tmp = target.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f)
    tmp.replace(target)
    return target
