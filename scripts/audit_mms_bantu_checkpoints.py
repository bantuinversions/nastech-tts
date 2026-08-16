from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

codes = [
    "eng",
    "lug",
    "nyn",
    "ach",
    "teo",
    "swh",
    "kin",
    "run",
    "kik",
    "kam",
    "luy",
    "luo",
    "zul",
    "xho",
    "sot",
    "nso",
    "tsn",
    "ven",
    "tso",
    "ssw",
    "nbl",
    "sna",
    "nya",
]
results = {}
for code in codes:
    url = f"https://huggingface.co/api/models/facebook/mms-tts-{code}"
    request = urllib.request.Request(
        url, headers={"User-Agent": "nastech-tts-availability-audit/0.10"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        results[code] = {
            "available": True,
            "id": payload.get("id"),
            "sha": payload.get("sha"),
            "private": payload.get("private", False),
        }
    except urllib.error.HTTPError as exc:
        results[code] = {"available": False, "status": exc.code}
    except Exception as exc:  # noqa: BLE001
        results[code] = {"available": False, "error": type(exc).__name__}
path = Path("/home/ubuntu/nastech-tts/docs/mms_bantu_checkpoint_audit.json")
path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
for code, result in results.items():
    print(code, result)
