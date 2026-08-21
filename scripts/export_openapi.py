"""Export the Nastech TTS OpenAPI schema without starting a network service."""

from __future__ import annotations

import json
from pathlib import Path

from nastech_tts.api import create_app
from nastech_tts.supertonic import CompactSettings


class StaticCompactRuntime:
    def __init__(self) -> None:
        self.settings = CompactSettings(default_voice="F1")

    def status(self):
        return {
            "provider": "nastech-native-onnx",
            "provider_mixer": "nastech",
            "model_assets_mib": 0.0,
            "target_max_deployment_mib": 1024,
        }


def main() -> None:
    app = create_app(StaticCompactRuntime())
    output = Path(__file__).resolve().parents[1] / "docs" / "openapi.json"
    output.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
