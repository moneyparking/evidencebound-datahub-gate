#!/usr/bin/env bash
set -Eeuo pipefail

: "${DATAHUB_GMS_URL:=http://localhost:8080}"
export DATAHUB_GMS_URL
export TOOLS_IS_MUTATION_ENABLED=true

python -m pip install --upgrade pip
python -m pip install -e '.[datahub,dev]' 'acryl-datahub>=1.3.1.7,<2'

datahub docker quickstart
datahub datapack load showcase-ecommerce

probe_output="evidence/readiness-probe"
probe_log="evidence/readiness-probe.log"
selected_query=""

# DataHub metadata writes and OpenSearch visibility are eventually consistent.
# Probe without write-back, then perform exactly one final read/write acceptance run.
for attempt in $(seq 1 40); do
  printf 'DATAHUB_SEARCH_READINESS_ATTEMPT=%s/40\n' "$attempt"
  for query in '/q orders' '*'; do
    rm -rf "$probe_output"
    if evidencebound-datahub demo \
      --search-query "$query" \
      --output "$probe_output" \
      --replace-output \
      --no-writeback >"$probe_log" 2>&1; then
      selected_query="$query"
      break 2
    fi
  done
  tail -n 8 "$probe_log" || true
  sleep 15
done

if [[ -z "$selected_query" ]]; then
  cat "$probe_log" >&2 || true
  printf 'RESULT=BLOCKED\nREASON=DATAHUB_SEARCH_INDEX_NOT_READY\n' >&2
  exit 1
fi

printf 'DATAHUB_SEARCH_READINESS=PASS\n'
printf 'SELECTED_SEARCH_QUERY=%s\n' "$selected_query"
rm -rf "$probe_output" "$probe_log"

evidencebound-datahub demo \
  --search-query "$selected_query" \
  --output evidence/live-datahub-smoke \
  --replace-output

python - <<'PY'
import json
from pathlib import Path

path = Path("evidence/live-datahub-smoke/demo-summary.json")
data = json.loads(path.read_text(encoding="utf-8"))
expected = {
    "mcp_read": "PASS",
    "verified_path": "VERIFIED",
    "blocked_path": "BLOCKED",
    "mcp_write_back": "PASS",
}
assert data["acceptance"] == expected, data["acceptance"]
print("DATAHUB_MCP_READ_WRITE_ACCEPTANCE=PASS")
PY
