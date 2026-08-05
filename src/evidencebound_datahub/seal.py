"""Optional detached Ed25519 attestation for a verified Proof Pack."""

from __future__ import annotations

import base64
import binascii
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .core import canonical_json_bytes, sha256_bytes
from .pack import ProofPackError, verify_proof_pack

SEAL_FILE = "ed25519-seal.json"
SEAL_SCHEMA_VERSION = "evidencebound-datahub-ed25519-seal/1.0"
SIGNED_SUBJECT_SCHEMA_VERSION = "evidencebound-datahub-ed25519-subject/1.0"


@dataclass(frozen=True)
class SealResult:
    pack_path: Path
    public_key_sha256: str
    signed_subject_sha256: str
    key_id: str
    trusted_key_matched: bool


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofPackError(f"SEAL_JSON_INVALID:{path.name}") from exc
    if not isinstance(value, dict):
        raise ProofPackError(f"SEAL_JSON_INVALID:{path.name}")
    return value


def _write_canonical(path: Path, value: Any) -> None:
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _load_private_key(path: str | Path) -> Ed25519PrivateKey:
    try:
        key = serialization.load_pem_private_key(Path(path).read_bytes(), password=None)
    except (OSError, ValueError, TypeError) as exc:
        raise ProofPackError("ED25519_PRIVATE_KEY_INVALID") from exc
    if not isinstance(key, Ed25519PrivateKey):
        raise ProofPackError("ED25519_PRIVATE_KEY_INVALID")
    return key


def _load_public_key(path: str | Path) -> Ed25519PublicKey:
    try:
        key = serialization.load_pem_public_key(Path(path).read_bytes())
    except (OSError, ValueError, TypeError) as exc:
        raise ProofPackError("ED25519_PUBLIC_KEY_INVALID") from exc
    if not isinstance(key, Ed25519PublicKey):
        raise ProofPackError("ED25519_PUBLIC_KEY_INVALID")
    return key


def _public_key_raw(key: Ed25519PublicKey) -> bytes:
    return key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def _fingerprint(key: Ed25519PublicKey) -> str:
    return sha256_bytes(_public_key_raw(key))


def _decode_base64(value: Any, reason: str) -> bytes:
    if not isinstance(value, str):
        raise ProofPackError(reason)
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error) as exc:
        raise ProofPackError(reason) from exc


def _subject_from_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    manifest_body = manifest.get("manifest_body")
    manifest_body_sha256 = manifest.get("manifest_body_sha256")
    if not isinstance(manifest_body, dict) or not isinstance(manifest_body_sha256, str):
        raise ProofPackError("MANIFEST_BODY_INVALID")
    return {
        "schema_version": SIGNED_SUBJECT_SCHEMA_VERSION,
        "manifest_body_sha256": manifest_body_sha256,
        "evidence_root_sha256": manifest_body.get("evidence_root_sha256"),
        "dataset_urn": manifest_body.get("dataset_urn"),
        "candidate_id": manifest_body.get("candidate_id"),
        "verdict": manifest_body.get("verdict"),
        "policy_version": manifest_body.get("policy_version"),
    }


def generate_ed25519_keypair(
    private_key_path: str | Path,
    public_key_path: str | Path,
    *,
    replace: bool = False,
) -> str:
    private_path = Path(private_key_path)
    public_path = Path(public_key_path)
    if not replace and (private_path.exists() or public_path.exists()):
        raise FileExistsError("signing key output exists")
    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    private_bytes = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_bytes = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    private_path.write_bytes(private_bytes)
    public_path.write_bytes(public_bytes)
    os.chmod(private_path, 0o600)
    os.chmod(public_path, 0o644)
    return _fingerprint(public_key)


