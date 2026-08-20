import json

import yaml
from fastapi.testclient import TestClient

from nastech_tts.agent_bridge import TOOLS, handle
from nastech_tts.agent_integration import connect_to_nastech_home
from nastech_tts.api import create_app
from nastech_tts.console import CONSOLE_FEATURES, render_console
from nastech_tts.supertonic import CompactSettings


class ConsoleRuntime:
    def __init__(self) -> None:
        self.settings = CompactSettings(default_voice="F1")

    def status(self):
        return {"model_family": "supertonic-3", "provider": "supertonic-local"}


def test_console_feature_catalog_has_more_than_forty_local_features() -> None:
    document = render_console()

    assert len(CONSOLE_FEATURES) >= 40
    assert len(CONSOLE_FEATURES) == len(set(CONSOLE_FEATURES))
    for feature in (
        "draft_autosave",
        "voice_favorites",
        "audio_visualizer",
        "serial_line_batch",
        "download_session_json",
        "keyboard_shortcuts",
    ):
        assert feature in CONSOLE_FEATURES
    for control in (
        'id="queueLines"',
        'id="history"',
        'id="visualizer"',
        'id="playbackRate"',
        'id="highContrast"',
        'id="downloadSession"',
    ):
        assert control in document


def test_root_console_is_served_with_themes_and_real_audio_route() -> None:
    response = TestClient(create_app(ConsoleRuntime())).get("/")

    assert response.status_code == 200
    assert "Nastech Research" in response.text
    assert "Midnight" in response.text
    assert "Sunrise" in response.text
    assert "Paper" in response.text
    assert "Studio preferences" in response.text
    assert "Local session history" in response.text
    assert "Render lines in order" in response.text
    assert "/v1/agent/speech" in response.text
    assert "Generate &amp; play" in response.text or "Generate & play" in response.text


def test_agent_integration_preserves_existing_mcp_entries(tmp_path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "mcp_servers:\n  filesystem:\n    command: npx\n    args: ['-y', 'filesystem']\n",
        encoding="utf-8",
    )

    result = connect_to_nastech_home(tmp_path, ["python", "-m", "nastech_tts.cli", "mcp-server"])

    config = yaml.safe_load(result.read_text(encoding="utf-8"))
    assert config_path == result
    assert config["mcp_servers"]["filesystem"]["command"] == "npx"
    bridge = config["mcp_servers"]["nastech_tts"]
    assert bridge["command"] == "python"
    assert bridge["args"] == ["-m", "nastech_tts.cli", "mcp-server"]
    assert bridge["tools"]["include"] == ["nastech_tts_speak", "nastech_tts_status"]


def test_agent_bridge_lists_tools_and_reads_local_status() -> None:
    class StatusRuntime:
        def status(self):
            return {"provider": "supertonic-local", "cache_entries": 0}

    initialized = handle(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}, StatusRuntime()
    )
    listing = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, StatusRuntime())
    status = handle(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "nastech_tts_status"},
        },
        StatusRuntime(),
    )

    assert initialized["result"]["serverInfo"]["name"] == "nastech-tts"
    assert listing["result"]["tools"] == TOOLS
    assert json.loads(status["result"]["content"][0]["text"])["cache_entries"] == 0
