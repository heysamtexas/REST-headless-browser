##########################################################################
# MENU
##########################################################################

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[0-9a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

data/:
	mkdir -p data/

env:
	cp env.example env

.venv/: data/ env
	python -m venv .venv/
	source .venv/bin/activate && pip install --upgrade pip
	source .venv/bin/activate && pip install -r requirements.txt
	source .venv/bin/activate && pip install -r requirements-dev.txt
	source .venv/bin/activate && pre-commit install

.PHONY: boostrap-dev
bootstrap-dev: .venv/ ## Bootstrap the development environment

.PHONY: build
build:
	docker build -t rest-headless-browser .

.PHONY: run
run:
	docker run -p 8000:8000 --rm -it rest-headless-browser
