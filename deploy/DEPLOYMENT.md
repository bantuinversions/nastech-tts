# Nastech Compact Deployment

Nastech Compact is a **single local service**. It contains the Nastech agent API and uses Supertonic 3 ONNX assets on the same CPU host. It has no cloud TTS dependency and needs no GPU.

## Size Contract

The target maximum full deployment budget is **1 GiB**. On this cloud, the actual Supertonic model cache is 386 MiB and the isolated Python environment is 181 MiB, yielding a measured local runtime subtotal of 567 MiB before generated audio. Use the included budget script after every dependency or model update.

```bash
python scripts/check_compact_budget.py \
  --runtime /path/to/.venv \
  --model-cache ~/.cache/supertonic3 \
  --limit-mib 1024
```

Generated WAV files are runtime data; keep them in a mounted output directory or object storage rather than in a model image.

## Python Deployment

```bash
python -m venv .venv
source .venv/bin/activate
pip install 'nastech-tts[dev]'
export NASTECH_API_KEY='choose-a-secret'
nastech-tts status
nastech-tts serve --host 127.0.0.1 --port 8765
```

The first real synthesis downloads the model assets. Run a short synthesis during image or deployment preparation so traffic does not pay the first-download cost.

## Docker Deployment

The Dockerfile pre-downloads the actual Supertonic assets at build time. Build and measure it locally:

```bash
docker build -t nastech-compact:0.4.0 .
docker images nastech-compact:0.4.0

docker run --rm -p 8765:8765 \
  -e NASTECH_API_KEY='choose-a-secret' \
  nastech-compact:0.4.0
```

Check readiness with `GET /v1/health`, then make one `POST /v1/agent/compile` call before routing requests to the instance.

## Agent Authentication

Set `NASTECH_API_KEY` outside source control. Protected endpoints require:

```text
Authorization: Bearer <NASTECH_API_KEY>
```

Put any Internet-facing deployment behind TLS and a reverse proxy. If a local device is the deployment target, bind to loopback by default and explicitly opt in to a network interface only when needed.

## Persistent-Service Boundary

The current sandbox can build and test the compact system but hibernates when inactive. For a persistent API, deploy the same package or Docker image to a persistent CPU server. No GPU system is required for the selected Supertonic runtime.
