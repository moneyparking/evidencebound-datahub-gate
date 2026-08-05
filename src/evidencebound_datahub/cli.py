"""Command-line interface for EvidenceBound DataHub Gate."""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .core import (
    SCHEMA_VERSION,
    context_digests,
    evaluate_candidate,
    normalize_context,
)
from .mcp import DataHubMcp
from .pack import ProofPackError, export_proof_pack, verify_proof_pack
from .seal import generate_ed25519_keypair, seal_proof_pack, verify_ed25519_seal


def _source_template(record_field: str, left_field: str, right_field: str) -> str:
    return (
        "def transform(row):\n"
        f"    derived_value = row[{json.dumps(left_field)}] * row[{json.dumps(right_field)}]\n"
        "    return {\"derived_value\": derived_value, "
        f"\"record_id\": row[{json.dumps(record_field)}]}}\n"
    )


def _read_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _candidate(dataset_urn: str, context: Mapping[str, Any]) -> dict[str, Any]:
    schema_sha256, lineage_sha256 = context_digests(context)
    normalized = normalize_context(context)
    fields = [field["fieldPath"] for field in normalized["schema_fields"]]
    if len(fields) < 3:
        raise ValueError("A demo dataset must expose at least three schema fields")
    record_field, left_field, right_field = fields[:3]
    lineage_refs = normalized["lineage_urns"][:1]
    refs = [f"schema:{field}" for field in (record_field, left_field, right_field)]
    refs.extend(f"lineage:{urn}" for urn in lineage_refs)
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": "metadata-bound-transform-v1",
        "dataset_urn": dataset_urn,
        "expected_schema_sha256": schema_sha256,
        "expected_lineage_sha256": lineage_sha256,
        "required_fields": [record_field, left_field, right_field],
        "runtime_fixture": {record_field: "demo-1", left_field: 2, right_field: 1250},
        "source_code": _source_template(record_field, left_field, right_field),
        "claims": [
            {
                "claim_id": "claim.schema-lineage-bound-transform",
                "statement": (
                    "The transform uses fields observed in the selected DataHub dataset and "
                    "is bound to the observed lineage digest."
                ),
                "evidence_refs": refs,
            }
        ],
        "human_approval_required": True,
    }


def _receipt_markdown(receipt_root: str, receipt: Mapping[str, Any]) -> str:
    reasons = ", ".join(receipt["reasons"]) if receipt["reasons"] else "none"
    return (
        "\n\n---\n"
        "### EvidenceBound DataHub Gate\n"
        f"- Verdict: `{receipt['verdict']}`\n"
        f"- Proof Pack root: `sha256:{receipt_root}`\n"
        f"- Candidate: `{receipt['candidate_id']}`\n"
        f"- Schema digest: `sha256:{receipt['schema_sha256']}`\n"
        f"- Lineage digest: `sha256:{receipt['lineage_sha256']}`\n"
        f"- Reasons: `{reasons}`\n"
        "- Human approval: `REQUIRED`\n"
        "- Promotion authorization: `false`\n"
    )


def _export_one(
    output: Path,
    *,
    candidate: dict[str, Any],
    context: dict[str, Any],
    mcp_read: dict[str, Any],
    mcp_write: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], str]:
    receipt = evaluate_candidate(candidate, context)
    result = export_proof_pack(
        output,
        candidate=candidate,
        context=context,
        receipt=receipt,
        mcp_read=mcp_read,
        mcp_write=mcp_write,
    )
    return receipt.to_dict(), result.manifest_body_sha256


