"""Nastech TTS: English expressive speech based on one adaptable Orpheus model family."""

from .markup import NastechMarkupError, parse_nastechml
from .model import NASTECH_ORPHEUS_V1, NastechModelSpec
from .service import NastechService
from .types import RenderManifest, RenderResult

__all__ = [
    "NASTECH_ORPHEUS_V1",
    "NastechMarkupError",
    "NastechModelSpec",
    "NastechService",
    "RenderManifest",
    "RenderResult",
    "parse_nastechml",
]

__version__ = "0.2.0"
