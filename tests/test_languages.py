import pytest

from nastech_tts.languages import (
    ADAPTER_AVAILABLE,
    PLANNED,
    LanguageRegistryError,
    get_language,
    language_inventory,
    require_configured_language,
)
from nastech_tts.markup import parse_nastechml
from nastech_tts.providers import (
    ProviderActivationError,
    get_provider,
    provider_preflight,
    require_active_provider_for_language,
)


def test_bantu_language_inventory_declares_targets_without_false_availability() -> None:
    inventory = language_inventory()
    languages = {language["code"]: language for language in inventory["languages"]}

    assert inventory["default_language"] == "en"
    assert inventory["language_registry_size"] >= 20
    assert languages["lg"]["state"] == ADAPTER_AVAILABLE
    assert languages["zu"]["state"] == PLANNED
    assert languages["xh"]["state"] == PLANNED
    assert languages["tn"]["label"] == "Setswana"
    assert languages["sn"]["label"] == "Shona"
    assert languages["ve"]["label"] == "Tshivenda"


def test_language_aliases_and_disabled_pack_boundary_are_explicit() -> None:
    assert get_language("lug").code == "lg"
    assert get_language("Luganda").iso639_3 == "lug"
    assert get_language("Zulu").code == "zu"

    with pytest.raises(LanguageRegistryError, match="not enabled"):
        require_configured_language("lg")


def test_native_luganda_text_requires_explicit_language_selection() -> None:
    markup = "<speak>Nze njagala okwogera Luganda mu ngeri entuufu.</speak>"

    voice, spans = parse_nastechml(markup, language="lg")

    assert voice == "tara"
    assert spans[0].value == "Nze njagala okwogera Luganda mu ngeri entuufu."
    english_voice, english_spans = parse_nastechml(markup, language="en")
    assert english_voice == "tara"
    assert english_spans[0].value == spans[0].value


def test_luganda_provider_declares_only_luganda_and_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("NASTECH_ENABLE_LUGANDA_ADAPTER", raising=False)
    provider = get_provider("coqui-luganda-openbible")

    assert provider.language_codes == ("lg",)
    assert provider.supports_english is False
    preflight = provider_preflight("coqui-luganda-openbible")
    assert preflight["readiness"] == "adapter-installation-required"
    assert preflight["adapter_configuration"]["configured"] is False


def test_english_core_refuses_luganda_without_provider_fallback() -> None:
    with pytest.raises(ProviderActivationError, match="does not declare language 'lg'"):
        require_active_provider_for_language("nastech-native-onnx", "lg")


def test_luganda_language_state_reflects_explicit_configured_adapter(monkeypatch) -> None:
    monkeypatch.setenv("NASTECH_ENABLE_LUGANDA_ADAPTER", "1")
    monkeypatch.setenv("NASTECH_LUGANDA_TTS_COMMAND", "/usr/bin/true")
    monkeypatch.setenv("NASTECH_FFMPEG_COMMAND", "/usr/bin/true")
    monkeypatch.setenv("NASTECH_LUGANDA_TTS_MODEL", "multilingual-tts/VITS-OpenBible-Luganda")
    monkeypatch.setenv("NASTECH_LUGANDA_TTS_SPEAKER", "SPEAKER_00_Luganda")

    language = get_language("lg")

    assert language.state == "configured-local"
    assert "technical preview" in language.availability_note
