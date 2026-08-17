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
    assert len(payload) == 17
    assert {tool["name"] for tool in payload} >= {
        "nastech_list_providers",
        "nastech_list_languages",
        "nastech_language_preflight",
        "nastech_list_language_packs",
        "nastech_download_language_pack",
        "nastech_provider_preflight",
        "nastech_compose_story",
        "nastech_plan_speech",
        "nastech_compile_speech",
        "nastech_generate_speech",
        "nastech_stream_speech",
        "nastech_clean_wav",
        "nastech_list_platforms",
        "nastech_platform_preflight",
        "nastech_runtime_diagnostics",
        "nastech_warmup_runtime",
        "nastech_clear_runtime_cache",
    }


def test_provider_inventory_and_preflight_are_authenticated_and_truthful(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)
    headers = {"Authorization": "Bearer matrix-secret"}

    inventory = client.get("/v1/providers", headers=headers)
    preflight = client.post(
        "/v1/providers/preflight",
        headers=headers,
        json={"provider_id": "coqui-cli"},
    )

    assert inventory.status_code == 200
    assert inventory.json()["provider_catalog_size"] == 60
    assert inventory.json()["network_default"] == "disabled"
    assert preflight.status_code == 200
    assert preflight.json()["readiness"] == "adapter-installation-required"
    assert preflight.json()["network_request_made"] is False


def test_agent_identity_and_story_composition_credit_nastech_research(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)
    headers = {"Authorization": "Bearer matrix-secret"}

    identity = client.get("/v1/agent/identity", headers=headers)
    story = client.post(
        "/v1/agent/story",
        headers=headers,
        json={"theme": "discovery", "emotion": "hopeful", "sounds": ["sigh"]},
    )

    assert identity.status_code == 200
    assert identity.json()["publisher"] == "Nastech Research"
    assert identity.json()["repository_owner"] == "bantuinversions"
    assert story.status_code == 200
    assert story.json()["agent"]["name"] == "Nastech Agent"
    assert story.json()["story"]["theme"] == "discovery"
    assert '<sound type="sigh" />' in story.json()["story"]["markup"]
    assert story.json()["runtime"] == "nastech-provider-mixer"


def test_rendered_nastech_agent_story_uses_local_audio(monkeypatch) -> None:
    client, runtime = _secured_client(monkeypatch)

    response = client.post(
        "/v1/agent/story",
        headers={"Authorization": "Bearer matrix-secret"},
        json={"theme": "resilience", "emotion": "sad", "render": True},
    )

    assert response.status_code == 200
    assert response.content == b"RIFFmatrix"
    assert response.headers["x-nastech-agent"] == "nastech-agent"
    assert response.headers["x-nastech-publisher"] == "Nastech Research"
    assert response.headers["x-nastech-story-theme"] == "resilience"
    assert "Nastech Agent returned" in runtime.last_compiled.text


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
    assert response.headers["x-nastech-runtime"] == "nastech-provider-mixer"


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
    assert response.json()["version"] == "0.12.0"


