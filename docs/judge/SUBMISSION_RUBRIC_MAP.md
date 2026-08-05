# DataHub Hackathon Submission Rubric Map

## Purpose

This file maps the current project to the official equally weighted judging criteria and identifies the evidence a judge can inspect.

It is not a score guarantee. It is a claim-control checklist for the video, README, Devpost description, and repository.

## 1. Use of DataHub

### Current implementation

- DataHub OSS showcase dataset.
- Official DataHub MCP server through FastMCP.
- Dataset discovery through `search`.
- Exact entity identity through `get_entities`.
- Schema context through `list_schema_fields`.
- Bounded one-hop lineage through `get_lineage`.
- Native graph-visible write-back through `update_description`.

### Judge evidence

- `src/evidencebound_datahub/mcp.py`
- `scripts/run-local-datahub-smoke.sh`
- `docs/judge/DATAHUB_INTEGRATION_CONTRACT.md`
- retained real DataHub description receipt recording
- live acceptance output ending in `DATAHUB_MCP_READ_WRITE_ACCEPTANCE=PASS`

### Claim boundary

The current system does not claim Custom Aspects, DataHub Actions, tags, structured properties, or alerting.

## 2. Technical Execution

### Current implementation

- exact dataset and context binding;
- schema and lineage digests;
- restricted AST policy;
- bounded no-exec interpreter;
- explicit claim-to-evidence references;
- deterministic `VERIFIED` and `BLOCKED` outcomes;
- tamper-evident content-addressed Proof Packs;
- one-byte mutation rejection;
- read-only and write-back evidence separation.

### Judge evidence

- `src/evidencebound_datahub/core.py`
- `src/evidencebound_datahub/pack.py`
- `tests/`
- `evidence/controlled-verified/`
- `evidence/controlled-blocked/`
- `make test-repro`
- GitHub Actions exact-head validation

## 3. Originality

### Differentiated contribution

DataHub supplies current context and a durable metadata graph. EvidenceBound contributes a verification boundary that:

1. binds an exact candidate to current DataHub schema and lineage;
2. rejects stale contracts before bounded interpretation;
3. requires material claims to cite observed evidence;
4. exports a reproducible Proof Pack;
5. returns a narrow verification receipt to DataHub;
6. keeps promotion outside automation.

The project composes DataHub capabilities rather than rebuilding metadata discovery, lineage, or governance from scratch.

### Disclosure

The broader EvidenceBound concept predates the hackathon. The DataHub MCP adapter, DataHub-bound candidate contract, bounded demo runtime, native description receipt path, DataHub-specific Proof Packs, tests, and submission materials were authored during the submission period.

## 4. Real-World Usefulness

### Target users

- data platform teams;
- AI platform teams;
- data governance teams;
- risk and audit reviewers of agent-generated data actions.

### Recurring problem

A generated transformation or data action can be syntactically valid while being bound to stale schema, incomplete lineage, or unsupported claims.

### Outcome

Before human approval, the team receives:

- a deterministic current-context verdict;
- visible reasons for a block;
- the exact evidence references used;
- a reproducible Proof Pack;
- a durable DataHub receipt;
- explicit promotion denial until review.

### Measurement targets

These are proposed operational metrics, not measured production claims:

- stale-contract block count;
- Proof Pack reproduction success rate;
- tamper-rejection success rate;
- median human review latency;
- time from agent output to reviewable evidence;
- percentage of material claims with valid DataHub evidence references.

## 5. Submission Quality

### Judge path

Controlled one-command reproduction:

```bash
make test-repro
```

Full local DataHub path:

```bash
make live-datahub-smoke
```

Recording-specific paths:

```bash
make recording-demo-read-only
make recording-demo-writeback
```

### Submission assets

- public Apache-2.0 repository;
- README with setup and claim boundaries;
- sample Proof Packs;
- static public judge explorer;
- under-three-minute demo video;
- real terminal, GitHub Actions, and DataHub footage;
- explicit pre-existing-work disclosure;
- no unsupported production, certification, transaction-blocking, or customer-acceptance claims.

## Bonus: Open-source contribution

No bonus contribution to the upstream DataHub repositories is currently claimed.

A contribution should be pursued only if it is useful independently of this submission and can be reviewed without weakening the core delivery timeline.
