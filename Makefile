SHELL := /usr/bin/env bash
VENV ?= .venv
PYTHON ?= python3

.PHONY: help install-dev test-repro verify-packs independent-repro live-datahub-smoke serve-judge recording-demo-read-only recording-demo-writeback

help:
	@printf '%s\n' \
	  'make test-repro               Install dev dependencies, validate, and reproduce both retained packs' \
	  'make verify-packs             Reproduce the retained VERIFIED and BLOCKED packs only' \
	  'make independent-repro        Clone into a fresh temporary directory and run independent reproduction' \
	  'make live-datahub-smoke       Run the full local DataHub MCP read/write acceptance path' \
	  'make recording-demo-read-only Run the exact OBS recording path without metadata mutation' \
	  'make recording-demo-writeback Run the explicit local OBS recording path with native write-back' \
	  'make serve-judge              Serve the static public judge journey on localhost:8000'

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

recording-demo-read-only: install-dev
	PATH="$(CURDIR)/$(VENV)/bin:$$PATH" ./scripts/run-recording-demo.sh --read-only

recording-demo-writeback: install-dev
	PATH="$(CURDIR)/$(VENV)/bin:$$PATH" ./scripts/run-recording-demo.sh --writeback

serve-judge:
	$(PYTHON) -m http.server 8000 --directory docs/judge
