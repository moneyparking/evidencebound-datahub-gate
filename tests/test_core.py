from __future__ import annotations

import copy
import json
from pathlib import Path

from evidencebound_datahub.cli import _candidate
from evidencebound_datahub.core import evaluate_candidate

ROOT = Path(__file__).resolve().parents[1]


def context() -> dict:
    return json.loads((ROOT / "examples/mock-context.json").read_text(encoding="utf-8"))


def test_verified_candidate_executes_and_remains_human_gated() -> None:
    raw_context = context()
    candidate = _candidate(raw_context["dataset_urn"], raw_context)
    receipt = evaluate_candidate(candidate, raw_context)
    assert receipt.verdict == "VERIFIED"
    assert receipt.reasons == ()
    assert receipt.runtime_result_sha256 is not None
    assert receipt.human_approval_required is True
    assert receipt.promotion_authorized is False


def test_stale_schema_fails_closed() -> None:
    raw_context = context()
    candidate = _candidate(raw_context["dataset_urn"], raw_context)
    candidate["expected_schema_sha256"] = "0" * 64
    receipt = evaluate_candidate(candidate, raw_context)
    assert receipt.verdict == "BLOCKED"
    assert "SCHEMA_MISMATCH" in receipt.reasons
    assert receipt.runtime_result_sha256 is None


def test_unbound_claim_is_blocked() -> None:
    raw_context = context()
    candidate = _candidate(raw_context["dataset_urn"], raw_context)
    candidate["claims"][0]["evidence_refs"] = []
    receipt = evaluate_candidate(candidate, raw_context)
    assert receipt.verdict == "BLOCKED"
    assert "CLAIM_UNBOUND:claim.schema-lineage-bound-transform" in receipt.reasons


def test_import_and_attribute_access_are_blocked() -> None:
    raw_context = context()
    candidate = _candidate(raw_context["dataset_urn"], raw_context)
    candidate["source_code"] = (
        "import os\n"
        "def transform(row):\n"
        "    return {\"x\": os.getenv(\"X\")}\n"
    )
    receipt = evaluate_candidate(candidate, raw_context)
    assert receipt.verdict == "BLOCKED"
    assert any(reason.startswith("AST_NODE_BLOCKED") for reason in receipt.reasons)
    assert "CALL_NOT_ALLOWED" in receipt.reasons


def test_dataset_identity_mismatch_is_blocked() -> None:
    raw_context = context()
    candidate = _candidate(raw_context["dataset_urn"], raw_context)
    changed = copy.deepcopy(raw_context)
    changed["dataset_urn"] = "urn:li:dataset:(urn:li:dataPlatform:postgres,other.table,PROD)"
    receipt = evaluate_candidate(candidate, changed)
    assert receipt.verdict == "BLOCKED"
    assert "DATASET_IDENTITY_MISMATCH" in receipt.reasons