async def _demo(args: argparse.Namespace) -> int:
    client = DataHubMcp.from_env()
    if args.dataset_urn:
        dataset_urn = args.dataset_urn
        read = await client.read_context(dataset_urn)
        normalized = normalize_context(read.context)
        if len(normalized["schema_fields"]) < 3 or not normalized["lineage_urns"]:
            raise RuntimeError(
                "The selected dataset must expose at least three schema fields and one visible "
                "upstream or downstream lineage edge."
            )
    else:
        read = None
        dataset_urn = ""
        inspected: list[str] = []
        for candidate_urn in await client.discover_datasets(args.search_query):
            inspected.append(candidate_urn)
            candidate_read = await client.read_context(candidate_urn)
            normalized = normalize_context(candidate_read.context)
            if len(normalized["schema_fields"]) >= 3 and normalized["lineage_urns"]:
                dataset_urn = candidate_urn
                read = candidate_read
                break
        if read is None:
            raise RuntimeError(
                "No discovered dataset exposed both at least three schema fields and lineage. "
                f"Inspected {len(inspected)} dataset(s)."
            )
    assert read is not None
    baseline = _candidate(dataset_urn, read.context)

    root = Path(args.output)
    if root.exists():
        if not args.replace_output:
            raise FileExistsError(f"output exists: {root}")
        shutil.rmtree(root)
    root.mkdir(parents=True)

    verified_candidate = copy.deepcopy(baseline)
    blocked_candidate = copy.deepcopy(baseline)
    blocked_candidate["candidate_id"] = "metadata-bound-transform-stale-schema-v1"
    blocked_candidate["expected_schema_sha256"] = "0" * 64

    summaries: list[dict[str, Any]] = []
    for name, candidate in (("verified", verified_candidate), ("blocked", blocked_candidate)):
        receipt = evaluate_candidate(candidate, read.context)
        provisional_write = {"status": "NOT_RUN"}
        pack = export_proof_pack(
            root / name,
            candidate=candidate,
            context=read.context,
            receipt=receipt,
            mcp_read=read.raw,
            mcp_write=provisional_write,
        )
        write_result: dict[str, Any] | None = None
        if not args.no_writeback:
            write_result = await client.write_receipt(
                dataset_urn=dataset_urn,
                markdown=_receipt_markdown(pack.evidence_root_sha256, receipt.to_dict()),
            )
            shutil.rmtree(root / name)
            pack = export_proof_pack(
                root / name,
                candidate=candidate,
                context=read.context,
                receipt=receipt,
                mcp_read=read.raw,
                mcp_write=write_result,
            )
        verify_proof_pack(root / name)
        summaries.append(
            {
                "path": name,
                "verdict": receipt.verdict,
                "reasons": list(receipt.reasons),
                "evidence_root_sha256": pack.evidence_root_sha256,
                "manifest_body_sha256": pack.manifest_body_sha256,
                "write_back": write_result or provisional_write,
            }
        )

    summary = {
        "schema_version": "evidencebound-datahub-demo/1.0",
        "dataset_urn": dataset_urn,
        "results": summaries,
        "acceptance": {
            "mcp_read": "PASS",
            "verified_path": summaries[0]["verdict"],
            "blocked_path": summaries[1]["verdict"],
            "mcp_write_back": "NOT_RUN" if args.no_writeback else "PASS",
        },
    }
    (root / "demo-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _offline(args: argparse.Namespace) -> int:
    candidate = _read_json(args.candidate)
    context = _read_json(args.context)
    receipt, root = _export_one(
        Path(args.output),
        candidate=candidate,
        context=context,
        mcp_read={"status": "CONTROLLED_FIXTURE"},
    )
    print(json.dumps({"receipt": receipt, "manifest_body_sha256": root}, indent=2))
    return 0 if receipt["verdict"] == "VERIFIED" else 3


def _verify(args: argparse.Namespace) -> int:
    try:
        result = verify_proof_pack(args.pack)
    except ProofPackError as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc)}))
        return 1
    print(
        json.dumps(
            {
                "status": "REPRODUCED",
                "manifest_body_sha256": result.manifest_body_sha256,
                "cryptographic_seal": (
                    "PRESENT_REQUIRES_VERIFY_SEAL"
                    if (Path(args.pack) / "ed25519-seal.json").is_file()
                    else "NOT_PRESENT"
                ),
            },
            indent=2,
        )
    )
    return 0