def seal_proof_pack(
    pack_dir: str | Path,
    private_key_path: str | Path,
    *,
    key_id: str | None = None,
    replace: bool = False,
) -> SealResult:
    pack_path = Path(pack_dir)
    verified = verify_proof_pack(pack_path)
    seal_path = pack_path / SEAL_FILE
    if seal_path.exists() and not replace:
        raise FileExistsError(f"seal exists: {seal_path}")

    manifest_path = pack_path / "manifest.json"
    manifest = _read_json(manifest_path)
    subject = _subject_from_manifest(manifest)
    if subject["manifest_body_sha256"] != verified.manifest_body_sha256:
        raise ProofPackError("SEAL_SUBJECT_MISMATCH")
    if subject["evidence_root_sha256"] != verified.evidence_root_sha256:
        raise ProofPackError("SEAL_SUBJECT_MISMATCH")

    private_key = _load_private_key(private_key_path)
    public_key = private_key.public_key()
    public_key_raw = _public_key_raw(public_key)
    public_key_sha256 = _fingerprint(public_key)
    subject_bytes = canonical_json_bytes(subject)
    signed_subject_sha256 = sha256_bytes(subject_bytes)
    resolved_key_id = key_id or f"sha256:{public_key_sha256[:16]}"
    signature = private_key.sign(subject_bytes)

    seal = {
        "schema_version": SEAL_SCHEMA_VERSION,
        "algorithm": "Ed25519",
        "key_id": resolved_key_id,
        "public_key_encoding": "raw-base64",
        "public_key": base64.b64encode(public_key_raw).decode("ascii"),
        "public_key_sha256": public_key_sha256,
        "signed_subject": subject,
        "signed_subject_sha256": signed_subject_sha256,
        "signature_encoding": "base64",
        "signature": base64.b64encode(signature).decode("ascii"),
        "trust_boundary": (
            "The signature proves possession of the matching private key. Signer identity "
            "requires a public key pinned through an independent trusted channel."
        ),
    }
    seal_metadata = {
        "schema_version": SEAL_SCHEMA_VERSION,
        "file": SEAL_FILE,
        "algorithm": "Ed25519",
        "key_id": resolved_key_id,
        "public_key_sha256": public_key_sha256,
        "signed_subject_sha256": signed_subject_sha256,
    }
    manifest["optional_cryptographic_seal"] = seal_metadata
    _write_canonical(seal_path, seal)
    _write_canonical(manifest_path, manifest)
    verify_proof_pack(pack_path)
    return verify_ed25519_seal(pack_path)


def verify_ed25519_seal(
    pack_dir: str | Path,
    *,
    trusted_public_key_path: str | Path | None = None,
) -> SealResult:
    pack_path = Path(pack_dir)
    verified = verify_proof_pack(pack_path)
    manifest = _read_json(pack_path / "manifest.json")
    seal = _read_json(pack_path / SEAL_FILE)

    if seal.get("schema_version") != SEAL_SCHEMA_VERSION or seal.get("algorithm") != "Ed25519":
        raise ProofPackError("SEAL_CONTRACT_INVALID")
    subject = _subject_from_manifest(manifest)
    if seal.get("signed_subject") != subject:
        raise ProofPackError("SEAL_SUBJECT_MISMATCH")
    if subject["manifest_body_sha256"] != verified.manifest_body_sha256:
        raise ProofPackError("SEAL_SUBJECT_MISMATCH")
    if subject["evidence_root_sha256"] != verified.evidence_root_sha256:
        raise ProofPackError("SEAL_SUBJECT_MISMATCH")

    subject_bytes = canonical_json_bytes(subject)
    signed_subject_sha256 = sha256_bytes(subject_bytes)
    if seal.get("signed_subject_sha256") != signed_subject_sha256:
        raise ProofPackError("SEAL_SUBJECT_DIGEST_MISMATCH")

    public_key_raw = _decode_base64(seal.get("public_key"), "SEAL_PUBLIC_KEY_INVALID")
    if len(public_key_raw) != 32:
        raise ProofPackError("SEAL_PUBLIC_KEY_INVALID")
    try:
        public_key = Ed25519PublicKey.from_public_bytes(public_key_raw)
    except ValueError as exc:
        raise ProofPackError("SEAL_PUBLIC_KEY_INVALID") from exc
    public_key_sha256 = _fingerprint(public_key)
    if seal.get("public_key_sha256") != public_key_sha256:
        raise ProofPackError("SEAL_PUBLIC_KEY_FINGERPRINT_MISMATCH")

    signature = _decode_base64(seal.get("signature"), "SEAL_SIGNATURE_INVALID")
    try:
        public_key.verify(signature, subject_bytes)
    except InvalidSignature as exc:
        raise ProofPackError("SEAL_SIGNATURE_INVALID") from exc

    seal_metadata = manifest.get("optional_cryptographic_seal")
    expected_metadata = {
        "schema_version": SEAL_SCHEMA_VERSION,
        "file": SEAL_FILE,
        "algorithm": "Ed25519",
        "key_id": seal.get("key_id"),
        "public_key_sha256": public_key_sha256,
        "signed_subject_sha256": signed_subject_sha256,
    }
    if seal_metadata != expected_metadata:
        raise ProofPackError("CRYPTOGRAPHIC_SEAL_METADATA_MISMATCH")

    trusted_key_matched = False
    if trusted_public_key_path is not None:
        trusted_key = _load_public_key(trusted_public_key_path)
        if _public_key_raw(trusted_key) != public_key_raw:
            raise ProofPackError("SEAL_TRUSTED_KEY_MISMATCH")
        trusted_key_matched = True

    key_id = seal.get("key_id")
    if not isinstance(key_id, str) or not key_id:
        raise ProofPackError("SEAL_KEY_ID_INVALID")
    return SealResult(
        pack_path=pack_path,
        public_key_sha256=public_key_sha256,
        signed_subject_sha256=signed_subject_sha256,
        key_id=key_id,
        trusted_key_matched=trusted_key_matched,
    )
