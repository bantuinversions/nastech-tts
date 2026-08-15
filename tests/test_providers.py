import pytest

from nastech_tts.providers import (
    ACTIVE_LOCAL,
    ProviderActivationError,
    get_provider,
    provider_inventory,
    provider_preflight,
    require_active_provider,
)


def test_provider_catalog_has_fifty_nine_nastech_adapter_targets() -> None:
    inventory = provider_inventory()

    assert inventory["provider_catalog_size"] == 59
    assert len(inventory["providers"]) == 59
    assert inventory["default_provider_id"] == "nastech-native-onnx"
    assert inventory["network_default"] == "disabled"
    assert inventory["states"][ACTIVE_LOCAL] == 1


def test_default_provider_is_the_only_active_local_provider() -> None:
    provider = require_active_provider(None)

    assert provider.id == "nastech-native-onnx"
    assert provider.state == ACTIVE_LOCAL


def test_inactive_provider_never_silently_falls_back_to_default() -> None:
    with pytest.raises(ProviderActivationError, match="not enabled for synthesis"):
        require_active_provider("coqui-cli")


def test_provider_preflight_is_explicit_and_does_not_make_network_requests() -> None:
    plan = provider_preflight("coqui-cli")

    assert plan["provider"]["id"] == "coqui-cli"
    assert plan["readiness"] == "adapter-installation-required"
    assert plan["network_request_made"] is False
    assert any("Install or configure" in action for action in plan["actions"])


def test_managed_provider_preflight_requires_network_opt_in_and_credential() -> None:
    plan = provider_preflight("openai-speech")

    assert plan["readiness"] == "credential-and-network-opt-in-required"
    assert plan["network_request_made"] is False
    assert any("credential" in action.lower() for action in plan["actions"])


def test_unknown_provider_is_rejected() -> None:
    with pytest.raises(ProviderActivationError, match="Unknown Nastech provider"):
        get_provider("not-a-provider")


def test_coqui_adapter_becomes_active_only_with_explicit_local_configuration(monkeypatch) -> None:
    monkeypatch.setenv("NASTECH_ENABLE_COQUI_ADAPTER", "1")
    monkeypatch.setenv("NASTECH_COQUI_TTS_COMMAND", "/usr/bin/true")
    monkeypatch.setenv("NASTECH_COQUI_TTS_MODEL", "reviewed-local-model")

    provider = require_active_provider("coqui-cli")
    plan = provider_preflight("coqui-cli")

    assert provider.state == ACTIVE_LOCAL
    assert plan["readiness"] == "ready-local"
    assert plan["network_request_made"] is False
    assert plan["adapter_configuration"] == {
        "configured": True,
        "command_executable": "/usr/bin/true",
        "executable_exists": True,
        "model_name_configured": True,
        "speaker_configured": False,
        "network_request_made": False,
        "output_contract": "mono 16-bit PCM WAV at 44100 Hz",
    }
