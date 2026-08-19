"""Truthful regional language registry for Nastech TTS provider selection.

The registry distinguishes an explicit language target from a runnable local
model route. A displayed label always begins with the short selection code,
for example ``lg - Luganda``.
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

    @property
    def display_label(self) -> str:
        """Return the clear code-first label shown in Nastech inventories."""

        return f"{self.code} - {self.label}"

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["provider_ids"] = list(self.provider_ids)
        result["display_label"] = self.display_label
        return result


MMS_LAZY_CODES = frozenset(
    {
        "ach",
        "bem",
        "bss",
        "cwe",
        "flr",
        "gog",
        "hay",
        "heh",
        "kde",
        "ki",
        "ksb",
        "lg",
        "lon",
        "mgh",
        "myx",
        "ngl",
        "nyn",
        "ny",
        "nyf",
        "nyo",
        "nyy",
        "rn",
        "ruf",
        "rw",
        "seh",
        "sn",
        "suk",
        "sw",
        "teo",
        "toh",
        "ts",
        "vmw",
        "xog",
        "yao",
        "ziw",
    }
)

_MMS_NOTE = (
    "Optional MMS pack is lazy-downloadable after explicit request; the published "
    "checkpoint licence is non-commercial and native-language review is still required."
)
_PLANNED_NOTE = "No verified local checkpoint is currently mapped for this language target."

# The product-facing catalog covers major and representative Bantu-speaking
# communities from East Africa through Central and Southern Africa. Neighbouring
# regional languages already requested by users are retained and explicitly marked.
_BANTU_TARGETS = (
    # East Africa and Great Lakes
    ("lg", "lug", "Luganda", "Uganda / Great Lakes"),
    ("nyn", "nyn", "Runyankole", "Uganda / Great Lakes"),
    ("ach", "ach", "Acholi", "Uganda / Great Lakes"),
    ("teo", "teo", "Ateso", "Uganda"),
    ("sw", "swa", "Kiswahili", "East Africa"),
    ("rw", "kin", "Kinyarwanda", "Great Lakes"),
    ("rn", "run", "Kirundi", "Great Lakes"),
    ("ki", "kik", "Gikuyu", "Kenya"),
    ("kam", "kam", "Kamba", "Kenya"),
    ("luy", "luy", "Luhya", "Kenya"),
    ("luo", "luo", "Dholuo", "Kenya"),
    ("flr", "flr", "Fuliiru", "Great Lakes"),
    ("nyf", "nyf", "Kigiryama", "Kenya"),
    ("myx", "myx", "Masaaba", "Uganda / Kenya"),
    ("xog", "xog", "Lusoga", "Uganda"),
    ("nyo", "nyo", "Runyoro", "Uganda"),
    ("nyy", "nyy", "Nyakyusa-Ngonde", "Tanzania / Malawi"),
    ("hay", "hay", "Haya", "Tanzania"),
    ("heh", "heh", "Hehe", "Tanzania"),
    ("gog", "gog", "Gogo", "Tanzania"),
    ("ruf", "ruf", "Luguru", "Tanzania"),
    ("cwe", "cwe", "Kwere", "Tanzania"),
    ("ziw", "ziw", "Zigula", "Tanzania / Kenya"),
    ("ksb", "ksb", "Shambala", "Tanzania"),
    ("suk", "suk", "Sukuma", "Tanzania"),
    # Central Africa
    ("bem", "bem", "Bemba", "Zambia / Central Africa"),
    ("bss", "bss", "Akoose", "Cameroon / Central Africa"),
    ("lin", "lin", "Lingala", "Central Africa"),
    ("kon", "kon", "Kikongo", "Central Africa"),
    ("lua", "lua", "Tshiluba", "Democratic Republic of the Congo"),
    ("lub", "lub", "Luba-Katanga", "Democratic Republic of the Congo"),
    ("dua", "dua", "Duala", "Cameroon"),
    ("ewo", "ewo", "Ewondo", "Cameroon"),
    ("fan", "fan", "Fang", "Gabon / Equatorial Guinea / Cameroon"),
    ("kmb", "kmb", "Kimbundu", "Angola"),
    ("umb", "umb", "Umbundu", "Angola"),
    ("cjk", "cjk", "Chokwe", "Angola / Democratic Republic of the Congo / Zambia"),
    ("lun", "lun", "Lunda", "Angola / Democratic Republic of the Congo / Zambia"),
    ("lue", "lue", "Luvale", "Angola / Zambia"),
    # Southern Africa
    ("ngl", "ngl", "Lomwe", "Malawi / Mozambique"),
    ("lon", "lon", "Malawi Lomwe", "Malawi"),
    ("vmw", "vmw", "Makhuwa", "Mozambique"),
    ("mgh", "mgh", "Makhuwa-Meetto", "Mozambique"),
    ("kde", "kde", "Makonde", "Mozambique / Tanzania"),
    ("yao", "yao", "Yao", "Malawi / Mozambique / Tanzania"),
    ("seh", "seh", "Sena", "Malawi / Mozambique"),
    ("toh", "toh", "Malawi Tonga", "Malawi"),
    ("tum", "tum", "Tumbuka", "Malawi / Tanzania / Zambia"),
    ("zu", "zul", "isiZulu", "South Africa"),
    ("xh", "xho", "isiXhosa", "South Africa"),
    ("st", "sot", "Sesotho", "Lesotho / South Africa"),
    ("nso", "nso", "Sepedi / Northern Sotho", "South Africa"),
    ("tn", "tsn", "Setswana", "Botswana / South Africa"),
    ("ve", "ven", "Tshivenda", "South Africa"),
    ("ts", "tso", "Xitsonga", "South Africa / Mozambique"),
    ("ss", "ssw", "siSwati", "Eswatini / South Africa"),
    ("nd", "nde", "isiNdebele (Northern)", "Zimbabwe"),
    ("nr", "nbl", "isiNdebele (Southern)", "South Africa"),
    ("sn", "sna", "Shona", "Zimbabwe"),
    ("ny", "nya", "Chichewa / Nyanja", "Malawi / Zambia"),
)


def _regional_definition(
    code: str,
    iso639_3: str,
    label: str,
    region: str,
) -> LanguageDefinition:
    """Build a target whose route is enabled only after a verified checkpoint audit."""

    if code in MMS_LAZY_CODES:
        providers = ("mms-lazy",)
        if code == "lg":
            providers = ("coqui-luganda-openbible", "mms-lazy")
        return LanguageDefinition(
            code,
            iso639_3,
            label,
            region,
            ADAPTER_AVAILABLE,
            providers,
            _MMS_NOTE,
        )
    return LanguageDefinition(code, iso639_3, label, region, PLANNED, (), _PLANNED_NOTE)


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
    *(_regional_definition(*target) for target in _BANTU_TARGETS),
)

LANGUAGE_REGISTRY = {definition.code: definition for definition in _LANGUAGE_ROWS}
_LANGUAGE_ALIASES = {definition.iso639_3: definition.code for definition in _LANGUAGE_ROWS} | {
    "luganda": "lg",
    "ganda": "lg",
    "runyankole": "nyn",
    "runyoro": "nyo",
    "swahili": "sw",
    "kiswahili": "sw",
    "kinyarwanda": "rw",
    "kirundi": "rn",
    "gikuyu": "ki",
    "kikuyu": "ki",
    "zulu": "zu",
    "xhosa": "xh",
    "sotho": "st",
    "sepedi": "nso",
    "tswana": "tn",
    "venda": "ve",
    "tsonga": "ts",
    "shona": "sn",
    "chichewa": "ny",
    "nyanja": "ny",
    "lingala": "lin",
    "kikongo": "kon",
    "tshiluba": "lua",
    "bemba": "bem",
    "makhuwa": "vmw",
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
