#!/usr/bin/env python3
"""Generate deterministic verified and stale-schema candidates for examples."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from evidencebound_datahub.cli import _candidate

ROOT = Path(__file__).resolve().parents[1]
context = json.loads((ROOT / "examples/mock-context.json").read_text(encoding="utf-8"))
verified = _candidate(context["dataset_urn"], context)
blocked = copy.deepcopy(verified)
blocked["candidate_id"] = "metadata-bound-transform-stale-schema-v1"
blocked["expected_schema_sha256"] = "0" * 64
for name, value in (("verified-candidate.json", verified), ("blocked-candidate.json", blocked)):
    (ROOT / "examples" / name).write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
