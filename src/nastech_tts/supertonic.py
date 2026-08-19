"""Local Supertonic runtime for Nastech Compact.

The runtime loads one ONNX model family locally. It never proxies synthesis to a
cloud provider and exposes bounded CPU execution appropriate for small servers.
"""

from __future__ import annotations

import hashlib
import html
import io
import os
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .cpu import CpuTuning
from .markup import parse_nastechml
from .types import AudioSpan, Fidelity, SpanKind
from .voices import resolve_english_voice_profile


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
    "angry": ("<angry>", Fidelity.APPROXIMATED, "Native tag request; confirm on pinned release."),
    "sad": ("<sad>", Fidelity.APPROXIMATED, "Native tag request; confirm on pinned release."),
    "happy": (None, Fidelity.APPROXIMATED, "No deterministic happy tag in compact runtime."),
    "excited": (
        "<surprise>",
        Fidelity.APPROXIMATED,
        "Mapped to the upstream surprise expression tag.",
    ),
    "surprised": (
        "<surprise>",
        Fidelity.DIRECT,
        "Upstream Supertonic expression tag.",
    ),
    "fearful": (
        "<surprise>",
        Fidelity.APPROXIMATED,
        "Native tag request; confirm on pinned release.",
    ),
    "disgusted": (None, Fidelity.UNAVAILABLE, "No compact-model control for this emotion."),
    "frustrated": ("<angry>", Fidelity.APPROXIMATED, "Mapped to an anger tag request."),
    "neutral": (None, Fidelity.DIRECT, "Neutral speech requires no expression tag."),
    "calm": ("<breath>", Fidelity.APPROXIMATED, "Breath cue may support a calmer delivery."),
}
_SOUND_TAGS: dict[str, tuple[str, Fidelity, str]] = {
    "laugh": ("<laugh>", Fidelity.DIRECT, "Officially documented Supertonic expression tag."),
    "sigh": ("<sigh>", Fidelity.DIRECT, "Officially documented Supertonic expression tag."),
    "chuckle": ("<laugh>", Fidelity.APPROXIMATED, "Mapped to documented laugh tag."),
    "gasp": (
        "<surprise>",
        Fidelity.APPROXIMATED,
        "Native tag request; confirm on pinned release.",
    ),
    "cough": ("<cough>", Fidelity.APPROXIMATED, "Native tag request; confirm on pinned release."),
    "sniffle": ("<breath>", Fidelity.APPROXIMATED, "Mapped to documented breath tag."),
    "groan": ("<sigh>", Fidelity.APPROXIMATED, "Mapped to documented sigh tag."),
    "yawn": ("<yawn>", Fidelity.APPROXIMATED, "Native tag request; confirm on pinned release."),
    "cry": ("<sad>", Fidelity.APPROXIMATED, "Mapped to sad tag request; no direct cry event."),
    "scream": ("<scream>", Fidelity.DIRECT, "Upstream Supertonic expression tag."),
    "throatclear": ("<throatclear>", Fidelity.DIRECT, "Upstream Supertonic expression tag."),
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
    markup: str,
    settings: CompactSettings | None = None,
    *,
    language: str | None = None,
) -> CompactCompiledRequest:
    """Compile stable NastechML into a provider-ready prompt with a declared language."""
    settings = settings or CompactSettings.from_env()
    selected_language = language or settings.language
    voice, spans = parse_nastechml(markup, language=selected_language)
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
    profile = resolve_english_voice_profile(selected_voice) if selected_language == "en" else None
    base_voice = profile.base_voice if profile is not None else selected_voice
    requested_speed = round(sum(speeds) / len(speeds), 2) if speeds else settings.speed
    effective_speed = (
        round(requested_speed * profile.default_speed, 2) if profile else requested_speed
    )
    request_id = os.urandom(12).hex()
    manifest = {
        "request_id": request_id,
        "language": selected_language,
        "model_family": "supertonic-3",
        "source_markup": markup,
        "compiled_text": " ".join(compiled),
        "voice": base_voice,
        "requested_voice": selected_voice,
        "voice_profile": {
            "profile_id": profile.profile_id,
            "base_voice": profile.base_voice,
            "kind": profile.kind,
            "default_speed": profile.default_speed,
            "description": profile.description,
        }
        if profile
        else None,
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
        voice=base_voice,
        speed=effective_speed,
        steps=settings.total_steps,
        manifest=manifest,
    )


