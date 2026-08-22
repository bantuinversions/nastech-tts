"""Nastech Voice Core public local-runtime interface.

Use this module for Nastech TTS integrations. It presents the stable Nastech
Voice Core identity while preserving the existing local runtime implementation.
"""

from .supertonic import (
    CompactAudio,
    CompactCompiledRequest,
    CompactRuntimeError,
    CompactSettings,
    SupertonicRuntime,
    compile_nastechml,
)

NastechVoiceCoreRuntime = SupertonicRuntime

__all__ = [
    "CompactAudio",
    "CompactCompiledRequest",
    "CompactRuntimeError",
    "CompactSettings",
    "NastechVoiceCoreRuntime",
    "compile_nastechml",
]
