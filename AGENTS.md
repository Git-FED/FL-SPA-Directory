# AGENTS.md — Instructions for AI Coding Agents Working on FED-SPA

This file is the standing instruction set for any AI agent (or human pair) contributing code to this repository. It exists so that agent-assisted PRs arrive already inside the project's constraints instead of being bounced for violating them.

## The three constraints — read before writing any code

1. **No backend.** Static files only, updated once a year. If your task seems to need a server, an API, a cron job, a remote config, or "just one endpoint," the task is mis-framed — re-read the docs, not the requirement.
2. **No third-party.** No external libraries, SDKs, services, analytics, fonts, CDNs, or icon packs on any surface. Allowed, exhaustively: Python stdlib · Node's native `crypto` · vanilla JS/CSS · androidx core-ktx + appcompat · SwiftUI + CryptoKit + CommonCrypto (zero SPM dependencies). In CI: only GitHub-owned actions (`actions/checkout`, `actions/setup-python`, `actions/setup-node`, `actions/upload-artifact`).
3. **Annual cadence.** No auto-refresh, no polling, no update-available UI, no freshness assumptions. Data is a dated snapshot; the surfaces say so plainly.

**These are enforced in review and CI.** A PR that adds a dependency is closed on that ground alone, regardless of code quality. When in doubt, the argument for *why* is in [wiki/FAQ.md](wiki/FAQ.md) and [ADR.md](ADR.md) — read it, don't relitigate it in code.

## Repo map (where things live and what touches what)

```
data/public/licensed.json            # single source of truth (plaintext, public)
data/private/unlicensed.encrypted.json  # committed subscriber envelope
data/private/unlicensed.plain.json   # NEVER committed, never pasted, never attached
data/meta/schema.json                # the data contract
admin_scripts/                       # annual workflow (stdlib Python, native-crypto Node)
web/ extension/                      # vanilla JS/CSS surfaces (Web Crypto)
android/ android_auto/ watch/        # Kotlin, classic views (javax.crypto)
ios/                                 # SwiftUI (CommonCrypto + CryptoKit)
.github/workflows/build.yml          # validate → fan-out drift → smoke → envelope test → zip
wiki/ docs/ prompts/                 # the written reasoning; update with behavior changes
styles.css                           # the design-token contract at repo root
```

**The load-bearing invariants:**

- **Fan-out:** bundled data in `web/data/`, `extension/data/`, `android*/app/src/main/assets/data/`, and `ios/Resources/Data/` is *generated* by `admin_scripts/generate_public_files.py`. If you edit source data, you re-run the fan-out, or CI's drift check fails. Never hand-edit a bundled copy.
- **Crypto × 5:** the envelope spec ([wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md)) is frozen at v1 — PBKDF2-SHA256 @ 310,000 iterations (read from the envelope), 16-byte salt, 12-byte IV, AES-256-GCM, **auth tag appended to ciphertext**, base64 fields `{v, kdf, iterations, salt, iv, data}`. Five implementations must stay byte-compatible: `admin_scripts/encrypt_unlicensed.js`, `web/js/crypto.js`, the extension's crypto, `CryptoHelper.kt` (×3 modules), `ios/CryptoManager.swift`. **Touch one → touch all, in the same PR.** The CI round-trip self-test is the gate.
- **Tokens:** design tokens and the status-color mapping are a cross-surface contract (ADR-008). The mapping: clear/active → `#2dd4a7`; delinquent/probation → `#f2c14e`; expired/revoked/no_license_found → `#ff5f6d`; else → gray/muted. "Fixing" one surface's token is a defect.
- **Data honesty:** every record needs `verified_by`, `last_checked`, `data_as_of`; every watchlist record needs a `status_note` documenting the search. You may *draft* records; you may never *verify* them — verification is a human looking at the MQA portal, by definition ([prompts/verify-a-record.md](prompts/verify-a-record.md)).

## Hard prohibitions (instant PR rejection)

- Committing, pasting, attaching, or screenshotting `data/private/unlicensed.plain.json` or its contents — including in this conversation, in an issue, or in a PR description.
- Adding any dependency, on any surface, for any reason ("tiny," "standard," "everyone uses it" — all no).
- Fabricating MQA portal results, check dates, or record fields. Missing data is left missing, visibly.
- Hand-editing fan-out output instead of re-running the generator.
- Changing one crypto implementation without the other four in the same PR.
- Introducing network calls: the Android manifest has no INTERNET permission; keep it that way everywhere it's true today.

## Task protocol

1. **Read the relevant docs first.** Data work → [docs/annual_update_workflow.md](docs/annual_update_workflow.md). Crypto → the spec wiki page. Surfaces → [wiki/Platform-surface-map.md](wiki/Platform-surface-map.md). The answer to most "can I…" questions is already written down.
2. **Issue-first** for anything non-trivial; link it in the PR.
3. **Match the local idiom, don't import one.** Vanilla JS is IIFE-namespaced (`FedSpaUI`, `FedSpaSearch`, `FedSpaCrypto`); Kotlin is single-activity classic views; SwiftUI is a single scene with `ObservableObject`. No frameworks, no patterns-for-patterns.
4. **Run the local pipeline before pushing** — it's the CI pipeline, reproduced exactly:
   ```
   python3 admin_scripts/validate_schema.py
   python3 admin_scripts/generate_public_files.py && git status --short   # must be clean
   node --check web/js/app.js   # (and every JS file you touched)
   ```
5. **Docs travel with behavior.** Behavior change without a docs/wiki update is an incomplete PR.
6. **Commit style:** plain imperative subjects — `Fix county line on watch row`, `Bump envelope iterations per spec v2`. No emoji, no monolith commits.

## What agents are good for here (and not)

**Good:** drafting records from human-supplied portal evidence; writing the boring duplicated parts (a sixth surface's token block, a new strings file); doc upkeep; the fan-out and validation mechanics; review passes against the constraint checklist ([prompts/review-a-pr.md](prompts/review-a-pr.md)).

**Not acceptable:** any act of "verification" (agents don't check the portal); anything requiring a secret, server, or dependency to accomplish; softening language in data records ("unlicensed" ← never; "no license found in a search on <date>" ← always).

## If the task seems impossible under these rules

It usually isn't — the constraints have an answer for nearly everything, and the [ROADMAP.md](ROADMAP.md) shows what "inside the constraints" looks like at ambition. But if a request genuinely can't be done first-party, the correct agent behavior is to **say so and stop**, not to find the loophole. The loophole is always a dependency in a trench coat.
