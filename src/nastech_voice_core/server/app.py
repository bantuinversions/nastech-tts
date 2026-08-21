"""FastAPI application factory for ``supertonic serve``.

Designed so that:

* ``cmd_serve`` builds the app, uvicorn drives it.
* Tests can inject a pre-built :class:`ServerState` (with a fake ``TTS``) so
  no real ONNX session is created.
* Anyone embedding the server inside a larger ASGI app can mount the
  ``FastAPI`` returned by :func:`create_app`.
"""

from __future__ import annotations

import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Iterable, Optional, TYPE_CHECKING

from fastapi import FastAPI

from .. import __version__
from ..config import DEFAULT_MODEL
from . import styles_store
from .routes import MAX_STYLE_IMPORT_BYTES, register_routes
from .schemas import ErrorDetail, ErrorEnvelope

if TYPE_CHECKING:
    from ..pipeline import TTS

logger = logging.getLogger(__name__)


# Apply the size pre-flight to /v1/styles/import only — every other route
# either takes small JSON bodies or returns audio (no large request body).
_SIZE_LIMITED_PATHS = ("/v1/styles/import",)


class StyleImportSizeLimit:
    """ASGI middleware: reject ``POST /v1/styles/import`` when the request
    ``Content-Length`` exceeds :data:`MAX_STYLE_IMPORT_BYTES`.

    The check runs *before* FastAPI's dependency machinery starts buffering
    the multipart body, so a malicious or accidental oversized upload is
    rejected at the headers stage. Requests without ``Content-Length``
    (chunked transfer encoding) fall through; the handler's ``read(MAX+1)``
    enforces the same cap there.
    """

    def __init__(self, app, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        if scope["method"] != "POST" or scope["path"] not in _SIZE_LIMITED_PATHS:
            return await self.app(scope, receive, send)

        cl_raw: Optional[bytes] = None
        for name, value in scope["headers"]:
            if name == b"content-length":
                cl_raw = value
                break
        if cl_raw is None:
            # Chunked transfer encoding — no header pre-flight possible.
            return await self.app(scope, receive, send)

        try:
            cl = int(cl_raw)
        except ValueError:
            return await self._send_error(
                send, 400, "invalid Content-Length header", "invalid_content_length"
            )
        if cl > self.max_bytes:
            return await self._send_error(
                send,
                413,
                f"Content-Length {cl} exceeds {self.max_bytes} bytes",
                "payload_too_large",
            )
        return await self.app(scope, receive, send)

    @staticmethod
    async def _send_error(send, status: int, message: str, code: str) -> None:
        envelope = ErrorEnvelope(
            error=ErrorDetail(message=message, type="invalid_request_error", code=code)
        )
        body = envelope.model_dump_json().encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})


class ServerState:
    """Mutable shared state used by every request handler.

    Attributes:
        model: Model name to load (e.g. ``"supertonic-3"``).
        tts: Loaded :class:`supertonic.TTS` instance, ``None`` until the
            lifespan finishes.
        custom_styles: ``{stem: path}`` for user-imported style JSONs.
        custom_styles_dir: Directory on disk that backs ``custom_styles``.
        synth_lock: Serializes ONNX Runtime inference across threads (FastAPI
            executes sync handlers in a threadpool).
        is_ready: ``True`` once the lifespan has finished initialization.
    """

    __slots__ = (
        "model",
        "tts",
        "custom_styles",
        "custom_styles_dir",
        "synth_lock",
        "is_ready",
    )

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        *,
        tts: Optional["TTS"] = None,
        custom_styles_dir: Optional[Path] = None,
        custom_styles: Optional[Dict[str, Path]] = None,
    ) -> None:
        self.model = model
        self.tts = tts
        # Custom styles default to the *model's* cache dir, so the same name
        # cannot collide across model versions.
        self.custom_styles_dir = (
            Path(custom_styles_dir)
            if custom_styles_dir
            else styles_store.default_custom_styles_dir(model)
        )
        self.custom_styles = dict(custom_styles or {})
        self.synth_lock = threading.Lock()
        self.is_ready = False


def create_app(
    *,
    state: Optional[ServerState] = None,
    model: str = DEFAULT_MODEL,
    custom_styles_dir: Optional[Path] = None,
    cors_origins: Optional[Iterable[str]] = None,
) -> FastAPI:
    """Build a configured FastAPI app.

    Args:
        state: Pre-built state to reuse. When provided, the lifespan does *not*
            instantiate :class:`supertonic.TTS` — useful for tests that inject
            a fake. Pass ``None`` for normal use.
        model: Model name to load if ``state.tts`` is ``None``.
        custom_styles_dir: Override the on-disk location of user-imported
            voice styles. Defaults to
            :func:`supertonic.server.styles_store.default_custom_styles_dir`.
        cors_origins: If non-empty, install ``CORSMiddleware`` for these
            origins. Browser-extension or Electron clients need this; n8n and
            curl do not.
    """
    if state is None:
        state = ServerState(model=model, custom_styles_dir=custom_styles_dir)
    elif custom_styles_dir is not None:
        state.custom_styles_dir = Path(custom_styles_dir)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if state.tts is None:
            # Import here so that ``supertonic.server`` import does not pull
            # the model loader into hot paths or test harnesses that mock it.
            from ..pipeline import TTS

            logger.info("Loading TTS model %r ...", state.model)
            state.tts = TTS(model=state.model)
        state.custom_styles = styles_store.scan(state.custom_styles_dir)
        state.is_ready = True
        logger.info(
            "supertonic serve ready: model=%s builtin=%d custom=%d",
            state.model,
            len(state.tts.voice_style_names) if state.tts else 0,
            len(state.custom_styles),
        )
        try:
            yield
        finally:
            state.is_ready = False

    app = FastAPI(
        title="Nastech Voice Core TTS",
        description=(
            "Local HTTP server for Nastech Voice Core TTS. Exposes a native /v1/* "
            "namespace plus an OpenAI Audio Speech-compatible alias at "
            "POST /v1/audio/speech so existing clients work with just a "
            "base-URL change."
        ),
        version=__version__,
        lifespan=lifespan,
    )
    app.state.server_state = state

    # Note: middlewares execute in reverse order of addition (the *last*
    # added wraps everything below it). Add the size limit last so it
    # short-circuits before FastAPI's routing/dependency layers start
    # buffering the multipart body.
    if cors_origins:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(cors_origins),
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.add_middleware(StyleImportSizeLimit, max_bytes=MAX_STYLE_IMPORT_BYTES)

    register_routes(app)
    return app
