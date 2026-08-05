# EvidenceBound DataHub Gate — Devpost Submission V12

## Project name

EvidenceBound DataHub Gate

## Elevator pitch

Fail-closed governance for DataHub agents: read current metadata, verify deterministically, retain tamper-evident evidence, and write back a review receipt while keeping approval human.

## Challenge category

**Agents That Do Real Work**

## Prize targets

- Grand Prize
- Challenge Winner
- Most Valuable Feedback Survey Prize

## About the project

## Inspiration

Data agents can generate actions that are syntactically valid but bound to stale schemas, incomplete lineage, or unsupported claims. A successful tool call does not prove that the exact candidate is ready for human review, and asking the same model to certify its own action does not create independent, reproducible evidence.

EvidenceBound DataHub Gate was built around a narrower question:

> Before a human approves an agent-generated data action, can the exact candidate be bound to current DataHub context, evaluated deterministically, retained as reproducible evidence, and returned to the metadata graph without implying production authorization?

The project creates a fail-closed review boundary between current metadata context, agent-generated code, and human approval.

## What it does

**Read Context → Restricted AST Gate → Tamper-Evident Proof Pack → Native DataHub Write-Back → Mandatory Human Review**

### 1. Read current DataHub context

The official DataHub MCP Server discovers the dataset, reads its exact identity and current schema fields, and retrieves a bounded one-hop lineage edge. EvidenceBound canonicalizes that observed context and derives schema and lineage digests.

The accepted live dataset was:

```text
urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.ORDER_ENTRY_DB.analytics.order_history,PROD)
```

Lineage reads are deliberately bounded to one hop and at most five results. The adapter checks upstream first and skips the opposite direction after a visible edge is found. Missing lineage still blocks the selected candidate path.

### 2. Bind and verify the candidate deterministically

The candidate is bound to:

- the selected dataset identity;
- the observed schema digest;
- the observed lineage digest;
- a versioned Restricted AST Policy;
- explicit evidence references for material claims.

Unsupported syntax and capabilities are rejected. Permitted operations run in a Fail-Closed Bounded Interpreter without arbitrary `exec`.

A candidate reaches `VERIFIED` only when dataset identity, schema and lineage digests, Restricted AST Policy, bounded execution, and claim-to-evidence references all pass.

Changing only the expected schema digest produces:

```text
BLOCKED: SCHEMA_MISMATCH
runtime_result: null
promotion_authorized: false
```

The stale candidate is blocked before runtime interpretation.

### 3. Export a reproducible Proof Pack

Every result becomes a SHA-256 content-addressed Proof Pack containing the candidate, observed DataHub context, typed receipt, MCP read and write evidence, manifest, and checksums.

Reproduction rejects:

- changed artifacts;
- non-canonical JSON;
- symlinks;
- missing files;
- unexpected files.

The retained mutation test appends one byte to a temporary `gate-receipt.json` and requires:

```text
ARTIFACT_TAMPERING_DETECTED
```

The retained controlled `VERIFIED` and `BLOCKED` Proof Packs also contain detached Ed25519 seals under the published key ID:

```text
key_id: evidencebound-datahub-hackathon-2026
public_key_sha256: fdf31b458136d39b3c22fe041e9ae7c986365c40275383d09e8a38ae81f0680d
```

A valid signature proves possession of the matching private key. The repository-published key makes verification reproducible, but independent signer identity still requires comparison of the fingerprint through a separately trusted channel.

### 4. Return evidence to DataHub

Both `VERIFIED` and `BLOCKED` outcomes are appended to the same DataHub dataset through the official `update_description` MCP mutation.

Each Native DataHub Description Receipt records the verdict, Proof Pack root, schema and lineage digests, reasons, mandatory review state, and:

```text
promotion_authorized=false
```

This is graph-visible metadata evidence. It is not production approval, transaction authorization, or permission to deploy.

Read-only verification and write-back are intentionally separate evidence classes. A read-only recording is never represented as if it performed metadata mutation.

## Why DataHub is essential

A local source-code checker can inspect syntax, but it cannot prove that a candidate is bound to the current cataloged dataset and its observed relationships.

DataHub provides both sides of the governed loop:

