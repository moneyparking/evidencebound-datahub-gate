# Devpost Submission Draft

## Project name

EvidenceBound DataHub Gate: Fail-Closed Verification & Proof Packs for DataHub AI Agents

## Tagline

Fail-Closed Read → Verify → Write-Back Governance for Data Agents.

## Track

Agents That Do Real Work

## How judges can verify the evidence

### Controlled reproduction

```bash
git clone https://github.com/moneyparking/evidencebound-datahub-gate.git
cd evidencebound-datahub-gate
make test-repro
```

This command creates a local virtual environment, installs the validation dependencies, runs the deterministic suite, regenerates the controlled current-context `VERIFIED` and stale-schema `BLOCKED` Proof Packs, and reproduces both packs.

Expected states include:

```text
VERIFIED
BLOCKED: SCHEMA_MISMATCH
REPRODUCED
ARTIFACT_TAMPERING_DETECTED
```

### Independent clean-clone reproduction

```bash
make independent-repro
```

This clones the public repository into a fresh temporary directory, runs the same validation path, emits a report, and prints the exact reproduced artifact hashes. No fixed completion time is claimed because dependency and network speed vary.

### Exact video source snapshot

```bash
git checkout 4209f1326ae8805fd069b0240d27b2521ada792c
make test-repro
```

The V7.1 video is bound to this immutable release source commit. It does not claim that the release source will remain equal to mutable branch `main` after the media manifest is committed.

### Public judge journey

The repository includes a static public judge evidence explorer with separate current-context, stale-schema, and one-byte tamper scenarios. It is explicitly labeled as editorial: it does not represent live DataHub UI, execute DataHub, create new acceptance evidence, or authorize deployment.

## Demo video integrity

Recommended Devpost/YouTube master:

```text
EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V7.1_AUDITED_CAPTIONED.mp4
SHA-256: 3b747380157051b2293a3bf1b743ac82c4b1584ec71bf37207a57311c9c3f7b2
Release source commit: 4209f1326ae8805fd069b0240d27b2521ada792c
```

The master contains burned narration captions. Do not enable the standalone SRT over it. The clean-master alternative, SRT hash, QA evidence, and caption policy are recorded in `submission/datahub-v71-video-proof.json` and `submission/DATAHUB_DEVPOST_MEDIA_V71.md`.

## Inspiration

Metadata-aware agents can still act on stale schemas, incomplete lineage, or claims that are not bound to evidence. A successful MCP call or generated code sample is not durable proof that the intended action was safe.

The project asks a narrower question: before a human approves an agent-generated data action, can the exact candidate be bound to current DataHub context, evaluated deterministically, retained as reproducible evidence, and written back to the graph without implying deployment authorization?

## What it does

**Read Context → Restricted AST Gate → Tamper-Evident Proof Pack → Native DataHub Write-Back**

EvidenceBound DataHub Gate uses the official DataHub MCP server to discover a dataset, read its identity and schema, and obtain a bounded one-hop lineage edge. The deterministic gate then:

- binds the candidate to the selected dataset identity;
- compares expected and observed schema and lineage digests;
- applies a Restricted AST Policy;
- runs supported code in a Fail-Closed Bounded Interpreter without `exec`;
- binds material claims to explicit schema or lineage references;
- emits a typed `VERIFIED` or `BLOCKED` receipt;
- exports a Tamper-Evident Content-Addressed Proof Pack;
- appends a Native DataHub Description Receipt through the official `update_description` MCP mutation.

Mandatory Human Review remains required. `promotion_authorized` is always `false`.

## DataHub native write-back security

Read-only verification and native write-back are intentionally separate evidence classes.

- Read-only verification can prove MCP read, both deterministic candidate paths, and fresh Proof Pack generation without mutating DataHub metadata.
- Native write-back runs only through the explicit live acceptance path and uses the official `update_description` MCP mutation.
- The Native DataHub Description Receipt records the verdict, evidence roots, digests, reasons, `promotion_authorized=false`, and Mandatory Human Review.
- A read-only recording is never represented as if it performed write-back.

This is a fail-closed operating policy: metadata mutation is explicit and reviewable, while the final promotion decision remains outside automation.

## How we built it

Built with the official DataHub MCP server via FastMCP, the DataHub SDK, a restricted AST policy, a bounded no-exec interpreter, and a Python standard-library verification core. The public repository is Apache-2.0 licensed.

