# Repository Automation and Templates

Nastech Compact includes a small, reviewable GitHub automation layer. The workflows favor deterministic local checks and draft releases; they do not send text to a cloud TTS provider and do not publish packages automatically to PyPI.

| YAML or template | Trigger or use | Maintainer outcome |
|---|---|---|
| `.github/workflows/ci.yml` | Pushes, pull requests, manual runs, and daily at 03:17 UTC | Runs formatting, static analysis, the 90-test suite on Python 3.10–3.12, generated 500-capability catalog drift checks, JSON/YAML contract checks, OpenAPI drift check, package build, distribution metadata check, and artifact upload |
| `.github/workflows/release.yml` | Pushed `v*` tags or manual release run | Rebuilds and checks a tagged distribution, then creates a **draft** GitHub release for human approval |
| `.github/dependabot.yml` | Monthly | Opens limited dependency and GitHub Actions update pull requests |
| `.github/ISSUE_TEMPLATE/*.yml` | New issue | Collects reproducible, redacted bug reports or constrained feature requests |
| `.github/PULL_REQUEST_TEMPLATE.md` | New pull request | Prompts for test evidence, API impacts, CPU/budget review, and security checks |
| `.github/labels.yml` | Repository setup reference | Defines consistent triage, dependency, API, CPU-performance, and documentation labels |
| `project-summary.yml` | Agent, CI, and integration reference | Provides a compact machine-readable product, runtime, quality, budget, and tool summary |

## Applying Repository Labels

The labels template is intentionally versioned rather than applied through an opaque workflow. A maintainer can review it and apply it with the GitHub CLI:

```bash
gh label create "cpu-performance" --color "0e8a16" --description "CPU policy, queue, cache, warm-up, or benchmark change."
```

Repeat the command for each entry in `.github/labels.yml`, or use a repository-administration script that reads the YAML after review. This explicit process avoids silently changing organization-level GitHub metadata.

## Release Safety

The release workflow uses a draft release so a maintainer can inspect distributions, checksums, license notices, release notes, and model-license boundaries before publishing it publicly. PyPI publishing remains a separate deliberate step requiring credentials and a verified release checklist.

## Local Parity

Before relying on hosted CI, run the same core checks locally. The hosted workflow also runs automatically every day at **03:17 UTC**:

```bash
make lint
pytest -q
make catalog
make openapi
make contract
make verify
```

The CI workflow verifies that regenerating both `docs/CAPABILITY_CATALOG_500.md` and `docs/openapi.json` produces no uncommitted drift. When a taxonomy or API change is intentional, regenerate the relevant artifact locally and commit the updated contract with its tests.
