#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/moneyparking/evidencebound-datahub-gate.git}"
REF="${REF:-main}"
ROOT="${1:-$(mktemp -d)}"
REPORT="${REPORT:-$PWD/independent-reproduction-report.txt}"

exec > >(tee "$REPORT") 2>&1

printf 'EVIDENCEBOUND INDEPENDENT REPRODUCTION\n'
printf 'UTC=%s\nREPO=%s\nREF=%s\nROOT=%s\n' \
  "$(date -u +%FT%TZ)" "$REPO_URL" "$REF" "$ROOT"

git clone --depth 1 --branch "$REF" "$REPO_URL" "$ROOT/repo"
cd "$ROOT/repo"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'

./scripts/validate.sh

evidencebound-datahub verify-pack evidence/controlled-verified
evidencebound-datahub verify-pack evidence/controlled-blocked

printf '\nRESULT=PASS\nHEAD=%s\n' "$(git rev-parse HEAD)"
sha256sum evidence/controlled-verified/* evidence/controlled-blocked/* | sort
