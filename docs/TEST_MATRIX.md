# Nastech Compact TTS Test Matrix

## Quality Objective

Nastech Compact maintains **72 collected Python tests**. The suite is intentionally structured around deterministic behavior that can run without model download, GPU access, cloud credentials, or a live network service. Real local synthesis, API smoke tests, package builds, and budget checks remain available as separate release verification commands.

| Test area | Focus | Coverage style |
|---|---|---|
| NastechML baseline | Speech, emotions, sounds, pauses, and English validation | Existing unit tests |
| NastechML matrix | Every allowed sound and emotion, supported prosody, invalid shapes | Parameterized parser tests |
| Compiler baseline | Direct tags, release-dependent warnings, and prosody mapping | Existing unit tests |
| Compiler matrix | Default voice aliases, direct/approximate sound compilation, emotion fidelity | Parameterized compiler tests |
| CPU tuning | Profiles, overrides, and invalid policy configuration | Unit tests |
| Runtime cache | Cache-key isolation, retrieval, LRU eviction, byte bounds, status, and clearing | Unit tests without model loading |
| Agent API baseline | Compile, WAV response, OpenAI alias, diagnostics, and warm-up contracts | Existing FastAPI test-client tests |
| Agent API matrix | Bearer authentication, tool discovery, cache endpoint, invalid markup, capability discovery, and speed mapping | FastAPI test-client tests |

## Required Local Commands

```bash
# Formatting and static analysis.
make lint

# All 72 deterministic Python tests.
pytest -q

# Confirm exact collection count when changing tests.
pytest --collect-only -q

# Build source and wheel distributions, regenerate OpenAPI, and measure bundle size.
make verify
```

## Runtime Verification Commands

The deterministic suite intentionally does not load the real ONNX model. Run these commands on a machine with Supertonic assets when validating a release candidate.

```bash
# Inspect the active local CPU policy and model cache.
nastech-tts status

# Load sessions and create a short local WAV.
nastech-tts warmup

# Validate and compile an example without synthesis.
nastech-tts validate examples/compact_agent_story.xml
nastech-tts compile examples/compact_agent_story.xml

# Synthesize a real local WAV and its manifest.
nastech-tts synthesize examples/compact_agent_story.xml --output output/release_story.wav

# Measure uncached local CPU work.
NASTECH_CPU_PROFILE=balanced \
  nastech-tts benchmark examples/compact_agent_story.xml --runs 3
```

## Contribution Gate

Every pull request should preserve or improve meaningful test coverage. A behavior change must include a test that would have failed before the change, rather than only a test that repeats an existing assertion. Changes to runtime dependencies, package contents, or model assets must also pass `make budget` against the actual target environment.
