"""Nastech Compact agent API backed by a local tuned Supertonic ONNX runtime."""

from __future__ import annotations

import html
import logging
import os
from collections.abc import Iterator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from .cleanup import VoiceCleanupError, clean_wav
from .markup import NastechMarkupError
from .platforms import PlatformPlanError, host_platform_report, platform_preflight
from .supertonic import CompactAudio, CompactRuntimeError, SupertonicRuntime, compile_nastechml

logger = logging.getLogger(__name__)
MAX_CLEANUP_BYTES = 64 * 1024 * 1024
VERSION = "0.8.0"


class AgentCompileRequest(BaseModel):
    """A structured NastechML request with local-runtime controls."""

    markup: str = Field(min_length=1, max_length=12000)
    voice: str | None = Field(default=None, pattern="^[A-Za-z0-9_-]{1,64}$")
    steps: int | None = Field(default=None, ge=5, le=12)


class AgentSpeechRequest(AgentCompileRequest):
    """NastechML request that produces local Supertonic audio."""

    cleanup: bool = False


class AgentStreamRequest(AgentSpeechRequest):
    """Chunked WAV delivery request.

    Audio is synthesized completely by the local model before it is emitted as
    chunks. This preserves one-model inference and WAV correctness; it is not
    falsely advertised as token- or frame-level TTS streaming.
    """

    chunk_bytes: int = Field(default=65536, ge=4096, le=1048576)


class AgentPlanRequest(AgentSpeechRequest):
    """Agent-facing plan request that compiles speech without creating audio."""

    objective: str = Field(
        default="Generate an auditable local expressive English WAV response.",
        min_length=1,
        max_length=280,
    )
    delivery: str = Field(default="wav", pattern="^(wav|chunked-wav)$")


class PlatformPreflightRequest(BaseModel):
    """Named portable runtime target to evaluate against the current host."""

    target: str = Field(min_length=1, max_length=64, pattern="^[a-z0-9-]+$")


class OpenAISpeechRequest(BaseModel):
    """Small OpenAI-compatible request shape for existing agent clients."""

    model: str = "nastech-compact-en-v1"
    input: str = Field(min_length=1, max_length=12000)
    voice: str | None = Field(default=None, pattern="^[A-Za-z0-9_-]{1,64}$")
    response_format: str = Field(default="wav", pattern="^wav$")
    speed: float = Field(default=1.0, ge=0.7, le=2.0)
    cleanup: bool = False


class AgentToolDescriptor(BaseModel):
    """Machine-readable description of an agent-callable local API operation."""

    name: str
    description: str
    method: str
    path: str
    input_schema: dict[str, Any]


