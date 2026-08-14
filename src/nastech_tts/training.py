"""Dataset validation for Nastech parameter-efficient adapter training.

This module intentionally validates data and produces a training-ready summary. It
never downloads data or starts a GPU job without an explicitly supplied manifest.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import soundfile as sf

from .markup import _ALLOWED_EMOTIONS, _ALLOWED_SOUNDS, _validate_english

_REQUIRED_FIELDS = {
    "audio_path",
    "transcript",
    "speaker_id",
    "consent_id",
    "emotion",
    "intensity",
    "behavior_events",
    "recording_quality",
    "split",
}
_ALLOWED_SPLITS = {"train", "validation", "test"}
_ALLOWED_QUALITY = {"studio", "clean", "acceptable"}


class DatasetValidationError(ValueError):
    """Raised when a Nastech adapter-training manifest is invalid."""


@dataclass(frozen=True)
class TrainingRecord:
    audio_path: str
    transcript: str
    speaker_id: str
    consent_id: str
    emotion: str
    intensity: float
    behavior_events: tuple[str, ...]
    recording_quality: str
    split: str

    @classmethod
    def from_mapping(cls, raw: dict[str, Any], manifest_dir: Path) -> TrainingRecord:
        missing = _REQUIRED_FIELDS - raw.keys()
        if missing:
            raise DatasetValidationError(f"Manifest record is missing required fields: {sorted(missing)}")
        try:
            intensity = float(raw["intensity"])
        except (TypeError, ValueError) as exc:
            raise DatasetValidationError("Record intensity must be numeric from 0 through 1.") from exc
        return cls(
            audio_path=str(raw["audio_path"]),
            transcript=str(raw["transcript"]),
            speaker_id=str(raw["speaker_id"]),
            consent_id=str(raw["consent_id"]),
            emotion=str(raw["emotion"]).lower(),
            intensity=intensity,
            behavior_events=tuple(str(item).lower() for item in raw["behavior_events"]),
            recording_quality=str(raw["recording_quality"]).lower(),
            split=str(raw["split"]).lower(),
        )

    def validate(self, manifest_dir: Path) -> None:
        if not self.audio_path or not self.speaker_id or not self.consent_id:
            raise DatasetValidationError("audio_path, speaker_id, and consent_id must not be blank.")
        _validate_english(self.transcript)
        if not self.transcript.strip():
            raise DatasetValidationError("Transcript must not be blank.")
        if self.emotion not in _ALLOWED_EMOTIONS:
            raise DatasetValidationError(f"Unsupported emotion '{self.emotion}'.")
        if not 0.0 <= self.intensity <= 1.0:
            raise DatasetValidationError("Intensity must be from 0 through 1.")
        unsupported_events = set(self.behavior_events) - _ALLOWED_SOUNDS
        if unsupported_events:
            raise DatasetValidationError(f"Unsupported behavior events: {sorted(unsupported_events)}")
        if self.recording_quality not in _ALLOWED_QUALITY:
            raise DatasetValidationError(f"Unsupported recording_quality '{self.recording_quality}'.")
        if self.split not in _ALLOWED_SPLITS:
            raise DatasetValidationError(f"Unsupported split '{self.split}'.")

        audio_file = (manifest_dir / self.audio_path).resolve()
        if not audio_file.is_file():
            raise DatasetValidationError(f"Audio file not found: {audio_file}")
        try:
            info = sf.info(str(audio_file))
        except RuntimeError as exc:
            raise DatasetValidationError(f"Cannot read audio file: {audio_file}") from exc
        if info.channels != 1:
            raise DatasetValidationError(f"Audio must be mono: {audio_file}")
        if info.samplerate < 16_000:
            raise DatasetValidationError(f"Audio sample rate must be >=16 kHz: {audio_file}")
        if not 0.4 <= info.duration <= 30.0:
            raise DatasetValidationError(
                f"Audio duration must be 0.4 to 30 seconds; got {info.duration:.2f}s for {audio_file}"
            )

    def nastech_prompt(self) -> str:
        behavior = ",".join(self.behavior_events) if self.behavior_events else "none"
        return (
            f"[nastech:voice={self.speaker_id}]"
            f"[emotion={self.emotion}]"
            f"[intensity={self.intensity:.2f}]"
            f"[events={behavior}]\n{self.transcript}"
        )


@dataclass
class DatasetSummary:
    total_records: int = 0
    by_split: dict[str, int] = field(default_factory=dict)
    by_emotion: dict[str, int] = field(default_factory=dict)
    by_event: dict[str, int] = field(default_factory=dict)
    speaker_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_manifest(manifest_path: str | Path) -> DatasetSummary:
    """Validate a JSONL manifest and return a reproducible data-composition summary."""
    path = Path(manifest_path).resolve()
    if not path.is_file():
        raise DatasetValidationError(f"Manifest does not exist: {path}")

    records: list[TrainingRecord] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DatasetValidationError(f"Invalid JSON at line {line_number}.") from exc
        if not isinstance(raw, dict):
            raise DatasetValidationError(f"Manifest line {line_number} must be a JSON object.")
        record = TrainingRecord.from_mapping(raw, path.parent)
        try:
            record.validate(path.parent)
        except DatasetValidationError as exc:
            raise DatasetValidationError(f"Manifest line {line_number}: {exc}") from exc
        records.append(record)

    if not records:
        raise DatasetValidationError("Manifest contains no training records.")
    if not any(record.split == "train" for record in records):
        raise DatasetValidationError("Manifest must include at least one training record.")
    if not any(record.split == "validation" for record in records):
        raise DatasetValidationError("Manifest must include at least one validation record.")

    summary = DatasetSummary(total_records=len(records))
    speakers: set[str] = set()
    for record in records:
        summary.by_split[record.split] = summary.by_split.get(record.split, 0) + 1
        summary.by_emotion[record.emotion] = summary.by_emotion.get(record.emotion, 0) + 1
        for event in record.behavior_events:
            summary.by_event[event] = summary.by_event.get(event, 0) + 1
        speakers.add(record.speaker_id)
    summary.speaker_count = len(speakers)
    return summary
