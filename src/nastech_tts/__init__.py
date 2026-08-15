"""Nastech Compact: local-first English expressive TTS with a provider mixer."""

from .cpu import CpuConfigurationError, CpuTuning
from .markup import NastechMarkupError, parse_nastechml
from .providers import (
    ProviderActivationError,
    get_provider,
    list_providers,
    provider_inventory,
    provider_preflight,
    require_active_provider,
)
from .supertonic import (
    CompactAudio,
    CompactCompiledRequest,
    CompactRuntimeError,
    CompactSettings,
    SupertonicRuntime,
    compile_nastechml,
)

NastechLocalRuntime = SupertonicRuntime

__all__ = [
    "CompactAudio",
    "CpuConfigurationError",
    "CpuTuning",
    "CompactCompiledRequest",
    "CompactRuntimeError",
    "CompactSettings",
    "NastechLocalRuntime",
    "NastechMarkupError",
    "ProviderActivationError",
    "SupertonicRuntime",
    "compile_nastechml",
    "get_provider",
    "list_providers",
    "provider_inventory",
    "provider_preflight",
    "require_active_provider",
    "parse_nastechml",
]

__version__ = "0.9.1"
