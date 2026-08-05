# DataHub Devpost media package — V7 AUDITED

## Primary video configuration

Use this combination for the YouTube video embedded by Devpost:

- Video: `EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V7_AUDITED_CLEAN.mp4`
- SHA-256: `47acd1b1152e36a66482735038767e0d3b844da9fea7f76d8d317303b70b6352`
- Captions: `EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V7_AUDITED.srt`
- SRT SHA-256: `aa52bfa9da4895072bf11b0358baac9f9eee8e42edaf8bd5bb3f3d92cc65208c`

The clean master does not burn narration captions into the picture, so the uploaded YouTube caption track does not duplicate them.

## Burned-caption fallback

- Video: `EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V7_AUDITED_CAPTIONED.mp4`
- SHA-256: `a1a4b00b2b8c8140e4dc10f0cc490e712d084d76cfe9e2918a375334914c13d4`

Do not attach or enable the standalone SRT over this fallback. Its narration captions are already burned into the picture.

## Devpost description block

```text
Reproduce the controlled evidence path:

make test-repro

The repository also includes an independent clean-runner reproduction workflow. On source commit 4209f1326ae8805fd069b0240d27b2521ada792c, validation run 30975467991 and independent-reproduction run 30975467842 completed successfully on GitHub Actions.

The read-only recording and native DataHub write-back are intentionally distinct evidence classes. Read-only verification can prove the MCP read, VERIFIED and stale-schema BLOCKED paths, and fresh Proof Packs without mutating DataHub metadata. Native `update_description` write-back belongs to the explicit acceptance path, remains subject to Mandatory Human Review, and never sets `promotion_authorized=true`.

Primary demo video SHA-256:
47acd1b1152e36a66482735038767e0d3b844da9fea7f76d8d317303b70b6352

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
| Hosted judge journey | NOT VERIFIED — the latest attempted GitHub Pages deployment failed at `Configure GitHub Pages` |
| Automated FLITE terminology recognition | RISK DETECTED — exact terms were not recovered reliably |
| Manual human review of FLITE technical pronunciation | REQUIRED |
| Actual YouTube processing and Devpost embed inspection | REQUIRED |

## Caption and accessibility rule

Devpost embeds a publicly hosted video rather than accepting this local MP4 as the final judge player. For YouTube, upload the clean master and its SRT together. The burned-caption fallback exists for environments where an external caption track cannot be guaranteed.

The 960×540 reduction preserves headings, verdicts, captions, and main commands. At 640×360, hashes, URNs, and detailed terminal lines are not forensic-readable; those exact values remain available in the repository manifest and high-resolution source material. The actual processed YouTube/Devpost embed must still be inspected before publication.

## Source and claim boundary

The V7 audited video was rendered against source commit:

`4209f1326ae8805fd069b0240d27b2521ada792c`

The media hashes are recorded in `submission/datahub-v7-video-proof.json`. The manifest preserves the hosted-deployment gap and does not present the editorial judge explorer as live DataHub execution.
