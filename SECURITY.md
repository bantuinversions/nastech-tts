# Nastech Research Security and Responsible Use Policy

## Private vulnerability reporting

Please **do not** disclose vulnerabilities, access tokens, private recordings, consent artifacts, or exploit details in public issues or discussions. Use the repository's private [Security Advisories](https://github.com/bantuinversions/nastech-tts/security/advisories/new) channel to report a suspected vulnerability to Nastech Research project stewards.

A useful report identifies the affected release or commit, reproduction steps, expected and actual behavior, impact, and mitigations already tested. Reports involving generated or user-provided speech must use synthetic or appropriately authorized examples.

## Scope

In scope are the Python package, local FastAPI gateway, NastechML parsing, release automation, package supply-chain metadata, documented deployment paths, and release voice-fixture handling. The upstream Supertonic model and its distribution infrastructure are external dependencies; report upstream-model defects to the upstream maintainers as well when appropriate.

## Responsible speech technology use

Do not include API keys, Hugging Face tokens, credentials, consent documents, private audio, model caches, or private production logs in issues, commits, releases, or training manifests. Store consent records separately from model-training data and reference them only with pseudonymous consent identifiers.

Nastech Compact TTS must not be used to impersonate a person without consent, create deceptive calls or news, evade authentication, or train from voices lacking documented permission. Any published Nastech adapter must include a model card and a clear use-policy statement.

## Response principles

Nastech Research aims to acknowledge credible reports promptly, investigate privately, coordinate a fix where possible, and publish a concise disclosure after affected users have a reasonable update path. Response timing depends on severity, reproducibility, and maintainer availability; no response-time guarantee is implied.
