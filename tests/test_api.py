from fastapi.testclient import TestClient

from nastech_tts.api import create_app
from nastech_tts.fish import NastechGateway


class CompileOnlyProvider:
    async def health(self):
        return {"status": "compile_only", "provider": "none"}


class NastechApiTests:
    def test_health_exposes_fish_gateway_runtime(self):
        client = TestClient(
            create_app(NastechGateway(provider=CompileOnlyProvider(), provider_mode="compile-only"))
        )
        response = client.get("/v1/health")

        assert response.status_code == 200
        payload = response.json()
        assert payload["service"] == "nastech-tts"
        assert payload["version"] == "0.3.0"
        assert payload["provider_mode"] == "compile-only"

    def test_capabilities_expose_real_feature_control_contract(self):
        client = TestClient(
            create_app(NastechGateway(provider=CompileOnlyProvider(), provider_mode="compile-only"))
        )
        response = client.get("/v1/capabilities")

        assert response.status_code == 200
        payload = response.json()
        assert payload["model_family"] == "fish-s2"
        assert "sad" in payload["emotions"]
        assert "laugh" in payload["direct_events"]
