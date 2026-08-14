.PHONY: install lint test build verify compile-example serve

install:
	python -m pip install -e '.[dev]'

lint:
	ruff format --check src tests
	ruff check src tests

test:
	pytest -q

build:
	rm -rf build dist src/nastech_tts.egg-info
	python -m build

verify: lint test build

compile-example:
	nastech-tts compile examples/fish_s2_agent_story.xml --output output/fish_s2_agent_story.compile.json

serve:
	nastech-tts serve --host 127.0.0.1 --port 8765
