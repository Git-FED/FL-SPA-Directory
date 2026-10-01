# Security Policy

## The honest threat model, first

FED-SPA has **no server, no database, no accounts, no telemetry**. The entire attack surface is: static files on a host, the subscriber's own device, and the crypto envelope. There is nothing to breach in the middle. That is a design decision ([README](README.md) — the three constraints), not an oversight, and it means the interesting security questions are all about the envelope and the distribution of the shared code.

The envelope is **client-side encryption with a shared symmetric code**. It is a deliberate access-tier speed bump, not a per-subscriber security system, and it should not be described as more than that. This honesty is a feature: [wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md) and [docs/password_distribution.md](docs/password_distribution.md) document exactly what the system is and is not.

## What is genuinely sensitive in this repo

1. **`data/private/unlicensed.plain.json` — the plaintext watchlist.** It must never be committed, pushed, attached, or pasted anywhere. `.gitignore` covers it; the annual workflow never requires it to leave the maintainer's machine; CI refuses plaintext. If it has ever been exposed, the incident is a code rotation, not a patch — see below.
2. **The shared subscriber code.** Possession of the code plus the public envelope equals the data. The code is rotated annually with the release (see [docs/password_distribution.md](docs/password_distribution.md)).

## Supported versions

The project ships a single supported line — the current release. Data releases are tagged `data-<year>`; security fixes to code ship on `main` and are noted in [CHANGELOG.md](CHANGELOG.md). There is no LTS branch, no backporting, and no legacy surface support: static files are re-shipped, not patched in place.

| Version | Supported |
|---|---|
| current `main` / latest `data-*` tag | ✅ |
| anything older | ❌ — pull the latest files |

## Reporting a vulnerability

**Do not open a public issue for a security problem.** Instead, use GitHub's **private vulnerability reporting** on this repository (Security tab → "Report a vulnerability"), which is the preferred channel. If private reporting is unavailable to you for some reason, open a Discussion in the **Q&A** category titled "Security contact" with no details, and a maintainer will provide a contact path.

Please include:

- The surface(s) affected (web / extension / Android / Auto / watch / iOS), with version or commit.
- Whether the issue is in the **crypto envelope** (spec in [wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md)), the **data pipeline** (`admin_scripts/`), or the **UI/hosting** layer.
- A description of the impact in terms of this project's actual assets: plaintext exposure, code compromise, record integrity (a forged or wrong record being trusted), or availability of the static host.
- Reproduction steps or a proof of concept where possible.

You will get an acknowledgment within a reasonable volunteer timeframe. FED-SPA is maintained by volunteers on an annual-cycle project; there is no SLA, and we appreciate that reporters keep that in mind.

## What is and is not in scope

**In scope:**

- Any way the plaintext watchlist could be committed, leaked, or reconstructed from the repo.
- Cross-platform crypto envelope inconsistencies — the five implementations drifting from the frozen spec ([wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md)).
- Weaknesses in the annual pipeline that could let a wrong or fabricated record enter the dataset ("record integrity").
- XSS or content-injection in the web app / extension surfaces (all code is vanilla, no third-party scripts, no eval, no remote HTML — a finding here is a real finding).
- Supply-chain risk introduced by a PR adding any dependency (the no-third-party rule is also a security control).

**Out of scope:**

- "The shared code can be shared" — yes. That is the documented model, not a flaw. See [docs/password_distribution.md](docs/password_distribution.md).
- Brute-forcing the envelope with the code holder's cooperation, or the fact that a holder can decrypt and rehost the watchlist — the license ([COPYING.md](COPYING.md)) and the threat model already account for this.
- "No backend" as a finding. If a report argues the project needs server-side auth to be "really secure," the answer is in the FAQ and the constraints — we will not add one.
- Automated scanner noise on static files that requires no user interaction and exposes nothing (e.g., "missing header X on a static page").
- The Florida DOH MQA portal itself — it is not ours; report issues with the portal to the State of Florida.

## Handling process

1. Acknowledge the report privately.
2. Triage against the constraints — a "fix" that requires a backend or a third-party library is not available to us; the fix will be first-party or the design will change.
3. Crypto-envelope findings affect five implementations; all five change together, the envelope `v` bumps if the format moves, and CI's round-trip self-test ([.github/workflows/build.yml](.github/workflows/build.yml)) must pass for every surface.
4. If plaintext data was exposed: rotate the code, re-encrypt, re-ship the release, and disclose plainly in [CHANGELOG.md](CHANGELOG.md). Because the dataset itself is ODbL and the encryption is an access tier (not a protection measure), an exposure is primarily a *courtesy and expectations* problem — it is still treated as a real incident.
5. Credit reporters in the changelog entry, by name or anonymously, at their choice.

## One standing caution for contributors

The most likely real-world incident in this project's life is not a crypto break — it is a maintainer accidentally committing `unlicensed.plain.json` during the annual refresh. The workflow is deliberately built to make that hard (placeholders in the repo, CI checks, `.gitignore`), but the human rule stands: **before every push during data season, run `git status` and look for `data/private/unlicensed.plain.json` with your own eyes.**
