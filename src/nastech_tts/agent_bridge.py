"""JSON-RPC stdio bridge that exposes local Nastech TTS as MCP tools."""

from __future__ import annotations

import base64
import html
import json
import sys
from typing import Any

from .languages import get_language
from .providers import require_active_provider_for_language, synthesize_with_provider
from .supertonic import SupertonicRuntime, compile_nastechml

SERVER_INFO = {"name": "nastech-tts", "version": "0.12.2"}
TOOLS = [
    {
        "name": "nastech_tts_speak",
        "description": (
            "Generate a local WAV with Nastech TTS. The audio remains on this machine and is "
            "returned as an MCP audio content item."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "minLength": 1, "maxLength": 12000},
                "voice": {"type": "string", "default": "siya"},
                "language": {"type": "string", "default": "en"},
                "emotion": {
                    "type": "string",
                    "enum": [
                        "neutral",
                        "calm",
                        "happy",
                        "excited",
                        "surprised",
                        "sad",
                        "angry",
                        "frustrated",
                        "fearful",
                        "disgusted",
                    ],
                    "default": "neutral",
                },
                "rate": {"type": "string", "enum": ["slow", "normal", "fast"], "default": "normal"},
                "sounds": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "laugh",
                            "chuckle",
                            "sigh",
                            "cough",
                            "sniffle",
                            "groan",
                            "yawn",
                            "gasp",
                            "cry",
                            "scream",
                            "throatclear",
                        ],
                    },
                    "maxItems": 3,
                    "default": [],
                },
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    },
    {
        "name": "nastech_tts_status",
        "description": "Read the local Nastech TTS runtime status without generating audio.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]


def _response(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _markup(arguments: dict[str, Any]) -> str:
    text = html.escape(str(arguments["text"]))
    voice = html.escape(str(arguments.get("voice") or "siya"), quote=True)
    emotion = str(arguments.get("emotion") or "neutral")
    rate = str(arguments.get("rate") or "normal")
    sounds = arguments.get("sounds") or []
    spoken = text if emotion == "neutral" else f'<emotion name="{emotion}">{text}</emotion>'
    cues = "".join(f'<sound type="{html.escape(str(sound), quote=True)}" />' for sound in sounds)
    return f'<speak voice="{voice}"><prosody rate="{rate}">{spoken}{cues}</prosody></speak>'


def _tool_result(
    runtime: SupertonicRuntime, name: str, arguments: dict[str, Any]
) -> dict[str, Any]:
    if name == "nastech_tts_status":
        return {"content": [{"type": "text", "text": json.dumps(runtime.status(), indent=2)}]}
    if name != "nastech_tts_speak":
        raise ValueError(f"Unknown Nastech TTS tool: {name}.")

    language = get_language(str(arguments.get("language") or "en"))
    provider = require_active_provider_for_language(None, language.code)
    compiled = compile_nastechml(_markup(arguments), runtime.settings, language=language.code)
    audio = synthesize_with_provider(provider.id, runtime, compiled, language=language.code)
    return {
        "content": [
            {
                "type": "audio",
                "mimeType": "audio/wav",
                "data": base64.b64encode(audio.data).decode("ascii"),
            },
            {
                "type": "text",
                "text": json.dumps(
                    {
                        "publisher": "Nastech Research",
                        "request_id": compiled.request_id,
                        "language": language.display_label,
                        "provider": provider.id,
                        "duration_seconds": round(audio.duration_seconds, 3),
                        "delivery": "local WAV via Nastech TTS MCP bridge",
                    }
                ),
            },
        ]
    }


def handle(request: dict[str, Any], runtime: SupertonicRuntime) -> dict[str, Any] | None:
    """Handle one newline-delimited JSON-RPC MCP request."""

    method = request.get("method")
    request_id = request.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return _response(
            request_id,
            {
                "protocolVersion": request.get("params", {}).get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
                "instructions": "Nastech TTS runs locally and returns WAV audio content.",
            },
        )
    if method == "tools/list":
        return _response(request_id, {"tools": TOOLS})
    if method == "tools/call":
        params = request.get("params", {})
        try:
            return _response(
                request_id, _tool_result(runtime, params["name"], params.get("arguments", {}))
            )
        except (KeyError, TypeError, ValueError) as exc:
            return _response(
                request_id, {"content": [{"type": "text", "text": str(exc)}], "isError": True}
            )
    return _error(request_id, -32601, f"Unsupported MCP method: {method}.")


def run_stdio() -> int:
    """Run a newline-delimited JSON-RPC MCP session over standard input/output."""

    runtime = SupertonicRuntime()
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = handle(request, runtime)
        except json.JSONDecodeError as exc:
            response = _error(None, -32700, f"Invalid JSON-RPC request: {exc.msg}.")
        except Exception as exc:  # Keep the bridge alive after a single request failure.
            response = _error(None, -32603, f"Nastech TTS bridge error: {exc}.")
        if response is not None:
            print(json.dumps(response), flush=True)
    return 0
