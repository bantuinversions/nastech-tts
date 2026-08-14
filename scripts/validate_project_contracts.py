"""Validate Nastech machine-readable JSON and YAML repository contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _read_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    agent = _read_json(ROOT / "agent_tools" / "nastech_tts_tool.json")
    tools = agent.get("tools", [])
    tool_names = {tool.get("name") for tool in tools}
    expected_tools = {
        "nastech_compile_speech",
        "nastech_generate_speech",
        "nastech_runtime_diagnostics",
        "nastech_warmup_runtime",
        "nastech_clear_runtime_cache",
    }
    _require(agent.get("service") == "nastech-tts", "Agent catalog has an invalid service name.")
    _require(tool_names == expected_tools, "Agent catalog does not expose the expected tool set.")

    openapi = _read_json(ROOT / "docs" / "openapi.json")
    paths = set(openapi.get("paths", {}))
    expected_paths = {
        "/v1/health",
        "/v1/capabilities",
        "/v1/agent/tools",
        "/v1/agent/compile",
        "/v1/agent/speech",
        "/v1/audio/speech",
        "/v1/runtime/diagnostics",
        "/v1/runtime/warmup",
        "/v1/runtime/cache/clear",
    }
    _require(expected_paths <= paths, "OpenAPI contract is missing a required local endpoint.")

    summary = _read_yaml(ROOT / "project-summary.yml")
    _require(summary["project"]["package"] == "nastech-tts", "Project summary package mismatch.")
    _require(summary["quality"]["test_target"] == 72, "Project summary test target mismatch.")

    yaml_paths = [
        ROOT / ".github" / "dependabot.yml",
        ROOT / ".github" / "labels.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml",
        ROOT / ".github" / "workflows" / "ci.yml",
        ROOT / ".github" / "workflows" / "release.yml",
    ]
    for path in yaml_paths:
        _require(_read_yaml(path) is not None, f"YAML contract is empty: {path.relative_to(ROOT)}")

    print("Validated Nastech JSON and YAML project contracts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