The implementation also uses canonical JSON, SHA-256 content addressing, pytest, Ruff, Mypy, and GitHub Actions.

The live adapter deliberately bounds lineage reads to one hop and at most five results. It checks upstream first and skips the opposite direction after a visible lineage edge is found. Missing lineage still blocks verification.

## Demo flow

1. Cold-open on the stale-schema candidate: `BLOCKED`, `SCHEMA_MISMATCH`, no runtime result, no promotion authorization.
2. Open the public judge journey and switch between current-context, stale-schema, and one-byte tamper scenarios.
3. Show the exact `make test-repro` path and the independent clean-clone workflow.
4. Open the accepted DataHub dataset and show its schema plus a bounded one-hop lineage edge.
5. Run the current-context candidate: `VERIFIED`.
6. Change only the expected schema digest and show deterministic `BLOCKED` before runtime interpretation.
7. Show the two Proof Pack roots and the `ARTIFACT_TAMPERING_DETECTED` mutation result.
8. Separate the current read-only recording from the retained Native DataHub Description Receipt write-back evidence.
9. Show the public repository and successful exact-head GitHub Actions validation.
10. Close on the architecture: DataHub MCP → EvidenceBound Gate → Proof Pack + Description Receipt → Mandatory Human Review.

## Accomplishments that we are proud of

- a complete read → verify → write-back loop using DataHub OSS and the official DataHub MCP server;
- deterministic `VERIFIED` and stale-schema `BLOCKED` contrast;
- bounded one-hop lineage behavior aligned across code, README, video, and Devpost;
- native description write-back carrying evidence instead of an unsupported confidence score;
- retained Proof Packs that reproduce and reject a one-byte mutation;
- a one-command controlled judge path plus a fresh-clone independent reproduction workflow;
- a public judge evidence explorer that preserves evidence-class boundaries;
- public repository with deterministic GitHub Actions validation;
- no automatic deployment, production authorization, or transaction authorization;
- no custom DataHub badge or aspect claim;
- clean separation from SignalReview production and private enterprise code.

## Real-world usefulness

The project targets platform, governance, and risk teams that want to use DataHub-connected agents without treating generated code or successful tool calls as self-authenticating evidence.

The narrow value is a reviewable control boundary:

- stale contracts fail before bounded interpretation;
- supported candidates are bound to exact DataHub identity, schema, and lineage evidence;
- every outcome becomes a reproducible Proof Pack;
- evidence can be returned to the DataHub graph through a native mutation;
- human approval remains mandatory.

The design is compatible with DataOps and CI review workflows because the controlled path is command-line reproducible and returns explicit exit states. This repository does not claim completed enterprise integration, customer acceptance, certification, or production readiness.

## Challenges we overcame

We built a bidirectional read-and-write integration without requiring judges to register fragile custom schemas on a clean DataHub instance. The result is written back through the official native `update_description` MCP mutation.

Additional challenges included:

- avoiding a circular hash when the variable MCP write result must be retained;
- preserving deterministic evidence while timestamps and external write responses vary;
- bounding lineage reads after a larger graph expansion exceeded the local GMS timeout;
- separating pre-existing EvidenceBound concepts from newly authored hackathon code;
- keeping `VERIFIED` narrowly scoped to the recorded candidate, context, policy, and interpreter;
- separating current read-only footage from retained write-back evidence in the judge narrative.

## What is next

- independent reproduction by an external reviewer, using the published attestation template;
- broader mutation and human-comprehension testing;
- additional supported AST constructs only when they retain fail-closed semantics;
- non-production integration evaluation with design partners.

These are future directions, not claims of current production readiness, enterprise readiness, certification, or customer acceptance.

## Pre-existing work disclosure

The EvidenceBound concept and earlier private/open-core verification work predate the hackathon. The DataHub MCP adapter, metadata-bound candidate contract, bounded demo runtime, Native DataHub Description Receipt flow, DataHub-specific Proof Pack, tests, and submission materials were newly authored during the submission period.

## Explicit non-claims

- no transaction blocking claim;
- no production authorization;
- no digital-signature or cryptographic-guarantee claim;
- no immutable-storage claim;
- no custom DataHub badge or aspect claim;
- no LLM integration claim;
- no fixed 60-second or 90-second clean-install promise;
- no enterprise-ready, deployment-ready, customer-accepted, or certification claim.
