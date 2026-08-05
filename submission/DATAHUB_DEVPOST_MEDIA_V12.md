# EvidenceBound DataHub Hackathon — V12 Devpost Media Release

## Recommended submission master

```text
EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V12_JUDGE_CAPTIONED.mp4
SHA-256: e51fbd9d9ddf69d87d7754be05f80f765cf05f768d63aff21c854c5815bd2a9a
Duration: 169.813000 seconds
Resolution: 1920×1080
Frame rate: 30 fps
Video: H.264, yuv420p
Audio: AAC, 48 kHz, stereo
Captions: burned English narration captions present
```

The recommended Devpost and YouTube upload is the JUDGE CAPTIONED master. Do not add a second subtitle track over the burned captions.

## Clean alternative

```text
EvidenceBound_DataHub_Hackathon_FINAL_MASTER_V12_CLEAN.mp4
SHA-256: 743817a456761207c87461475498e419835694b623c2cf23a1a703bfc16c2009
Duration: 169.866667 seconds
Resolution: 1920×1080
Frame rate: 30 fps
Video: H.264, yuv420p
Audio: AAC, 48 kHz, stereo
```

## Release binding

```text
Repository: moneyparking/evidencebound-datahub-gate
Release source commit: 9f39bcf2498a05a47dd7b0a82049e95893770642
Pull request: #10
Ed25519 key ID: evidencebound-datahub-hackathon-2026
Public-key SHA-256: fdf31b458136d39b3c22fe041e9ae7c986365c40275383d09e8a38ae81f0680d
```

Release acceptance shown in V12:

- deterministic gates: PASS, workflow run 26;
- independent reproduction: PASS, workflow run 22;
- GitHub Pages deployment: PASS, workflow run 4;
- Pages deployment artifact digest: `sha256:d1459dee4762c3a2fb3ba950b1f18549aca6065b017429998a17437a4ad86636`.

## Audio QA

```text
AAC stream SHA-256: b671d773648747fb49dcf7a522a4b0defe0862bdf5c9b13c0910b01f1a582251
Integrated loudness: −14.2 LUFS
Loudness range: 2.0 LU
True peak: −1.9 dBFS
```

The V12 CLEAN and JUDGE CAPTIONED audio streams are byte-identical to the accepted V11 audio stream truncated to the V12 duration. No additional gain was applied.

## Visual evidence

V12 retains the real terminal, DataHub, and GitHub evidence and adds a final judge-visible release section showing:

- redesigned public Judge Explorer;
- current-context `VERIFIED` and stale-schema `BLOCKED` paths;
- one-byte `ARTIFACT_TAMPERING_DETECTED` rejection;
- detached Ed25519 verification for the retained controlled `VERIFIED` and `BLOCKED` Proof Packs;
- repository-published public-key fingerprint;
- release source SHA and successful CI, independent-reproduction, and Pages deployment states;
- `NO AUTOMATIC PROMOTION` and Mandatory Human Review.

## Evidence-class boundary

The retained controlled Ed25519-sealed packs are distinct from the accepted live DataHub MCP dataset and live description write-back evidence. V12 does not represent the controlled seals as signatures over the separate live acceptance run.

The public Judge Explorer is a static editorial evidence explorer. It does not execute DataHub, represent live DataHub UI, create new acceptance evidence, or authorize deployment.

## Explicit non-claims

V12 does not claim:

- transaction blocking or deployment permission;
- production authorization or certification;
- immutable storage;
- automatic promotion;
- independent legal identity solely from a repository-published key;
- that every newly generated or live DataHub Proof Pack is Ed25519-signed;
- a custom DataHub badge or aspect;
- customer acceptance or enterprise production readiness.

A valid Ed25519 signature proves possession of the matching private key. Independent signer identity requires comparison of the published fingerprint through a separately trusted channel.

## YouTube publication

```text
Video ID: dEWJ2eGiDO8
Short URL: https://youtu.be/dEWJ2eGiDO8
Canonical watch URL: https://www.youtube.com/watch?v=dEWJ2eGiDO8
Publication mode: standard public video; premiere removed by owner
YouTube oEmbed endpoint: PASS (HTTP 200)
YouTube embeddable-player endpoint: PASS (HTTP 200)
YouTube max-resolution thumbnail endpoint: PASS (HTTP 200)
OEmbed title: EvidenceBound DataHub Gate
OEmbed author: RV
Owner-confirmed 1080p selection: PASS
```

The successful publication probe ran on a GitHub-hosted runner as workflow run `31024839874`. Its retained artifact digest is `sha256:09aeef97414587143b28a4e20ad26402cf44fa5e644a211dda26b70f709afc9f`.

An earlier unauthenticated `yt-dlp` metadata probe was blocked by YouTube's anti-bot challenge. The later official oEmbed, embed, and thumbnail endpoint checks passed; the earlier anti-bot result is therefore retained only as a probe limitation and not interpreted as a video failure.

## Publication gate

Technical render and automated QA: PASS.

Public YouTube publication and embeddability: PASS. Full start-to-finish playback in the processed YouTube stream and verification of the embedded Devpost player remain the final external publication gates.
