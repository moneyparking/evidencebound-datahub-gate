# V11 OBS Split-Screen Recording Runbook

## Goal

Record one new evidence clip that shows the terminal execution and the corresponding DataHub state in the same frame without implying capabilities that are not implemented.

The clip will replace separate terminal and DataHub shots where simultaneous context materially improves judge comprehension.

## Required result

A judge must be able to see, in one continuous recording:

1. the exact selected DataHub dataset;
2. the terminal command and acceptance markers;
3. `VERIFIED` and stale-schema `BLOCKED` outcomes;
4. explicit distinction between read-only and write-back execution;
5. the Native DataHub Description Receipt after the explicit write-back run;
6. `promotion_authorized=false` and Mandatory Human Review.

## Layout

OBS canvas:

```text
1920 × 1080 @ 30 fps
```

Recommended split:

```text
┌───────────────────────────┬──────────────────────────────────────────┐
│ Terminal                  │ DataHub browser                          │
│ 42% width                 │ 58% width                               │
│                           │                                          │
│ command + verdicts        │ dataset identity + description receipt  │
└───────────────────────────┴──────────────────────────────────────────┘
```

Rules:

- capture each window directly; do not crop the terminal output or browser address bar;
- terminal font must remain readable at 1080p;
- browser zoom should be 100% unless the complete receipt is unreadable;
- hide bookmarks, notifications, account data, tokens, and unrelated tabs;
- do not place burned subtitles over hashes, verdicts, dataset identity, or receipt text;
- use one small lower-third classification label only after editing.

## Preflight

From the repository root:

```bash
source .venv/bin/activate
export DATAHUB_GMS_URL=http://localhost:8080
```

Verify the local DataHub UI:

```text
http://localhost:9002
```

Open this exact dataset before recording:

```text
urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.ORDER_ENTRY_DB.analytics.order_history,PROD)
```

Confirm that the repository command is available:

```bash
evidencebound-datahub --help
```

## Recording A — read-only proof

Terminal:

```bash
make recording-demo-read-only
```

Keep DataHub open on the selected dataset. Do not imply a metadata mutation occurred.

Required terminal end state:

```text
RECORDING_MODE=READ_ONLY
SCENE_MARKER=VERIFIED_AND_BLOCKED_COMPLETE
SCENE_MARKER=MCP_WRITE_BACK_NOT_RUN
RECORDING_DEMO_ACCEPTANCE=PASS
```

Recommended clip use:

- dataset identity;
- MCP read;
- current-context `VERIFIED`;
- stale-schema `BLOCKED`;
- Proof Pack generation;
- clear `WRITE-BACK NOT_RUN` boundary.

## Recording B — explicit native write-back

This run mutates the description in the local hackathon DataHub instance.

Terminal:

```bash
make recording-demo-writeback
```

Required terminal end state:

```text
RECORDING_MODE=WRITEBACK
SCENE_MARKER=VERIFIED_AND_BLOCKED_COMPLETE
SCENE_MARKER=MCP_WRITE_BACK_PASS
RECORDING_DEMO_ACCEPTANCE=PASS
```

Then, without stopping OBS:

1. refresh the DataHub dataset page;
2. open the dataset description;
3. scroll slowly to the newly appended receipts;
4. hold the following fields for at least three seconds:
   - verdict;
   - Proof Pack root;
   - schema digest;
   - lineage digest;
   - reasons;
   - human approval required;
   - promotion authorization false.

## Suggested V11 video structure

### 0:00–0:07 — architecture and outcome

Use a clean editorial card:

```text
Agent → DataHub Context → EvidenceBound Gate → Proof Pack → Native Receipt → Human Review
```

Do not show a terminal before the viewer understands the outcome.

### 0:07–0:25 — split-screen fail-closed proof

Show:

- exact dataset on the right;
- stale-schema `BLOCKED` on the left;
- runtime result remains null;
- promotion authorization remains false.

### 0:25–0:55 — DataHub depth

Show:

- dataset identity;
- schema fields;
- bounded one-hop lineage;
- the reason DataHub is required: current graph context and durable write-back.

### 0:55–1:30 — deterministic gate

Show:

- current-context `VERIFIED`;
- stale-schema `BLOCKED`;
- restricted AST / bounded interpreter explanation;
- no-exec and evidence-reference boundaries.

### 1:30–2:05 — Proof Pack and tamper rejection

Show the exact one-byte mutation while Ethan says “change one byte,” then hold `ARTIFACT_TAMPERING_DETECTED` until the sentence ends.

### 2:05–2:32 — native write-back

Use Recording B. Show the terminal mutation acceptance and the refreshed DataHub receipt in the same continuous clip.

### 2:32–2:52 — reproducibility

Show public repository, `make test-repro`, and successful GitHub Actions.

### 2:52–2:59 — final value

Close with:

```text
Fail closed. Preserve evidence. Return knowledge to DataHub. Keep approval human.
```

## Stop conditions

Do not use the recording if any of these occur:

- dataset identity is cropped or unreadable;
- terminal output is cut off horizontally;
- the write-back run does not end in `MCP_WRITE_BACK_PASS`;
- the DataHub description does not visibly contain the new receipt;
- a read-only run is presented as a write-back run;
- a custom aspect, DataHub Action, alert, or state transition is implied without real implementation;
- personal data, secrets, access tokens, or unrelated browser content are visible.
