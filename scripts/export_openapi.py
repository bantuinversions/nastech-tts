"""Export the Nastech gateway OpenAPI schema without starting a network service."""

from __future__ import annotations

import json
from pathlib import Path

from nastech_tts.api import create_app
from nastech_tts.fish import NastechGateway


class CompileOnlyProvider:
    async def health(self):
        return {"status": "compile_only", "provider": "none"}


def main() -> None:
    app = create_app(NastechGateway(provider=CompileOnlyProvider(), provider_mode="compile-only"))
    output = Path(__file__).resolve().parents[1] / "docs" / "openapi.json"
    output.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
