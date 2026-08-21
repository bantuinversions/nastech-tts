"""Optional local Nastech Vocal Events Pack for natural non-verbal cues.

This module is intentionally lazy. Importing Nastech TTS never loads the optional
model or downloads its weights. Operators explicitly invoke ``vocal-event`` after
installing the optional dependency and provide a voice-authorized reference WAV.
"""

from __future__ import annotations

import io
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .markup import _ALLOWED_SOUNDS

PACK_ID = "nastech-vocal-events-turbo"
PACK_LABEL = "Nastech Vocal Events Pack"
PACK_LICENSE = "MIT"
PACK_LANGUAGE = "en"
REFERENCE_SECONDS_MINIMUM = 10
DEFAULT_CACHE = Path.home() / ".cache" / "nastech-vocal-events"

# These tags are documented by the selected optional local event renderer. They
# are routed as native events only after a successful local render. Other tags
# remain on the Nastech Voice Core expression fallback path.
_NATIVE_TAGS = {
    "laugh": "[laugh]",
    "chuckle": "[chuckle]",
    "cough": "[cough]",
    "sigh": "[sigh]",
    "gasp": "[gasp]",
    "sniffle": "[sniff]",
    "groan": "[groan]",
    "throatclear": "[clear throat]",
}
_FALLBACK_REASONS = {
    "cry": "No validated native cry tag is currently available in the local event pack.",
    "scream": "No validated native scream tag is currently available in the local event pack.",
    "yawn": "No validated native yawn tag is currently available in the local event pack.",
}


class VocalEventError(RuntimeError):
    """Raised when an explicit local vocal-event render cannot be completed."""


@dataclass(frozen=True)
class VocalEventRoute:
    """Truthful per-cue routing contract before any event model is loaded."""

    sound: str
    route: str
    event_tag: str | None
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def supported_event_sounds() -> tuple[str, ...]:
    """Return the stable NastechML sound vocabulary supported by event routing."""

    return tuple(sorted(_ALLOWED_SOUNDS))


def event_route(sound: str) -> VocalEventRoute:
    """Return the local native-event or core-expression fallback route for one cue."""

    normalized = sound.strip().lower()
    if normalized not in _ALLOWED_SOUNDS:
        raise VocalEventError(f"Unsupported Nastech vocal event '{sound}'.")
    if normalized in _NATIVE_TAGS:
        return VocalEventRoute(
            sound=normalized,
            route="native-event-when-pack-installed",
            event_tag=_NATIVE_TAGS[normalized],
            reason="Rendered locally by the optional Nastech Vocal Events Pack after acceptance.",
        )
    return VocalEventRoute(
        sound=normalized,
        route="core-expression-fallback",
        event_tag=None,
        reason=_FALLBACK_REASONS[normalized],
    )


def _optional_dependency_installed() -> bool:
    try:
        import chatterbox.tts_turbo  # noqa: F401
    except ImportError:
        return False
    return True


def cache_root() -> Path:
    """Return the external local cache root for optional event-model weights."""

    return Path(os.environ.get("NASTECH_VOCAL_EVENTS_CACHE", str(DEFAULT_CACHE))).expanduser()


def pack_status() -> dict[str, Any]:
    """Return pack metadata without loading a model or initiating a download."""

    installed = _optional_dependency_installed()
    routes = [event_route(sound).as_dict() for sound in sorted(_ALLOWED_SOUNDS)]
    return {
        "id": PACK_ID,
        "label": PACK_LABEL,
        "language": PACK_LANGUAGE,
        "state": "installed-not-loaded" if installed else "optional-dependency-missing",
        "installed": installed,
        "cache_root": str(cache_root()),
        "startup_downloads": 0,
        "startup_loaded_models": 0,
        "license": PACK_LICENSE,
        "reference_audio": {
            "required": True,
            "minimum_seconds": REFERENCE_SECONDS_MINIMUM,
            "operator_confirmation_required": True,
            "notice": "Use only a voice reference you are authorized to use.",
        },
        "routes": routes,
        "fallback_provider": "nastech-voice-core",
        "research_record": "docs/research_nonverbal_vocalization_options.md",
    }


def _device() -> str:
    preferred = os.getenv("NASTECH_VOCAL_EVENTS_DEVICE", "auto").strip().lower()
    if preferred not in {"auto", "cpu", "cuda"}:
        raise VocalEventError("NASTECH_VOCAL_EVENTS_DEVICE must be auto, cpu, or cuda.")
    try:
        import torch
    except ImportError as exc:
        raise VocalEventError(
            "The Nastech Vocal Events Pack needs its optional local dependencies. "
            "Install nastech-tts[vocal-events] first."
        ) from exc
    if preferred == "cuda":
        if not torch.cuda.is_available():
            raise VocalEventError("CUDA was requested for vocal events but is not available.")
        return "cuda"
    if preferred == "cpu":
        return "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


def _load_model(device: str) -> Any:
    # The optional model stays outside the Nastech Voice Core cache and repository.
    os.environ.setdefault("HF_HOME", str(cache_root()))
    try:
        from chatterbox.tts_turbo import ChatterboxTurboTTS
    except ImportError as exc:
        raise VocalEventError(
            "The Nastech Vocal Events Pack is not installed. "
            "Install nastech-tts[vocal-events] and retry explicitly."
        ) from exc
    try:
        return ChatterboxTurboTTS.from_pretrained(device=device)
    except Exception as exc:
        raise VocalEventError(f"Unable to load the local Nastech Vocal Events Pack: {exc}") from exc


def _event_prompt(tag: str) -> str:
    return f"A brief natural vocal reaction {tag}"


def render_vocal_event(sound: str, reference_audio: Path) -> tuple[bytes, dict[str, Any]]:
    """Render one accepted native vocal event locally from an authorized reference WAV.

    This function never silently falls back. A cue without a validated native route
    raises a clear error so callers can use the existing Nastech Voice Core path and
    preserve truthful manifest fidelity.
    """

    route = event_route(sound)
    if route.event_tag is None:
        raise VocalEventError(
            f"'{route.sound}' has no validated native event route. {route.reason} "
            "Use Nastech Voice Core synthesis for its explicit expression fallback."
        )
    reference = Path(reference_audio).expanduser().resolve()
    if not reference.is_file():
        raise VocalEventError(f"Voice-authorized reference WAV is not available: {reference}")
    device = _device()
    model = _load_model(device)
    try:
        waveform = model.generate(_event_prompt(route.event_tag), audio_prompt_path=str(reference))
        samples = waveform.detach().cpu().numpy().squeeze()
        import soundfile as sf

        buffer = io.BytesIO()
        sf.write(buffer, samples, model.sr, format="WAV", subtype="PCM_16")
    except Exception as exc:
        raise VocalEventError(
            f"Local native event generation failed for '{route.sound}': {exc}"
        ) from exc
    manifest = {
        "kind": "nastech_vocal_event",
        "sound": route.sound,
        "render_route": "native-event",
        "event_tag": route.event_tag,
        "pack": PACK_ID,
        "pack_label": PACK_LABEL,
        "device": device,
        "sample_rate": int(model.sr),
        "reference_audio": str(reference),
        "reference_authorization": "operator-confirmed-at-invocation",
        "local_only": True,
        "fallback": "nastech-voice-core-expression",
    }
    return buffer.getvalue(), manifest
