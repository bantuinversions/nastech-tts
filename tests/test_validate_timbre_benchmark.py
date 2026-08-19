from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from benchmark_base_timbres import BASE_TIMBRES  # noqa: E402
from validate_timbre_benchmark import validate  # noqa: E402


def _valid_payload() -> dict[str, object]:
    return {
        "voices": [
            {
                "voice": voice,
                "warm_runs": [
                    {
                        "audio_quality": {
                            "sample_rate_hz": 44100,
                            "clipped_samples": 0,
                            "rms_dbfs": -24.0,
                        }
                    }
                ],
            }
            for voice in BASE_TIMBRES
        ]
    }


def test_validator_accepts_all_ten_unclipped_44khz_timbres() -> None:
    validate(_valid_payload(), runs=1)


def test_validator_refuses_wrong_timbre_matrix() -> None:
    payload = _valid_payload()
    payload["voices"] = payload["voices"][:-1]
    with pytest.raises(ValueError, match="ten base timbres"):
        validate(payload, runs=1)


def test_validator_refuses_bad_audio_quality() -> None:
    payload = _valid_payload()
    payload["voices"][0]["warm_runs"][0]["audio_quality"]["clipped_samples"] = 1
    with pytest.raises(ValueError, match="quality gate"):
        validate(payload, runs=1)
