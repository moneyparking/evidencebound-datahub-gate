# EvidenceBound DataHub Gate

**Fail-closed read → verify → write-back governance for DataHub-connected agents.**

This repository is the newly authored DataHub hackathon vertical slice of the broader EvidenceBound design. It is intentionally independent of SignalReview production, private enterprise workers, customer code, billing, authentication, and proprietary sports logic.

## The problem

Agents can read metadata and still take unsafe actions when their generated code is bound to a stale schema, incomplete lineage, or unsupported claims. A successful tool call is not proof that the intended action is safe.

## The vertical slice

```text
DataHub MCP
  ├─ get_entities
  ├─ list_schema_fields
  └─ get_lineage
          ↓
EvidenceBound deterministic gate
  ├─ dataset identity binding
  ├─ schema + lineage digests
  ├─ restricted AST policy
  ├─ bounded no-exec interpreter
  ├─ claim-to-evidence binding
  └─ VERIFIED / BLOCKED receipt
          ↓
Content-addressed Proof Pack
          ↓
DataHub MCP update_description write-back
          ↓
mandatory human review (never automatic promotion)
```

Two paths are mandatory:

1. **VERIFIED** — current schema and lineage match the candidate contract.
2. **BLOCKED** — a stale schema digest fails closed before runtime execution.

Both outcomes are written back to the same DataHub dataset as a visible markdown receipt. The write-back is metadata, not approval to deploy or transact.

## Why description write-back instead of a custom aspect

The hackathon criterion rewards contributing knowledge back to the graph. `update_description` is an official DataHub MCP mutation, visible in DataHub OSS, and requires no custom schema registration. A custom aspect or structured property can be added after the end-to-end path is stable; it is not required for the smallest reproducible demonstration.

## Quick controlled proof (no Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
./scripts/validate.sh
```

This generates two controlled Proof Packs under `evidence/` and reproduces both.

## Live local DataHub acceptance

Prerequisites: Linux/WSL, Docker with sufficient memory, Python 3.11+, and network access for the first install.

```bash
python -m venv .venv
source .venv/bin/activate
./scripts/run-local-datahub-smoke.sh
```

The script:

1. installs DataHub and the official DataHub MCP server;
2. runs `datahub docker quickstart`;
3. loads the Apache-2.0 showcase ecommerce datapack;
4. discovers a dataset through MCP;
5. reads entity, schema, upstream lineage, and downstream lineage;
6. runs VERIFIED and stale-schema BLOCKED candidates;
7. writes both receipts back through MCP `update_description`;
8. reproduces each Proof Pack;
9. prints `DATAHUB_MCP_READ_WRITE_ACCEPTANCE=PASS` only when every gate passes.

### Stop condition

If the live smoke cannot prove all four states within the first build day, do not expand scope:

- MCP read: PASS
- verified path: VERIFIED
- stale path: BLOCKED
- MCP write-back: PASS

Preserve the logs, classify the blocker, and either repair the one integration or stop the hackathon build. A controlled fixture is not presented as live DataHub acceptance.

## Proof Pack

Each path contains:

```text
candidate.json
datahub-context.json
gate-receipt.json
mcp-read.json
mcp-write.json
manifest.json
SHA256SUMS
```

`evidence_root_sha256` deterministically binds the candidate, DataHub context, receipt, and MCP read evidence; it is the root written back to DataHub. `manifest_body_sha256` additionally binds the MCP write result. Timestamps and an optional future cryptographic seal are excluded from both deterministic roots. Reproduction rejects modified artifacts, non-canonical JSON, symlinks, missing files, and unexpected files.

## Claim boundary

`VERIFIED` means only that the exact candidate matched the observed DataHub context, passed the restricted AST policy, executed in the bounded deterministic interpreter, and bound every material claim to schema or lineage evidence.

It does **not** mean production approval, data truth, regulatory certification, model accuracy, financial safety, customer acceptance, or permission to deploy. `promotion_authorized` is always `false`; human approval is always required.

## Hackathon positioning

- Track: **Agents That Do Real Work**
- DataHub technologies: DataHub OSS + DataHub MCP Server
- Judge-visible loop: read → deterministic action gate → Proof Pack → write-back
- Submission disclosure: the EvidenceBound concept and earlier private/open-core work predate this hackathon; this DataHub adapter, bounded demo runtime, MCP workflow, and shared evidence pack were newly authored during the submission period.

## Grant synchronization

`grant-sync/claim-map.json` is the single claim boundary for Startup EDGE and Microsoft for Startups materials. It distinguishes controlled evidence, live MCP acceptance, and prohibited claims. A hackathon demo alone does not establish TRL level, funding, certification, production readiness, or customer acceptance.

## License

Apache License 2.0. See `LICENSE`.
