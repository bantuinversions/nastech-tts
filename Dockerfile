FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd --create-home --uid 10001 nastech

COPY pyproject.toml README.md NOTICE.md ./
COPY src ./src
RUN pip install --no-cache-dir .

USER nastech
EXPOSE 8765

ENV NASTECH_PROVIDER=fish-local \
    FISH_BASE_URL=http://host.docker.internal:8080

CMD ["nastech-tts", "serve", "--host", "0.0.0.0", "--port", "8765"]
