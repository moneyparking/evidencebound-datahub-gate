from __future__ import annotations

import json
from pathlib import Path

import pytest

from evidencebound_datahub.cli import _candidate
from evidencebound_datahub.core import evaluate_candidate
from evidencebound_datahub.pack import ProofPackError, export_proof_pack, verify_proof_pack
from evidencebound_datahub.seal import (
    generate_ed25519_keypair,
    seal_proof_pack,
    verify_ed25519_seal,
)

ROOT = Path(__file__).resolve().parents[1]


def _pack(tmp_path: Path) -> Path:
    context = json.loads((ROOT / "examples/mock-context.json").read_text(encoding="utf-8"))
    candidate = _candidate(context["dataset_urn"], context)
    receipt = evaluate_candidate(candidate, context)
    result = export_proof_pack(
        tmp_path / "pack",
        candidate=candidate,
        context=context,
        receipt=receipt,
        mcp_read={"status": "CONTROLLED_FIXTURE"},
        mcp_write=None,
    )
    return result.path


def test_ed25519_seal_round_trip_with_pinned_public_key(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    private_key = tmp_path / "private.pem"
    public_key = tmp_path / "public.pem"
    fingerprint = generate_ed25519_keypair(private_key, public_key)

    sealed = seal_proof_pack(pack, private_key, key_id="test-release-key")
    verified = verify_ed25519_seal(pack, trusted_public_key_path=public_key)

    assert sealed.public_key_sha256 == fingerprint
    assert verified.public_key_sha256 == fingerprint
    assert verified.key_id == "test-release-key"
    assert verified.trusted_key_matched is True
    assert (pack / "ed25519-seal.json").is_file()
    verify_proof_pack(pack)


def test_ed25519_seal_rejects_signature_tampering(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    private_key = tmp_path / "private.pem"
    public_key = tmp_path / "public.pem"
    generate_ed25519_keypair(private_key, public_key)
    seal_proof_pack(pack, private_key)

    seal_path = pack / "ed25519-seal.json"
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    signature = seal["signature"]
    seal["signature"] = ("A" if signature[0] != "A" else "B") + signature[1:]
    seal_path.write_text(
        json.dumps(seal, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ProofPackError, match="SEAL_SIGNATURE_INVALID"):
        verify_ed25519_seal(pack)


def test_ed25519_seal_rejects_untrusted_public_key(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    private_key = tmp_path / "private.pem"
    public_key = tmp_path / "public.pem"
    other_private_key = tmp_path / "other-private.pem"
    other_public_key = tmp_path / "other-public.pem"
    generate_ed25519_keypair(private_key, public_key)
    generate_ed25519_keypair(other_private_key, other_public_key)
    seal_proof_pack(pack, private_key)

    with pytest.raises(ProofPackError, match="SEAL_TRUSTED_KEY_MISMATCH"):
        verify_ed25519_seal(pack, trusted_public_key_path=other_public_key)
