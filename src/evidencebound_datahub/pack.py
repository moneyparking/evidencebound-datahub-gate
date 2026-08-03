"""Content-addressed Proof Pack export and reproduction."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .core import GateReceipt, canonical_json_bytes, sha256_bytes

MANIFEST_SCHEMA_VERSION = "evidencebound-datahub-manifest/1.0"
PACK_FILES = (
    "candidate.json",
    "datahub-context.json",
    "gate-receipt.json",
    "mcp-read.json",
    "mcp-write.json",
)


class ProofPackError(ValueError):
    """Raised when a Proof Pack cannot be verified."""


@dataclass(frozen=True)
class ProofPackResult:
    path: Path
    evidence_root_sha256: str
    manifest_body_sha256: str
    artifact_sha256: Mapping[str, str]


def _write_canonical(path: Path, value: Any) -> None:
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofPackError(f"PACK_JSON_INVALID:{path.name}") from exc


def export_proof_pack(
    output_dir: str | Path,
    *,
    candidate: Mapping[str, Any],
    context: Mapping[str, Any],
    receipt: GateReceipt,
    mcp_read: Mapping[str, Any],
    mcp_write: Mapping[str, Any] | None,
) -> ProofPackResult:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    artifacts: dict[str, Any] = {
        "candidate.json": candidate,
        "datahub-context.json": context,
        "gate-receipt.json": receipt.to_dict(),
        "mcp-read.json": mcp_read,
        "mcp-write.json": mcp_write or {"status": "NOT_RUN"},
    }
    artifact_sha256: dict[str, str] = {}
    for filename in PACK_FILES:
        _write_canonical(output / filename, artifacts[filename])
        artifact_sha256[filename] = sha256_bytes((output / filename).read_bytes())

    evidence_root_body = {
        "schema_version": "evidencebound-datahub-evidence-root/1.0",
        "dataset_urn": receipt.dataset_urn,
        "candidate_id": receipt.candidate_id,
        "verdict": receipt.verdict,
        "policy_version": receipt.policy_version,
        "artifact_sha256": {
            filename: artifact_sha256[filename]
            for filename in (
                "candidate.json",
                "datahub-context.json",
                "gate-receipt.json",
                "mcp-read.json",
            )
        },
    }
    evidence_root_sha256 = sha256_bytes(canonical_json_bytes(evidence_root_body))
    manifest_body = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "dataset_urn": receipt.dataset_urn,
        "candidate_id": receipt.candidate_id,
        "verdict": receipt.verdict,
        "policy_version": receipt.policy_version,
        "human_approval_required": True,
        "promotion_authorized": False,
        "evidence_root_sha256": evidence_root_sha256,
        "artifact_sha256": artifact_sha256,
    }
    manifest_body_sha256 = sha256_bytes(canonical_json_bytes(manifest_body))
    manifest = {
        "observed_at_utc": datetime.now(UTC).isoformat(),
        "manifest_body": manifest_body,
        "manifest_body_sha256": manifest_body_sha256,
        "optional_cryptographic_seal": None,
    }
    _write_canonical(output / "manifest.json", manifest)
    sums = "".join(
        f"{digest}  {filename}\n"
        for filename, digest in sorted(artifact_sha256.items())
    )
    (output / "SHA256SUMS").write_text(sums, encoding="utf-8")
    return ProofPackResult(output, evidence_root_sha256, manifest_body_sha256, artifact_sha256)


def verify_proof_pack(output_dir: str | Path) -> ProofPackResult:
    output = Path(output_dir)
    if output.is_symlink() or not output.is_dir():
        raise ProofPackError("PACK_PATH_INVALID")
    expected = {*PACK_FILES, "manifest.json", "SHA256SUMS"}
    actual = {path.name for path in output.iterdir() if path.is_file()}
    if actual != expected:
        raise ProofPackError("PACK_FILE_SET_MISMATCH")

    manifest = _read_json(output / "manifest.json")
    manifest_body = manifest.get("manifest_body")
    if not isinstance(manifest_body, dict):
        raise ProofPackError("MANIFEST_BODY_INVALID")
    computed_root = sha256_bytes(canonical_json_bytes(manifest_body))
    if computed_root != manifest.get("manifest_body_sha256"):
        raise ProofPackError("MANIFEST_TAMPERING_DETECTED")

    recorded = manifest_body.get("artifact_sha256")
    if not isinstance(recorded, dict) or set(recorded) != set(PACK_FILES):
        raise ProofPackError("ARTIFACT_BINDINGS_INVALID")
    for filename in PACK_FILES:
        path = output / filename
        if path.is_symlink():
            raise ProofPackError(f"SYMLINK_BLOCKED:{filename}")
        digest = sha256_bytes(path.read_bytes())
        if digest != recorded[filename]:
            raise ProofPackError(f"ARTIFACT_TAMPERING_DETECTED:{filename}")
        value = _read_json(path)
        if path.read_bytes() != canonical_json_bytes(value) + b"\n":
            raise ProofPackError(f"NON_CANONICAL_JSON:{filename}")

    expected_sums = "".join(
        f"{recorded[filename]}  {filename}\n" for filename in sorted(PACK_FILES)
    )
    if (output / "SHA256SUMS").read_text(encoding="utf-8") != expected_sums:
        raise ProofPackError("SHA256SUMS_MISMATCH")
    evidence_root_sha256 = manifest_body.get("evidence_root_sha256")
    evidence_root_body = {
        "schema_version": "evidencebound-datahub-evidence-root/1.0",
        "dataset_urn": manifest_body.get("dataset_urn"),
        "candidate_id": manifest_body.get("candidate_id"),
        "verdict": manifest_body.get("verdict"),
        "policy_version": manifest_body.get("policy_version"),
        "artifact_sha256": {
            filename: recorded[filename]
            for filename in (
                "candidate.json",
                "datahub-context.json",
                "gate-receipt.json",
                "mcp-read.json",
            )
        },
    }
    computed_evidence_root = sha256_bytes(canonical_json_bytes(evidence_root_body))
    if evidence_root_sha256 != computed_evidence_root:
        raise ProofPackError("EVIDENCE_ROOT_MISMATCH")
    return ProofPackResult(output, computed_evidence_root, computed_root, recorded)
