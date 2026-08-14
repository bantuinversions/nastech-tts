# Nastech TTS Deployment

## What Deploys Where

Nastech has two separate services. The **Nastech Agent Gateway** is a small Python/HTTP service. The **Fish S2 provider** is a GPU model server that performs actual expressive speech generation. Separating them makes the agent API portable while allowing the heavy model to run on dedicated GPU infrastructure.

| Service | Minimum responsibility | Runtime requirement |
|---|---|---|
| Nastech Gateway | NastechML, authentication, behavior compilation, manifests, API routing | Python 3.10+ or Docker |
| Fish S2 Provider | Real emotion/event synthesis and voice generation | Persistent GPU-capable host with official Fish Speech setup |

## Self-hosted Provider Mode

First, deploy Fish Speech S2 on a GPU machine by following the [official server guide](https://speech.fish.audio/server/). Protect that server with its own `--api-key` when it is reachable outside a private network.

Then deploy the Nastech gateway on a host that can reach the Fish server:

```bash
cp deploy/.env.example deploy/.env
# Edit deploy/.env:
# NASTECH_PROVIDER=fish-local
# FISH_BASE_URL=http://fish-s2.internal:8080
# FISH_LOCAL_API_KEY=...
# NASTECH_API_KEY=...

docker compose --env-file deploy/.env -f deploy/docker-compose.gateway.yml up -d --build
curl http://127.0.0.1:8765/v1/health
```

## Hosted Provider Mode

For the official managed route, do not add a provider token to this repository. Set it only in the deployment secret manager or runtime environment:

```bash
export NASTECH_PROVIDER=fish-cloud
export FISH_AUDIO_API_KEY='provider-key-from-fish-audio'
export FISH_CLOUD_MODEL=s2.1-pro-free
export NASTECH_API_KEY='gateway-secret'
nastech-tts serve --host 127.0.0.1 --port 8765
```

The Fish cloud route follows the official `/v1/tts` API. Nastech forwards a W3C `traceparent` header when an agent includes one.

## Agent Authentication

Set `NASTECH_API_KEY` in production. Client requests must then include:

```text
Authorization: Bearer <NASTECH_API_KEY>
```

Place the public gateway behind TLS and a reverse proxy. Do not expose a self-hosted Fish model port publicly unless it is separately authenticated and network-restricted.

## Health and Readiness

The Nastech health endpoint is `GET /v1/health`. It reports the configured provider mode and, for a local provider, checks the upstream `GET /v1/health` endpoint. `POST /v1/agent/compile` is the safest readiness check because it validates NastechML and produces the exact provider payload without generating audio.

## Persistence Boundary

The default sandbox is for development and verification only; it hibernates and does not offer GPU hosting. Production requires a persistent deployment target for the gateway and a GPU-capable environment for a self-hosted Fish S2 provider, or the official hosted provider route.
