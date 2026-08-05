# DataHub Devpost media package — V7.1 AUDITED

## Recommended publication configuration

Upload this master to YouTube and embed that public YouTube URL in Devpost:

- Video: `EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V7.1_AUDITED_CAPTIONED.mp4`
- SHA-256: `3b747380157051b2293a3bf1b743ac82c4b1584ec71bf37207a57311c9c3f7b2`
- Captions: burned into the video
- External SRT: **do not enable**
- YouTube automatic captions: review and disable if they create duplicate text over the burned captions

Alternative accessibility path:

- Clean video: `EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V7.1_AUDITED_CLEAN.mp4`
- SHA-256: `5733a3c41ca83bae41ee81b1d754c053e406303ace3f1977c5f80b18d3619427`
- SRT: `EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V7.1_AUDITED.srt`
- SRT SHA-256: `9c3199c91e0613303913ca634a9d3b7564d66bb9ceb215bc472fb28d23c18200`

Use exactly one caption path. Do not combine the burned-caption master with the standalone SRT.

## Source binding

The video is bound to immutable release source commit:

`4209f1326ae8805fd069b0240d27b2521ada792c`

Its parent is `922b58103f35dc64b4e645c5c13e3210824c3fad`. The parent is not the current release source. The media does not claim that the immutable release source will remain equal to mutable branch `main` after the media manifest is committed.

## Devpost verification block

```text
Controlled reproduction:

git clone https://github.com/moneyparking/evidencebound-datahub-gate.git
cd evidencebound-datahub-gate
make test-repro

Exact video source snapshot:
git checkout 4209f1326ae8805fd069b0240d27b2521ada792c
make test-repro

The read-only recording and native DataHub write-back are intentionally distinct evidence classes. Read-only verification proves the MCP read, current-context VERIFIED path, stale-schema BLOCKED path, and fresh Proof Packs without mutating DataHub metadata. Native update_description write-back belongs to the explicit acceptance path. Mandatory Human Review remains required and promotion_authorized=false.

Primary demo video SHA-256:
3b747380157051b2293a3bf1b743ac82c4b1584ec71bf37207a57311c9c3f7b2
```

## Evidence status

| Gate | Status |
|---|---|
| Source validation on `4209f132` | PASS — run `30975467991` |
| Independent clean GitHub-hosted reproduction | PASS — run `30975467842` |
| Exact advertised `make test-repro` with project env cleared | PENDING current PR CI |
| Full decode of clean master | PASS |
| Full decode of captioned master | PASS |
| Simulated 960×540 readability | PASS for headings, verdicts, commands, captions and source revision |
| Simulated 640×360 readability | PASS for narrative and major states; full hashes/URNs are not forensic-readable |
| Manual FLITE terminology listening | REQUIRED |
| Actual processed YouTube/Devpost embed | NOT RUN |
| Hosted public judge journey | NOT VERIFIED |

## Technical terminology

The regenerated narration fragments use explicit spoken forms:

- `M. C. P.`
- `A. S. T.`
- `U. R. N.`
- `S. H. A. two five six`
- `promotion underscore authorized equals false`

Automated speech recognition was inconclusive. Exact terms remain visible in the burned captions and evidence screens. Human playback remains a release requirement.

## Claim boundary

This package does not claim a digital signature, immutable storage, hosted application, production authorization, customer acceptance, certification, automatic promotion, or that the read-only recording performed native write-back.