def _generate_keypair(args: argparse.Namespace) -> int:
    fingerprint = generate_ed25519_keypair(
        args.private_key,
        args.public_key,
        replace=args.replace,
    )
    print(
        json.dumps(
            {
                "status": "KEYPAIR_CREATED",
                "algorithm": "Ed25519",
                "private_key": str(Path(args.private_key)),
                "public_key": str(Path(args.public_key)),
                "public_key_sha256": fingerprint,
                "private_key_handling": "KEEP_SECRET_AND_OUT_OF_REPOSITORY",
            },
            indent=2,
        )
    )
    return 0


def _seal(args: argparse.Namespace) -> int:
    try:
        result = seal_proof_pack(
            args.pack,
            args.private_key,
            key_id=args.key_id,
            replace=args.replace,
        )
    except ProofPackError as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc)}))
        return 1
    print(
        json.dumps(
            {
                "status": "SEALED",
                "algorithm": "Ed25519",
                "pack": str(result.pack_path),
                "key_id": result.key_id,
                "public_key_sha256": result.public_key_sha256,
                "signed_subject_sha256": result.signed_subject_sha256,
                "identity_boundary": "PIN_PUBLIC_KEY_OUT_OF_BAND",
            },
            indent=2,
        )
    )
    return 0


def _verify_seal(args: argparse.Namespace) -> int:
    try:
        result = verify_ed25519_seal(
            args.pack,
            trusted_public_key_path=args.public_key,
        )
    except ProofPackError as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc)}))
        return 1
    print(
        json.dumps(
            {
                "status": "SIGNATURE_VALID",
                "algorithm": "Ed25519",
                "pack": str(result.pack_path),
                "key_id": result.key_id,
                "public_key_sha256": result.public_key_sha256,
                "signed_subject_sha256": result.signed_subject_sha256,
                "trusted_public_key_matched": result.trusted_key_matched,
                "identity_boundary": (
                    "PINNED_KEY_MATCHED"
                    if result.trusted_key_matched
                    else "EMBEDDED_KEY_ONLY_NOT_IDENTITY_TRUST"
                ),
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evidencebound-datahub")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Run live DataHub MCP read, gate, and write-back")
    demo.add_argument("--dataset-urn")
    demo.add_argument("--search-query", default="*")
    demo.add_argument("--output", default="evidence/live-demo")
    demo.add_argument("--no-writeback", action="store_true")
    demo.add_argument("--replace-output", action="store_true")

    offline = sub.add_parser("offline", help="Run a controlled fixture without DataHub")
    offline.add_argument("--candidate", required=True)
    offline.add_argument("--context", required=True)
    offline.add_argument("--output", required=True)

    verify = sub.add_parser("verify-pack", help="Reproduce and verify a Proof Pack")
    verify.add_argument("pack")

    keypair = sub.add_parser(
        "generate-keypair",
        help="Generate an operator-controlled Ed25519 keypair outside the repository",
    )
    keypair.add_argument("--private-key", required=True)
    keypair.add_argument("--public-key", required=True)
    keypair.add_argument("--replace", action="store_true")

    seal = sub.add_parser("seal-pack", help="Add a detached Ed25519 seal to a verified pack")
    seal.add_argument("pack")
    seal.add_argument("--private-key", required=True)
    seal.add_argument("--key-id")
    seal.add_argument("--replace", action="store_true")

    verify_seal = sub.add_parser(
        "verify-seal",
        help="Verify a detached Ed25519 seal and optionally require a pinned public key",
    )
    verify_seal.add_argument("pack")
    verify_seal.add_argument("--public-key")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "demo":
        return asyncio.run(_demo(args))
    if args.command == "offline":
        return _offline(args)
    if args.command == "verify-pack":
        return _verify(args)
    if args.command == "generate-keypair":
        return _generate_keypair(args)
    if args.command == "seal-pack":
        return _seal(args)
    if args.command == "verify-seal":
        return _verify_seal(args)
    raise AssertionError("unreachable")
