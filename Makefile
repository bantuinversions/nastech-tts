.PHONY: install lint test catalog contract build verify compile-example validate-example plan-example synthesize-example clean-example budget openapi serve warmup clear-cache platforms preflight benchmark benchmark-throughput

install:
	python -m pip install -e '.[dev]'

lint:
	ruff format --check src tests scripts
	ruff check src tests scripts

test:
	pytest -q

catalog:
	python scripts/generate_capability_catalog.py

contract:
	python scripts/validate_project_contracts.py

build:
	rm -rf build dist src/nastech_tts.egg-info
	python -m build

openapi:
	python scripts/export_openapi.py

budget:
	python scripts/check_compact_budget.py --runtime $${VIRTUAL_ENV:?activate a virtual environment} --model-cache $${NASTECH_MODEL_CACHE:-$$HOME/.cache/nastech-voice-core} --release . --limit-mib 1024

verify: lint test catalog openapi contract build budget

compile-example:
	nastech-tts compile examples/compact_agent_story.xml --output output/compact_agent_story.compile.json

validate-example:
	nastech-tts validate examples/compact_agent_story.xml --output output/compact_agent_story.validate.json

plan-example:
	nastech-tts plan examples/compact_agent_story.xml --delivery chunked-wav --clean --output output/compact_agent_story.plan.json

synthesize-example:
	nastech-tts synthesize examples/compact_agent_story.xml --output output/compact_agent_story.wav

clean-example:
	nastech-tts clean output/compact_agent_story.wav --output output/compact_agent_story.cleaned.wav --report output/compact_agent_story.cleanup.json

warmup:
	nastech-tts warmup

clear-cache:
	nastech-tts clear-cache

platforms:
	nastech-tts platforms

preflight:
	nastech-tts preflight $${TARGET:-python-cuda}

providers:
	nastech-tts providers

provider-preflight:
	nastech-tts provider-preflight $${PROVIDER:-coqui-cli}

benchmark:
	NASTECH_CPU_PROFILE=$${NASTECH_CPU_PROFILE:-balanced} nastech-tts benchmark examples/compact_agent_story.xml --runs $${RUNS:-3}

benchmark-throughput:
	NASTECH_CPU_PROFILE=throughput nastech-tts benchmark examples/compact_agent_story.xml --runs $${RUNS:-4} --concurrency 2

serve:
	nastech-tts serve --host 127.0.0.1 --port 8765