def agent_tool_descriptors() -> list[AgentToolDescriptor]:
    """Return the stable catalog of agent-callable local operations."""
    empty_input = {"type": "object", "properties": {}, "additionalProperties": False}
    binary_wav_input = {
        "content_type": "audio/wav",
        "body": "binary WAV bytes (mono signed-16-bit PCM)",
        "maximum_bytes": MAX_CLEANUP_BYTES,
    }
    return [
        AgentToolDescriptor(
            name="nastech_plan_speech",
            description=(
                "Compile English NastechML into an auditable execution plan before synthesis."
            ),
            method="POST",
            path="/v1/agent/plan",
            input_schema=AgentPlanRequest.model_json_schema(),
        ),
        AgentToolDescriptor(
            name="nastech_compile_speech",
            description="Compile English NastechML into a local Supertonic expression plan.",
            method="POST",
            path="/v1/agent/compile",
            input_schema=AgentCompileRequest.model_json_schema(),
        ),
        AgentToolDescriptor(
            name="nastech_generate_speech",
            description="Generate local English expressive WAV audio with Supertonic ONNX.",
            method="POST",
            path="/v1/agent/speech",
            input_schema=AgentSpeechRequest.model_json_schema(),
        ),
        AgentToolDescriptor(
            name="nastech_stream_speech",
            description="Deliver a completed local WAV response in bounded post-synthesis chunks.",
            method="POST",
            path="/v1/agent/speech/stream",
            input_schema=AgentStreamRequest.model_json_schema(),
        ),
        AgentToolDescriptor(
            name="nastech_clean_wav",
            description="Apply conservative local PCM cleanup to a mono signed-16-bit WAV file.",
            method="POST",
            path="/v1/audio/clean",
            input_schema=binary_wav_input,
        ),
        AgentToolDescriptor(
            name="nastech_list_platforms",
            description=(
                "Report host facts, registered ONNX providers, and truthful platform profiles."
            ),
            method="GET",
            path="/v1/platforms",
            input_schema=empty_input,
        ),
        AgentToolDescriptor(
            name="nastech_platform_preflight",
            description="Create a portable CPU, GPU, Android, iOS, or browser activation plan.",
            method="POST",
            path="/v1/platforms/preflight",
            input_schema=PlatformPreflightRequest.model_json_schema(),
        ),
        AgentToolDescriptor(
            name="nastech_runtime_diagnostics",
            description="Read the local CPU policy, model state, cache state, and runtime metrics.",
            method="GET",
            path="/v1/runtime/diagnostics",
            input_schema=empty_input,
        ),
        AgentToolDescriptor(
            name="nastech_warmup_runtime",
            description="Load the local ONNX runtime and perform a short local warm-up synthesis.",
            method="POST",
            path="/v1/runtime/warmup",
            input_schema=empty_input,
        ),
        AgentToolDescriptor(
            name="nastech_clear_runtime_cache",
            description="Discard cached WAV responses without unloading local ONNX sessions.",
            method="POST",
            path="/v1/runtime/cache/clear",
            input_schema=empty_input,
        ),
    ]


def _authorization_required() -> bool:
    return bool(os.getenv("NASTECH_API_KEY"))


def require_agent_key(authorization: Annotated[str | None, Header()] = None) -> None:
    expected = os.getenv("NASTECH_API_KEY")
    if not expected:
        return
    if authorization != f"Bearer {expected}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid Nastech bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _runtime(request: Request) -> SupertonicRuntime:
    return request.app.state.runtime


def _text_to_markup(text: str, voice: str | None = None, speed: float = 1.0) -> str:
    safe_text = html.escape(text)
    voice_attr = f' voice="{html.escape(voice, quote=True)}"' if voice else ""
    rate = "slow" if speed < 0.93 else "fast" if speed > 1.07 else "normal"
    return f'<speak{voice_attr}><prosody rate="{rate}">{safe_text}</prosody></speak>'


def _compiled(payload: AgentCompileRequest, runtime: SupertonicRuntime):
    settings = runtime.settings
    if payload.voice:
        settings = type(settings)(
            default_voice=payload.voice,
            language=settings.language,
            total_steps=payload.steps or settings.total_steps,
            speed=settings.speed,
            cache_dir=settings.cache_dir,
        )
    elif payload.steps:
        settings = type(settings)(
            default_voice=settings.default_voice,
            language=settings.language,
            total_steps=payload.steps,
            speed=settings.speed,
            cache_dir=settings.cache_dir,
        )
    return compile_nastechml(payload.markup, settings)


def _compiled_payload(compiled: Any) -> dict[str, Any]:
    return {
        "request_id": compiled.request_id,
        "runtime": "supertonic-local-onnx-cpu",
        "text": compiled.text,
        "voice": compiled.voice,
        "steps": compiled.steps,
        "speed": compiled.speed,
        "manifest": compiled.manifest,
    }


