"""Nastech Compact: local-first expressive TTS with a multilingual provider mixer."""

from .cpu import CpuConfigurationError, CpuTuning
from .hardware import HardwareConfigurationError, HardwarePlan
from .languages import LanguageRegistryError, get_language, language_inventory
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
    "HardwareConfigurationError",
    "HardwarePlan",
    "CompactCompiledRequest",
    "CompactRuntimeError",
    "CompactSettings",
    "NastechLocalRuntime",
    "NastechMarkupError",
    "LanguageRegistryError",
    "ProviderActivationError",
    "SupertonicRuntime",
    "compile_nastechml",
    "get_language",
    "get_provider",
    "language_inventory",
    "list_providers",
    "provider_inventory",
    "provider_preflight",
    "require_active_provider",
    "parse_nastechml",
]

__version__ = "0.12.2"
