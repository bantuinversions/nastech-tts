import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_language_self_test.py"


def _validator_module():
    spec = importlib.util.spec_from_file_location("language_self_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _matrix(validator):
    rows = []
    for code, definition in validator.LANGUAGE_REGISTRY.items():
        has_pack = code in validator.MMS_LAZY_CODES
        rows.append(
            {
                "language": code,
                "display_label": definition.display_label,
                "model_id": f"facebook/mms-tts-{definition.iso639_3}" if has_pack else None,
                "pack_state": "lazy-downloadable" if has_pack else "no-verified-pack",
                "story_available": code in validator.EXPECTED_STORY_LANGUAGES,
            }
        )
    return rows


def _inventory(rows) -> str:
    labels = "\n".join(row["display_label"] for row in rows)
    return (
        "# Nastech TTS Voice Inventory\n"
        f"| Bantu registry targets | {len(rows)} |\n"
        "| Verified Bantu story routes | 11 |\n"
        f"{labels}\n"
    )


def test_language_self_audit_accepts_complete_code_first_matrix() -> None:
    validator = _validator_module()
    matrix = _matrix(validator)

    result = validator.validate(matrix, _inventory(matrix))

    assert result == {
        "registry_targets": 61,
        "lazy_download_routes": 35,
        "native_story_routes": 11,
    }


def test_language_self_audit_rejects_stale_inventory() -> None:
    validator = _validator_module()
    matrix = _matrix(validator)

    stale_inventory = _inventory(matrix).replace("lg - Luganda", "")
    with pytest.raises(ValueError, match="missing 'lg - Luganda'"):
        validator.validate(matrix, stale_inventory)


def test_language_self_audit_rejects_unsupported_pack_mapping() -> None:
    validator = _validator_module()
    matrix = _matrix(validator)
    row = next(item for item in matrix if item["language"] == "zu")
    row["model_id"] = "facebook/mms-tts-zul"
    row["pack_state"] = "lazy-downloadable"

    with pytest.raises(ValueError, match="inconsistent lazy-pack route"):
        validator.validate(matrix, _inventory(matrix))


def test_committed_language_matrix_passes_self_audit() -> None:
    validator = _validator_module()
    matrix = json.loads(
        (ROOT / "release" / "nastech-bantu-language-voice-registry.json").read_text(
            encoding="utf-8"
        )
    )
    inventory = (ROOT / "release" / "Nastech_TTS_All_Voices.md").read_text(encoding="utf-8")

    assert validator.validate(matrix, inventory)["registry_targets"] == 61