def _agent_plan(payload: AgentPlanRequest, compiled: Any) -> dict[str, Any]:
    decisions = compiled.manifest["decisions"]
    direct = sum(item["fidelity"] == "direct" for item in decisions)
    approximated = sum(item["fidelity"] == "approximated" for item in decisions)
    unavailable = sum(item["fidelity"] == "unavailable" for item in decisions)
    delivery_path = (
        "/v1/agent/speech/stream" if payload.delivery == "chunked-wav" else "/v1/agent/speech"
    )
    return {
        **_compiled_payload(compiled),
        "objective": payload.objective,
        "execution": {
            "model_family": "supertonic-3",
            "inference": "local-onnx-cpu",
            "delivery": payload.delivery,
            "delivery_endpoint": delivery_path,
            "voice_cleanup_requested": payload.cleanup,
            "steps": [
                "Validate English NastechML.",
                "Compile controls into a local Supertonic expression prompt.",
                "Run one bounded local ONNX synthesis request.",
                "Optionally apply deterministic local PCM cleanup.",
                "Return WAV bytes or bounded post-synthesis chunks.",
            ],
            "fidelity_summary": {
                "direct": direct,
                "approximated": approximated,
                "unavailable": unavailable,
            },
        },
        "warnings": compiled.manifest.get("warnings", []),
    }


def _error_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, (NastechMarkupError, VoiceCleanupError, PlatformPlanError, ValueError)):
        code = status.HTTP_422_UNPROCESSABLE_CONTENT
    elif isinstance(exc, CompactRuntimeError):
        code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return JSONResponse(status_code=code, content={"detail": str(exc)})


def _maybe_clean_audio(
    audio: CompactAudio, requested: bool
) -> tuple[CompactAudio, dict[str, Any] | None]:
    if not requested:
        return audio, None
    cleaned = clean_wav(audio.data)
    return (
        CompactAudio(
            data=cleaned.data,
            content_type="audio/wav",
            duration_seconds=audio.duration_seconds,
            sample_rate=audio.sample_rate,
        ),
        cleaned.report,
    )


def _audio_headers(
    audio: CompactAudio, request_id: str, cleanup_report: dict[str, Any] | None = None
) -> dict[str, str]:
    return {
        "X-Nastech-Request-Id": request_id,
        "X-Nastech-Runtime": "supertonic-local-onnx-cpu",
        "X-Nastech-Duration-Seconds": f"{audio.duration_seconds:.2f}",
        "X-Nastech-Manifest-Endpoint": "/v1/agent/compile",
        "X-Nastech-Voice-Cleanup": "local-pcm-hygiene" if cleanup_report else "not-requested",
    }


def _audio_response(
    audio: CompactAudio, request_id: str, cleanup_report: dict[str, Any] | None = None
) -> Response:
    return Response(
        content=audio.data,
        media_type=audio.content_type,
        headers=_audio_headers(audio, request_id, cleanup_report),
    )


def _stream_bytes(data: bytes, chunk_bytes: int) -> Iterator[bytes]:
    for start in range(0, len(data), chunk_bytes):
        yield data[start : start + chunk_bytes]


