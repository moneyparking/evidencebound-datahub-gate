SHELL := /usr/bin/env bash
VENV ?= .venv
PYTHON ?= python3

.PHONY: help install-dev test-repro verify-packs independent-repro live-datahub-smoke serve-judge

help:
	@printf '%s\n' \
	  'make test-repro          Install dev dependencies, validate, and reproduce both retained packs' \
	  'make verify-packs        Reproduce the retained VERIFIED and BLOCKED packs only' \
	  'make independent-repro   Clone into a fresh temporary directory and run independent reproduction' \
	  'make live-datahub-smoke  Run the full local DataHub MCP read/write acceptance path' \
	  'make serve-judge         Serve the static public judge journey on localhost:8000'

$(VENV)/bin/python:
	$(PYTHON) -m venv $(VENV)

install-dev: $(VENV)/bin/python
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -e '.[dev]'

test-repro: install-dev
	PATH="$(CURDIR)/$(VENV)/bin:$$PATH" ./scripts/validate.sh

verify-packs: install-dev
	$(VENV)/bin/evidencebound-datahub verify-pack evidence/controlled-verified
	$(VENV)/bin/evidencebound-datahub verify-pack evidence/controlled-blocked

independent-repro:
	./scripts/run-independent-reproduction.sh

live-datahub-smoke:
	./scripts/run-local-datahub-smoke.sh

serve-judge:
	$(PYTHON) -m http.server 8000 --directory docs/judge
