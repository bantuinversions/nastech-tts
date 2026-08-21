"""Safe local Nastech Agent configuration for the Nastech TTS MCP bridge."""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import yaml

DEFAULT_NASTECH_HOME = Path.home() / ".nastech"


def nastech_home() -> Path:
    """Resolve Nastech Agent's documented per-user data directory."""

    return Path(os.environ.get("NASTECH_HOME", DEFAULT_NASTECH_HOME)).expanduser()


def bridge_config(command: Sequence[str]) -> dict[str, Any]:
    """Return the minimal stdio MCP definition for the local TTS bridge."""

    if not command:
        raise ValueError("A Nastech TTS bridge command is required.")
    return {
        "command": command[0],
        "args": list(command[1:]),
        "enabled": True,
        "tools": {
            "include": [
                "nastech_tts_speak",
                "nastech_tts_status",
                "nastech_tts_capabilities",
            ]
        },
    }


def connect_to_nastech_home(home: Path, command: Sequence[str]) -> Path:
    """Register Nastech TTS as a local stdio MCP server without destructive merges."""

    config_path = home / "config.yaml"
    home.mkdir(parents=True, exist_ok=True)
    if config_path.exists():
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"Nastech configuration must be a mapping: {config_path}")
    else:
        loaded = {}

    servers = loaded.setdefault("mcp_servers", {})
    if not isinstance(servers, dict):
        raise ValueError(f"mcp_servers must be a mapping: {config_path}")
    servers["nastech_tts"] = bridge_config(command)
    config_path.write_text(
        yaml.safe_dump(loaded, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    return config_path