def test_agent_plan_exposes_local_execution_and_fidelity_summary(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)

    response = client.post(
        "/v1/agent/plan",
        headers={"Authorization": "Bearer matrix-secret"},
        json={
            "markup": "<speak><emotion name='sad'>Plan this.</emotion></speak>",
            "delivery": "chunked-wav",
            "cleanup": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["execution"]["inference"] == "active-local-provider"
    assert payload["execution"]["provider"]["id"] == "nastech-native-onnx"
    assert payload["execution"]["delivery_endpoint"] == "/v1/agent/speech/stream"
    assert payload["execution"]["voice_cleanup_requested"] is True


def test_stream_endpoint_delivers_post_synthesis_wav_chunks(monkeypatch) -> None:
    client, runtime = _secured_client(monkeypatch)

    response = client.post(
        "/v1/agent/speech/stream",
        headers={"Authorization": "Bearer matrix-secret"},
        json={"markup": "<speak>Chunk me.</speak>", "chunk_bytes": 4096},
    )

    assert response.status_code == 200
    assert response.content == b"RIFFmatrix"
    assert response.headers["x-nastech-delivery"] == "chunked-post-synthesis"
    assert response.headers["x-nastech-chunk-bytes"] == "4096"
    assert runtime.last_compiled.text == "Chunk me."


def test_cleanup_endpoint_requires_wav_content_type(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)

    response = client.post(
        "/v1/audio/clean",
        headers={
            "Authorization": "Bearer matrix-secret",
            "Content-Type": "application/octet-stream",
        },
        content=b"not-wav",
    )

    assert response.status_code == 422


def test_capabilities_advertise_streaming_and_local_cleanup(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)

    response = client.get("/v1/capabilities", headers={"Authorization": "Bearer matrix-secret"})

    assert response.status_code == 200
    payload = response.json()
    assert "/v1/providers" in payload["agent_endpoints"]
    assert "/v1/providers/preflight" in payload["agent_endpoints"]
    assert payload["provider_inventory"]["catalog_size"] == 60
    assert "/v1/agent/identity" in payload["agent_endpoints"]
    assert "/v1/agent/story" in payload["agent_endpoints"]
    assert "/v1/agent/speech/stream" in payload["agent_endpoints"]
    assert payload["publisher"] == "Nastech Research"
    assert (
        payload["delivery"]["streaming_semantics"]
        == "post-synthesis WAV chunks; not incremental model inference"
    )
    assert payload["voice_cleanup"]["processor"] == "nastech-local-pcm-cleanup"


def test_platform_inventory_exposes_cpu_and_mobile_profiles(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)

    response = client.get("/v1/platforms", headers={"Authorization": "Bearer matrix-secret"})

    assert response.status_code == 200
    profiles = {profile["id"]: profile for profile in response.json()["profiles"]}
    assert profiles["python-cpu"]["status"] == "verified"
    assert profiles["android-nnapi"]["status"] == "planned-device-specific"


def test_platform_preflight_keeps_cuda_claim_validation_gated(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)

    response = client.post(
        "/v1/platforms/preflight",
        headers={"Authorization": "Bearer matrix-secret"},
        json={"target": "python-cuda"},
    )

    assert response.status_code == 200
    assert response.json()["target"]["status"] == "planned"
    assert response.json()["readiness"] in {
        "provider-registered-but-model-validation-required",
        "target-runtime-not-registered-on-current-host",
    }


def test_platform_preflight_rejects_unknown_target(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)

    response = client.post(
        "/v1/platforms/preflight",
        headers={"Authorization": "Bearer matrix-secret"},
        json={"target": "not-a-platform"},
    )

    assert response.status_code == 422


def test_language_inventory_and_luganda_preflight_are_authenticated_and_truthful(
    monkeypatch,
) -> None:
    client, _ = _secured_client(monkeypatch)
    headers = {"Authorization": "Bearer matrix-secret"}

    inventory = client.get("/v1/languages", headers=headers)
    preflight = client.post("/v1/languages/preflight", headers=headers, json={"language": "lg"})

    assert inventory.status_code == 200
    languages = {language["code"]: language for language in inventory.json()["languages"]}
    assert languages["lg"]["state"] == "adapter-available"
    assert languages["zu"]["state"] == "planned"
    assert preflight.status_code == 200
    assert preflight.json()["language"]["iso639_3"] == "lug"
    assert preflight.json()["network_request_made"] is False


def test_luganda_synthesis_refuses_english_core_without_fallback(monkeypatch) -> None:
    client, _ = _secured_client(monkeypatch)

    response = client.post(
        "/v1/agent/speech",
        headers={"Authorization": "Bearer matrix-secret"},
        json={
            "markup": "<speak>Nze njagala okwogera Luganda.</speak>",
            "language": "lg",
        },
    )

    assert response.status_code == 422
    assert "does not declare language 'lg'" in response.json()["detail"]
