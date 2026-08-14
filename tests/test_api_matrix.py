import pytest
from fastapi.testclient import TestClient

from nastech_tts.api import create_app
from nastech_tts.supertonic import CompactAudio, CompactSettings


class ToolRuntime:
    def __init__(self) -> None:
        self.settings = CompactSettings(default_voice="F1")
        self.last_compiled = None
        self.clear_calls = 0

    def status(self):
        return {
            "provider": "supertonic-local",
            "model_family": "supertonic-3",
            "cpu": {"profile": "balanced"},
            "audio_cache": {"entries": 2, "bytes": 10, "mib": 0.0},
            "metrics": {"synthesis_requests": 1},
        }

    def warmup(self):
        return {"status": "ready", "warmup_seconds": 0.1, "runtime": self.status()}

    def clear_audio_cache(self):
        self.clear_calls += 1
        return {"entries_cleared": 2, "bytes_cleared": 10}

    def synthesize(self, compiled):
        self.last_compiled = compiled
        return CompactAudio(data=b"RIFFmatrix", content_type="audio/wav", duration_seconds=0.5)


def _secured_client(monkeypatch) -> tuple[TestClient, ToolRuntime]:
    monkeypatch.setenv("NASTECH_API_KEY", "matrix-secret")
    runtime = ToolRuntime()
    return TestClient(create_app(runtime)), runtime


@pytest.mark.parametrize("path", ["/v1/runtime/diagnostics", "/v1/agent/tools"])
def test_protected_routes_reject_missing_bearer_token(monkeypatch, path: str) -> None:
    client, _ = _secured_client(monkeypatch)

    response = client.get(path)

    assert response.status_code == 401


def test_authorized_tool_catalog_exposes_all_local_operations(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)

    response = client.get("/v1/agent/tools", headers={"Authorization": "Bearer matrix-secret"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 5
    assert {tool["name"] for tool in payload} >= {
        "nastech_compile_speech",
        "nastech_generate_speech",
        "nastech_runtime_diagnostics",
        "nastech_warmup_runtime",
        "nastech_clear_runtime_cache",
    }


def test_cache_clear_endpoint_reports_result(monkeypatch) -> None:
    client, runtime = _secured_client(monkeypatch)

    response = client.post(
        "/v1/runtime/cache/clear", headers={"Authorization": "Bearer matrix-secret"}
    )

    assert response.status_code == 200
    assert response.json()["entries_cleared"] == 2
    assert runtime.clear_calls == 1


def test_compile_rejects_invalid_markup_with_client_error(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)

    response = client.post(
        "/v1/agent/compile",
        headers={"Authorization": "Bearer matrix-secret"},
        json={"markup": "<speak>café</speak>"},
    )

    assert response.status_code == 422


def test_openai_alias_maps_fast_speed_to_compiled_prosody(monkeypatch) -> None:
    client, runtime = _secured_client(monkeypatch)

    response = client.post(
        "/v1/audio/speech",
        headers={"Authorization": "Bearer matrix-secret"},
        json={"input": "Faster please.", "speed": 1.4, "response_format": "wav"},
    )

    assert response.status_code == 200
    assert runtime.last_compiled.speed == 1.18
    assert response.headers["x-nastech-runtime"] == "supertonic-local-onnx-cpu"


def test_capabilities_advertise_cache_management(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)

    response = client.get("/v1/capabilities", headers={"Authorization": "Bearer matrix-secret"})

    assert response.status_code == 200
    assert "/v1/runtime/cache/clear" in response.json()["runtime_endpoints"]


def test_health_remains_available_and_reports_authentication(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)

    response = client.get("/v1/health")

    assert response.status_code == 200
    assert response.json()["authentication_required"] is True
    assert response.json()["version"] == "0.6.0"
