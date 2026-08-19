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

    @property
    def display_label(self) -> str:
        """Return the code-first label used in pack selection screens."""

        return f"{self.language} - {self.label}"

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["display_label"] = self.display_label
        return result


# Official MMS archive/Hugging Face identifiers verified in the current audit.
# Other registry languages remain explicit no-model entries until an actual
# checkpoint is verified; they are not silently mapped to a different language.
_PACK_ROWS = (
    ("ach", "ach", "Acholi", "facebook/mms-tts-ach"),
    ("bem", "bem", "Bemba", "facebook/mms-tts-bem"),
    ("bss", "bss", "Akoose", "facebook/mms-tts-bss"),
    ("cwe", "cwe", "Kwere", "facebook/mms-tts-cwe"),
    ("flr", "flr", "Fuliiru", "facebook/mms-tts-flr"),
    ("gog", "gog", "Gogo", "facebook/mms-tts-gog"),
    ("hay", "hay", "Haya", "facebook/mms-tts-hay"),
    ("heh", "heh", "Hehe", "facebook/mms-tts-heh"),
    ("kde", "kde", "Makonde", "facebook/mms-tts-kde"),
    ("ki", "kik", "Gikuyu", "facebook/mms-tts-kik"),
    ("ksb", "ksb", "Shambala", "facebook/mms-tts-ksb"),
    ("lg", "lug", "Luganda", "facebook/mms-tts-lug"),
    ("lon", "lon", "Malawi Lomwe", "facebook/mms-tts-lon"),
    ("mgh", "mgh", "Makhuwa-Meetto", "facebook/mms-tts-mgh"),
    ("myx", "myx", "Masaaba", "facebook/mms-tts-myx"),
    ("ngl", "ngl", "Lomwe", "facebook/mms-tts-ngl"),
    ("ny", "nya", "Chichewa / Nyanja", "facebook/mms-tts-nya"),
    ("nyf", "nyf", "Kigiryama", "facebook/mms-tts-nyf"),
    ("nyn", "nyn", "Runyankole", "facebook/mms-tts-nyn"),
    ("nyo", "nyo", "Runyoro", "facebook/mms-tts-nyo"),
    ("nyy", "nyy", "Nyakyusa-Ngonde", "facebook/mms-tts-nyy"),
    ("rn", "run", "Kirundi", "facebook/mms-tts-run"),
    ("ruf", "ruf", "Luguru", "facebook/mms-tts-ruf"),
    ("rw", "kin", "Kinyarwanda", "facebook/mms-tts-kin"),
    ("seh", "seh", "Sena", "facebook/mms-tts-seh"),
    ("sn", "sna", "Shona", "facebook/mms-tts-sna"),
    ("suk", "suk", "Sukuma", "facebook/mms-tts-suk"),
    ("sw", "swa", "Kiswahili", "facebook/mms-tts-swh"),
    ("teo", "teo", "Ateso", "facebook/mms-tts-teo"),
    ("toh", "toh", "Malawi Tonga", "facebook/mms-tts-toh"),
    ("ts", "tso", "Xitsonga", "facebook/mms-tts-tso"),
    ("vmw", "vmw", "Makhuwa", "facebook/mms-tts-vmw"),
    ("xog", "xog", "Lusoga", "facebook/mms-tts-xog"),
    ("yao", "yao", "Yao", "facebook/mms-tts-yao"),
    ("ziw", "ziw", "Zigula", "facebook/mms-tts-ziw"),
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
