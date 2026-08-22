"""Nastech TTS provider registry and safe provider-selection policy.

The registry is intentionally declarative. A catalog entry is not an installed
model, a live credential, or a claim of supported deployment. Only entries in
``active/local`` state may receive a synthesis request; all other entries return
a deterministic preflight plan instead of downloading software or making a
network request.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from .languages import MMS_LAZY_CODES

ACTIVE_LOCAL = "active/local"
ADAPTER_AVAILABLE = "adapter/available"
LICENSE_REVIEW = "planned/license-review"
CREDENTIAL_REQUIRED = "planned/credential-required"


class ProviderActivationError(ValueError):
    """Raised when a provider is unknown or is not eligible for synthesis."""


@dataclass(frozen=True)
class ProviderDefinition:
    """One provider integration target in the Nastech catalog."""

    id: str
    label: str
    route_type: str
    state: str
    supports_english: bool
    language_codes: tuple[str, ...]
    activation_boundary: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _provider(
    provider_id: str,
    label: str,
    route_type: str,
    state: str,
    activation_boundary: str,
    language_codes: tuple[str, ...] = ("en",),
) -> ProviderDefinition:
    return ProviderDefinition(
        id=provider_id,
        label=label,
        route_type=route_type,
        state=state,
        supports_english="en" in language_codes,
        language_codes=language_codes,
        activation_boundary=activation_boundary,
    )


_PROVIDER_ROWS = (
    _provider(
        "nastech-native-onnx",
        "Nastech Voice Core (local ONNX)",
        "local-python",
        ACTIVE_LOCAL,
        "Included in the measured local Nastech TTS core.",
    ),
    _provider(
        "mms-lazy",
        "MMS per-language lazy local pack",
        "local-python",
        ACTIVE_LOCAL,
        (
            "Explicitly select a language; download only that pack into the external cache, "
            "load one model at a time, and retain CC-BY-NC-4.0 restrictions."
        ),
        tuple(sorted(MMS_LAZY_CODES)),
    ),
    _provider(
        "kokoro-local",
        "Kokoro local",
        "local-python",
        ADAPTER_AVAILABLE,
        "Install separately and measure the combined runtime and model assets.",
    ),
    _provider(
        "piper-native",
        "Piper native",
        "local-command",
        ADAPTER_AVAILABLE,
        "Pin a binary and an approved voice model with its own licence evidence.",
    ),
    _provider(
        "coqui-cli",
        "Coqui-compatible local command",
        "local-command",
        ADAPTER_AVAILABLE,
        "Use a separately managed compatible environment, executable, and model.",
    ),
    _provider(
        "coqui-luganda-openbible",
        "Luganda OpenBible VITS local pack",
        "local-command",
        ADAPTER_AVAILABLE,
        (
            "Install the reviewed isolated Luganda VITS environment, select an approved "
            "training-set speaker, preserve CC-BY-SA attribution, and complete native review."
        ),
        ("lg",),
    ),
    _provider(
        "mms-luganda-eval",
        "MMS Luganda evaluation pack",
        "local-python",
        LICENSE_REVIEW,
        "CC-BY-NC-4.0 model; non-commercial evaluation only until separately reviewed.",
        ("lg",),
    ),
    _provider(
        "mms-shona-eval",
        "MMS Shona evaluation pack",
        "local-python",
        LICENSE_REVIEW,
        "CC-BY-NC-4.0 model; non-commercial evaluation only until separately reviewed.",
        ("sn",),
    ),
    _provider(
        "mms-kinyarwanda-eval",
        "MMS Kinyarwanda evaluation pack",
        "local-python",
        LICENSE_REVIEW,
        "CC-BY-NC-4.0 model; non-commercial evaluation only until separately reviewed.",
        ("rw",),
    ),
    _provider(
        "mms-kirundi-eval",
        "MMS Kirundi evaluation pack",
        "local-python",
        LICENSE_REVIEW,
        "CC-BY-NC-4.0 model; non-commercial evaluation only until separately reviewed.",
        ("rn",),
    ),
    _provider(
        "mms-gikuyu-eval",
        "MMS Gikuyu evaluation pack",
        "local-python",
        LICENSE_REVIEW,
        "CC-BY-NC-4.0 model; non-commercial evaluation only until separately reviewed.",
        ("ki",),
    ),
    _provider(
        "mms-chichewa-eval",
        "MMS Chichewa evaluation pack",
        "local-python",
        LICENSE_REVIEW,
        "CC-BY-NC-4.0 model; non-commercial evaluation only until separately reviewed.",
        ("ny",),
    ),
    _provider(
        "mms-tsonga-eval",
        "MMS Xitsonga evaluation pack",
        "local-python",
        LICENSE_REVIEW,
        "CC-BY-NC-4.0 model; non-commercial evaluation only until separately reviewed.",
        ("ts",),
    ),
    _provider(
        "usoal-orpheus-luganda-family",
        "USOAL Ugandan language optional pack",
        "local-command",
        LICENSE_REVIEW,
        (
            "Review the 3B model pack licence, runtime, resource profile, and native language "
            "fixtures before enabling Runyankole, Acholi, or Ateso."
        ),
        ("nyn", "ach", "teo"),
    ),
    _provider(
        "coqui-python",
        "Coqui-compatible Python",
        "local-python",
        ADAPTER_AVAILABLE,
        "Use an isolated compatible Python environment and a named reviewed model.",
    ),
    _provider(
        "coqui-server",
        "Coqui-compatible local HTTP",
        "local-http",
        ADAPTER_AVAILABLE,
        "Configure an existing loopback endpoint; Nastech never starts it automatically.",
    ),
    _provider(
        "coqui-container",
        "Coqui-compatible local container",
        "local-command",
        ADAPTER_AVAILABLE,
        "Pin an image digest, selected model, and complete deployment budget.",
    ),
    _provider(
        "coqui-xtts-v2",
        "Coqui XTTS v2 profile",
        "local-python",
        LICENSE_REVIEW,
        "Review checkpoint terms, consent, CPU performance, and combined size.",
    ),
    _provider(
        "coqui-yourtts",
        "Coqui YourTTS profile",
        "local-python",
        LICENSE_REVIEW,
        "Review checkpoint terms, consent, CPU performance, and combined size.",
    ),
    _provider(
        "coqui-vits",
        "Coqui VITS profile",
        "local-python",
        LICENSE_REVIEW,
        "Review the exact model, its voice data terms, and quality evidence.",
    ),
    _provider(
        "coqui-fairseq-vits",
        "Coqui Fairseq VITS profile",
        "local-python",
        LICENSE_REVIEW,
        "Review language/model terms, model size, and English acceptance tests.",
    ),
    _provider(
        "coqui-bark",
        "Coqui Bark profile",
        "local-python",
        LICENSE_REVIEW,
        "Review model terms, expressive-output safety, and CPU feasibility.",
    ),
    _provider(
        "coqui-tortoise",
        "Coqui Tortoise profile",
        "local-python",
        LICENSE_REVIEW,
        "Review model terms, latency, and combined deployment measurement.",
    ),
    _provider(
        "melo-local",
        "Melo local",
        "local-python",
        ADAPTER_AVAILABLE,
        "Select and validate the exact English locale and model assets.",
    ),
    _provider(
        "f5-local",
        "F5 local",
        "local-python",
        LICENSE_REVIEW,
        "Review checkpoint licence, resource profile, and local English tests.",
    ),
    _provider(
        "styletts2-local",
        "StyleTTS 2 local",
        "local-python",
        LICENSE_REVIEW,
        "Review model terms, consent, and CPU acceptance evidence.",
    ),
    _provider(
        "chatterbox-local",
        "Chatterbox local",
        "local-python",
        LICENSE_REVIEW,
        "Review checkpoint terms, model size, and local quality evidence.",
    ),
    _provider(
        "parler-local",
        "Parler local",
        "local-python",
        LICENSE_REVIEW,
        "Review checkpoint terms, model size, and local quality evidence.",
    ),
    _provider(
        "fish-speech-local",
        "Fish Speech local",
        "local-python",
        LICENSE_REVIEW,
        "Review checkpoint terms, consent, and local quality evidence.",
    ),
    _provider(
        "openvoice-local",
        "OpenVoice local",
        "local-python",
        LICENSE_REVIEW,
        "Review conversion consent controls, model terms, and CPU evidence.",
    ),
    _provider(
        "cosyvoice-local",
        "CosyVoice local",
        "local-python",
        LICENSE_REVIEW,
        "Review model terms, hardware needs, and combined deployment size.",
    ),
    _provider(
        "gpt-sovits-local",
        "GPT-SoVITS local",
        "local-python",
        LICENSE_REVIEW,
        "Review consent, model terms, and safe reference-audio controls.",
    ),
    _provider(
        "index-tts-local",
        "IndexTTS local",
        "local-python",
        LICENSE_REVIEW,
        "Review model licence, CPU profile, and English acceptance tests.",
    ),
    _provider(
        "qwen3-tts-local",
        "Qwen TTS local",
        "local-python",
        LICENSE_REVIEW,
        "Review checkpoint terms, model size, and local English tests.",
    ),
    _provider(
        "e2-tts-local",
        "E2-TTS local",
        "local-python",
        LICENSE_REVIEW,
        "Review checkpoint terms, model size, consent, and CPU tests.",
    ),
    _provider(
        "bark-local",
        "Bark local",
        "local-python",
        LICENSE_REVIEW,
        "Review model terms, content controls, and CPU feasibility.",
    ),
    _provider(
        "tortoise-local",
        "Tortoise local",
        "local-python",
        LICENSE_REVIEW,
        "Review model terms, latency, and combined deployment size.",
    ),
    _provider(
        "sherpa-onnx-local",
        "Sherpa ONNX local",
        "local-command",
        LICENSE_REVIEW,
        "Review selected model terms and provider-specific ONNX validation.",
    ),
    _provider(
        "rhvoice-local",
        "RHVoice local",
        "local-command",
        LICENSE_REVIEW,
        "Review voice-data terms, packaging, and output-quality evidence.",
    ),
    _provider(
        "mimic3-local",
        "Mimic 3 local",
        "local-http",
        LICENSE_REVIEW,
        "Review the local endpoint, selected voice terms, and version pin.",
    ),
    _provider(
        "marytts-local",
        "MaryTTS local",
        "local-http",
        LICENSE_REVIEW,
        "Review Java runtime, voice-data terms, and endpoint security.",
    ),
    _provider(
        "festival-local",
        "Festival local",
        "local-command",
        LICENSE_REVIEW,
        "Review voice-data terms and position its quality truthfully.",
    ),
    _provider(
        "espeak-ng-local",
        "eSpeak NG local",
        "local-command",
        LICENSE_REVIEW,
        "Review distribution terms and position its quality truthfully.",
    ),
    _provider(
        "openai-speech",
        "OpenAI managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, pricing approval, and disclosure.",
    ),
    _provider(
        "azure-speech",
        "Azure managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, region, and pricing approval.",
    ),
    _provider(
        "google-cloud-tts",
        "Google Cloud managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, service account, and pricing approval.",
    ),
    _provider(
        "aws-polly",
        "AWS Polly",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, region, and pricing approval.",
    ),
    _provider(
        "elevenlabs-tts",
        "ElevenLabs managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, voice rights, and pricing approval.",
    ),
    _provider(
        "cartesia-tts",
        "Cartesia managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, and output acceptance tests.",
    ),
    _provider(
        "deepgram-aura",
        "Deepgram Aura",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, model choice, and pricing approval.",
    ),
    _provider(
        "playht-tts",
        "PlayHT managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, voice terms, and pricing approval.",
    ),
    _provider(
        "resemble-tts",
        "Resemble managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        (
            "Require explicit network opt-in, credential, consented voice source, and pricing "
            "approval."
        ),
    ),
    _provider(
        "murf-tts",
        "Murf managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, voice terms, and pricing approval.",
    ),
    _provider(
        "speechify-tts",
        "Speechify managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, voice terms, and pricing approval.",
    ),
    _provider(
        "lovo-tts",
        "LOVO managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, voice terms, and pricing approval.",
    ),
    _provider(
        "wellsaid-tts",
        "WellSaid managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, voice terms, and pricing approval.",
    ),
    _provider(
        "rime-tts",
        "Rime managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, voice terms, and pricing approval.",
    ),
    _provider(
        "sarvam-tts",
        "Sarvam managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, language fit, and pricing approval.",
    ),
    _provider(
        "inworld-tts",
        "Inworld managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, voice terms, and pricing approval.",
    ),
    _provider(
        "supertone-api",
        "Supertone managed speech",
        "managed-http",
        CREDENTIAL_REQUIRED,
        "Require explicit network opt-in, credential, voice terms, and pricing approval.",
    ),
)

PROVIDER_CATALOG = {provider.id: provider for provider in _PROVIDER_ROWS}
DEFAULT_PROVIDER_ID = "nastech-native-onnx"


def _configured_coqui_adapter() -> Any | None:
    """Return the optional operator-managed local Coqui-compatible adapter."""
    from .coqui_adapter import CoquiCommandAdapter

    return CoquiCommandAdapter.from_env()


def _configured_luganda_adapter() -> Any | None:
    """Return the optional reviewed local Luganda provider adapter."""
    from .luganda_adapter import LugandaCommandAdapter

    return LugandaCommandAdapter.from_env()


def _resolved_provider(provider: ProviderDefinition) -> ProviderDefinition:
    """Apply an explicit local adapter activation without changing catalog membership."""
    if provider.id == "coqui-cli":
        adapter = _configured_coqui_adapter()
        configuration = adapter.preflight() if adapter else {"configured": False}
        if configuration.get("executable_exists") and configuration.get("model_name_configured"):
            return replace(
                provider,
                state=ACTIVE_LOCAL,
                activation_boundary=(
                    "Operator-configured local Coqui-compatible command; verify output and "
                    "combined budget before production use."
                ),
            )
    if provider.id == "coqui-luganda-openbible":
        adapter = _configured_luganda_adapter()
        configuration = adapter.preflight() if adapter else {"configured": False}
        if (
            configuration.get("executable_exists")
            and configuration.get("normalizer_exists")
            and configuration.get("model_id_accepted")
            and configuration.get("speaker_configured")
        ):
            return replace(
                provider,
                state=ACTIVE_LOCAL,
                activation_boundary=(
                    "Operator-configured reviewed Luganda VITS local pack; native language review "
                    "and combined-budget evidence remain required before production promotion."
                ),
            )
    return provider


def list_providers() -> list[dict[str, Any]]:
    """Return all stable provider catalog entries in documented order."""
    return [_resolved_provider(provider).as_dict() for provider in _PROVIDER_ROWS]


def provider_inventory() -> dict[str, Any]:
    """Summarize the catalog without suggesting inactive providers are runnable."""
    states = {
        state: 0 for state in (ACTIVE_LOCAL, ADAPTER_AVAILABLE, LICENSE_REVIEW, CREDENTIAL_REQUIRED)
    }
    for provider in _PROVIDER_ROWS:
        states[_resolved_provider(provider).state] += 1
    return {
        "service": "nastech-tts",
        "provider_catalog_size": len(_PROVIDER_ROWS),
        "default_provider_id": DEFAULT_PROVIDER_ID,
        "network_default": "disabled",
        "states": states,
        "providers": list_providers(),
    }


def get_provider(provider_id: str) -> ProviderDefinition:
    """Look up a provider ID or raise a client-safe error."""
    provider = PROVIDER_CATALOG.get(provider_id)
    if provider is None:
        raise ProviderActivationError(f"Unknown Nastech provider '{provider_id}'.")
    return _resolved_provider(provider)


def require_active_provider(provider_id: str | None) -> ProviderDefinition:
    """Return the requested active local provider without silent fallback."""
    provider = get_provider(provider_id or DEFAULT_PROVIDER_ID)
    if provider.state != ACTIVE_LOCAL:
        raise ProviderActivationError(
            f"Provider '{provider.id}' is {provider.state}; it is not enabled for synthesis. "
            "Use /v1/providers/preflight to view its activation requirements."
        )
    return provider


def require_active_provider_for_language(
    provider_id: str | None, language: str
) -> ProviderDefinition:
    """Require an active provider that explicitly declares the selected language."""
    provider = require_active_provider(provider_id)
    if language not in provider.language_codes:
        supported = ", ".join(provider.language_codes)
        raise ProviderActivationError(
            f"Provider '{provider.id}' does not declare language '{language}'. "
            f"Supported: {supported}."
        )
    return provider


def provider_preflight(provider_id: str) -> dict[str, Any]:
    """Return a zero-side-effect activation plan for one catalog entry."""
    provider = get_provider(provider_id)
    coqui_configuration = None
    if provider.id == "coqui-cli":
        adapter = _configured_coqui_adapter()
        coqui_configuration = adapter.preflight() if adapter else {"configured": False}
    if provider.id == "coqui-luganda-openbible":
        adapter = _configured_luganda_adapter()
        coqui_configuration = adapter.preflight() if adapter else {"configured": False}
    languages = ", ".join(provider.language_codes)
    actions = [
        f"Confirm language-specific test coverage for: {languages}.",
        "Confirm provider-specific output acceptance and native-language review where required.",
    ]
    if provider.state == ACTIVE_LOCAL:
        readiness = "ready-local"
        actions = ["Use this active local provider through the Nastech synthesis endpoints."]
    elif provider.state == ADAPTER_AVAILABLE:
        readiness = "adapter-installation-required"
        actions = [
            "Install or configure the provider outside the Nastech core.",
            "Pin the provider version, model, and model licence.",
            "Measure the combined deployment against the 1 GiB cap.",
            *actions,
        ]
    elif provider.state == LICENSE_REVIEW:
        readiness = "license-and-integration-review-required"
        actions = [
            "Review the code, model, voice-data, and commercial-use terms.",
            "Document consent for any custom voice or reference audio.",
            "Prove local synthesis, quality, resource use, and budget compliance.",
            *actions,
        ]
    else:
        readiness = "credential-and-network-opt-in-required"
        actions = [
            "Explicitly allow network providers in the operator configuration.",
            "Supply a credential through an approved secret mechanism.",
            "Approve provider terms, data handling, costs, and voice rights.",
            "Implement an adapter-specific integration test using a non-sensitive fixture.",
            *actions,
        ]
    result = {
        "provider": provider.as_dict(),
        "readiness": readiness,
        "network_request_made": False,
        "actions": actions,
    }
    if coqui_configuration is not None:
        result["adapter_configuration"] = coqui_configuration
    return result


def synthesize_with_provider(
    provider_id: str | None,
    runtime: Any,
    compiled: Any,
    *,
    language: str = "en",
    use_cache: bool = True,
) -> Any:
    """Synthesize through one selected active provider without fallback routing."""
    provider = require_active_provider_for_language(provider_id, language)
    if provider.id == DEFAULT_PROVIDER_ID:
        if use_cache:
            return runtime.synthesize(compiled)
        return runtime.synthesize(compiled, use_cache=False)
    if provider.id == "mms-lazy":
        from .mms_lazy import synthesize_mms

        return synthesize_mms(language, compiled.text)
    if provider.id == "coqui-cli":
        adapter = _configured_coqui_adapter()
        if adapter is None:
            raise ProviderActivationError("Coqui-compatible adapter is not configured.")
        return adapter.synthesize(compiled)
    if provider.id == "coqui-luganda-openbible":
        adapter = _configured_luganda_adapter()
        if adapter is None:
            raise ProviderActivationError("Luganda OpenBible adapter is not configured.")
        return adapter.synthesize(compiled)
    raise ProviderActivationError(f"Provider '{provider.id}' has no installed adapter.")
