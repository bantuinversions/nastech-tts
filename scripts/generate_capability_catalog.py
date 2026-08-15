"""Generate the Nastech 500-capability catalog from a compact, reviewable taxonomy."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "CAPABILITY_CATALOG_500.md"

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

DOMAINS = [
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


def main() -> int:
    rows: list[str] = [
        "# Nastech 500-Capability Catalog",
        "",
        (
            "This catalog is a **product and research roadmap**, not a claim that 500 features "
            "already work. Every item is classified by a delivery state so cross-platform, GPU, "
            "mobile, cloning, and training work is not misrepresented. The source evidence and "
            "platform constraints are recorded in "
            "[cross_platform_research_notes.md](cross_platform_research_notes.md)."
        ),
        "",
        "| Delivery class | Meaning |",
        "|---|---|",
        (
            "| `implemented/core` | Available in the current Compact runtime and covered by tests "
            "or release verification. |"
        ),
        (
            "| `implemented plus planned` | A core exists; the listed extension "
            "needs implementation and tests. |"
        ),
        (
            "| `planned/... validation required` | Requires a provider/device/runtime "
            "compatibility test before it can be advertised. |"
        ),
        (
            "| `planned/consent required` | Requires consent, abuse-prevention, and policy design "
            "before implementation. |"
        ),
        (
            "| `research and license gate` | Requires model/data/license review and a separately "
            "measured deployment decision. |"
        ),
        "",
        "## Catalog Index",
        "",
        (
            "The catalog contains 20 domains × 25 capability records = **500 records**. Each "
            "record is a concrete engineering deliverable: an interface, control, validation, "
            "test, safety guardrail, metric, documentation artifact, or acceptance criterion."
        ),
        "",
    ]
    capability_id = 1
    for domain, delivery_class in DOMAINS:
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
    rows.extend(
        [
            "## Verification Rule",
            "",
            " ".join(
                (
                    "A record moves to `implemented/core` only when code and tests are committed.",
                    "Documentation, budget, and relevant platform proof must accompany them.",
                    "GPU/Android profiles need actual execution-provider/device validation.",
                    "Voice-cloning and training profiles need model/license/consent review.",
                    "The catalog rejects unsupported claims.",
                )
            ),
            "",
            f"**Generated record count:** {capability_id - 1}.",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(rows), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
