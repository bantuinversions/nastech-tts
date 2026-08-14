"""Nastech Compact: local English expressive TTS powered by Supertonic ONNX."""

from .markup import NastechMarkupError, parse_nastechml
from .supertonic import (
    CompactAudio,
    CompactCompiledRequest,
    CompactRuntimeError,
    CompactSettings,
    SupertonicRuntime,
    compile_nastechml,
)

__all__ = [
    "CompactAudio",
    "CompactCompiledRequest",
    "CompactRuntimeError",
    "CompactSettings",
    "NastechMarkupError",
    "SupertonicRuntime",
    "compile_nastechml",
    "parse_nastechml",
]

__version__ = "0.4.0"
