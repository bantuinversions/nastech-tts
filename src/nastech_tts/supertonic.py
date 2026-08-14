"""Local Supertonic runtime for Nastech Compact.

The runtime loads one small ONNX model family locally. It does not call a cloud
provider and does not bundle any upstream model weights in the Nastech package.
"""

from __future__ import annotations

import io
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .markup import parse_nastechml
from .types import AudioSpan, Fidelity, SpanKind


class CompactRuntimeError(RuntimeError):
    """Raised when local Supertonic inference is unavailable or fails."""


@dataclass(frozen=True)
class CompactSettings:
    """Configuration for the local Supertonic runtime."""

    default_voice: str = "F1"
    language: str = "en"
    total_steps: int = 8
    speed: float = 1.0
    cache_dir: Path = Path.home() / ".cache" / "supertonic3"

    @classmethod
    def from_env(cls) -> CompactSettings:
        return cls(
            default_voice=os.getenv("NASTECH_VOICE", "F1"),
            language=os.getenv("NASTECH_LANGUAGE", "en"),
            total_steps=int(os.getenv("NASTECH_STEPS", "8")),
            speed=float(os.getenv("NASTECH_SPEED", "1.0")),
            cache_dir=Path(
                os.getenv("NASTECH_MODEL_CACHE", str(Path.home() / ".cache" / "supertonic3"))
            ),
        )


@dataclass(frozen=True)
class CompactCompiledRequest:
    request_id: str
    text: str
    voice: str
    speed: float
    steps: int
    manifest: dict[str, Any]


@dataclass(frozen=True)
class CompactAudio:
    data: bytes
    content_type: str
    duration_seconds: float
    sample_rate: int = 44100


_EMOTION_TAGS: dict[str, tuple[str | None, Fidelity, str]] = {
    "angry": (
        "<angry>",
        Fidelity.APPROXIMATED,
        "Native tag request; confirm on the pinned model release.",
    ),
    "sad": (
        "<sad>",
        Fidelity.APPROXIMATED,
        "Native tag request; confirm on the pinned model release.",
    ),
    "happy": (
        None,
        Fidelity.APPROXIMATED,
        "No documented deterministic happy tag in the compact runtime.",
    ),
    "excited": (
        "<surprise>",
        Fidelity.APPROXIMATED,
        "Native tag request; confirm on the pinned model release.",
    ),
    "fearful": (
        "<surprise>",
        Fidelity.APPROXIMATED,
        "Native tag request; confirm on the pinned model release.",
    ),
    "disgusted": (
        None,
        Fidelity.UNAVAILABLE,
        "No documented compact-model control for this emotion.",
    ),
    "frustrated": ("<angry>", Fidelity.APPROXIMATED, "Mapped to an anger tag request."),
    "neutral": (None, Fidelity.DIRECT, "Neutral speech requires no expression tag."),
    "calm": (
        "<breath>",
        Fidelity.APPROXIMATED,
        "Breath cue may support a calmer delivery but is not deterministic.",
    ),
}
_SOUND_TAGS: dict[str, tuple[str, Fidelity, str]] = {
    "laugh": ("<laugh>", Fidelity.DIRECT, "Officially documented Supertonic expression tag."),
    "sigh": ("<sigh>", Fidelity.DIRECT, "Officially documented Supertonic expression tag."),
    "chuckle": ("<laugh>", Fidelity.APPROXIMATED, "Mapped to the documented laugh tag."),
    "gasp": (
        "<surprise>",
        Fidelity.APPROXIMATED,
        "Native tag request; confirm on the pinned model release.",
    ),
    "cough": (
        "<cough>",
        Fidelity.APPROXIMATED,
        "Native tag request; confirm on the pinned model release.",
    ),
    "sniffle": ("<breath>", Fidelity.APPROXIMATED, "Mapped to the documented breath tag."),
    "groan": ("<sigh>", Fidelity.APPROXIMATED, "Mapped to the documented sigh tag."),
    "yawn": (
        "<yawn>",
        Fidelity.APPROXIMATED,
        "Native tag request; confirm on the pinned model release.",
    ),
    "cry": (
        "<sad>",
        Fidelity.APPROXIMATED,
        "Mapped to a sad tag request; no documented direct cry event.",
    ),
}
_RATE_MAP = {"slow": 0.82, "normal": 1.0, "fast": 1.18}


def _cache_size_bytes(cache_dir: Path) -> int:
    if not cache_dir.exists():
        return 0
    return sum(path.stat().st_size for path in cache_dir.rglob("*") if path.is_file())


