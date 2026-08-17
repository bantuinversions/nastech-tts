"""Lazy, per-language Bantu model-pack acquisition and cache management.

The compact Nastech core never downloads or loads optional language packs at
import time. A caller explicitly requests one language, then this module
resolves only that pack into an external cache. Model weights remain outside
Git and outside the measured compact deployment budget.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .languages import normalize_language_code

MMS_SOURCE = "https://huggingface.co/facebook/{model_id}"
MMS_LICENSE = "CC-BY-NC-4.0"
DEFAULT_CACHE = Path.home() / ".cache" / "nastech-bantu"


class LazyPackError(RuntimeError):
    """Raised when a requested optional language pack cannot be resolved."""


@dataclass(frozen=True)
class LazyPackDefinition:
    """Metadata for one optional language pack; no model is loaded by this record."""

    language: str
    iso639_3: str
    label: str
    model_id: str | None
    source: str | None
    license: str | None
    state: str
    note: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


# Official MMS archive/Hugging Face identifiers verified in the current audit.
# Other registry languages remain explicit no-model entries until an actual
# checkpoint is verified; they are not silently mapped to a different language.
_PACK_ROWS = (
    ("lg", "lug", "Luganda", "facebook/mms-tts-lug"),
    ("nyn", "nyn", "Runyankole", "facebook/mms-tts-nyn"),
    ("ach", "ach", "Acholi", "facebook/mms-tts-ach"),
    ("teo", "teo", "Ateso", "facebook/mms-tts-teo"),
    ("sw", "swa", "Kiswahili", "facebook/mms-tts-swh"),
    ("rw", "kin", "Kinyarwanda", "facebook/mms-tts-kin"),
    ("rn", "run", "Kirundi", "facebook/mms-tts-run"),
    ("ki", "kik", "Gikuyu", "facebook/mms-tts-kik"),
    ("ts", "tso", "itsonga", "facebook/mms-tts-tso"),
    ("sn", "sna", "Shona", "facebook/mms-tts-sna"),
    ("ny", "nya", "Chichewa / Nyanja", "facebook/mms-tts-nya"),
)

_MODEL_BY_LANGUAGE = {language: model_id for language, _, _, model_id in _PACK_ROWS}


def _pack_definitions() -> dict[str, LazyPackDefinition]:
    from .languages import LANGUAGE_REGISTRY

    definitions: dict[str, LazyPackDefinition] = {}
    for code, definition in LANGUAGE_REGISTRY.items():
        model_id = _MODEL_BY_LANGUAGE.get(code)
        definitions[code] = LazyPackDefinition(
            language=code,
            iso639_3=definition.iso639_3,
            label=definition.label,
            model_id=model_id,
            source=MMS_SOURCE.format(model_id=model_id) if model_id else None,
            license=MMS_LICENSE if model_id else None,
            state="lazy-downloadable" if model_id else "no-verified-pack",
            note=(
                "Downloaded only when explicitly requested; model is loaded per language."
                if model_id
                else "No verified public local checkpoint is currently mapped for this target."
            ),
        )
    return definitions


def cache_root() -> Path:
    return Path(os.environ.get("NASTECH_BANTU_CACHE", str(DEFAULT_CACHE))).expanduser()


def pack_path(language: str | None) -> Path:
    code = normalize_language_code(language)
    return cache_root() / code


def pack_inventory() -> dict[str, Any]:
    """Return all registry targets and local cache state without downloading."""
    from .mms_lazy import resident_languages

    resident = set(resident_languages())
    records = []
    for code, definition in _pack_definitions().items():
        path = pack_path(code)
        present = path.is_dir() and any(path.iterdir())
        record = definition.as_dict()
        record.update(
            {
                "cache_path": str(path),
                "downloaded": present,
                "cache_bytes": _directory_bytes(path) if present else 0,
                "loaded": code in resident,
            }
        )
        records.append(record)
    return {
        "cache_root": str(cache_root()),
        "startup_downloads": 0,
        "startup_loaded_models": 0,
        "packs": records,
    }


def _directory_bytes(path: Path) -> int:
    if not path.is_dir():
        return 0
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _download_pack(definition: LazyPackDefinition, destination: Path) -> None:
    """Download one model snapshot atomically into the external cache."""
    if not definition.model_id:
        raise LazyPackError(
            f"No verified local model pack is mapped for language '{definition.language}'."
        )
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise LazyPackError(
            "huggingface_hub is required for lazy Bantu downloads; install the optional runtime."
        ) from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f"{definition.language}-", dir=destination.parent))
    try:
        snapshot_download(
            repo_id=definition.model_id,
            local_dir=str(temporary),
            local_dir_use_symlinks=False,
            resume_download=True,
        )
        manifest = {
            "language": definition.language,
            "model_id": definition.model_id,
            "license": definition.license,
            "source": definition.source,
        }
        (temporary / "nastech-pack.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        if destination.exists():
            shutil.rmtree(destination)
        temporary.rename(destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def ensure_pack(language: str | None, *, allow_download: bool = False) -> Path:
    """Return a cached pack, downloading only the requested language when allowed."""
    code = normalize_language_code(language)
    definition = _pack_definitions()[code]
    destination = pack_path(code)
    if destination.is_dir() and any(destination.iterdir()):
        return destination
    if not allow_download:
        raise LazyPackError(
            f"Language pack '{code}' is not cached. Set NASTECH_ALLOW_LAZY_DOWNLOAD=1 "
            "or call the explicit pack-download operation."
        )
    _download_pack(definition, destination)
    return destination


def download_language_pack(language: str | None) -> dict[str, Any]:
    """Explicitly acquire one requested pack and return its cache metadata."""
    code = normalize_language_code(language)
    path = ensure_pack(code, allow_download=True)
    return next(item for item in pack_inventory()["packs"] if item["language"] == code) | {
        "downloaded_now": True,
        "cache_path": str(path),
    }


def lazy_download_enabled() -> bool:
    return os.environ.get("NASTECH_ALLOW_LAZY_DOWNLOAD", "0").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
