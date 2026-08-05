# DataHub Integration Contract

## Purpose

This document defines the DataHub behavior that the repository currently implements and may claim in the hackathon submission.

It intentionally separates working integration from possible future extensions. Video, README, Devpost text, and judge instructions must not claim a DataHub capability that has not passed the acceptance path below.

## Current working integration

### DataHub context read

The adapter starts the official DataHub MCP server through FastMCP over stdio and reads the selected dataset using these MCP tools:

| Operation | MCP tool | Contract |
| --- | --- | --- |
| Dataset discovery | `search` | Finds DataHub dataset URNs only. |
| Entity identity | `get_entities` | Establishes the exact selected dataset identity. |
| Schema | `list_schema_fields` | Reads up to 100 schema fields for deterministic binding. |
| Lineage | `get_lineage` | Reads at most one hop and five results. Upstream is checked first; downstream is skipped after a visible upstream edge. |

The accepted showcase dataset is:

```text
urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.ORDER_ENTRY_DB.analytics.order_history,PROD)
```

The deterministic gate binds the candidate to:

- the exact dataset URN;
- the observed schema digest;
- the observed bounded-lineage digest;
- the required schema fields;
- explicit schema and lineage evidence references.

Missing schema or lineage blocks the path. Historical or editorial evidence cannot substitute for a successful MCP read.

### Native DataHub write-back

The current write path uses the official MCP mutation:

```text
update_description
```

The operation is `append` against the selected dataset description. Each Native DataHub Description Receipt includes:

- verdict: `VERIFIED` or `BLOCKED`;
- Proof Pack root;
- candidate ID;
- observed schema digest;
- observed lineage digest;
- reasons;
- human approval: `REQUIRED`;
- promotion authorization: `false`.

This is graph-visible metadata evidence. It is not a deployment action, transaction block, production authorization, certification, or automatic promotion.

## Read-only and write-back evidence classes

The recording and submission must keep these paths distinct:

### Read-only

```bash
scripts/run-recording-demo.sh --read-only
```

Expected acceptance:

```text
mcp_read=PASS
verified_path=VERIFIED
blocked_path=BLOCKED
mcp_write_back=NOT_RUN
```

### Explicit local write-back

```bash
scripts/run-recording-demo.sh --writeback
```

Expected acceptance:

```text
mcp_read=PASS
verified_path=VERIFIED
blocked_path=BLOCKED
mcp_write_back=PASS
```

`--writeback` mutates metadata in the configured DataHub instance. Use it only on the local hackathon environment after confirming the dataset identity.

## Capabilities not currently claimed

The current accepted system does **not** implement or claim:

- custom DataHub aspects;
- custom DataHub badges;
- DataHub Actions event processing;
- alert delivery on tamper detection;
- structured-property definitions for verification status;
- automatic workflow state changes;
- transaction blocking;
- automatic deployment or promotion.

These features must not appear in the video as working functionality.

## Future extension gate

A Custom Aspect, structured-property, tag, or DataHub Actions extension may be added only after all of the following are true:

1. the repository contains the exact schema or event contract;
2. deterministic tests cover the extension;
3. a fresh local DataHub instance accepts the contract;
4. the mutation is visible in the real DataHub UI;
5. rollback is documented;
6. the video records the real execution rather than an editorial simulation;
7. Devpost and README claims are updated to the exact accepted behavior.

Until then, the official `update_description` path remains the canonical write-back contract.

## Acceptance commands

Controlled judge reproduction without DataHub:

```bash
make test-repro
```

Full local DataHub MCP read/write acceptance:

```bash
make live-datahub-smoke
```

Recording-specific path with explicit mutation control:

```bash
make recording-demo-read-only
make recording-demo-writeback
```
