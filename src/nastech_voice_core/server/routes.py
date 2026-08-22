"""HTTP route handlers for ``supertonic serve``.

The route surface is intentionally narrow and follows two conventions so that
existing clients work with minimal changes:

1. **Native namespace** under ``/v1/...`` for first-class Nastech Voice Core features.
2. **OpenAI Audio Speech alias** at ``POST /v1/audio/speech`` so any client
   that already speaks the OpenAI API (n8n OpenAI node, openai-python, many
   browser extensions, Electron tools) can swap the base URL.

Errors use the OpenAI-shaped envelope::

    { "error": { "message": "...", "type": "...", "code": "..." } }

so that downstream error parsers keep working.
"""

from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

import numpy as np
from fastapi import APIRouter, FastAPI, File, Form, Request, Response, UploadFile
from fastapi.responses import JSONResponse

from .. import __version__
from ..config import AVAILABLE_LANGUAGES
from . import styles_store
from .audio import (
    SUPPORTED_FORMATS,
    UnsupportedAudioFormat,
    coerce_response_format,
    duration_seconds,
    encode_audio,
    format_to_mime,
)
from .schemas import (
    BatchRequest,
    BatchResponse,
    BatchResultItem,
    ErrorDetail,
    ErrorEnvelope,
    HealthResponse,
    OpenAISpeechRequest,
    StyleImportResponse,
    StyleInfo,
    StylesResponse,
    TTSRequest,
)

if TYPE_CHECKING:
    from .app import ServerState

logger = logging.getLogger(__name__)


# Maximum body size accepted by ``POST /v1/styles/import``. The bundled
# voice-style JSONs are ~290 kB; 1 MiB leaves comfortable headroom while
# bounding any single request's memory footprint. Enforced twice:
#
# 1. as a middleware-level ``Content-Length`` pre-flight check (so an
#    oversized request is rejected before the body is buffered), and
# 2. inside the import handler via ``file.read(MAX+1)`` (a fallback for
#    chunked transfer encoding where ``Content-Length`` is absent).
MAX_STYLE_IMPORT_BYTES = 1 * 1024 * 1024


class UnknownVoice(LookupError):
    """Voice name does not match any built-in or imported style."""


def _state(request: Request) -> "ServerState":
    return request.app.state.server_state  # type: ignore[no-any-return]


def _error(status_code: int, message: str, code: str, type_: str = "invalid_request_error"):
    env = ErrorEnvelope(error=ErrorDetail(message=message, type=type_, code=code))
    return JSONResponse(status_code=status_code, content=env.model_dump())


def _resolve_voice(state: "ServerState", voice_name: str):
    """Return a ``Style`` for ``voice_name`` from built-ins or imported custom styles.

    Built-ins are checked first; this is structurally equivalent to checking
    custom first because :func:`styles_store.save` refuses to write a custom
    name that collides with the model's built-ins.
    """
    tts = state.tts
    if tts is None:
        raise RuntimeError("server not ready")  # caller maps to 503
    if voice_name in tts.voice_style_names:
        return tts.get_voice_style(voice_name)
    custom_path = state.custom_styles.get(voice_name)
    if custom_path is not None:
        return tts.get_voice_style_from_path(custom_path)
    raise UnknownVoice(voice_name)


def _do_synthesize(
    state: "ServerState",
    *,
    text: str,
    voice: str,
    lang: Optional[str],
    speed: Optional[float],
    steps: Optional[int],
    max_chunk_length: Optional[int],
    silence_duration: Optional[float],
) -> tuple[np.ndarray, float]:
    """Resolve voice, take the synth lock, run synthesize, return (wav, duration_s)."""
    style = _resolve_voice(state, voice)
    kwargs: dict[str, Any] = {"voice_style": style}
    if speed is not None:
        kwargs["speed"] = speed
    if steps is not None:
        kwargs["total_steps"] = steps
    if max_chunk_length is not None:
        kwargs["max_chunk_length"] = max_chunk_length
    if silence_duration is not None:
        kwargs["silence_duration"] = silence_duration
    if lang is not None:
        kwargs["lang"] = lang

    # ONNX Runtime sessions are not guaranteed safe under concurrent calls
    # from threads. FastAPI executes our sync handlers in a threadpool, so we
    # serialize here. Within-process throughput is bounded by one synth at a
    # time — that's the right trade-off for a local helper.
    with state.synth_lock:
        wav, _ = state.tts.synthesize(text=text, **kwargs)

    return wav, duration_seconds(wav, state.tts.sample_rate)


def _audio_response(state: "ServerState", wav: np.ndarray, fmt: str, duration_s: float) -> Response:
    body = encode_audio(wav, state.tts.sample_rate, fmt)
    return Response(
        content=body,
        media_type=format_to_mime(fmt),
        headers={
            "X-Audio-Duration": f"{duration_s:.3f}",
            "X-Nastech Voice Core-Version": __version__,
            "X-Sample-Rate": str(state.tts.sample_rate),
        },
    )