def _compile_span(span: AudioSpan, index: int) -> tuple[str, dict[str, Any], float | None]:
    decision: dict[str, Any] = {
        "span_index": index,
        "kind": span.kind.value,
        "requested_behavior": None,
        "compiled_controls": [],
        "fidelity": Fidelity.DIRECT.value,
        "reason": "Plain speech.",
    }
    speed = _RATE_MAP.get(span.style.rate or "normal")
    if span.kind == SpanKind.PAUSE:
        decision.update(
            requested_behavior="pause",
            compiled_controls=["<breath>"],
            fidelity=Fidelity.APPROXIMATED.value,
            reason="Compact runtime maps pauses to a documented breath cue.",
        )
        return "<breath>", decision, speed
    if span.kind == SpanKind.SOUND:
        tag, fidelity, reason = _SOUND_TAGS[str(span.value)]
        decision.update(
            requested_behavior=str(span.value),
            compiled_controls=[tag],
            fidelity=fidelity.value,
            reason=reason,
        )
        return tag, decision, speed

    tag: str | None = None
    if span.style.emotion:
        tag, fidelity, reason = _EMOTION_TAGS[span.style.emotion]
        decision.update(
            requested_behavior=span.style.emotion,
            compiled_controls=[tag] if tag else [],
            fidelity=fidelity.value,
            reason=reason,
        )
    text = str(span.value)
    return (f"{tag} {text}" if tag else text), decision, speed


def compile_nastechml(
    markup: str, settings: CompactSettings | None = None
) -> CompactCompiledRequest:
    """Compile stable NastechML into compact Supertonic prompt text."""
    settings = settings or CompactSettings.from_env()
    voice, spans = parse_nastechml(markup)
    compiled: list[str] = []
    decisions: list[dict[str, Any]] = []
    speeds: list[float] = []
    for index, span in enumerate(spans):
        text, decision, speed = _compile_span(span, index)
        compiled.append(text)
        decisions.append(decision)
        if speed is not None:
            speeds.append(speed)
    selected_voice = (
        settings.default_voice if voice in {"", "nastech", "default", "tara"} else voice
    )
    effective_speed = round(sum(speeds) / len(speeds), 2) if speeds else settings.speed
    request_id = os.urandom(12).hex()
    manifest = {
        "request_id": request_id,
        "language": settings.language,
        "model_family": "supertonic-3",
        "source_markup": markup,
        "compiled_text": " ".join(compiled),
        "voice": selected_voice,
        "steps": settings.total_steps,
        "speed": effective_speed,
        "decisions": decisions,
        "warnings": [
            decision["reason"]
            for decision in decisions
            if decision["fidelity"] != Fidelity.DIRECT.value
        ],
    }
    return CompactCompiledRequest(
        request_id=request_id,
        text=manifest["compiled_text"],
        voice=selected_voice,
        speed=effective_speed,
        steps=settings.total_steps,
        manifest=manifest,
    )


@dataclass
class SupertonicRuntime:
    """Lazy local inference runtime backed by the official Supertonic Python SDK."""

    settings: CompactSettings = field(default_factory=CompactSettings.from_env)
    _tts: Any = field(default=None, init=False, repr=False)
    _styles: dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def _load(self) -> Any:
        if self._tts is not None:
            return self._tts
        try:
            from supertonic import TTS
        except ImportError as exc:
            raise CompactRuntimeError(
                "Supertonic is not installed. Install Nastech with the compact extra."
            ) from exc
        try:
            self._tts = TTS(auto_download=True)
        except Exception as exc:
            raise CompactRuntimeError(
                f"Unable to initialize local Supertonic assets: {exc}"
            ) from exc
        return self._tts

    def _style(self, voice: str) -> Any:
        if voice not in self._styles:
            try:
                self._styles[voice] = self._load().get_voice_style(voice_name=voice)
            except Exception as exc:
                raise CompactRuntimeError(
                    f"Unable to load Supertonic voice '{voice}': {exc}"
                ) from exc
        return self._styles[voice]

    def status(self) -> dict[str, Any]:
        return {
            "provider": "supertonic-local",
            "model_family": "supertonic-3",
            "loaded": self._tts is not None,
            "model_cache": str(self.settings.cache_dir),
            "model_assets_bytes": _cache_size_bytes(self.settings.cache_dir),
            "model_assets_mib": round(_cache_size_bytes(self.settings.cache_dir) / 1024 / 1024, 2),
            "target_max_deployment_mib": 1024,
        }

    def synthesize(self, compiled: CompactCompiledRequest) -> CompactAudio:
        tts = self._load()
        try:
            audio, duration = tts.synthesize(
                text=compiled.text,
                lang=self.settings.language,
                voice_style=self._style(compiled.voice),
                total_steps=compiled.steps,
                speed=compiled.speed,
            )
        except Exception as exc:
            raise CompactRuntimeError(f"Local Supertonic synthesis failed: {exc}") from exc
        try:
            import soundfile as sf

            buffer = io.BytesIO()
            sf.write(buffer, audio.squeeze(), 44100, format="WAV")
        except Exception as exc:
            raise CompactRuntimeError(f"Unable to encode Supertonic audio: {exc}") from exc
        return CompactAudio(
            data=buffer.getvalue(),
            content_type="audio/wav",
            duration_seconds=float(duration[0]),
        )
