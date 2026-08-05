# Security and Trust Model

## Integrity layer

Every Proof Pack remains content-addressed and fail-closed. Canonical JSON artifacts are bound by SHA-256 digests, `evidence_root_sha256`, `manifest_body_sha256`, and `SHA256SUMS`. Reproduction rejects changed artifacts, non-canonical JSON, symlinks, missing files, and unexpected files.

## Optional detached Ed25519 seal

The repository supports an optional detached `ed25519-seal.json` attestation over the verified manifest subject.

The signed subject binds:

- `manifest_body_sha256`;
- `evidence_root_sha256`;
- dataset URN;
- candidate ID;
- verdict;
- policy version.

The private key is operator-controlled and must remain outside the repository. The public key can be pinned through an independent trusted channel.

```bash
evidencebound-datahub generate-keypair \
  --private-key ~/.config/evidencebound/release-private.pem \
  --public-key ./release-public.pem

evidencebound-datahub seal-pack evidence/controlled-verified \
  --private-key ~/.config/evidencebound/release-private.pem \
  --key-id evidencebound-hackathon-release

evidencebound-datahub verify-seal evidence/controlled-verified \
  --public-key ./release-public.pem
```

Expected successful verification:

```text
SIGNATURE_VALID
trusted_public_key_matched: true
```

## Published retained release key

The retained controlled `VERIFIED` and `BLOCKED` Proof Packs contain detached Ed25519 seals using the same repository-published public key:

```text
key_id: evidencebound-datahub-hackathon-2026
public_key_sha256: fdf31b458136d39b3c22fe041e9ae7c986365c40275383d09e8a38ae81f0680d
```

Public key:

```text
docs/judge/keys/evidencebound-datahub-hackathon-public.pem
```

Reproduce the signature checks from a clean checkout:

```bash
evidencebound-datahub verify-seal \
  evidence/controlled-verified \
  --public-key docs/judge/keys/evidencebound-datahub-hackathon-public.pem

evidencebound-datahub verify-seal \
  evidence/controlled-blocked \
  --public-key docs/judge/keys/evidencebound-datahub-hackathon-public.pem
```

Expected identity boundary for both retained packs:

```text
SIGNATURE_VALID
trusted_public_key_matched: true
PINNED_KEY_MATCHED
```

The repository publication makes the key and fingerprint judge-visible and reproducible. It is not, by itself, an independent identity attestation; a reviewer who needs signer identity assurance must compare the fingerprint against a separately trusted channel.

## Trust boundary

An Ed25519 signature proves that the signer possessed the corresponding private key. It does not, by itself, establish the human or organization behind that key. Identity attribution requires a public key fingerprint pinned through an independent trusted channel.

Retained packs remain hash-bound unless an `ed25519-seal.json` file is actually present and verified. The retained controlled packs listed above do contain seal files. The public judge explorer does not fabricate a signature or imply that any other unsigned pack is signed.

## Non-claims

The cryptographic seal is not:

- production authorization;
- regulatory certification;
- immutable storage;
- a hardware-backed key guarantee;
- automatic promotion;
- evidence that a specific human approved the candidate.

Mandatory Human Review and `promotion_authorized=false` remain unchanged.
