"""Nastech Compact agent API backed by a local tuned Supertonic ONNX runtime."""

from __future__ import annotations

import html
import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .markup import NastechMarkupError
from .supertonic import CompactRuntimeError, SupertonicRuntime, compile_nastechml

logger = logging.getLogger(__name__)


class AgentCompileRequest(BaseModel):
    """A structured NastechML request with local-runtime controls."""

    markup: str = Field(min_length=1, max_length=12000)
    voice: str | None = Field(default=None, pattern="^[A-Za-z0-9_-]{1,64}$")
    steps: int | None = Field(default=None, ge=5, le=12)


class AgentSpeechRequest(AgentCompileRequest):
    """NastechML request that produces local Supertonic audio."""


class OpenAISpeechRequest(BaseModel):
    """Small OpenAI-compatible request shape for existing agent clients."""

    model: str = "nastech-compact-en-v1"
    input: str = Field(min_length=1, max_length=12000)
    voice: str | None = Field(default=None, pattern="^[A-Za-z0-9_-]{1,64}$")
    response_format: str = Field(default="wav", pattern="^wav$")
    speed: float = Field(default=1.0, ge=0.7, le=2.0)


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
    return [
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


def _error_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, NastechMarkupError):
        code = status.HTTP_422_UNPROCESSABLE_CONTENT
    elif isinstance(exc, CompactRuntimeError):
        code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return JSONResponse(status_code=code, content={"detail": str(exc)})


def _audio_response(audio: Any, request_id: str) -> Response:
    return Response(
        content=audio.data,
        media_type=audio.content_type,
        headers={
            "X-Nastech-Request-Id": request_id,
            "X-Nastech-Runtime": "supertonic-local-onnx-cpu",
            "X-Nastech-Duration-Seconds": f"{audio.duration_seconds:.2f}",
            "X-Nastech-Manifest-Endpoint": "/v1/agent/compile",
        },
    )


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
        version="0.6.0",
        description=(
            "A local, CPU-tuned, agent-ready expressive TTS API backed by Supertonic 3 ONNX "
            "assets. Use /v1/agent/compile for an auditable behavior plan before synthesis."
        ),
        lifespan=lifespan,
    )
    app.state.runtime = runtime or SupertonicRuntime()

    @app.get("/v1/health")
    async def health(local_runtime: SupertonicRuntime = Depends(_runtime)) -> dict[str, Any]:
        return {
            "status": "ok",
            "service": "nastech-tts",
            "version": "0.6.0",
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
                "/v1/agent/compile",
                "/v1/agent/speech",
                "/v1/audio/speech",
            ],
            "runtime_endpoints": [
                "/v1/runtime/diagnostics",
                "/v1/runtime/warmup",
                "/v1/runtime/cache/clear",
            ],
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

    @app.get("/v1/runtime/diagnostics")
    async def diagnostics(
        _: None = Depends(require_agent_key),
        local_runtime: SupertonicRuntime = Depends(_runtime),
    ) -> dict[str, Any]:
        return {"service": "nastech-tts", "version": "0.5.0", "runtime": local_runtime.status()}

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
        return {
            "request_id": compiled.request_id,
            "runtime": "supertonic-local-onnx-cpu",
            "text": compiled.text,
            "voice": compiled.voice,
            "steps": compiled.steps,
            "speed": compiled.speed,
            "manifest": compiled.manifest,
        }

    @app.post("/v1/agent/speech")
    async def synthesize_speech(
        payload: AgentSpeechRequest,
        _: None = Depends(require_agent_key),
        local_runtime: SupertonicRuntime = Depends(_runtime),
    ) -> Response:
        try:
            compiled = _compiled(payload, local_runtime)
            audio = await run_in_threadpool(local_runtime.synthesize, compiled)
        except (NastechMarkupError, CompactRuntimeError, ValueError) as exc:
            return _error_response(exc)
        return _audio_response(audio, compiled.request_id)

    @app.post("/v1/audio/speech")
    async def openai_compatible_speech(
        payload: OpenAISpeechRequest,
        _: None = Depends(require_agent_key),
        local_runtime: SupertonicRuntime = Depends(_runtime),
    ) -> Response:
        request = AgentSpeechRequest(
            markup=_text_to_markup(payload.input, payload.voice, payload.speed),
            voice=payload.voice,
        )
        try:
            compiled = _compiled(request, local_runtime)
            audio = await run_in_threadpool(local_runtime.synthesize, compiled)
        except (NastechMarkupError, CompactRuntimeError, ValueError) as exc:
            return _error_response(exc)
        return _audio_response(audio, compiled.request_id)

    return app


app = create_app()
