"""Fish Audio S2 provider integration and NastechML compilation.

Nastech is a control plane: it translates structured behavior requests into the
native Fish S2 inline controls and delegates audio generation to an official
self-hosted or cloud Fish endpoint. Model weights are never bundled here.
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx

from .markup import NastechMarkupError, parse_nastechml
from .types import AudioSpan, Fidelity, SpanKind


class ProviderError(RuntimeError):
    """Raised when a configured Fish provider cannot complete a request."""


@dataclass(frozen=True)
class ProviderSettings:
    """Runtime settings for an official Fish server or cloud endpoint."""

    mode: str = "fish-local"
    base_url: str = "http://127.0.0.1:8080"
    bearer_token: str | None = None
    cloud_model: str = "s2.1-pro-free"
    timeout_seconds: float = 180.0

    @classmethod
    def from_env(cls) -> ProviderSettings:
        mode = os.getenv("NASTECH_PROVIDER", "fish-local")
        default_url = "https://api.fish.audio" if mode == "fish-cloud" else "http://127.0.0.1:8080"
        return cls(
            mode=mode,
            base_url=os.getenv("FISH_BASE_URL", default_url).rstrip("/"),
            bearer_token=os.getenv("FISH_AUDIO_API_KEY") or os.getenv("FISH_LOCAL_API_KEY"),
            cloud_model=os.getenv("FISH_CLOUD_MODEL", "s2.1-pro-free"),
            timeout_seconds=float(os.getenv("NASTECH_PROVIDER_TIMEOUT_SECONDS", "180")),
        )


@dataclass(frozen=True)
class SynthesizedAudio:
    """Provider response data returned to the API layer."""

    data: bytes
    content_type: str
    provider_request_id: str | None = None


class FishProvider(Protocol):
    """Minimal provider contract shared by cloud and local Fish modes."""

    async def health(self) -> dict[str, Any]: ...

    async def synthesize(
        self, payload: dict[str, Any], traceparent: str | None = None
    ) -> SynthesizedAudio: ...


class FishHttpProvider:
    """Official Fish HTTP provider supporting local and cloud endpoint modes."""

    def __init__(self, settings: ProviderSettings) -> None:
        if settings.mode not in {"fish-local", "fish-cloud"}:
            raise ValueError("FishHttpProvider requires fish-local or fish-cloud mode.")
        self.settings = settings

    def _headers(self, traceparent: str | None = None) -> dict[str, str]:
        headers = {"Accept": "audio/wav, audio/mpeg, audio/opus, application/octet-stream"}
        if self.settings.bearer_token:
            headers["Authorization"] = f"Bearer {self.settings.bearer_token}"
        if self.settings.mode == "fish-cloud":
            headers["model"] = self.settings.cloud_model
        if traceparent:
            headers["traceparent"] = traceparent
        return headers

    async def health(self) -> dict[str, Any]:
        if self.settings.mode == "fish-cloud":
            return {
                "status": "configured" if self.settings.bearer_token else "missing_credentials",
                "provider": "fish-cloud",
                "endpoint": self.settings.base_url,
            }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.settings.base_url}/v1/health")
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            return {"status": "unavailable", "provider": "fish-local", "detail": str(exc)}
        return {"status": data.get("status", "ok"), "provider": "fish-local"}

    def _provider_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Translate the rich cloud payload to the documented local-server schema."""
        if self.settings.mode == "fish-cloud":
            return payload
        reference_id = payload.get("reference_id")
        if isinstance(reference_id, list):
            raise ProviderError(
                "The official self-hosted Fish server accepts one reference_id per request. "
                "Use fish-cloud for multi-speaker S2 requests."
            )
        local_payload = {
            "text": payload["text"],
            "chunk_length": payload.get("chunk_length", 300),
            "format": payload.get("format", "wav"),
            "latency": "balanced"
            if payload.get("latency") == "low"
            else payload.get("latency", "normal"),
            "reference_id": reference_id,
            "normalize": payload.get("normalize", True),
            "streaming": False,
            "max_new_tokens": payload.get("max_new_tokens", 1024),
            "top_p": payload.get("top_p", 0.7),
            "repetition_penalty": payload.get("repetition_penalty", 1.2),
            "temperature": payload.get("temperature", 0.7),
        }
        return {key: value for key, value in local_payload.items() if value is not None}

    async def synthesize(
        self, payload: dict[str, Any], traceparent: str | None = None
    ) -> SynthesizedAudio:
        if self.settings.mode == "fish-cloud" and not self.settings.bearer_token:
            raise ProviderError(
                "FISH_AUDIO_API_KEY is required for fish-cloud mode. Configure it as "
                "an environment variable or use a self-hosted Fish server."
            )
        try:
            async with httpx.AsyncClient(timeout=self.settings.timeout_seconds) as client:
                response = await client.post(
                    f"{self.settings.base_url}/v1/tts",
                    headers=self._headers(traceparent),
                    json=self._provider_payload(payload),
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:500]
            raise ProviderError(
                f"Fish provider returned HTTP {exc.response.status_code}: {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderError(f"Fish provider request failed: {exc}") from exc
        return SynthesizedAudio(
            data=response.content,
            content_type=response.headers.get("content-type", "audio/wav"),
            provider_request_id=response.headers.get("x-request-id"),
        )


@dataclass(frozen=True)
class CompiledRequest:
    """A Fish-native request and auditable compilation record."""

    request_id: str
    provider_payload: dict[str, Any]
    manifest: dict[str, Any]


_EMOTION_TAGS: dict[str, str | None] = {
    "angry": "angry",
    "sad": "sad",
    "happy": "delight",
    "excited": "excited",
    "fearful": "shocked",
    "disgusted": "disgusted",
    "frustrated": "frustrated",
    "neutral": None,
    "calm": "low voice",
}
_SOUND_TAGS: dict[str, tuple[str, Fidelity, str]] = {
    "laugh": ("laughing", Fidelity.DIRECT, "Documented Fish S2 event control."),
    "chuckle": ("chuckle", Fidelity.DIRECT, "Documented Fish S2 event control."),
    "sigh": ("sigh", Fidelity.DIRECT, "Documented Fish S2 event control."),
    "gasp": ("gasp", Fidelity.DIRECT, "Provider-native semantic tag."),
    "groan": ("groaning", Fidelity.DIRECT, "Documented Fish S2 event control."),
    "cry": ("sobbing", Fidelity.DIRECT, "Documented Fish S2 event control."),
    "cough": (
        "cough",
        Fidelity.APPROXIMATED,
        "Free-form S2 tag; acceptance-test for a chosen model release.",
    ),
    "sniffle": (
        "sniffle",
        Fidelity.APPROXIMATED,
        "Free-form S2 tag; acceptance-test for a chosen model release.",
    ),
    "yawn": (
        "yawn",
        Fidelity.APPROXIMATED,
        "Free-form S2 tag; acceptance-test for a chosen model release.",
    ),
}
_RATE_MAP = {"slow": 0.82, "normal": 1.0, "fast": 1.18}
_VOLUME_MAP = {"soft": -5.0, "normal": 0.0, "loud": 4.0}


def _control(tag: str) -> str:
    return f"[{tag}]"


def _compile_span(span: AudioSpan, index: int) -> tuple[str, dict[str, Any]]:
    decision: dict[str, Any] = {
        "span_index": index,
        "kind": span.kind.value,
        "requested_behavior": None,
        "compiled_controls": [],
        "fidelity": Fidelity.DIRECT.value,
        "reason": "Plain speech.",
    }
    if span.kind == SpanKind.PAUSE:
        tag = "short pause" if int(span.value) <= 700 else "pause"
        decision.update(
            requested_behavior="pause",
            compiled_controls=[tag],
            reason="Provider-native pause request.",
        )
        return _control(tag), decision
    if span.kind == SpanKind.SOUND:
        tag, fidelity, reason = _SOUND_TAGS[str(span.value)]
        decision.update(
            requested_behavior=str(span.value),
            compiled_controls=[tag],
            fidelity=fidelity.value,
            reason=reason,
        )
        return _control(tag), decision

    controls: list[str] = []
    emotion = span.style.emotion
    if emotion:
        emotion_tag = _EMOTION_TAGS[emotion]
        decision["requested_behavior"] = emotion
        if emotion_tag:
            controls.append(emotion_tag)
            decision["reason"] = "Documented Fish S2 semantic emotion control."
        else:
            decision["reason"] = "Neutral speech requested; no provider tag is necessary."
    rendered = "".join(_control(tag) for tag in controls)
    if controls:
        rendered = f"{rendered} {span.value}"
    else:
        rendered = str(span.value)
    decision["compiled_controls"] = controls
    return rendered, decision


def compile_nastechml(
    markup: str,
    *,
    reference_id: str | list[str] | None = None,
    output_format: str = "wav",
    sample_rate: int | None = 44100,
    latency: str = "normal",
    temperature: float = 0.7,
    traceparent: str | None = None,
) -> CompiledRequest:
    """Compile NastechML into a documented Fish S2 request payload.

    The compiler preserves every requested event in a manifest so an agent can
    distinguish provider-native controls from release-dependent free-form tags.
    """
    if output_format not in {"wav", "mp3", "opus", "pcm"}:
        raise NastechMarkupError("Output format must be wav, mp3, opus, or pcm.")
    if latency not in {"low", "balanced", "normal"}:
        raise NastechMarkupError("Latency must be low, balanced, or normal.")
    if not 0.0 <= temperature <= 1.0:
        raise NastechMarkupError("Temperature must be between 0 and 1.")

    voice, spans = parse_nastechml(markup)
    compiled: list[str] = []
    decisions: list[dict[str, Any]] = []
    speeds: list[float] = []
    volumes: list[float] = []
    for index, span in enumerate(spans):
        output, decision = _compile_span(span, index)
        compiled.append(output)
        decisions.append(decision)
        if span.style.rate:
            speeds.append(_RATE_MAP[span.style.rate])
        if span.style.volume:
            volumes.append(_VOLUME_MAP[span.style.volume])

    selected_reference = reference_id
    if selected_reference is None and voice not in {"", "default", "nastech", "tara"}:
        selected_reference = voice
    payload: dict[str, Any] = {
        "text": " ".join(compiled),
        "temperature": temperature,
        "top_p": 0.7,
        "prosody": {
            "speed": round(sum(speeds) / len(speeds), 2) if speeds else 1.0,
            "volume": round(sum(volumes) / len(volumes), 2) if volumes else 0.0,
            "normalize_loudness": True,
        },
        "chunk_length": 300,
        "normalize": True,
        "format": output_format,
        "sample_rate": sample_rate,
        "latency": latency,
        "max_new_tokens": 1024,
        "repetition_penalty": 1.2,
        "min_chunk_length": 50,
        "condition_on_previous_chunks": True,
    }
    if selected_reference:
        payload["reference_id"] = selected_reference

    request_id = str(uuid.uuid4())
    manifest = {
        "request_id": request_id,
        "language": "en",
        "model_family": "fish-s2",
        "source_markup": markup,
        "compiled_text": payload["text"],
        "voice": voice,
        "reference_id_supplied": bool(selected_reference),
        "traceparent": traceparent,
        "decisions": decisions,
        "warnings": [
            decision["reason"]
            for decision in decisions
            if decision["fidelity"] == Fidelity.APPROXIMATED.value
        ],
    }
    return CompiledRequest(request_id=request_id, provider_payload=payload, manifest=manifest)


@dataclass
class NastechGateway:
    """Application service used by the Nastech HTTP API and agent tools."""

    provider: FishProvider | None
    provider_mode: str
    request_history: list[dict[str, Any]] = field(default_factory=list)

    async def health(self) -> dict[str, Any]:
        if self.provider is None:
            return {"status": "compile_only", "provider": "none"}
        return await self.provider.health()

    def compile(self, markup: str, **options: Any) -> CompiledRequest:
        return compile_nastechml(markup, **options)

    async def synthesize(
        self, markup: str, **options: Any
    ) -> tuple[SynthesizedAudio, CompiledRequest]:
        compiled = self.compile(markup, **options)
        if self.provider is None:
            raise ProviderError(
                "Nastech is in compile-only mode; configure fish-local or fish-cloud."
            )
        audio = await self.provider.synthesize(
            compiled.provider_payload, traceparent=options.get("traceparent")
        )
        self.request_history.append(compiled.manifest)
        return audio, compiled


def build_gateway_from_env() -> NastechGateway:
    """Build the configured gateway without requiring provider credentials at import time."""
    settings = ProviderSettings.from_env()
    if settings.mode == "compile-only":
        return NastechGateway(provider=None, provider_mode=settings.mode)
    if settings.mode not in {"fish-local", "fish-cloud"}:
        raise ValueError("NASTECH_PROVIDER must be fish-local, fish-cloud, or compile-only.")
    return NastechGateway(provider=FishHttpProvider(settings), provider_mode=settings.mode)
