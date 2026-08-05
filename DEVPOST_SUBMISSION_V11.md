# EvidenceBound DataHub Gate — Devpost Submission V11

## Project name

EvidenceBound DataHub Gate: Fail-Closed Verification and Proof Packs for Data Agents

## Tagline

Read current DataHub context. Verify deterministically. Return evidence to the graph. Keep approval human.

## Challenge category

**Agents That Do Real Work**

## DataHub technologies used

- DataHub OSS / Core Platform
- Official DataHub MCP Server

## Problem

A data agent can generate code that is syntactically valid but bound to a stale schema, incomplete lineage, or unsupported claims. A successful tool call does not prove that the exact candidate is safe to review or promote.

EvidenceBound DataHub Gate asks a narrower question:

> Before a human approves an agent-generated data action, can the exact candidate be bound to current DataHub context, evaluated deterministically, retained as reproducible evidence, and returned to the metadata graph?

## Why DataHub is essential

This project depends on DataHub for two capabilities that a local code checker cannot provide alone.

### 1. Current organizational context

The official DataHub MCP server supplies:

- the exact dataset identity;
- current schema fields;
- bounded one-hop lineage;
- durable graph context shared by humans and agents.

Without DataHub, the verifier could check source syntax but could not prove that the candidate was bound to the current cataloged dataset and its observed relationships.

### 2. Durable knowledge returned to the graph

After verification, the project appends a Native DataHub Description Receipt through the official `update_description` MCP mutation. The next human or agent can inspect:

- the verdict;
- Proof Pack root;
- schema and lineage digests;
- reasons;
- mandatory human-review state;
- `promotion_authorized=false`.

DataHub is therefore both the source of current context and the durable destination for verification evidence.

## Architecture and fail-closed logic

```text
Agent candidate
      ↓
DataHub MCP context
  ├─ dataset identity
  ├─ schema fields
  └─ bounded one-hop lineage
      ↓
EvidenceBound deterministic gate
  ├─ dataset identity binding
  ├─ schema and lineage digests
  ├─ Restricted AST Policy
  ├─ Fail-Closed Bounded Interpreter
  ├─ claim-to-evidence binding
  └─ VERIFIED / BLOCKED receipt
      ↓
Tamper-Evident Content-Addressed Proof Pack
      ↓
Native DataHub Description Receipt
      ↓
Mandatory Human Review
```

The two mandatory paths are:

1. **VERIFIED** — the current schema and bounded lineage match the candidate contract.
2. **BLOCKED** — changing only the expected schema digest produces `SCHEMA_MISMATCH` before runtime interpretation.

`VERIFIED` is intentionally narrow. It does not mean production approval, data truth, model accuracy, certification, or permission to deploy.

## DataHub integration

The current working MCP contract uses:

| Purpose | Tool |
| --- | --- |
| Dataset discovery | `search` |
| Entity identity | `get_entities` |
| Schema context | `list_schema_fields` |
| Bounded lineage | `get_lineage` |
| Native write-back | `update_description` |

Lineage reads are bounded to one hop and five results. Upstream is checked first; after a visible upstream edge, downstream is not queried. Missing lineage blocks the selected candidate path.

Read-only and write-back executions are separate evidence classes. A read-only recording is never represented as if it performed metadata mutation.

## Reproducibility

### One-command controlled judge path

```bash
git clone https://github.com/moneyparking/evidencebound-datahub-gate.git
cd evidencebound-datahub-gate
make test-repro
```

This creates a local environment, installs the project, runs validation, regenerates the controlled `VERIFIED` and stale-schema `BLOCKED` Proof Packs, reproduces both packs, and requires the retained one-byte tamper test to return:

```text
ARTIFACT_TAMPERING_DETECTED
```

### Fresh-clone reproduction

```bash
make independent-repro
```

### Full DataHub MCP path

```bash
make live-datahub-smoke
```

The first full DataHub run downloads containers, so no fixed clean-install duration is claimed.

## Proof Pack output

Each path includes:

```text
candidate.json
datahub-context.json
gate-receipt.json
mcp-read.json
mcp-write.json
manifest.json
SHA256SUMS
```

Reproduction rejects modified artifacts, non-canonical JSON, symlinks, missing files, and unexpected files. The pack is content-addressed and tamper-evident; no digital-signature claim is made.

## Real-world usefulness

The target users are data platform, AI platform, governance, and risk teams reviewing agent-generated data actions.

The recurring job is not “generate more code.” It is:

> Decide whether the exact generated candidate is bound to current metadata context and ready for human review without hiding stale or missing evidence.

The project produces:

- a deterministic verdict;
- explicit block reasons;
- evidence references;
- a reproducible Proof Pack;
- a durable DataHub receipt;
- a fail-closed promotion state.

Proposed measurement targets include stale-contract blocks, Proof Pack reproduction success, tamper-rejection success, claim-reference coverage, and human-review latency. These are measurement targets, not production metrics already achieved.

## Demo flow

1. Start with a seven-second architecture and outcome card.
2. Use split-screen footage: exact DataHub dataset on one side and stale-schema `BLOCKED` on the other.
3. Show current schema and bounded lineage from the official MCP server.
4. Contrast current-context `VERIFIED` with stale-schema `BLOCKED`.
5. Change one byte and hold `ARTIFACT_TAMPERING_DETECTED` until the narration completes.
6. Run explicit local write-back and refresh the DataHub dataset description in the same continuous clip.
7. Show the Native DataHub Description Receipts.
8. Close on the public repository, `make test-repro`, and successful GitHub Actions validation.

## Accomplishments

- complete DataHub read → verify → write-back loop;
- exact dataset, schema, and lineage binding;
- deterministic current-context `VERIFIED` and stale-schema `BLOCKED` contrast;
- restricted AST policy and bounded no-exec interpreter;
- explicit claim-to-evidence references;
- tamper-evident content-addressed Proof Packs;
- one-byte mutation rejection;
- native graph-visible description receipts;
- one-command controlled reproduction;
- fresh-clone reproduction workflow;
- public Apache-2.0 repository;
- explicit human-review and claim boundaries.

## Challenges

- preserving deterministic evidence while external write responses and timestamps vary;
- avoiding a circular hash when the final pack must retain the MCP write result;
- bounding lineage after a larger graph expansion exceeded the local GMS timeout;
- separating controlled evidence, live read-only evidence, and retained write-back evidence;
- keeping `VERIFIED` narrow enough to avoid implying deployment authorization.

## What is next

Possible extensions include structured verification properties, Custom Aspects, or event-driven DataHub Actions. They are not current features and will only be added after schema, tests, live acceptance, UI evidence, and rollback are complete.

Other next steps:

- independent external reproduction;
- broader mutation testing;
- human-comprehension testing of receipts;
- non-production design-partner evaluation.

## Pre-existing work disclosure

The broader EvidenceBound concept and earlier open-core/private verification work predate the hackathon. The DataHub MCP adapter, DataHub-bound candidate contract, bounded demo runtime, Native DataHub Description Receipt flow, DataHub-specific Proof Packs, tests, and submission materials were newly authored during the submission period.

## Explicit non-claims

- no transaction blocking;
- no production authorization;
- no automatic promotion;
- no digital-signature guarantee;
- no immutable-storage claim;
- no Custom Aspect claim;
- no DataHub Actions or alerting claim;
- no custom DataHub badge claim;
- no enterprise-ready, customer-accepted, certification, or production-readiness claim.