1. **Current organizational context** — dataset identity, schema fields, and bounded lineage through the official MCP Server.
2. **Durable knowledge returned to the graph** — Native DataHub Description Receipts through the official `update_description` MCP mutation.

The next human or agent can inspect the verdict and evidence identity in the same metadata system that supplied the context.

## How we built it

The implementation uses:

- Python 3.11;
- DataHub OSS and the official DataHub MCP Server;
- FastMCP and the DataHub SDK;
- a Restricted AST Policy;
- a bounded no-`exec` interpreter;
- canonical JSON and SHA-256 content addressing;
- optional detached Ed25519 attestation;
- Docker for the local DataHub quickstart;
- pytest, Ruff, and Mypy;
- GitHub Actions for deterministic validation and clean-clone reproduction;
- GitHub Pages for the static public Judge Explorer.

The Judge Explorer presents retained `VERIFIED`, `BLOCKED`, tamper-detection, and signature-verification evidence. It is explicitly editorial: it does not execute DataHub, represent live DataHub UI, create new acceptance evidence, or authorize deployment.

## Challenges we faced

### Deterministic evidence around variable write-back

DataHub write responses and timestamps can vary. We had to retain the native MCP write result without creating a circular hash or weakening deterministic Proof Pack reproduction.

### Bounded lineage

A broader lineage expansion exceeded the local GMS timeout. We constrained the adapter to one hop and at most five results while preserving fail-closed behavior when no lineage evidence is available.

### Evidence-class separation

Controlled Proof Packs, live MCP read-only evidence, and retained native write-back evidence are different evidence classes. The repository, Judge Explorer, and final video keep them separate rather than combining them into one generic PASS.

### Preserving the approval boundary

Every path records `promotion_authorized=false`. `VERIFIED` remains narrowly scoped to the exact candidate, observed context, policy, evidence references, and bounded execution. Mandatory Human Review remains outside automation.

### Cryptographic trust boundaries

The retained controlled packs are Ed25519-signed, but a repository-published key is not independent identity attestation. The final release exposes the key fingerprint and states this limitation directly.

## Accomplishments we are proud of

- A complete DataHub read → verify → write-back loop using DataHub OSS and the official DataHub MCP Server.
- Exact dataset, schema, and bounded lineage binding.
- Deterministic current-context `VERIFIED` and stale-schema `BLOCKED: SCHEMA_MISMATCH` paths.
- Restricted AST enforcement and bounded interpretation without arbitrary `exec`.
- Material claim-to-evidence references.
- Reproducible SHA-256 content-addressed Proof Packs.
- Executable one-byte tamper rejection with `ARTIFACT_TAMPERING_DETECTED`.
- Detached Ed25519 verification for both retained controlled Proof Packs.
- Native graph-visible DataHub Description Receipts.
- A one-command controlled judge path and a fresh-clone independent reproduction workflow.
- A public static Judge Explorer and successful GitHub Pages deployment.
- Explicit human-review, production-authorization, and signer-identity boundaries.

## What we learned

Deterministic governance should sit outside the LLM context when approval depends on exact metadata evidence. Agent self-evaluation is not independently reproducible. An external fail-closed gate can bind the candidate to current context, expose missing or stale evidence, retain an auditable receipt, and keep the final decision with a human.

We also learned that provenance needs more than a successful tool response. Useful governance evidence must bind the candidate, catalog context, policy, execution result, and write-back receipt into one reproducible artifact set.

## Real-world usefulness

The target users are data-platform, AI-platform, governance, and risk teams reviewing agent-generated data actions.

Their recurring job is not simply “generate more code.” It is:

> Decide whether the exact generated candidate is bound to current metadata context and ready for human review without hiding stale, missing, or unsupported evidence.

EvidenceBound provides:

- an explicit deterministic verdict;
- visible block reasons;
- evidence references;
- a reproducible Proof Pack;
- a durable DataHub receipt;
- a fail-closed promotion state.

Potential operating measures include stale-contract block rate, Proof Pack reproduction success, tamper-rejection success, claim-reference coverage, and human-review latency. These are proposed measurement targets, not production customer metrics already achieved.

## How judges can verify it

### Controlled reproduction without DataHub