def create_app(runtime: SupertonicRuntime | None = None) -> FastAPI:
    """Create a local and independently testable Nastech Compact application."""

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        if os.getenv("NASTECH_WARMUP_ON_START", "0").lower() in {"1", "true", "yes"}:
            try:
                await run_in_threadpool(application.state.runtime.warmup)
                logger.info("Nastech CPU runtime warm-up completed.")
            except CompactRuntimeError as exc:
                logger.warning("Nastech CPU runtime warm-up failed: %s", exc)
        yield

    app = FastAPI(
        title="Nastech Compact TTS",
        version=VERSION,
        description=(
            "A local, CPU-tuned, agent-ready expressive TTS API backed by Supertonic 3 ONNX "
            "assets. Agent plans and chunked delivery remain auditable and local."
        ),
        lifespan=lifespan,
    )
    app.state.runtime = runtime or SupertonicRuntime()

    @app.get("/v1/health")
    async def health(local_runtime: SupertonicRuntime = Depends(_runtime)) -> dict[str, Any]:
        return {
            "status": "ok",
            "service": "nastech-tts",
            "version": VERSION,
            "runtime": local_runtime.status(),
            "authentication_required": _authorization_required(),
        }

    @app.get("/v1/capabilities")
    async def capabilities(_: None = Depends(require_agent_key)) -> dict[str, Any]:
        return {
            "language": "en",
            "model_family": "supertonic-3",
            "inference": "local-onnx-cpu",
            "agent_endpoints": [
                "/v1/agent/plan",
                "/v1/agent/compile",
                "/v1/agent/speech",
                "/v1/agent/speech/stream",
                "/v1/audio/speech",
                "/v1/audio/clean",
            ],
            "runtime_endpoints": [
                "/v1/runtime/diagnostics",
                "/v1/runtime/warmup",
                "/v1/runtime/cache/clear",
            ],
            "platform_endpoints": ["/v1/platforms", "/v1/platforms/preflight"],
            "platform_claim_boundary": (
                "CPU is verified. GPU, mobile, and browser profiles require actual provider/device "
                "synthesis acceptance before they are marked verified."
            ),
            "delivery": {
                "format": "wav",
                "chunked_endpoint": "/v1/agent/speech/stream",
                "streaming_semantics": "post-synthesis WAV chunks; not incremental model inference",
            },
            "voice_cleanup": {
                "available": True,
                "processor": "nastech-local-pcm-cleanup",
                "supported_input": "mono signed-16-bit PCM WAV",
                "operations": [
                    "dc-offset removal",
                    "near-silence gate",
                    "peak limiting",
                    "edge fades",
                ],
            },
            "cpu_optimizations": [
                "ORT_ENABLE_ALL graph optimization",
                "configurable ONNX thread pools",
                "bounded CPU synthesis queue",
                "bounded in-memory WAV cache",
                "optional startup warm-up",
            ],
            "documented_direct_events": ["laugh", "sigh"],
            "documented_native_tags": ["laugh", "breath", "sigh"],
            "release_dependent_tags": ["sad", "angry", "surprise", "cough", "yawn"],
            "formats": ["wav"],
            "max_deployment_mib": 1024,
        }

    @app.get("/v1/platforms")
    async def list_platforms(_: None = Depends(require_agent_key)) -> dict[str, Any]:
        return host_platform_report()

    @app.post("/v1/platforms/preflight", response_model=None)
    async def preflight_platform(
        payload: PlatformPreflightRequest,
        _: None = Depends(require_agent_key),
    ) -> dict[str, Any] | JSONResponse:
        try:
            return platform_preflight(payload.target)
        except PlatformPlanError as exc:
            return _error_response(exc)

    @app.get("/v1/runtime/diagnostics")
    async def diagnostics(
        _: None = Depends(require_agent_key),
        local_runtime: SupertonicRuntime = Depends(_runtime),
    ) -> dict[str, Any]:
        return {"service": "nastech-tts", "version": VERSION, "runtime": local_runtime.status()}

    @app.post("/v1/runtime/warmup", response_model=None)
    async def warmup(
        _: None = Depends(require_agent_key),
        local_runtime: SupertonicRuntime = Depends(_runtime),
    ) -> dict[str, Any] | JSONResponse:
        try:
            return await run_in_threadpool(local_runtime.warmup)
        except CompactRuntimeError as exc:
            return _error_response(exc)

    @app.post("/v1/runtime/cache/clear")
    async def clear_runtime_cache(
        _: None = Depends(require_agent_key),
        local_runtime: SupertonicRuntime = Depends(_runtime),
    ) -> dict[str, Any]:
        cleared = await run_in_threadpool(local_runtime.clear_audio_cache)
        return {"status": "cleared", **cleared, "runtime": local_runtime.status()}

    @app.get("/v1/agent/tools", response_model=list[AgentToolDescriptor])
    async def agent_tools(_: None = Depends(require_agent_key)) -> list[AgentToolDescriptor]:
        return agent_tool_descriptors()

    @app.post("/v1/agent/plan", response_model=None)
    async def plan_speech(
        payload: AgentPlanRequest,
        _: None = Depends(require_agent_key),
        local_runtime: SupertonicRuntime = Depends(_runtime),
    ) -> dict[str, Any] | JSONResponse:
        try:
            compiled = _compiled(payload, local_runtime)
        except (NastechMarkupError, ValueError) as exc:
            return _error_response(exc)
        return _agent_plan(payload, compiled)

    @app.post("/v1/agent/compile", response_model=None)
    async def compile_speech(
        payload: AgentCompileRequest,
        _: None = Depends(require_agent_key),
        local_runtime: SupertonicRuntime = Depends(_runtime),
    ) -> dict[str, Any] | JSONResponse:
        try:
            compiled = _compiled(payload, local_runtime)
        except (NastechMarkupError, ValueError) as exc:
            return _error_response(exc)
        return _compiled_payload(compiled)

    @app.post("/v1/agent/speech", response_model=None)
    async def synthesize_speech(
        payload: AgentSpeechRequest,
        _: None = Depends(require_agent_key),
        local_runtime: SupertonicRuntime = Depends(_runtime),
    ) -> Response | JSONResponse:
        try:
            compiled = _compiled(payload, local_runtime)
            audio = await run_in_threadpool(local_runtime.synthesize, compiled)
            audio, cleanup_report = await run_in_threadpool(
                _maybe_clean_audio, audio, payload.cleanup
            )
        except (NastechMarkupError, CompactRuntimeError, VoiceCleanupError, ValueError) as exc:
            return _error_response(exc)
        return _audio_response(audio, compiled.request_id, cleanup_report)

    @app.post("/v1/agent/speech/stream", response_model=None)
    async def stream_speech(
        payload: AgentStreamRequest,
        _: None = Depends(require_agent_key),
        local_runtime: SupertonicRuntime = Depends(_runtime),
    ) -> StreamingResponse | JSONResponse:
        try:
            compiled = _compiled(payload, local_runtime)
            audio = await run_in_threadpool(local_runtime.synthesize, compiled)
            audio, cleanup_report = await run_in_threadpool(
                _maybe_clean_audio, audio, payload.cleanup
            )
        except (NastechMarkupError, CompactRuntimeError, VoiceCleanupError, ValueError) as exc:
            return _error_response(exc)
        headers = _audio_headers(audio, compiled.request_id, cleanup_report)
        headers.update(
            {
                "X-Nastech-Delivery": "chunked-post-synthesis",
                "X-Nastech-Chunk-Bytes": str(payload.chunk_bytes),
            }
        )
        return StreamingResponse(
            _stream_bytes(audio.data, payload.chunk_bytes),
            media_type=audio.content_type,
            headers=headers,
        )

    @app.post("/v1/audio/clean", response_model=None)
    async def clean_audio(
        request: Request,
        _: None = Depends(require_agent_key),
    ) -> Response | JSONResponse:
        content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
        if content_type != "audio/wav":
            return _error_response(VoiceCleanupError("Content-Type must be audio/wav."))
        data = await request.body()
        if len(data) > MAX_CLEANUP_BYTES:
            return _error_response(
                VoiceCleanupError(f"WAV exceeds the {MAX_CLEANUP_BYTES}-byte cleanup limit.")
            )
        try:
            cleaned = await run_in_threadpool(clean_wav, data)
        except VoiceCleanupError as exc:
            return _error_response(exc)
        return Response(
            content=cleaned.data,
            media_type="audio/wav",
            headers={
                "X-Nastech-Voice-Cleanup": "local-pcm-hygiene",
                "X-Nastech-Cleanup-Report": html.escape(str(cleaned.report), quote=True),
            },
        )

    @app.post("/v1/audio/speech", response_model=None)
    async def openai_compatible_speech(
        payload: OpenAISpeechRequest,
        _: None = Depends(require_agent_key),
        local_runtime: SupertonicRuntime = Depends(_runtime),
    ) -> Response | JSONResponse:
        request = AgentSpeechRequest(
            markup=_text_to_markup(payload.input, payload.voice, payload.speed),
            voice=payload.voice,
            cleanup=payload.cleanup,
        )
        try:
            compiled = _compiled(request, local_runtime)
            audio = await run_in_threadpool(local_runtime.synthesize, compiled)
            audio, cleanup_report = await run_in_threadpool(
                _maybe_clean_audio, audio, payload.cleanup
            )
        except (NastechMarkupError, CompactRuntimeError, VoiceCleanupError, ValueError) as exc:
            return _error_response(exc)
        return _audio_response(audio, compiled.request_id, cleanup_report)

    return app


app = create_app()
