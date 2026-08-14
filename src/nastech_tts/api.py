"""Nastech's agent-facing HTTP API for real Fish S2 expressive controls."""

from __future__ import annotations

import html
import os
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .fish import NastechGateway, ProviderError, build_gateway_from_env
from .markup import NastechMarkupError


class AgentCompileRequest(BaseModel):
    """A structured agent request expressed in stable NastechML."""

    markup: str = Field(min_length=1, max_length=12000)
    reference_id: str | list[str] | None = None
    output_format: str = Field(default="wav", pattern="^(wav|mp3|opus|pcm)$")
    sample_rate: int | None = Field(default=44100, ge=8000, le=48000)
    latency: str = Field(default="normal", pattern="^(low|balanced|normal)$")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


class AgentSpeechRequest(AgentCompileRequest):
    """NastechML request that produces a provider audio response."""


class OpenAISpeechRequest(BaseModel):
    """Small OpenAI-compatible request shape for existing agent clients."""

    model: str = "nastech-fish-s2"
    input: str = Field(min_length=1, max_length=12000)
    voice: str | None = None
    response_format: str = Field(default="wav", pattern="^(wav|mp3|opus|pcm)$")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


class AgentToolDescriptor(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]


def _authorization_required() -> bool:
    return bool(os.getenv("NASTECH_API_KEY"))


def require_agent_key(authorization: Annotated[str | None, Header()] = None) -> None:
    """Require bearer auth only when NASTECH_API_KEY has been configured."""
    expected = os.getenv("NASTECH_API_KEY")
    if not expected:
        return
    if authorization != f"Bearer {expected}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid Nastech bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _text_to_markup(text: str, voice: str | None = None, speed: float = 1.0) -> str:
    safe_text = html.escape(text)
    voice_attr = f' voice="{html.escape(voice, quote=True)}"' if voice else ""
    rate = "slow" if speed < 0.93 else "fast" if speed > 1.07 else "normal"
    return f'<speak{voice_attr}><prosody rate="{rate}">{safe_text}</prosody></speak>'


def _compile_options(payload: AgentCompileRequest, traceparent: str | None) -> dict[str, Any]:
    return {
        "reference_id": payload.reference_id,
        "output_format": payload.output_format,
        "sample_rate": payload.sample_rate,
        "latency": payload.latency,
        "temperature": payload.temperature,
        "traceparent": traceparent,
    }


def _gateway(request: Request) -> NastechGateway:
    return request.app.state.gateway


def _error_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, NastechMarkupError):
        code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, ProviderError):
        code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return JSONResponse(status_code=code, content={"detail": str(exc)})


def create_app(gateway: NastechGateway | None = None) -> FastAPI:
    """Create an independently testable FastAPI application."""
    app = FastAPI(
        title="Nastech TTS Agent Gateway",
        version="0.3.0",
        description=(
            "A structured expressive-speech gateway that compiles NastechML to Fish S2 controls. "
            "Use /v1/agent/compile before synthesis when an agent needs auditable provider intent."
        ),
    )
    app.state.gateway = gateway or build_gateway_from_env()

    @app.get("/v1/health")
    async def health(service: NastechGateway = Depends(_gateway)) -> dict[str, Any]:
        provider_health = await service.health()
        return {
            "status": "ok"
            if provider_health.get("status") in {"ok", "configured", "compile_only"}
            else "degraded",
            "service": "nastech-tts",
            "version": "0.3.0",
            "provider_mode": service.provider_mode,
            "provider": provider_health,
            "authentication_required": _authorization_required(),
        }

    @app.get("/v1/capabilities")
    async def capabilities(_: None = Depends(require_agent_key)) -> dict[str, Any]:
        return {
            "language": "en",
            "model_family": "fish-s2",
            "agent_endpoints": ["/v1/agent/compile", "/v1/agent/speech", "/v1/audio/speech"],
            "emotions": [
                "angry",
                "sad",
                "happy",
                "excited",
                "fearful",
                "disgusted",
                "frustrated",
                "calm",
            ],
            "direct_events": ["laugh", "chuckle", "sigh", "gasp", "groan", "cry"],
            "release_dependent_events": ["cough", "sniffle", "yawn"],
            "formats": ["wav", "mp3", "opus", "pcm"],
        }

    @app.get("/v1/agent/tools", response_model=list[AgentToolDescriptor])
    async def agent_tools(_: None = Depends(require_agent_key)) -> list[AgentToolDescriptor]:
        return [
            AgentToolDescriptor(
                name="nastech_compile_speech",
                description=(
                    "Compile English NastechML into an auditable Fish S2 request "
                    "without generating audio."
                ),
                input_schema=AgentCompileRequest.model_json_schema(),
            ),
            AgentToolDescriptor(
                name="nastech_generate_speech",
                description=(
                    "Generate English expressive speech from NastechML through the "
                    "configured Fish S2 provider."
                ),
                input_schema=AgentSpeechRequest.model_json_schema(),
            ),
        ]

    @app.post("/v1/agent/compile")
    async def compile_speech(
        payload: AgentCompileRequest,
        traceparent: Annotated[str | None, Header()] = None,
        _: None = Depends(require_agent_key),
        service: NastechGateway = Depends(_gateway),
    ) -> dict[str, Any]:
        try:
            compiled = service.compile(payload.markup, **_compile_options(payload, traceparent))
        except (NastechMarkupError, ValueError) as exc:
            return _error_response(exc)
        return {
            "request_id": compiled.request_id,
            "provider_mode": service.provider_mode,
            "provider_payload": compiled.provider_payload,
            "manifest": compiled.manifest,
        }

    @app.post("/v1/agent/speech")
    async def synthesize_speech(
        payload: AgentSpeechRequest,
        traceparent: Annotated[str | None, Header()] = None,
        _: None = Depends(require_agent_key),
        service: NastechGateway = Depends(_gateway),
    ) -> Response:
        try:
            audio, compiled = await service.synthesize(
                payload.markup, **_compile_options(payload, traceparent)
            )
        except (NastechMarkupError, ProviderError, ValueError) as exc:
            return _error_response(exc)
        headers = {
            "X-Nastech-Request-Id": compiled.request_id,
            "X-Nastech-Provider": service.provider_mode,
            "X-Nastech-Manifest-Endpoint": "/v1/agent/compile",
        }
        if audio.provider_request_id:
            headers["X-Provider-Request-Id"] = audio.provider_request_id
        return Response(content=audio.data, media_type=audio.content_type, headers=headers)

    @app.post("/v1/audio/speech")
    async def openai_compatible_speech(
        payload: OpenAISpeechRequest,
        traceparent: Annotated[str | None, Header()] = None,
        _: None = Depends(require_agent_key),
        service: NastechGateway = Depends(_gateway),
    ) -> Response:
        markup = _text_to_markup(payload.input, payload.voice, payload.speed)
        request = AgentSpeechRequest(
            markup=markup,
            reference_id=payload.voice,
            output_format=payload.response_format,
        )
        try:
            audio, compiled = await service.synthesize(
                request.markup, **_compile_options(request, traceparent)
            )
        except (NastechMarkupError, ProviderError, ValueError) as exc:
            return _error_response(exc)
        return Response(
            content=audio.data,
            media_type=audio.content_type,
            headers={
                "X-Nastech-Request-Id": compiled.request_id,
                "X-Nastech-Provider": service.provider_mode,
            },
        )

    return app


app = create_app()
