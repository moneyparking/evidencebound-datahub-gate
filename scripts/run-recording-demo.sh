#!/usr/bin/env bash
set -Eeuo pipefail

mode="read-only"
dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.ORDER_ENTRY_DB.analytics.order_history,PROD)"
output="evidence/recording-demo"

usage() {
  cat <<'EOF'
Usage: scripts/run-recording-demo.sh [options]

Run the exact DataHub MCP path used for judge recording.

Options:
  --read-only             Read DataHub and generate both Proof Packs without metadata mutation.
                          This is the default.
  --writeback             Explicitly append VERIFIED and BLOCKED Native DataHub Description
                          Receipts through the official update_description MCP mutation.
  --dataset-urn <urn>     Dataset to inspect. Defaults to the accepted showcase dataset.
  --output <path>         Output directory. Defaults to evidence/recording-demo.
  -h, --help              Show this help.

Safety:
  --writeback mutates metadata in the configured DataHub instance. Use it only on the local
  hackathon environment after the dataset identity and recording scene are confirmed.
EOF
}

while (($#)); do
  case "$1" in
    --read-only)
      mode="read-only"
      shift
      ;;
    --writeback)
      mode="writeback"
      shift
      ;;
    --dataset-urn)
      dataset_urn="${2:?--dataset-urn requires a value}"
      shift 2
      ;;
    --output)
      output="${2:?--output requires a value}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

command -v evidencebound-datahub >/dev/null 2>&1 || {
  printf 'RESULT=BLOCKED\nREASON=EVIDENCEBOUND_DATAHUB_CLI_NOT_FOUND\n' >&2
  exit 1
}

: "${DATAHUB_GMS_URL:=http://localhost:8080}"
export DATAHUB_GMS_URL

args=(
  demo
  --dataset-urn "$dataset_urn"
  --output "$output"
  --replace-output
)

if [[ "$mode" == "read-only" ]]; then
  args+=(--no-writeback)
  printf 'RECORDING_MODE=READ_ONLY\n'
  printf 'EXPECTED_WRITE_BACK=NOT_RUN\n'
else
  export TOOLS_IS_MUTATION_ENABLED=true
  printf 'RECORDING_MODE=WRITEBACK\n'
  printf 'EXPECTED_WRITE_BACK=PASS\n'
fi

printf 'DATASET_URN=%s\n' "$dataset_urn"
printf 'OUTPUT=%s\n' "$output"
printf 'SCENE_MARKER=DATAHUB_MCP_READ_START\n'

evidencebound-datahub "${args[@]}"

python - "$output/demo-summary.json" "$mode" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

summary_path = Path(sys.argv[1])
mode = sys.argv[2]
summary = json.loads(summary_path.read_text(encoding="utf-8"))
acceptance = summary["acceptance"]
expected_write = "NOT_RUN" if mode == "read-only" else "PASS"
expected = {
    "mcp_read": "PASS",
    "verified_path": "VERIFIED",
    "blocked_path": "BLOCKED",
    "mcp_write_back": expected_write,
}
if acceptance != expected:
    raise SystemExit(
        "RECORDING_DEMO_ACCEPTANCE=BLOCKED\n"
        f"EXPECTED={json.dumps(expected, sort_keys=True)}\n"
        f"ACTUAL={json.dumps(acceptance, sort_keys=True)}"
    )
print("SCENE_MARKER=VERIFIED_AND_BLOCKED_COMPLETE")
print(f"SCENE_MARKER=MCP_WRITE_BACK_{expected_write}")
print("RECORDING_DEMO_ACCEPTANCE=PASS")
PY
