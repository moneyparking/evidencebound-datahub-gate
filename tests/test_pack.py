from __future__ import annotations

import json
from pathlib import Path

import pytest

from evidencebound_datahub.cli import _candidate
from evidencebound_datahub.core import evaluate_candidate
from evidencebound_datahub.pack import ProofPackError, export_proof_pack, verify_proof_pack

ROOT = Path(__file__).resolve().parents[1]


def test_pack_reproduces_and_detects_tampering(tmp_path: Path) -> None:
    context = json.loads((ROOT / "examples/mock-context.json").read_text(encoding="utf-8"))
    candidate = _candidate(context["dataset_urn"], context)
    receipt = evaluate_candidate(candidate, context)
    pack = export_proof_pack(
        tmp_path / "pack",
        candidate=candidate,
        context=context,
        receipt=receipt,
        mcp_read={"status": "CONTROLLED_FIXTURE"},
        mcp_write=None,
    )
    reproduced = verify_proof_pack(pack.path)
    assert reproduced.manifest_body_sha256 == pack.manifest_body_sha256

    with (pack.path / "gate-receipt.json").open("a", encoding="utf-8") as handle:
        handle.write(" ")
    with pytest.raises(ProofPackError, match="ARTIFACT_TAMPERING_DETECTED"):
        verify_proof_pack(pack.path)


def test_evidence_root_is_stable_across_write_back_result(tmp_path: Path) -> None:
    context = json.loads((ROOT / "examples/mock-context.json").read_text(encoding="utf-8"))
    candidate = _candidate(context["dataset_urn"], context)
    receipt = evaluate_candidate(candidate, context)
    first = export_proof_pack(
        tmp_path / "before",
        candidate=candidate,
        context=context,
        receipt=receipt,
        mcp_read={"status": "LIVE_MCP_READ"},
        mcp_write={"status": "NOT_RUN"},
    )
    second = export_proof_pack(
        tmp_path / "after",
        candidate=candidate,
        context=context,
        receipt=receipt,
        mcp_read={"status": "LIVE_MCP_READ"},
        mcp_write={"success": True, "message": "receipt appended"},
    )
    assert first.evidence_root_sha256 == second.evidence_root_sha256
    assert first.manifest_body_sha256 != second.manifest_body_sha256
