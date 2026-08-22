"""Local HTTP server for Nastech Voice Core TTS.

This subpackage is optional. It depends on ``fastapi``, ``uvicorn``, and
``python-multipart`` which install via the ``[serve]`` extra:

    pip install supertonic[serve]

It exposes a thin FastAPI wrapper around :class:`supertonic.pipeline.TTS`
designed for local-only integration with n8n, browser extensions, Electron,
Unity, Home Assistant, robotics devices, and any client that already speaks the
OpenAI Audio Speech API.

Public surface:

* :func:`create_app` — build a FastAPI ASGI app (model loads in lifespan).
* :class:`ServerState` — shared runtime state if you need to inject a
  pre-loaded ``TTS`` (e.g. tests).
* :data:`__all__` listed below.
"""

from .app import ServerState, create_app

__all__ = ["create_app", "ServerState"]