def _validate_lang(lang: Optional[str]):
    if lang is not None and lang not in AVAILABLE_LANGUAGES:
        return _error(
            400,
            f"unsupported lang {lang!r}; valid: {', '.join(AVAILABLE_LANGUAGES)}",
            "unsupported_lang",
        )
    return None


def register_routes(app: FastAPI) -> None:
    """Attach all `/v1/...` routes to ``app``.

    Called from :func:`supertonic.server.app.create_app` after the lifespan and
    ``app.state.server_state`` have been set up.
    """
    router = APIRouter()

    @router.get("/v1/health", response_model=HealthResponse)
    def health(request: Request):
        state = _state(request)
        if not state.is_ready or state.tts is None:
            return JSONResponse(
                status_code=503,
                content=HealthResponse(
                    status="loading",
                    model=state.model,
                    version=__version__,
                    voices_loaded=0,
                ).model_dump(),
            )
        return HealthResponse(
            status="ok",
            model=state.model,
            sample_rate=state.tts.sample_rate,
            version=__version__,
            voices_loaded=len(state.tts.voice_style_names) + len(state.custom_styles),
        )

    @router.get("/v1/styles", response_model=StylesResponse)
    def list_styles(request: Request):
        state = _state(request)
        if state.tts is None:
            return _error(503, "server not ready", "not_ready", type_="server_error")
        builtin = [StyleInfo(name=n, kind="builtin") for n in state.tts.voice_style_names]
        custom = [
            StyleInfo(name=n, kind="custom", path=str(p))
            for n, p in sorted(state.custom_styles.items())
        ]
        return StylesResponse(styles=builtin + custom)

    @router.post("/v1/styles/import", response_model=StyleImportResponse)
    async def import_style(
        request: Request,
        overwrite: bool = False,
        file: Optional[UploadFile] = File(None),
        name: Optional[str] = Form(None),
    ):
        state = _state(request)
        if state.tts is None:
            return _error(503, "server not ready", "not_ready", type_="server_error")

        ct = request.headers.get("content-type", "")
        chosen_name: Optional[str]
        if ct.startswith("multipart/form-data"):
            if file is None:
                return _error(400, "missing 'file' part", "missing_file")
            # Read with an explicit cap as a fallback for chunked uploads
            # that bypass the middleware's Content-Length pre-flight check.
            raw = await file.read(MAX_STYLE_IMPORT_BYTES + 1)
            if len(raw) > MAX_STYLE_IMPORT_BYTES:
                return _error(
                    413,
                    f"uploaded voice style exceeds {MAX_STYLE_IMPORT_BYTES} bytes",
                    "payload_too_large",
                )
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                return _error(400, f"invalid JSON in uploaded file: {e}", "invalid_json")
            chosen_name = name or Path(file.filename or "").stem or "imported"
        else:
            try:
                body = await request.json()
            except json.JSONDecodeError:
                return _error(400, "invalid JSON body", "invalid_json")
            if not isinstance(body, dict):
                return _error(400, "JSON body must be an object", "invalid_body")
            chosen_name = body.get("name")
            if not chosen_name:
                return _error(400, "missing 'name' in JSON body", "missing_name")
            data = {k: body[k] for k in ("style_ttl", "style_dp") if k in body}

        try:
            target = styles_store.save(
                state.custom_styles_dir,
                chosen_name,
                data,
                builtin_names=state.tts.voice_style_names,
                overwrite=overwrite,
            )
        except styles_store.InvalidStyleName as e:
            return _error(400, str(e), "invalid_style_name")
        except styles_store.StyleNameConflict as e:
            status = 409 if "already exists" in str(e) else 400
            return _error(status, str(e), "style_name_conflict")
        except ValueError as e:
            return _error(400, str(e), "invalid_style_payload")

        state.custom_styles[target.stem] = target
        return StyleImportResponse(name=target.stem, stored_at=str(target))

    @router.post("/v1/tts")
    def synth_native(req: TTSRequest, request: Request):
        state = _state(request)
        if state.tts is None:
            return _error(503, "server not ready", "not_ready", type_="server_error")
        try:
            fmt = coerce_response_format(req.response_format)
        except UnsupportedAudioFormat as e:
            return _error(
                400,
                f"unsupported response_format {str(e)!r}",
                "unsupported_response_format",
            )
        err = _validate_lang(req.lang)
        if err is not None:
            return err
        try:
            wav, dur = _do_synthesize(
                state,
                text=req.text,
                voice=req.voice,
                lang=req.lang,
                speed=req.speed,
                steps=req.steps,
                max_chunk_length=req.max_chunk_length,
                silence_duration=req.silence_duration,
            )
        except UnknownVoice as e:
            return _error(400, f"unknown voice {str(e)!r}", "unknown_voice")
        except Exception as e:  # noqa: BLE001 — surface as 500 with code
            logger.exception("synthesis failed")
            return _error(500, f"synthesis failed: {e}", "synthesis_failed", type_="server_error")
        return _audio_response(state, wav, fmt, dur)

    @router.post("/v1/audio/speech")
    def openai_compat_speech(req: OpenAISpeechRequest, request: Request):
        # Validate ``model`` against AVAILABLE_MODELS but only *accept* the
        # model currently loaded — switching at request time is out of scope.
        state = _state(request)
        if req.model not in OpenAISpeechRequest.valid_models():
            return _error(
                400,
                f"unknown model {req.model!r}; valid: {', '.join(OpenAISpeechRequest.valid_models())}",
                "unknown_model",
            )
        if req.model != state.model:
            return _error(
                400,
                f"this server serves {state.model!r}; request asked for {req.model!r}. "
                f"Restart with --model {req.model} to switch.",
                "model_not_loaded",
            )
        if state.tts is None:
            return _error(503, "server not ready", "not_ready", type_="server_error")
        # OpenAI clients default to ``response_format='mp3'`` — surface a
        # clear error rather than silently emitting WAV.
        try:
            fmt = coerce_response_format(req.response_format)
        except UnsupportedAudioFormat as e:
            return _error(
                400,
                f"unsupported response_format {str(e)!r}; "
                f"set response_format to one of: {', '.join(SUPPORTED_FORMATS)}",
                "unsupported_response_format",
            )
        err = _validate_lang(req.lang)
        if err is not None:
            return err
        try:
            wav, dur = _do_synthesize(
                state,
                text=req.input,
                voice=req.voice,
                lang=req.lang,
                speed=req.speed,
                steps=None,
                max_chunk_length=None,
                silence_duration=None,
            )
        except UnknownVoice as e:
            return _error(400, f"unknown voice {str(e)!r}", "unknown_voice")
        except Exception as e:  # noqa: BLE001
            logger.exception("synthesis failed")
            return _error(500, f"synthesis failed: {e}", "synthesis_failed", type_="server_error")
        return _audio_response(state, wav, fmt, dur)

    @router.post("/v1/tts/batch", response_model=BatchResponse)
    def synth_batch(req: BatchRequest, request: Request):
        state = _state(request)
        if state.tts is None:
            return _error(503, "server not ready", "not_ready", type_="server_error")
        try:
            fmt = coerce_response_format(req.response_format)
        except UnsupportedAudioFormat as e:
            return _error(
                400,
                f"unsupported response_format {str(e)!r}",
                "unsupported_response_format",
            )
        defaults = req.defaults
        results: list[BatchResultItem] = []
        for idx, item in enumerate(req.items):
            voice = item.voice or (defaults.voice if defaults else None) or "M1"
            lang = item.lang or (defaults.lang if defaults else None)
            speed = item.speed if item.speed is not None else (defaults.speed if defaults else None)
            steps = item.steps if item.steps is not None else (defaults.steps if defaults else None)
            mcl = (
                item.max_chunk_length
                if item.max_chunk_length is not None
                else (defaults.max_chunk_length if defaults else None)
            )
            sil = (
                item.silence_duration
                if item.silence_duration is not None
                else (defaults.silence_duration if defaults else None)
            )
            if lang is not None and lang not in AVAILABLE_LANGUAGES:
                return _error(
                    400,
                    f"items[{idx}].lang: unsupported lang {lang!r}",
                    "unsupported_lang",
                )
            try:
                wav, dur = _do_synthesize(
                    state,
                    text=item.text,
                    voice=voice,
                    lang=lang,
                    speed=speed,
                    steps=steps,
                    max_chunk_length=mcl,
                    silence_duration=sil,
                )
            except UnknownVoice as e:
                return _error(
                    400,
                    f"items[{idx}]: unknown voice {str(e)!r}",
                    "unknown_voice",
                )
            except Exception as e:  # noqa: BLE001
                logger.exception("batch item %d synthesis failed", idx)
                return _error(
                    500,
                    f"items[{idx}]: synthesis failed: {e}",
                    "synthesis_failed",
                    type_="server_error",
                )
            body = encode_audio(wav, state.tts.sample_rate, fmt)
            results.append(
                BatchResultItem(
                    audio_base64=base64.b64encode(body).decode("ascii"),
                    duration_s=dur,
                    format=fmt,
                    sample_rate=state.tts.sample_rate,
                )
            )
        return BatchResponse(items=results)

    app.include_router(router)
