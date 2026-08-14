from fastapi.testclient import TestClient

from nastech_tts.api import create_app
from nastech_tts.supertonic import CompactSettings


class CompactStatusRuntime:
    def __init__(self) -> None:
        self.settings = CompactSettings(default_voice="F1")

    def status(self):
        return {
            "provider": "supertonic-local",
            "model_family": "supertonic-3",
            "model_assets_mib": 386.0,
            "target_max_deployment_mib": 1024,
        }


class NastechApiTests:
    def test_health_exposes_compact_local_runtime(self):
        client = TestClient(create_app(CompactStatusRuntime()))
        response = client.get("/v1/health")

        assert response.status_code == 200
        payload = response.json()
        assert payload["service"] == "nastech-tts"
        assert payload["version"] == "0.4.0"
        assert payload["runtime"]["model_family"] == "supertonic-3"

    def test_capabilities_expose_compact_real_feature_contract(self):
        client = TestClient(create_app(CompactStatusRuntime()))
        response = client.get("/v1/capabilities")

        assert response.status_code == 200
        payload = response.json()
        assert payload["model_family"] == "supertonic-3"
        assert "laugh" in payload["documented_direct_events"]
        assert payload["max_deployment_mib"] == 1024
