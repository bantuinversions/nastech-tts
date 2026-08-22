from fastapi.testclient import TestClient

from nastech_tts import (
    PRODUCT_NAME,
    PUBLISHER,
    VOICE_CORE_NAME,
    NastechVoiceCoreRuntime,
    product_identity,
)
from nastech_tts.api import create_app
from nastech_tts.supertonic import CompactSettings


class BrandRuntime:
    def __init__(self) -> None:
        self.settings = CompactSettings(default_voice="F1")

    def status(self):
        return {"provider": "nastech-voice-core", "voice_core": "nastech-voice-core"}


def test_package_exposes_nastech_tts_product_identity() -> None:
    identity = product_identity()

    assert PRODUCT_NAME == "Nastech TTS"
    assert VOICE_CORE_NAME == "Nastech Voice Core"
    assert PUBLISHER == "Nastech Research"
    assert identity["product"] == PRODUCT_NAME
    assert identity["voice_core"] == VOICE_CORE_NAME
    assert identity["publisher"] == PUBLISHER
    assert callable(NastechVoiceCoreRuntime)


def test_api_exposes_only_nastech_product_branding() -> None:
    client = TestClient(create_app(BrandRuntime()))

    assert client.app.title == "Nastech TTS"
    assert "Nastech Voice Core" in client.app.description
    health = client.get("/v1/health")
    capabilities = client.get("/v1/capabilities")

    assert health.status_code == 200
    assert health.json()["product"] == "Nastech TTS"
    assert health.json()["voice_core"] == "Nastech Voice Core"
    assert capabilities.status_code == 200
    assert capabilities.json()["product"] == "Nastech TTS"
    assert capabilities.json()["voice_core"] == "Nastech Voice Core"
