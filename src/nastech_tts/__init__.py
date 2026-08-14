"""Nastech TTS: agent-ready expressive speech control for Fish Audio S2."""

from .fish import (
    CompiledRequest,
    FishHttpProvider,
    NastechGateway,
    ProviderError,
    ProviderSettings,
    build_gateway_from_env,
    compile_nastechml,
)
from .markup import NastechMarkupError, parse_nastechml

__all__ = [
    "CompiledRequest",
    "FishHttpProvider",
    "NastechGateway",
    "NastechMarkupError",
    "ProviderError",
    "ProviderSettings",
    "build_gateway_from_env",
    "compile_nastechml",
    "parse_nastechml",
]

__version__ = "0.3.0"