@dataclass
class SupertonicRuntime:
    """Lazy Supertonic runtime with tuned ONNX sessions and bounded CPU work."""

    settings: CompactSettings = field(default_factory=CompactSettings.from_env)
    cpu: CpuTuning = field(default_factory=CpuTuning.from_env)
    _tts: Any = field(default=None, init=False, repr=False)
    _styles: dict[str, Any] = field(default_factory=dict, init=False, repr=False)
    _audio_cache: OrderedDict[str, CompactAudio] = field(default_factory=OrderedDict, init=False)
    _cache_bytes: int = field(default=0, init=False)
    _synthesis_slots: threading.BoundedSemaphore = field(init=False, repr=False)
    _state_lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _started_at: float = field(default_factory=time.monotonic, init=False, repr=False)
    _metrics: dict[str, float | int] = field(
        default_factory=lambda: {
            "synthesis_requests": 0,
            "synthesis_failures": 0,
            "audio_cache_hits": 0,
            "total_queue_wait_seconds": 0.0,
            "total_synthesis_seconds": 0.0,
        },
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        self._synthesis_slots = threading.BoundedSemaphore(self.cpu.max_parallel_synthesis)

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
            self._tts = TTS(
                model="supertonic-3",
                model_dir=self.settings.cache_dir,
                auto_download=True,
                intra_op_num_threads=self.cpu.intra_op_threads,
                inter_op_num_threads=self.cpu.inter_op_threads,
            )
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

    @staticmethod
    def _cache_key(compiled: CompactCompiledRequest) -> str:
        source = f"{compiled.text}\x00{compiled.voice}\x00{compiled.speed}\x00{compiled.steps}"
        return hashlib.sha256(source.encode("utf-8")).hexdigest()

    def _read_cached_audio(self, key: str) -> CompactAudio | None:
        with self._state_lock:
            audio = self._audio_cache.get(key)
            if audio is not None:
                self._audio_cache.move_to_end(key)
                self._metrics["audio_cache_hits"] = int(self._metrics["audio_cache_hits"]) + 1
            return audio

    def _store_cached_audio(self, key: str, audio: CompactAudio) -> None:
        max_bytes = self.cpu.audio_cache_mib * 1024 * 1024
        if len(audio.data) > max_bytes:
            return
        with self._state_lock:
            previous = self._audio_cache.pop(key, None)
            if previous is not None:
                self._cache_bytes -= len(previous.data)
            self._audio_cache[key] = audio
            self._cache_bytes += len(audio.data)
            while (
                len(self._audio_cache) > self.cpu.audio_cache_entries
                or self._cache_bytes > max_bytes
            ):
                _, evicted = self._audio_cache.popitem(last=False)
                self._cache_bytes -= len(evicted.data)

    def _record(self, name: str, value: int | float = 1) -> None:
        with self._state_lock:
            self._metrics[name] = self._metrics[name] + value

    def status(self) -> dict[str, Any]:
        with self._state_lock:
            metrics = dict(self._metrics)
            cache_entries = len(self._audio_cache)
            cache_bytes = self._cache_bytes
        requests = int(metrics["synthesis_requests"])
        return {
            "provider": "supertonic-local",
            "model_family": "supertonic-3",
            "loaded": self._tts is not None,
            "model_cache": str(self.settings.cache_dir),
            "model_assets_bytes": _cache_size_bytes(self.settings.cache_dir),
            "model_assets_mib": round(_cache_size_bytes(self.settings.cache_dir) / 1024 / 1024, 2),
            "target_max_deployment_mib": 1024,
            "cpu": self.cpu.as_dict(),
            "audio_cache": {
                "entries": cache_entries,
                "bytes": cache_bytes,
                "mib": round(cache_bytes / 1024 / 1024, 4),
            },
            "metrics": {
                **metrics,
                "mean_synthesis_seconds": round(
                    float(metrics["total_synthesis_seconds"]) / requests, 4
                )
                if requests
                else 0.0,
                "uptime_seconds": round(time.monotonic() - self._started_at, 3),
            },
        }

    def clear_audio_cache(self) -> dict[str, int]:
        """Discard cached WAV responses without unloading the local ONNX sessions."""
        with self._state_lock:
            entries = len(self._audio_cache)
            bytes_cleared = self._cache_bytes
            self._audio_cache.clear()
            self._cache_bytes = 0
        return {"entries_cleared": entries, "bytes_cleared": bytes_cleared}

    def synthesize_mixed(
        self, markup: str, *, language: str | None = None
    ) -> tuple[CompactAudio, dict[str, Any]]:
        """Synthesize a document whose spans may use different voices and delivery styles.

        Each span is rendered locally with the requested voice and expression, then the
        PCM segments are concatenated without a cloud provider or voice-conversion stage.
        Volume is applied as a deterministic gain after synthesis: soft is attenuated and
        loud is bounded before the final WAV is encoded.
        """
        import numpy as np
        import soundfile as sf

        selected_language = language or self.settings.language
        root_voice, spans = parse_nastechml(markup, language=selected_language)
        segments: list[np.ndarray] = []
        segment_manifests: list[dict[str, Any]] = []
        sample_rate = 44100
        for index, span in enumerate(spans):
            voice = span.voice
            if voice in {"", "nastech", "default", "tara"}:
                voice = self.settings.default_voice or root_voice
            if span.kind == SpanKind.SPEECH:
                body = html.escape(str(span.value), quote=False)
                if span.style.emotion:
                    intensity = span.style.intensity if span.style.intensity is not None else 0.7
                    body = (
                        f'<emotion name="{html.escape(span.style.emotion)}"'
                        f' intensity="{intensity}">{body}</emotion>'
                    )
                if span.style.rate or span.style.volume:
                    rate = span.style.rate or "normal"
                    volume = span.style.volume or "normal"
                    body = f'<prosody rate="{rate}" volume="{volume}">{body}</prosody>'
            elif span.kind == SpanKind.SOUND:
                body = f'<sound type="{html.escape(str(span.value))}" />'
            else:
                body = f'<pause ms="{int(span.value)}" />'
            fragment = f'<speak voice="{html.escape(voice)}">{body}</speak>'
            compiled = compile_nastechml(fragment, self.settings, language=selected_language)
            audio = self.synthesize(compiled, use_cache=False)
            data, _ = sf.read(io.BytesIO(audio.data), dtype="int16")
            samples = np.asarray(data, dtype=np.int16).reshape(-1)
            gain = {"soft": 0.55, "normal": 1.0, "loud": 1.2}.get(
                span.style.volume or "normal", 1.0
            )
            if gain != 1.0:
                samples = np.clip(samples.astype(np.float32) * gain, -32767, 32767).astype(np.int16)
            segments.append(samples)
            segment_manifests.append(
                {
                    "span_index": index,
                    "voice": voice,
                    "kind": span.kind.value,
                    "emotion": span.style.emotion,
                    "sound": str(span.value) if span.kind == SpanKind.SOUND else None,
                    "rate": span.style.rate or "normal",
                    "volume": span.style.volume or "normal",
                    "compiled_text": compiled.text,
                    "decisions": compiled.manifest["decisions"],
                }
            )
        merged = np.concatenate(segments) if segments else np.zeros(1, dtype=np.int16)
        output = io.BytesIO()
        sf.write(output, merged, sample_rate, format="WAV", subtype="PCM_16")
        audio = CompactAudio(
            data=output.getvalue(),
            content_type="audio/wav",
            duration_seconds=len(merged) / sample_rate,
            sample_rate=sample_rate,
        )
        manifest = {
            "language": selected_language,
            "voice_mode": "mixed",
            "root_voice": root_voice,
            "segments": segment_manifests,
            "sample_rate_hz": sample_rate,
            "duration_seconds": audio.duration_seconds,
        }
        return audio, manifest

    def warmup(self) -> dict[str, Any]:
        """Load ONNX sessions, voice vectors, and run one short local synthesis."""
        started = time.perf_counter()
        compiled = compile_nastechml(
            f'<speak voice="{self.settings.default_voice}">Nastech is ready.</speak>', self.settings
        )
        audio = self.synthesize(compiled)
        return {
            "status": "ready",
            "warmup_seconds": round(time.perf_counter() - started, 4),
            "audio_duration_seconds": round(audio.duration_seconds, 4),
            "runtime": self.status(),
        }

    def synthesize(
        self, compiled: CompactCompiledRequest, *, use_cache: bool = True
    ) -> CompactAudio:
        """Generate local WAV audio, optionally bypassing the bounded response cache."""
        key = self._cache_key(compiled)
        if use_cache:
            cached = self._read_cached_audio(key)
            if cached is not None:
                return cached

        queue_started = time.perf_counter()
        acquired = self._synthesis_slots.acquire(timeout=self.cpu.queue_timeout_seconds)
        queue_wait = time.perf_counter() - queue_started
        if not acquired:
            self._record("synthesis_failures")
            raise CompactRuntimeError(
                "Timed out waiting for CPU synthesis capacity. Reduce clients or increase "
                "NASTECH_MAX_PARALLEL_SYNTHESIS."
            )
        try:
            # A request may have completed while this request waited in the queue.
            if use_cache:
                cached = self._read_cached_audio(key)
                if cached is not None:
                    return cached
            started = time.perf_counter()
            tts = self._load()
            try:
                waveform, duration = tts.synthesize(
                    text=compiled.text,
                    lang=self.settings.language,
                    voice_style=self._style(compiled.voice),
                    total_steps=compiled.steps,
                    speed=compiled.speed,
                )
            except Exception as exc:
                self._record("synthesis_failures")
                raise CompactRuntimeError(f"Local Supertonic synthesis failed: {exc}") from exc
            try:
                import soundfile as sf

                buffer = io.BytesIO()
                sf.write(buffer, waveform.squeeze(), 44100, format="WAV")
            except Exception as exc:
                self._record("synthesis_failures")
                raise CompactRuntimeError(f"Unable to encode Supertonic audio: {exc}") from exc
            audio = CompactAudio(
                data=buffer.getvalue(),
                content_type="audio/wav",
                duration_seconds=float(duration[0]),
            )
            if use_cache:
                self._store_cached_audio(key, audio)
            self._record("synthesis_requests")
            self._record("total_queue_wait_seconds", queue_wait)
            self._record("total_synthesis_seconds", time.perf_counter() - started)
            return audio
        finally:
            self._synthesis_slots.release()
