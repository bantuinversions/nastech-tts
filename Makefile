.PHONY: install lint test build verify compile-example synthesize-example budget openapi serve

install:
	python -m pip install -e '.[dev]'

lint:
	ruff format --check src tests scripts
	ruff check src tests scripts

test:
	pytest -q

build:
	rm -rf build dist src/nastech_tts.egg-info
	python -m build

openapi:
	python scripts/export_openapi.py

budget:
	python scripts/check_compact_budget.py --runtime $${VIRTUAL_ENV:?activate a virtual environment} --model-cache $${NASTECH_MODEL_CACHE:-$$HOME/.cache/supertonic3} --release . --limit-mib 1024

verify: lint test build openapi budget

compile-example:
	nastech-tts compile examples/compact_agent_story.xml --output output/compact_agent_story.compile.json

synthesize-example:
	nastech-tts synthesize examples/compact_agent_story.xml --output output/compact_agent_story.wav

serve:
	nastech-tts serve --host 127.0.0.1 --port 8765