```bash
git clone https://github.com/moneyparking/evidencebound-datahub-gate.git
cd evidencebound-datahub-gate
make test-repro
```

Expected terminal states include:

```text
VERIFIED
BLOCKED: SCHEMA_MISMATCH
REPRODUCED
ARTIFACT_TAMPERING_DETECTED
SIGNATURE_VALID
```

### Independent fresh-clone reproduction

```bash
make independent-repro
```

### Full local DataHub MCP path

```bash
make live-datahub-smoke
```

The first full run downloads and starts DataHub containers, so no fixed clean-install duration is claimed.

### Public Judge Explorer

https://moneyparking.github.io/evidencebound-datahub-gate/

### Public repository

https://github.com/moneyparking/evidencebound-datahub-gate

## What is next

- Independent reproduction by an external reviewer.
- Broader mutation and human-comprehension testing.
- Additional supported AST constructs only when fail-closed semantics remain enforceable.
- Evaluation of structured multi-hop lineage contracts with bounded reads and explicit timeout behavior.
- Exploration of DataHub Actions or Custom Aspects for structured tamper alerts, subject to schema design, tests, live acceptance, UI evidence, and rollback validation.
- Non-production design-partner evaluation.

These are future directions, not claims of current production readiness, enterprise readiness, certification, or customer acceptance.

## Pre-existing work disclosure

The broader EvidenceBound concept and earlier open-core and private verification work predate this hackathon. The DataHub MCP adapter, DataHub-bound candidate contract, bounded demo runtime, Native DataHub Description Receipt flow, DataHub-specific Proof Packs, tests, Judge Explorer, and submission materials were newly authored during the submission period.

## Explicit claim boundary

`VERIFIED` means only that the exact candidate matched the observed DataHub context, passed the Restricted AST Policy, executed in the Fail-Closed Bounded Interpreter, and bound material claims to schema or lineage evidence.

This project does not claim:

- transaction blocking;
- production or deployment authorization;
- data truth or model accuracy;
- regulatory certification;
- immutable storage;
- automatic promotion;
- a custom DataHub badge or aspect;
- that every new or live Proof Pack is Ed25519-signed;
- independent signer identity solely from the repository-published key;
- completed customer acceptance or enterprise production readiness;
- an embedded LLM integration.

Mandatory Human Review always remains required.

## Built with

- Python 3.11
- DataHub OSS
- Official DataHub MCP Server
- MCP
- FastMCP
- DataHub SDK
- Docker
- Ed25519
- SHA-256
- Canonical JSON
- GitHub
- GitHub Actions
- GitHub Pages
- pytest
- Ruff
- Mypy

## Try it out links

1. Public Judge Explorer: https://moneyparking.github.io/evidencebound-datahub-gate/
2. Public GitHub repository: https://github.com/moneyparking/evidencebound-datahub-gate

## Project media

Recommended gallery order:

1. Judge Explorer overview with the `VERIFIED` / `BLOCKED` contrast.
2. Exact DataHub dataset page showing schema and bounded lineage context.
3. Native DataHub Description Receipts for both outcomes.
4. Terminal frame showing `ARTIFACT_TAMPERING_DETECTED`.
5. Final release card showing `SIGNATURE_VALID`, the public-key fingerprint, release source `9f39bcf…`, CI PASS, independent reproduction PASS, Pages deployment PASS, and Mandatory Human Review.

Use JPG, PNG, or GIF in a 3:2 crop. Do not use an editorial card that could be mistaken for live DataHub UI.

## Video demo

Recommended upload asset:

```text
EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V12_JUDGE_CAPTIONED.mp4
SHA-256: e51fbd9d9ddf69d87d7754be05f80f765cf05f768d63aff21c854c5815bd2a9a
Duration: 169.813000 seconds
Resolution: 1920×1080
Frame rate: 30 fps
Captions: burned English narration captions present
Release source commit: 9f39bcf2498a05a47dd7b0a82049e95893770642
```

Devpost video demo URL:

https://youtu.be/dEWJ2eGiDO8

The video is now available as a standard public YouTube video. Independent publication verification returned HTTP 200 for YouTube oEmbed, the embeddable player endpoint, and the max-resolution thumbnail. Full start-to-finish playback and the Devpost embedded-player review remain external acceptance gates.
