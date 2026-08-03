# Pre-existing work disclosure

The general EvidenceBound concept, earlier verification contracts, and private/open-core work existed before the DataHub hackathon submission period.

This repository's DataHub-specific vertical slice was newly authored during the submission period:

- DataHub MCP read adapter;
- schema and lineage normalization;
- metadata-bound candidate contract;
- restricted no-`exec` deterministic demo runtime;
- DataHub MCP receipt write-back;
- DataHub-specific Proof Pack and reproduction flow;
- shared grant claim map;
- hackathon setup, tests, and documentation.

No SignalReview production code, provider payloads, customer data, private enterprise worker implementation, credentials, billing logic, or proprietary sports algorithms are included.

## Live acceptance repair

The first local live run reached DataHub MCP search before the showcase datapack was visible in the search index. DataHub search indexing is eventually consistent, so the public smoke script uses a bounded no-writeback readiness probe before performing exactly one final MCP receipt write-back run. Controlled gate behavior and Proof Pack contracts were unchanged.

## Bounded lineage repair

The first live OSS run successfully discovered a showcase dataset and read its entity and schema, but a three-hop, fifty-result MCP lineage expansion exceeded the local GMS 30-second read timeout. The public adapter now requests a bounded one-hop lineage read with at most five results and skips the opposite direction once a visible lineage edge is obtained. This preserves schema-plus-lineage evidence while avoiding an unbounded local graph expansion. Missing lineage still blocks verification.
