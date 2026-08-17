"""Truthful language registry for Nastech TTS provider selection.

The registry describes language targets and evidence state; it does not itself
install a model, contact a service, or turn a research candidate into an active
speech capability.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

VERIFIED_LOCAL = "verified-local"
CONFIGURED_LOCAL = "configured-local"
ADAPTER_AVAILABLE = "adapter-available"
RESEARCH_CANDIDATE = "research-candidate"
PLANNED = "planned"
REJECTED = "rejected"


class LanguageRegistryError(ValueError):
    """Raised when an unknown or unsupported language identifier is requested."""


@dataclass(frozen=True)
class LanguageDefinition:
    """One language target, its language tag, and a provider evidence boundary."""

    code: str
    iso639_3: str
    label: str
    region: str
    state: str
    provider_ids: tuple[str, ...]
    availability_note: str
    reviewer_required: bool = True

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["provider_ids"] = list(self.provider_ids)
        return result


_LANGUAGE_ROWS = (
    LanguageDefinition(
        "en",
        "eng",
        "English",
        "Global",
        VERIFIED_LOCAL,
        ("nastech-native-onnx",),
        "Verified local Nastech core language with expressive release evidence.",
        False,
    ),
    LanguageDefinition(
        "lg",
        "lug",
        "Luganda",
        "Uganda / Great Lakes",
        ADAPTER_AVAILABLE,
        ("coqui-luganda-openbible", "mms-luganda-eval"),
        (
            "Optional local Luganda VITS pack; native reviewer approval is required before "
            "a pure-language claim."
        ),
    ),
    LanguageDefinition(
        "nyn",
        "nyn",
        "Runyankole",
        "Uganda / Great Lakes",
        ADAPTER_AVAILABLE,
        ("usoal-orpheus-luganda-family", "mms-lazy"),
        "Optional MMS pack is lazy-downloadable; published model licence is non-commercial.",
    ),
    LanguageDefinition(
        "ach",
        "ach",
        "Acholi",
        "Uganda",
        ADAPTER_AVAILABLE,
        ("usoal-orpheus-luganda-family", "mms-lazy"),
        "Optional MMS pack is lazy-downloadable; published model licence is non-commercial.",
    ),
    LanguageDefinition(
        "teo",
        "teo",
        "Ateso",
        "Uganda",
        ADAPTER_AVAILABLE,
        ("usoal-orpheus-luganda-family", "mms-lazy"),
        "Optional MMS pack is lazy-downloadable; published model licence is non-commercial.",
    ),
    LanguageDefinition(
        "sw",
        "swa",
        "Kiswahili",
        "East Africa",
        ADAPTER_AVAILABLE,
        ("mms-lazy",),
        "Optional MMS pack is lazy-downloadable; published model licence is non-commercial.",
    ),
    LanguageDefinition(
        "rw",
        "kin",
        "Kinyarwanda",
        "East Africa",
        ADAPTER_AVAILABLE,
        ("mms-kinyarwanda-eval",),
        "Optional MMS evaluation route; published model licence is non-commercial.",
    ),
    LanguageDefinition(
        "rn",
        "run",
        "Kirundi",
        "East Africa",
        ADAPTER_AVAILABLE,
        ("mms-kirundi-eval",),
        "Optional MMS evaluation route; published model licence is non-commercial.",
    ),
    LanguageDefinition(
        "ki",
        "kik",
        "Gikuyu",
        "East Africa",
        ADAPTER_AVAILABLE,
        ("mms-gikuyu-eval",),
        "Optional MMS evaluation route; published model licence is non-commercial.",
    ),
    LanguageDefinition(
        "kam",
        "kam",
        "Kamba",
        "East Africa",
        PLANNED,
        (),
        "No accepted local model route is currently registered.",
    ),
    LanguageDefinition(
        "luy",
        "luy",
        "Luhya",
        "East Africa",
        PLANNED,
        (),
        "No accepted local model route is currently registered.",
    ),
    LanguageDefinition(
        "luo",
        "luo",
        "Dholuo",
        "East Africa",
        PLANNED,
        (),
        "No accepted local model route is currently registered.",
    ),
    LanguageDefinition(
        "zu",
        "zul",
        "isiZulu",
        "Southern Africa",
        PLANNED,
        (),
        "No accepted local model route is currently registered.",
    ),
    LanguageDefinition(
        "xh",
        "xho",
        "isiXhosa",
        "Southern Africa",
        PLANNED,
        (),
        "No accepted local model route is currently registered.",
    ),
    LanguageDefinition(
        "st",
        "sot",
        "Sesotho",
        "Southern Africa",
        PLANNED,
        (),
        "No accepted local model route is currently registered.",
    ),
    LanguageDefinition(
        "nso",
        "nso",
        "Sepedi / Northern Sotho",
        "Southern Africa",
        ADAPTER_AVAILABLE,
        ("mms-lazy",),
        "Optional MMS pack is lazy-downloadable; published model licence is non-commercial.",
    ),
    LanguageDefinition(
        "tn",
        "tsn",
        "Setswana",
        "Southern Africa",
        PLANNED,
        (),
        "No accepted local model route is currently registered.",
    ),
    LanguageDefinition(
        "ve",
        "ven",
        "Tshivenda",
        "Southern Africa",
        ADAPTER_AVAILABLE,
        ("mms-lazy",),
        "Optional MMS pack is lazy-downloadable; published model licence is non-commercial.",
    ),
    LanguageDefinition(
        "ts",
        "tso",
        "Xitsonga",
        "Southern Africa",
        ADAPTER_AVAILABLE,
        ("mms-tsonga-eval",),
        "Optional MMS evaluation route; published model licence is non-commercial.",
    ),
    LanguageDefinition(
        "ss",
        "ssw",
        "siSwati",
        "Southern Africa",
        PLANNED,
        (),
        "No accepted local model route is currently registered.",
    ),
    LanguageDefinition(
        "nr",
        "nbl",
        "isiNdebele",
        "Southern Africa",
        PLANNED,
        (),
        "No accepted local model route is currently registered.",
    ),
    LanguageDefinition(
        "sn",
        "sna",
        "Shona",
        "Southern Africa",
        ADAPTER_AVAILABLE,
        ("mms-shona-eval",),
        "Optional MMS evaluation route; published model licence is non-commercial.",
    ),
    LanguageDefinition(
        "ny",
        "nya",
        "Chichewa / Nyanja",
        "Southern Africa",
        ADAPTER_AVAILABLE,
        ("mms-chichewa-eval",),
        "Optional MMS evaluation route; published model licence is non-commercial.",
    ),
)

LANGUAGE_REGISTRY = {definition.code: definition for definition in _LANGUAGE_ROWS}
_LANGUAGE_ALIASES = {definition.iso639_3: definition.code for definition in _LANGUAGE_ROWS} | {
    "luganda": "lg",
    "zulu": "zu",
    "xhosa": "xh",
    "sotho": "st",
    "tswana": "tn",
    "shona": "sn",
    "venda": "ve",
}


def normalize_language_code(value: str | None) -> str:
    """Return a stable BCP-47 base code or raise a client-safe error."""
    candidate = (value or "en").strip().lower().replace("_", "-")
    base = candidate.split("-", maxsplit=1)[0]
    normalized = _LANGUAGE_ALIASES.get(base, base)
    if normalized not in LANGUAGE_REGISTRY:
        raise LanguageRegistryError(f"Unknown Nastech language '{value}'.")
    return normalized


def _resolved_language(definition: LanguageDefinition) -> LanguageDefinition:
    """Reflect an explicitly configured Luganda local pack without auto-enabling it."""
    if definition.code == "lg":
        from .providers import ACTIVE_LOCAL, get_provider

        if get_provider("coqui-luganda-openbible").state == ACTIVE_LOCAL:
            return replace(
                definition,
                state=CONFIGURED_LOCAL,
                availability_note=(
                    "Configured local Luganda VITS technical preview; native reviewer approval "
                    "is still required before a pure-language claim."
                ),
            )
    return definition


def get_language(value: str | None) -> LanguageDefinition:
    """Resolve a code, ISO identifier, or selected language name."""
    return _resolved_language(LANGUAGE_REGISTRY[normalize_language_code(value)])


def language_inventory() -> dict[str, Any]:
    """Return registry records without claiming planned languages can synthesize."""
    states = {
        state: 0
        for state in (
            VERIFIED_LOCAL,
            CONFIGURED_LOCAL,
            ADAPTER_AVAILABLE,
            RESEARCH_CANDIDATE,
            PLANNED,
            REJECTED,
        )
    }
    resolved = [_resolved_language(definition) for definition in _LANGUAGE_ROWS]
    for definition in resolved:
        states[definition.state] += 1
    return {
        "service": "nastech-tts",
        "language_registry_size": len(_LANGUAGE_ROWS),
        "default_language": "en",
        "states": states,
        "languages": [definition.as_dict() for definition in resolved],
    }


def require_configured_language(value: str | None) -> LanguageDefinition:
    """Require an accepted active language state for direct synthesis."""
    definition = get_language(value)
    if definition.state not in {VERIFIED_LOCAL, CONFIGURED_LOCAL}:
        raise LanguageRegistryError(
            f"Language '{definition.code}' is {definition.state}; it is not enabled for synthesis. "
            "Use /v1/languages to inspect its provider and evidence requirements."
        )
    return definition
