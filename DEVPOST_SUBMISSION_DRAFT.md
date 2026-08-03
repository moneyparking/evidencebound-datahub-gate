# Devpost Submission Draft

## Project name

EvidenceBound DataHub Gate: Fail-Closed Governance for Data Agents

## Tagline

Read schema and lineage, verify the intended action, and write a reproducible receipt back to DataHub before a human approves anything.

## Track

Agents That Do Real Work

## Problem

Metadata-aware agents can still act on stale schemas, incomplete lineage, or claims that are not bound to evidence. A successful MCP call or generated code sample is not durable proof that the intended action was safe.

## Solution

EvidenceBound DataHub Gate uses the official DataHub MCP server to read a dataset, schema fields, and lineage. A deterministic gate then binds the candidate to those observations, applies a restricted AST policy, runs a small bounded interpreter without `exec`, verifies every material claim against schema or lineage references, and emits a typed `VERIFIED` or `BLOCKED` receipt. A content-addressed Proof Pack is generated and the evidence root is written back to the same DataHub dataset through MCP. Human approval remains mandatory.

## How it was built

- DataHub OSS local quickstart and showcase metadata;
- official DataHub MCP server through FastMCP stdio;
- Python 3.11 standard-library verification core;
- canonical JSON and SHA-256 content addressing;
- restricted AST profile and bounded deterministic interpreter;
- pytest, Ruff, Mypy, and GitHub Actions;
- Apache License 2.0.

## Demo flow

1. Discover a dataset with schema and lineage through MCP.
2. Run the current-context candidate: `VERIFIED`.
3. Mutate only the expected schema digest: `BLOCKED` before runtime.
4. Show both Proof Pack roots.
5. Open DataHub and show both receipts appended to the dataset description.
6. Reproduce both packs from the CLI.

## Accomplishments

- one complete read → verify → write-back loop;
- deterministic happy and blocked paths;
- write-back carries evidence rather than an unsupported confidence score;
- no automatic deployment or transaction authorization;
- public clean-room DataHub integration separated from private enterprise code.

## Challenges

- keeping the write-back judge-visible without requiring a custom DataHub aspect schema;
- avoiding a circular hash when the write result itself must be retained;
- preserving deterministic evidence while timestamps and external write responses vary;
- separating pre-existing EvidenceBound concepts from newly authored hackathon code.

## What is next

After hackathon acceptance, add an optional DataHub structured-property schema, an independent clean-install reproduction, and an Azure non-production validation environment. These are not claimed as complete in the submission.

## Pre-existing work disclosure

The EvidenceBound concept and earlier private/open-core verification work predate the hackathon. The DataHub MCP adapter, metadata-bound candidate contract, bounded demo runtime, DataHub receipt write-back, DataHub-specific Proof Pack, tests, and submission materials were newly authored during the submission period.
