# EvidenceBound DataHub Gate — 2:45 Video Master

- Resolution: 1920×1080
- Target duration: 2:40–2:50
- Language: English voiceover and captions
- Evidence classes: controlled public-repository evidence, retained live DataHub MCP acceptance evidence, current GitHub evidence, and clearly labeled editorial architecture cards.
- Accepted dataset: `urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.ORDER_ENTRY_DB.analytics.order_history,PROD)`

## 01 · BLOCKED BEFORE RUNTIME

This is the failure we want to see. A stale-schema candidate reaches EvidenceBound and returns BLOCKED with SCHEMA MISMATCH. The runtime result stays null, promotion authorization stays false, and no deployment or transaction claim is made.

## 02 · FAIL-CLOSED GOVERNANCE FOR DATA AGENTS

EvidenceBound DataHub Gate adds a narrow boundary between metadata access and human approval: Read Context, Restricted AST Gate, Tamper-Evident Proof Pack, and Native DataHub Write-Back. Mandatory Human Review remains outside automation.

## 03 · THE ACCEPTED LIVE DATASET

The accepted live run used the DataHub showcase order-history dataset. MCP discovered this exact URN, read entity and schema context, obtained lineage evidence, ran both candidate paths, and appended both receipts to the same description.

## 04 · SCHEMA PLUS BOUNDED ONE-HOP LINEAGE

The read is deliberately bounded to one lineage hop and five results. Upstream is checked first; after a visible edge, the opposite direction is skipped. This avoids unbounded expansion, while missing lineage still blocks verification.

## 05 · RESTRICTED AST POLICY

The candidate enters the deterministic gate. Dataset identity and observed digests bind first. The Restricted AST Policy rejects unsupported constructs. Supported operations run in a Fail-Closed Bounded Interpreter without `exec`, and claims require evidence references.

## 06 · CURRENT CONTEXT: VERIFIED

With current DataHub context, the candidate matches observed schema and lineage digests, producing VERIFIED. The verdict covers only the recorded candidate, context, policy, and interpreter. Promotion remains false and human review remains required.

## 07 · ONE DIGEST CHANGED: BLOCKED

Change only the expected schema digest. The source does not run. EvidenceBound returns BLOCKED with SCHEMA MISMATCH, a different Proof Pack root, and no runtime result. Stale contracts do not silently pass.

## 08 · NATIVE DATAHUB DESCRIPTION RECEIPTS

Both outcomes become Native DataHub Description Receipts through official `update_description`. Each records verdict, Proof Pack root, digests, reasons, human review, and false promotion authorization. It is graph-visible metadata evidence, not a badge or production authorization.

## 09 · TAMPER-EVIDENT CONTENT-ADDRESSED PROOF PACK

Each result becomes a Tamper-Evident Content-Addressed Proof Pack. The retained VERIFIED pack reproduced with manifest `b41f3692…`; the BLOCKED pack with `3f83fed5…`. Candidate, context, receipt, MCP evidence, manifest, and SHA-256 sums remain inspectable.

## 10 · ONE-BYTE TAMPER REJECTION

Tamper evidence is executable. The public test appends one byte to `gate-receipt.json` and reruns verification. The required result is `ARTIFACT_TAMPERING_DETECTED`. This is hash-based detection, not a digital-signature claim.

## 11 · PUBLIC REPOSITORY · GREEN GITHUB ACTIONS

The implementation is public at `moneyparking/evidencebound-datahub-gate`. Accepted commit `c8279f…` is validated by Actions run `30833135318`. Checkout, Python setup, installation, and deterministic validation all succeeded.

## 12 · A NARROW, REVIEWABLE GOVERNANCE BOUNDARY

The architecture is deliberately narrow. DataHub MCP supplies identity, schema, and bounded lineage. EvidenceBound applies the Restricted AST Policy and Fail-Closed Bounded Interpreter, then emits the Proof Pack and Native Description Receipt. The final decision is Mandatory Human Review.

## Claim boundary

This video does not claim transaction blocking, production authorization, a digital signature, a custom DataHub badge or aspect, LLM integration, a fixed clean-install duration, enterprise readiness, or certification.

## Visual integrity rule

No editorial frame is represented as a DataHub UI or terminal screenshot. Live acceptance statements are limited to retained acceptance output, and controlled Proof Pack evidence is labeled separately from live DataHub MCP evidence.
