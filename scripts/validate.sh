#!/usr/bin/env bash
set -euo pipefail
python scripts/build-examples.py
pytest -q
python -m compileall -q src tests scripts
ruff check .
mypy src
rm -rf evidence/controlled-verified evidence/controlled-blocked
set +e
evidencebound-datahub offline \
  --candidate examples/verified-candidate.json \
  --context examples/mock-context.json \
  --output evidence/controlled-verified
verified_exit=$?
evidencebound-datahub offline \
  --candidate examples/blocked-candidate.json \
  --context examples/mock-context.json \
  --output evidence/controlled-blocked
blocked_exit=$?
set -e
[[ "$verified_exit" -eq 0 ]]
[[ "$blocked_exit" -eq 3 ]]
evidencebound-datahub verify-pack evidence/controlled-verified
evidencebound-datahub verify-pack evidence/controlled-blocked
