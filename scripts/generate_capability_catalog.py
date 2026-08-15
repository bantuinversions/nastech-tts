"""Generate the Nastech foundation, research-expansion, and combined capability catalogs."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOUNDATION_OUTPUT = ROOT / "docs" / "CAPABILITY_CATALOG_500.md"
EXPANSION_OUTPUT = ROOT / "docs" / "CAPABILITY_EXPANSION_500.md"
MASTER_OUTPUT = ROOT / "docs" / "CAPABILITY_CATALOG_1000.md"

DIMENSIONS = [
    "core interface",
    "configuration profile",
    "input validation",
    "structured metadata",
    "preflight compatibility check",
    "error taxonomy",
    "performance metric",
    "fallback policy",
    "default behavior",
    "advanced behavior",
    "deterministic fixture",
    "unit-test coverage",
    "integration-test coverage",
    "documentation page",
    "worked example",
    "CLI control",
    "REST control",
    "SDK binding",
    "security guardrail",
    "privacy control",
    "audit record",
    "observability signal",
    "CI validation",
    "release checklist item",
    "acceptance benchmark",
]

FOUNDATION_DOMAINS = [
    ("Text intake and normalization", "implemented/core"),
    ("NastechML and semantic markup", "implemented/core"),
    ("Pronunciation and linguistic controls", "planned/validation required"),
    ("Voice selection and speaker governance", "planned/consent required"),
    ("Prosody and expression control", "implemented plus validation-gated"),
    ("Audio rendering and file formats", "implemented/core"),
    ("Audio cleanup and mastering hygiene", "implemented plus planned"),
    ("Chunked delivery and real-time interaction", "implemented transfer plus model-gated"),
    ("Agent orchestration and tool use", "implemented plus planned"),
    ("HTTP APIs, SDKs, and interoperability", "implemented plus planned"),
    ("CPU inference and capacity control", "implemented/core"),
    ("GPU and hardware-accelerator execution", "planned/provider validation required"),
    ("Android, iOS, and mobile deployment", "planned/device validation required"),
    ("Desktop, browser, and edge clients", "planned/runtime validation required"),
    ("Data preparation, adaptation, and training", "research and license gate"),
    ("Quality evaluation and listening acceptance", "implemented plus planned"),
    ("Reliability, diagnostics, and observability", "implemented plus planned"),
    ("Privacy, safety, consent, and abuse prevention", "planned/policy required"),
    ("Deployment, packaging, and release engineering", "implemented plus planned"),
    ("Developer workflow, documentation, and community", "implemented plus planned"),
]

EXPANSION_DOMAINS = [
    ("Accessible reader semantics and multimodal navigation", "planned/client validation required"),
    ("Audio-description authoring and timed media delivery", "planned/media validation required"),
    ("Voice identity consent, verification, and revocation", "planned/consent required"),
    ("Speaker adaptation and controlled personalization", "research and license gate"),
    ("Voice conversion and transformed-speech safeguards", "planned/consent required"),
    ("Dialogue, multi-speaker, and scene choreography", "planned/model validation required"),
    (
        "Conversational turn, barge-in, and interruption handling",
        "planned/interaction validation required",
    ),
    ("Incremental synthesis and low-latency playout", "planned/model validation required"),
    (
        "Post-processing, restoration, and spatial-audio workflows",
        "planned/audio validation required",
    ),
    (
        "Speech analytics, alignment, and transcript-quality assurance",
        "planned/integration validation required",
    ),
    (
        "Accessibility preferences, reading aids, and cognitive supports",
        "planned/client validation required",
    ),
    (
        "Media authoring, timed text, and description-track workflows",
        "planned/media validation required",
    ),
    ("Provenance, content credentials, and audit trails", "planned/security validation required"),
    ("Safety, abuse prevention, consent, and red-team evaluation", "planned/policy required"),
    (
        "Quality metrics, human studies, and benchmark governance",
        "planned/evaluation validation required",
    ),
    ("Data governance, annotation, licensing, and retention", "research and license gate"),
    ("Fine-tuning, adaptation, and model-lifecycle management", "research and license gate"),
    ("Hardware power, thermal, and energy measurement", "planned/device validation required"),
    ("Enterprise integration, policy, and compliance", "planned/integration validation required"),
    ("Ecosystem plugins, templates, and stewardship", "planned/ecosystem validation required"),
]


class CatalogError(RuntimeError):
    """Raised when a declared catalog taxonomy is not internally consistent."""


def _legend() -> list[str]:
    return [
        "| Delivery class | Meaning |",
        "|---|---|",
        (
            "| `implemented/core` | Available in the Compact runtime and covered by tests or "
            "release verification. |"
        ),
        (
            "| `implemented plus planned` | A core exists; the listed extension "
            "needs implementation and tests. |"
        ),
        (
            "| `planned/... validation required` | Requires provider, device, runtime, "
            "client, media, or evaluation evidence before advertisement. |"
        ),
        (
            "| `planned/consent required` | Requires consent, abuse prevention, and policy design "
            "before implementation. |"
        ),
        (
            "| `research and license gate` | Requires model, data, license, and deployment-budget "
            "review before implementation. |"
        ),
    ]


def _catalog_rows(
    *,
    title: str,
    introduction: str,
    domains: list[tuple[str, str]],
    start_id: int,
    include_legend: bool,
    evidence_link: str,
) -> tuple[list[str], int]:
    """Build one deterministic catalog section and return its next numeric identifier."""
    expected_records = len(domains) * len(DIMENSIONS)
    if expected_records != 500:
        raise CatalogError("Every catalog tranche must contain exactly 500 records.")

    rows = [f"# {title}", "", introduction, ""]
    if include_legend:
        rows.extend(_legend())
        rows.append("")
    rows.extend(
        [
            "## Catalog Index",
            "",
            " ".join(
                (
                    f"This tranche contains {len(domains)} domains × {len(DIMENSIONS)} records =",
                    f"**{expected_records} records**.",
                    "Each record is an interface, control, validation, test, safety guardrail,",
                    "metric, documentation artifact, or acceptance criterion.",
                    f"Evidence is recorded in [{evidence_link}]({evidence_link}).",
                )
            ),
            "",
        ]
    )

    capability_id = start_id
    for domain, delivery_class in domains:
        rows.extend(
            [
                f"## {domain}",
                "",
                f"Default delivery class: `{delivery_class}`.",
                "",
                "| ID | Capability record | Delivery class |",
                "|---:|---|---|",
            ]
        )
        for dimension in DIMENSIONS:
            rows.append(f"| {capability_id} | {domain} — {dimension} | `{delivery_class}` |")
            capability_id += 1
        rows.append("")
    return rows, capability_id


def _verification_rule(total_records: int) -> list[str]:
    return [
        "## Verification Rule",
        "",
        " ".join(
            (
                "A record moves to `implemented/core` only when code and tests are committed.",
                "Documentation, budget, and relevant platform proof must accompany them.",
                "GPU/mobile profiles need actual execution-provider and device validation.",
                "Voice identity, conversion, and training profiles need model, license,",
                "and consent review.",
                "Provenance profiles need the stated cryptographic or audit evidence.",
                "The catalog rejects unsupported claims.",
            )
        ),
        "",
        f"**Generated record count:** {total_records}.",
        "",
    ]


def _write(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join(rows), encoding="utf-8")


def main() -> int:
    foundation_intro = " ".join(
        (
            "This foundation catalog is a **product and research roadmap**.",
            "It does not claim that all 500 features already work.",
            "Every item is classified by delivery state so GPU, mobile, cloning, and training work",
            "is not misrepresented. Source evidence appears in the linked",
            "[cross_platform_research_notes.md](cross_platform_research_notes.md).",
        )
    ).replace("] (", "](")
    expansion_intro = " ".join(
        (
            "This second tranche adds **500 research-grounded capability records**.",
            "They cover accessibility, media description, voice identity governance, analytics,",
            "provenance, evaluation, and production maturity.",
            "It is a roadmap, not a claim that these capabilities are bundled",
            "in the Compact runtime.",
        )
    )
    master_intro = " ".join(
        (
            "Nastech maintains a transparent **1,000-record capability roadmap**: 500 foundation",
            "records and 500 research-expansion records. Delivery classes prevent a broad plan",
            "from becoming an unsupported product claim.",
        )
    )

    foundation_rows, after_foundation = _catalog_rows(
        title="Nastech 500-Capability Foundation Catalog",
        introduction=foundation_intro,
        domains=FOUNDATION_DOMAINS,
        start_id=1,
        include_legend=True,
        evidence_link="cross_platform_research_notes.md",
    )
    foundation_rows.extend(_verification_rule(after_foundation - 1))
    _write(FOUNDATION_OUTPUT, foundation_rows)

    expansion_rows, after_expansion = _catalog_rows(
        title="Nastech Additional 500-Capability Research Expansion",
        introduction=expansion_intro,
        domains=EXPANSION_DOMAINS,
        start_id=501,
        include_legend=True,
        evidence_link="CAPABILITY_EXPANSION_RESEARCH.md",
    )
    expansion_rows.extend(_verification_rule(after_expansion - 501))
    _write(EXPANSION_OUTPUT, expansion_rows)

    master_rows = ["# Nastech 1,000-Capability Catalog", "", master_intro, ""]
    master_rows.extend(_legend())
    master_rows.extend(["", "## Foundation Tranche", ""])
    master_rows.extend(
        foundation_rows[
            foundation_rows.index("## Catalog Index") : foundation_rows.index(
                "## Verification Rule"
            )
        ]
    )
    master_rows.extend(["## Research Expansion Tranche", ""])
    master_rows.extend(
        expansion_rows[
            expansion_rows.index("## Catalog Index") : expansion_rows.index("## Verification Rule")
        ]
    )
    master_rows.extend(_verification_rule(after_expansion - 1))
    _write(MASTER_OUTPUT, master_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
