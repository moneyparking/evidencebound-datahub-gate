# Devpost Submission Draft

## Project name

EvidenceBound DataHub Gate: Fail-Closed Governance for Data Agents

## Tagline

Fail-Closed Read → Verify → Write-Back Governance for Data Agents.

## Track

Agents That Do Real Work

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

## How we built it

Built with the official DataHub MCP server via FastMCP, the DataHub SDK, a restricted AST policy, a bounded no-exec interpreter, and a Python standard-library verification core. The public repository is Apache-2.0 licensed.

The implementation also uses canonical JSON, SHA-256 content addressing, pytest, Ruff, Mypy, and GitHub Actions.

The live adapter deliberately bounds lineage reads to one hop and at most five results. It checks upstream first and skips the opposite direction after a visible lineage edge is found. Missing lineage still blocks verification.

## Demo flow

1. Cold-open on the stale-schema candidate: `BLOCKED`, `SCHEMA_MISMATCH`, no runtime result, no promotion authorization.
2. Open the accepted DataHub dataset and show its schema plus a bounded one-hop lineage edge.
3. Run the current-context candidate: `VERIFIED`.
4. Change only the expected schema digest and show deterministic `BLOCKED` before runtime interpretation.
5. Show the two Proof Pack roots.
6. Open the same DataHub dataset and show both Native DataHub Description Receipts.
7. Reproduce the retained VERIFIED and BLOCKED packs from the CLI.
8. Change one byte in a pack and show `ARTIFACT_TAMPERING_DETECTED`.
9. Show the public repository and successful GitHub Actions run.
10. Close on the architecture: DataHub MCP → EvidenceBound Gate → Proof Pack + Description Receipt → Mandatory Human Review.

## Accomplishments that we are proud of

- a complete read → verify → write-back loop using DataHub OSS and the official DataHub MCP server;
- deterministic `VERIFIED` and stale-schema `BLOCKED` contrast;
- bounded one-hop lineage behavior aligned across code, README, video, and Devpost;
- native description write-back carrying evidence instead of an unsupported confidence score;
- retained Proof Packs that reproduce and reject a one-byte mutation;
- public repository with deterministic GitHub Actions validation;
- no automatic deployment, production authorization, or transaction authorization;
- no custom DataHub badge or aspect claim;
- clean separation from SignalReview production and private enterprise code.

## Challenges we overcame

We built a bidirectional read-and-write integration without requiring judges to register fragile custom schemas on a clean DataHub instance. The result is written back through the official native `update_description` MCP mutation.

Additional challenges included:

- avoiding a circular hash when the variable MCP write result must be retained;
- preserving deterministic evidence while timestamps and external write responses vary;
- bounding lineage reads after a larger graph expansion exceeded the local GMS timeout;
- separating pre-existing EvidenceBound concepts from newly authored hackathon code;
- keeping `VERIFIED` narrowly scoped to the recorded candidate, context, policy, and interpreter.

## What is next

- independent clean-install reproduction on another machine;
- broader mutation and human-comprehension testing;
- additional supported AST constructs only when they retain fail-closed semantics;
- non-production integration evaluation with design partners.

These are future directions, not claims of current production readiness, enterprise readiness, certification, or customer acceptance.

## Pre-existing work disclosure

The EvidenceBound concept and earlier private/open-core verification work predate the hackathon. The DataHub MCP adapter, metadata-bound candidate contract, bounded demo runtime, Native DataHub Description Receipt flow, DataHub-specific Proof Pack, tests, and submission materials were newly authored during the submission period.

## Explicit non-claims

- no transaction blocking claim;
- no production authorization;
- no digital-signature claim;
- no custom DataHub badge or aspect claim;
- no LLM integration claim;
- no fixed 90-second clean-install promise;
- no enterprise-ready or certification claim.
