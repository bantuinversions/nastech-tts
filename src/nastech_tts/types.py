"""Core typed data structures for Nastech TTS."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class SpanKind(str, Enum):
    SPEECH = "speech"
    SOUND = "sound"
    PAUSE = "pause"


class Fidelity(str, Enum):
    DIRECT = "direct"
    APPROXIMATED = "approximated"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class SpeechStyle:
    emotion: str | None = None
    intensity: float | None = None
    rate: str | None = None
    volume: str | None = None


@dataclass(frozen=True)
class AudioSpan:
    kind: SpanKind
    value: str | int
    voice: str = "tara"
    style: SpeechStyle = field(default_factory=SpeechStyle)


@dataclass(frozen=True)
class RenderDecision:
    span_index: int
    engine: str
    fidelity: Fidelity
    reason: str
    requested_behavior: str | None = None


@dataclass
class RenderManifest:
    voice: str
    language: str = "en"
    decisions: list[RenderDecision] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "voice": self.voice,
            "language": self.language,
            "decisions": [
                {
                    **asdict(decision),
                    "fidelity": decision.fidelity.value,
                }
                for decision in self.decisions
            ],
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class AudioChunk:
    samples: Any
    sample_rate: int


@dataclass(frozen=True)
class RenderResult:
    audio_path: Path
    manifest_path: Path
    manifest: RenderManifest
