"""Pydantic request/response schemas for the local TTS server.

The wire format mirrors common TTS-server conventions so existing clients
(n8n HTTP nodes, openedai-speech-compatible browser extensions, OpenAI SDKs)
can talk to ``supertonic serve`` with little or no code change.
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ..config import AVAILABLE_MODELS, DEFAULT_MODEL
from .audio import SUPPORTED_FORMATS


class TTSRequest(BaseModel):
    """Native synthesis request — ``POST /v1/tts``."""

    text: str = Field(..., min_length=1, description="Text to synthesize")
    voice: str = Field("M1", description="Voice style name (built-in or imported)")
    lang: Optional[str] = Field(None, description="Language code or 'na' for fallback")
    speed: Optional[float] = Field(None, ge=0.7, le=2.0)
    steps: Optional[int] = Field(None, ge=1, le=100)
    max_chunk_length: Optional[int] = Field(None, ge=1, le=10000)
    silence_duration: Optional[float] = Field(None, ge=0.0, le=10.0)
    response_format: Optional[str] = Field(
        None, description=f"One of: {', '.join(SUPPORTED_FORMATS)}"
    )


class OpenAISpeechRequest(BaseModel):
    """OpenAI Audio Speech-compatible request — ``POST /v1/audio/speech``.

    Field names match the OpenAI API so existing clients (n8n's OpenAI node,
    openai-python, openedai-speech-style browser extensions) only need to
    swap the base URL.
    """

    model: str = Field(..., description="Model name (must match the loaded model)")
    input: str = Field(..., min_length=1, description="Text to synthesize")
    voice: str = Field("M1", description="Voice style name")
    response_format: Optional[str] = Field(None)
    speed: Optional[float] = Field(None, ge=0.7, le=2.0)
    # Nastech Voice Core-specific extension fields are accepted but optional — clients
    # that only know OpenAI will simply not send them.
    lang: Optional[str] = Field(None)

    @classmethod
    def valid_models(cls) -> tuple[str, ...]:
        return tuple(AVAILABLE_MODELS)


class BatchItem(BaseModel):
    text: str = Field(..., min_length=1)
    voice: str = Field("M1")
    lang: Optional[str] = None
    speed: Optional[float] = Field(None, ge=0.7, le=2.0)
    steps: Optional[int] = Field(None, ge=1, le=100)
    max_chunk_length: Optional[int] = Field(None, ge=1, le=10000)
    silence_duration: Optional[float] = Field(None, ge=0.0, le=10.0)


class BatchDefaults(BaseModel):
    voice: Optional[str] = None
    lang: Optional[str] = None
    speed: Optional[float] = Field(None, ge=0.7, le=2.0)
    steps: Optional[int] = Field(None, ge=1, le=100)
    max_chunk_length: Optional[int] = Field(None, ge=1, le=10000)
    silence_duration: Optional[float] = Field(None, ge=0.0, le=10.0)


class BatchRequest(BaseModel):
    items: List[BatchItem] = Field(..., min_length=1, max_length=64)
    response_format: Optional[str] = None
    defaults: Optional[BatchDefaults] = None


class BatchResultItem(BaseModel):
    audio_base64: str
    duration_s: float
    format: str
    sample_rate: int


class BatchResponse(BaseModel):
    items: List[BatchResultItem]


class StyleInfo(BaseModel):
    name: str
    kind: Literal["builtin", "custom"]
    path: Optional[str] = None


class StylesResponse(BaseModel):
    styles: List[StyleInfo]


class StyleImportJSON(BaseModel):
    """JSON-body variant of ``POST /v1/styles/import``.

    The endpoint also accepts ``multipart/form-data`` with a ``file`` field;
    that path bypasses this schema and is handled directly in the route.
    """

    name: str
    style_ttl: dict
    style_dp: dict


class StyleImportResponse(BaseModel):
    name: str
    stored_at: str


class HealthResponse(BaseModel):
    status: Literal["ok", "loading"]
    model: str = DEFAULT_MODEL
    sample_rate: Optional[int] = None
    version: str
    voices_loaded: int = 0


class ErrorDetail(BaseModel):
    message: str
    type: str = "invalid_request_error"
    code: Optional[str] = None


class ErrorEnvelope(BaseModel):
    """OpenAI-shaped error envelope so integrators can reuse existing parsers."""

    error: ErrorDetail
