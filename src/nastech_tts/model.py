"""Nastech's single upstream model-family specification."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class NastechModelSpec:
    """Immutable provenance and behavior contract for the sole Nastech base model."""

    product_model_id: str
    upstream_model_id: str
    upstream_project: str
    upstream_license: str
    language: str
    adaptation_method: str
    default_voice: str
    direct_sounds: tuple[str, ...]
    direct_emotions: tuple[str, ...]
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


NASTECH_ORPHEUS_V1 = NastechModelSpec(
    product_model_id="nastech-voice-en-v1",
    upstream_model_id="canopylabs/orpheus-3b-0.1-ft",
    upstream_project="https://github.com/canopyai/Orpheus-TTS",
    upstream_license="Apache-2.0",
    language="en",
    adaptation_method="Nastech LoRA/QLoRA adapter on the ready-made Orpheus finetune",
    default_voice="tara",
    direct_sounds=("laugh", "chuckle", "sigh", "cough", "sniffle", "groan", "yawn", "gasp"),
    direct_emotions=(),
    notes=(
        "Nastech v0.2 uses one Orpheus model family only. Direct generic emotion tags are "
        "not claimed until a Nastech adapter has been trained and evaluated."
    ),
)
