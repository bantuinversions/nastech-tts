from fastapi.testclient import TestClient

from nastech_tts.api import create_app


def test_voice_inventory_endpoint_reports_profiles_and_truth_boundary() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/voices")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"] == {
        "selectable_profiles": 40,
        "verified_base_timbres": 10,
        "delivery_profiles": 30,
    }
    assert len(payload["profiles"]) == 40
    assert "not claimed as forty separately trained speakers" in payload["claim_boundary"]
