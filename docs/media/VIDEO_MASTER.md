# EvidenceBound DataHub Gate — V12 Video Master

## Release decision

The final Devpost master is:

```text
EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V12_JUDGE_CAPTIONED.mp4
SHA-256: e51fbd9d9ddf69d87d7754be05f80f765cf05f768d63aff21c854c5815bd2a9a
Duration: 169.813000 seconds
Resolution: 1920×1080
Frame rate: 30 fps
Video: H.264, yuv420p
Audio: AAC, 48 kHz, stereo
Captions: burned English narration captions present
Release source commit: 9f39bcf2498a05a47dd7b0a82049e95893770642
```

The clean alternative is:

```text
EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V12_CLEAN.mp4
SHA-256: 743817a456761207c87461475498e419835694b623c2cf23a1a703bfc16c2009
Duration: 169.866667 seconds
```

The recommended upload is the JUDGE CAPTIONED master. Do not overlay a second subtitle track.

## Audio acceptance

```text
AAC stream SHA-256: b671d773648747fb49dcf7a522a4b0defe0862bdf5c9b13c0910b01f1a582251
Integrated loudness: −14.2 LUFS
Loudness range: 2.0 LU
True peak: −1.9 dBFS
```

The V12 CLEAN and JUDGE CAPTIONED audio streams are byte-identical to the accepted V11 audio stream truncated to the V12 duration. No additional gain was applied.

## Evidence classes

The video distinguishes:

- controlled public-repository Proof Pack evidence;
- retained live DataHub MCP read and native description write-back evidence;
- current GitHub release evidence;
- clearly labeled editorial Judge Explorer and architecture cards.

The retained controlled Ed25519-sealed packs are distinct from the accepted live DataHub MCP dataset and live write-back evidence. V12 does not represent the controlled seals as signatures over the separate live acceptance run.

Accepted live dataset:

```text
urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.ORDER_ENTRY_DB.analytics.order_history,PROD)
```

## 01 · BLOCKED BEFORE RUNTIME

A stale-schema candidate reaches EvidenceBound and returns `BLOCKED: SCHEMA_MISMATCH`. The runtime result remains `null`, `promotion_authorized` remains `false`, and Mandatory Human Review remains required.

## 02 · FAIL-CLOSED GOVERNANCE FOR DATA AGENTS

EvidenceBound DataHub Gate adds a narrow boundary between metadata access and human approval:

```text
Read Context
  → Restricted AST Gate
  → Tamper-Evident Proof Pack
  → Native DataHub Write-Back
  → Mandatory Human Review
```

## 03 · THE ACCEPTED LIVE DATASET

The live run uses the DataHub showcase order-history dataset. The official MCP Server discovers the exact URN, reads entity and schema context, obtains a bounded one-hop lineage edge, runs both candidate paths, and appends both receipts to the same dataset description.

## 04 · SCHEMA PLUS BOUNDED ONE-HOP LINEAGE

The read is bounded to one lineage hop and at most five results. Upstream is checked first; after a visible edge, the opposite direction is skipped. Missing lineage still blocks verification.

## 05 · RESTRICTED AST POLICY

The candidate is bound to the observed dataset, schema digest, and lineage digest. The Restricted AST Policy rejects unsupported constructs. Supported operations run in a Fail-Closed Bounded Interpreter without arbitrary `exec`, and material claims require explicit evidence references.

## 06 · CURRENT CONTEXT: VERIFIED

With current DataHub context, the candidate passes dataset identity, schema and lineage binding, Restricted AST Policy, bounded execution, and claim-to-evidence validation. The resulting `VERIFIED` verdict covers only the exact candidate and recorded context. It is not production approval or permission to deploy.

## 07 · ONE DIGEST CHANGED: BLOCKED

Changing only the expected schema digest blocks the stale candidate before runtime interpretation. EvidenceBound returns `BLOCKED: SCHEMA_MISMATCH`, a distinct Proof Pack root, `runtime_result: null`, and `promotion_authorized: false`.

## 08 · NATIVE DATAHUB DESCRIPTION RECEIPTS

Both outcomes become Native DataHub Description Receipts through the official `update_description` MCP mutation. Each receipt records verdict, Proof Pack root, schema and lineage digests, reasons, and Mandatory Human Review. The write-back is graph-visible metadata evidence, not transaction or deployment authorization.

## 09 · CONTENT-ADDRESSED PROOF PACKS

Each result becomes a SHA-256 content-addressed Proof Pack containing candidate, context, typed receipt, MCP evidence, manifest, and checksums. Reproduction rejects modified or unexpected artifacts, non-canonical JSON, symlinks, and missing files.

## 10 · ONE-BYTE TAMPER REJECTION

The public test appends one byte to a temporary `gate-receipt.json` and reruns verification. The required result is:

```text
ARTIFACT_TAMPERING_DETECTED
```

## 11 · DETACHED ED25519 RELEASE SEALS

The retained controlled `VERIFIED` and `BLOCKED` Proof Packs contain detached Ed25519 seals under:

```text
key_id: evidencebound-datahub-hackathon-2026
public_key_sha256: fdf31b458136d39b3c22fe041e9ae7c986365c40275383d09e8a38ae81f0680d
```

Both retained packs show:

```text
SIGNATURE_VALID
trusted_public_key_matched: true
PINNED_KEY_MATCHED
```

A valid signature proves possession of the corresponding private key. Independent signer identity still requires comparison of the fingerprint through a separately trusted channel.

## 12 · CURRENT PUBLIC RELEASE ACCEPTANCE

The final release section shows:

- release source `9f39bcf2498a05a47dd7b0a82049e95893770642`;
- deterministic gates PASS, workflow run 26;
- independent reproduction PASS, workflow run 22;
- GitHub Pages deployment PASS, workflow run 4;
- Pages artifact digest `sha256:d1459dee4762c3a2fb3ba950b1f18549aca6065b017429998a17437a4ad86636`;
- `NO AUTOMATIC PROMOTION`;
- Mandatory Human Review.

## Judge Explorer boundary

The public Judge Explorer is a static editorial evidence explorer. It does not execute DataHub, represent live DataHub UI, create new acceptance evidence, or authorize deployment.

## Claim boundary

V12 does not claim:

- transaction blocking;
- production or deployment authorization;
- regulatory certification;
- immutable storage;
- automatic promotion;
- a custom DataHub badge or aspect;
- that the separate live DataHub acceptance Proof Packs were Ed25519-signed;
- that every newly generated Proof Pack is signed;
- independent legal identity solely from the repository-published key;
- completed customer acceptance or enterprise production readiness;
- embedded LLM integration.

## Publication gate

Technical render and automated QA: PASS.

Owner playback on the actual upload device, completed YouTube processing, and Devpost embedded-player review remain required before final publication acceptance.
