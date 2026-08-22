FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/opt/nastech \
    NASTECH_MODEL_CACHE=/opt/nastech/.cache/nastech-voice-core \
    NASTECH_CPU_PROFILE=balanced \
    NASTECH_WARMUP_ON_START=1

WORKDIR /app

RUN useradd --create-home --home-dir /opt/nastech --uid 10001 nastech

COPY pyproject.toml README.md NOTICE.md ./
COPY src ./src
RUN pip install --no-cache-dir . && chown -R nastech:nastech /opt/nastech /app

# Bake the real compact ONNX assets into the image. This is intentionally
# separate from source release artifacts and is checked by the runtime budget script.
USER nastech
RUN python -c "from nastech_voice_core import TTS; TTS(model_dir='/opt/nastech/.cache/nastech-voice-core', auto_download=True)"

EXPOSE 8765

CMD ["nastech-tts", "serve", "--host", "0.0.0.0", "--port", "8765"]
