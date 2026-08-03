# DataHub Hackathon Sprint — August 3–10, 2026

## Product decision

Build one judge-visible workflow for the **Agents That Do Real Work** track:

```text
DataHub MCP read schema + lineage
  -> deterministic EvidenceBound gate
  -> VERIFIED or stale-schema BLOCKED
  -> reproducible Proof Pack
  -> DataHub MCP receipt write-back
  -> mandatory human review
```

Do not build a generic agent platform, second control plane, custom aspect registry, multi-cloud runtime, or SignalReview sports UI for this submission.

## Ultimate outcome

A first-time judge can start DataHub OSS, run one command, observe both paths in the terminal, inspect the receipts in the DataHub dataset description, and reproduce the same evidence roots from the public Apache-2.0 repository.

## External acceptance condition

The sprint may proceed beyond Gate 0 only after the live local run prints:

```text
DATAHUB_MCP_READ_WRITE_ACCEPTANCE=PASS
```

This requires all of:

- MCP schema and lineage read: PASS;
- current-context path: VERIFIED;
- stale-schema path: BLOCKED before runtime execution;
- MCP description write-back: PASS;
- both Proof Packs reproduce.

## Gate 0 stop condition

Deadline: **August 4, 2026 at 12:36 Europe/Kyiv**.

If live DataHub MCP read and write-back are not both proven by then:

1. preserve logs and controlled Proof Packs;
2. classify the blocker as environment, DataHub version, MCP contract, dataset fixture, or code;
3. attempt only the smallest repair;
4. stop the hackathon scope if the same acceptance condition remains unproven after the 24-hour gate.

A mock or controlled fixture cannot be relabeled as live DataHub acceptance.

## Schedule

| Date | Deliverable | Acceptance |
| --- | --- | --- |
| Aug 3 | Public-ready Apache-2.0 repo, deterministic gate, controlled packs, MCP adapter | unit tests and controlled reproduction pass |
| Aug 3–4 | DataHub OSS + MCP live read/write smoke | Gate 0 acceptance string and retained live packs |
| Aug 4 | Minimal receipt viewer and failure diagnostics only if Gate 0 passes | judge can distinguish VERIFIED/BLOCKED and evidence roots |
| Aug 5 | Clean-install reproduction on second environment | first-time run succeeds without developer intervention |
| Aug 6 | 3-minute video v1 and screenshots | complete read→verify→write loop visible |
| Aug 7 | Devpost draft and license/disclosure audit | all required fields complete, no unsupported claims |
| Aug 8 | External reproduction review | independent reproduction or visible blocker report |
| Aug 9 | Submission freeze | public repo, video, evidence pack, claim map aligned |
| Aug 10, 18:00 Kyiv | Submit early | Devpost submission saved and publicly testable |
| Aug 10, 21:00 Kyiv | Internal no-new-feature freeze | only critical submission repair afterward |
| Aug 11, 00:00 Kyiv | Official deadline | no reliance on last-minute upload |

## Evidence classes

- `CONTROLLED`: mock DataHub-shaped context and deterministic local proof.
- `LIVE_LOCAL_DATAHUB`: actual DataHub OSS and official MCP server read/write evidence.
- `PUBLIC_REPRODUCTION`: clean public-repo reproduction by a first-time operator.
- `HACKATHON_SUBMISSION`: public Devpost, video, repo, and claims aligned.
- `GRANT_APPLICATION`: separately reviewed application claims; no automatic TRL, funding, certification, or customer claim.

## Grant synchronization

One `grant-sync/claim-map.json` governs both applications. The same live evidence artifacts may support:

- Startup EDGE: controlled-environment DeepTech prototype evidence;
- Microsoft for Startups: non-production metadata-governance workload suitable for later Azure validation.

The artifacts do not prove a specific TRL level, Azure deployment, funding approval, certification, production readiness, or customer acceptance.

## Rollback

- remove or revert the hackathon subtree and funding references;
- do not change SignalReview production, database, auth, billing, providers, DNS, or deployment;
- preserve retained Proof Packs and failure logs as audit evidence;
- do not publish private enterprise internals or customer data.
