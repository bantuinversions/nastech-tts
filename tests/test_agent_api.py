from fastapi.testclient import TestClient

from nastech_tts.api import create_app
from nastech_tts.fish import NastechGateway, SynthesizedAudio


class FakeFishProvider:
    async def health(self):
        return {"status": "ok", "provider": "fake-fish"}

    async def synthesize(self, payload, traceparent=None):
        assert payload["text"]
        if traceparent is not None:
            assert traceparent == "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-00"
        return SynthesizedAudio(
            data=b"RIFFfake-wave", content_type="audio/wav", provider_request_id="fake-1"
        )


def _client() -> TestClient:
    gateway = NastechGateway(provider=FakeFishProvider(), provider_mode="fish-local")
    return TestClient(create_app(gateway))


def test_compile_endpoint_returns_auditable_provider_payload() -> None:
    response = _client().post(
        "/v1/agent/compile",
        json={"markup": '<speak><emotion name="sad">The lantern faded.</emotion></speak>'},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "fish-local"
    assert body["provider_payload"]["text"] == "[sad] The lantern faded."
    assert body["manifest"]["model_family"] == "fish-s2"


def test_speech_endpoint_returns_provider_audio_and_trace_metadata() -> None:
    response = _client().post(
        "/v1/agent/speech",
        headers={"traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-00"},
        json={"markup": '<speak><emotion name="sad">The lantern faded.</emotion></speak>'},
    )

    assert response.status_code == 200
    assert response.content == b"RIFFfake-wave"
    assert response.headers["x-nastech-provider"] == "fish-local"
    assert response.headers["x-provider-request-id"] == "fake-1"


def test_openai_compatible_endpoint_accepts_plain_text() -> None:
    client = _client()
    response = client.post(
        "/v1/audio/speech",
        json={"model": "nastech-fish-s2", "input": "The lantern faded.", "response_format": "wav"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
