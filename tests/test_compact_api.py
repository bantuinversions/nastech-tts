from fastapi.testclient import TestClient

from nastech_tts.api import create_app
from nastech_tts.supertonic import CompactAudio, CompactSettings


class FakeCompactRuntime:
    def __init__(self) -> None:
        self.settings = CompactSettings(default_voice="F1")

    def status(self):
        return {
            "provider": "supertonic-local",
            "model_family": "supertonic-3",
            "model_assets_mib": 386.0,
            "target_max_deployment_mib": 1024,
            "cpu": {"profile": "balanced", "intra_op_threads": 4},
        }

    def warmup(self):
        return {"status": "ready", "warmup_seconds": 0.25, "runtime": self.status()}

    def synthesize(self, compiled):
        assert compiled.text
        return CompactAudio(
            data=b"RIFFcompact-wave",
            content_type="audio/wav",
            duration_seconds=1.25,
        )


def _client() -> TestClient:
    return TestClient(create_app(FakeCompactRuntime()))


def test_compile_returns_auditable_local_expression_plan() -> None:
    response = _client().post(
        "/v1/agent/compile",
        json={
            "markup": '<speak><emotion name="sad">Hello.</emotion><sound type="laugh" /></speak>'
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["runtime"] == "supertonic-local-onnx-cpu"
    assert body["text"] == "<sad> Hello. <laugh>"
    assert body["manifest"]["model_family"] == "supertonic-3"


def test_speech_endpoint_returns_local_audio() -> None:
    response = _client().post(
        "/v1/agent/speech",
        json={"markup": '<speak>Hello <sound type="laugh" /></speak>'},
    )

    assert response.status_code == 200
    assert response.content == b"RIFFcompact-wave"
    assert response.headers["x-nastech-runtime"] == "supertonic-local-onnx-cpu"
    assert response.headers["x-nastech-duration-seconds"] == "1.25"


def test_openai_compatible_alias_is_local() -> None:
    response = _client().post(
        "/v1/audio/speech",
        json={"input": "Hello", "voice": "F1", "response_format": "wav"},
    )

    assert response.status_code == 200
    assert response.headers["x-nastech-runtime"] == "supertonic-local-onnx-cpu"


def test_runtime_diagnostics_and_warmup_are_available() -> None:
    diagnostics = _client().get("/v1/runtime/diagnostics")
    warmup = _client().post("/v1/runtime/warmup")

    assert diagnostics.status_code == 200
    assert diagnostics.json()["runtime"]["cpu"]["profile"] == "balanced"
    assert warmup.status_code == 200
    assert warmup.json()["status"] == "ready"
