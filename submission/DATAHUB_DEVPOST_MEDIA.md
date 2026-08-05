# DataHub Devpost media package — V7 AUDITED

## Primary video configuration

Use this combination for the YouTube video embedded by Devpost:

- Video: `EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V7_AUDITED_CLEAN.mp4`
- SHA-256: `4355c09c713630f8157e06ffba428e0749e04effd41bbf0dc7f1d5d46749b9cb`
- Captions: `EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V7_AUDITED.srt`
- SRT SHA-256: `d0447de6491c5da808e9fd3caf35605a988cbffb685ab0f0c95a2d4e50087ac4`

The clean master does not burn the narration captions into the picture, so the uploaded YouTube caption track does not duplicate them.

## Burned-caption fallback

- Video: `EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V7_AUDITED_CAPTIONED.mp4`
- SHA-256: `c43f36d12339f050ea205b8a712e613235e084005c610f451e2f39cc0806f371`

Do not attach or enable the standalone SRT over this fallback. Its narration captions are already burned into the picture.

## Devpost description block

```text
Reproduce the controlled evidence path:

make test-repro

The repository also includes an independent clean-runner reproduction workflow. On source commit 922b58103f35dc64b4e645c5c13e3210824c3fad, validation run 30902198099 and independent-reproduction run 30902198411 completed successfully on GitHub Actions.

The read-only recording and native DataHub write-back are intentionally distinct evidence classes. Read-only verification can prove the MCP read, VERIFIED and stale-schema BLOCKED paths, and fresh Proof Packs without mutating DataHub metadata. Native `update_description` write-back belongs to the explicit acceptance path, remains subject to Mandatory Human Review, and never sets `promotion_authorized=true`.

Primary demo video SHA-256:
4355c09c713630f8157e06ffba428e0749e04effd41bbf0dc7f1d5d46749b9cb

This submission does not claim a digital signature, immutable storage, production authorization, customer acceptance, or a verified hosted judge deployment.
```

## Current evidence status

| Gate | Status |
|---|---|
| Repository validation on source commit | PASS |
| Independent GitHub-hosted reproduction | PASS |
| Retained VERIFIED pack reproduction | PASS |
| Retained BLOCKED pack reproduction | PASS |
| One-byte tamper rejection | PASS |
| Hosted GitHub Pages judge journey | NOT VERIFIED — deployment workflow failed at `Configure GitHub Pages` |
| Manual human review of FLITE technical pronunciation | REQUIRED |
| Actual YouTube processing and Devpost embed inspection | REQUIRED |

## Caption and accessibility rule

Devpost embeds a publicly hosted YouTube, Vimeo, or Youku video rather than accepting the MP4 directly. For YouTube, upload the clean master and its SRT together. The burned-caption fallback exists for environments where an external caption track cannot be guaranteed.

## Source and claim boundary

The V7 audited video was rendered against source commit:

`922b58103f35dc64b4e645c5c13e3210824c3fad`

The media hashes are recorded in `submission/datahub-v7-video-proof.json`. The manifest intentionally records the failed Pages deployment and does not present the editorial judge explorer as live DataHub execution.
