import unittest

try:
    from fastapi.testclient import TestClient

    from nastech_tts.api import create_app
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False


@unittest.skipUnless(API_AVAILABLE, "FastAPI API extra is not installed")
class NastechApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app())

    def test_health_exposes_single_model_runtime(self):
        response = self.client.get("/v1/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["product_model_id"], "nastech-voice-en-v1")
        self.assertEqual(payload["runtime"], "nastech-orpheus")
        self.assertNotIn("kokoro", str(payload).lower())

    def test_model_endpoint_preserves_upstream_provenance(self):
        response = self.client.get("/v1/models/nastech-voice-en-v1")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["upstream_model_id"], "canopylabs/orpheus-3b-0.1-ft")
        self.assertEqual(payload["upstream_license"], "Apache-2.0")


if __name__ == "__main__":
    unittest.main()
