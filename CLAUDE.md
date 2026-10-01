# CLAUDE.md

Standing instructions for Claude (and any Claude-based agent) working in this repository. The project-wide rules live in [AGENTS.md](AGENTS.md) — read it first; this file adds the Claude-specific operating notes and the project memory that saves a session from re-deriving the basics.

## What this project is (the 30-second memory)

FED-SPA — Florida Establishment Directory, Spa & Parlor Assurance. A **no-backend, no-third-party, annual-cadence** directory of licensed Florida massage establishments, verified against the Florida DOH MQA portal, shipping to six surfaces: web PWA, Chrome MV3 extension, Android, Android Auto, watch, iOS. Two tiers: a public plaintext licensed list and a client-side-encrypted subscriber watchlist. Current release: **`2026.1`, data as of 2026-09-07**, one seed record (Halo Asian Spa, MM41109, Boynton Beach).

## The rules that will bounce your PR (all enforced in CI/review)

1. **No backend.** Static files. The "backend" is `admin_scripts/` run once a year by a human.
2. **No third-party.** Python stdlib · Node native crypto · vanilla JS/CSS · androidx core-ktx + appcompat only · SwiftUI + CryptoKit + CommonCrypto only. GitHub-owned actions only in CI. **Never suggest a library, package, service, or CDN — the answer is always no.**
3. **Annual cadence.** No polling, auto-refresh, or liveness pretense anywhere.
4. **`data/private/unlicensed.plain.json` is radioactive.** Never commit, paste, print, attach, or summarize its contents — including "just to check." The envelope's *committed* form is `unlicensed.encrypted.json`; that's what you work with.
5. **Crypto is five implementations of one frozen spec** ([wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md)): PBKDF2-SHA256 @ 310k (from the envelope's own `iterations`), 16-byte salt, 12-byte IV, AES-256-GCM, **tag appended after ciphertext**, base64 `{v, kdf, iterations, salt, iv, data}`. Change one → change all five in the same PR.
6. **Bundled data is generated.** `web/data/`, `extension/data/`, the three Android `assets/data/`, `ios/Resources/Data/` all come from `admin_scripts/generate_public_files.py`. Re-run it after any data edit; CI's drift check compares.
7. **Tokens are contracts.** Status colors: clear/active `#2dd4a7` · delinquent/probation `#f2c14e` · expired/revoked/no_license_found `#ff5f6d` · else gray. Palette and tokens in `styles.css` and [ADR-008](ADR.md). Identical on all six surfaces.
8. **You draft, humans verify.** Records enter the dataset only with a human's portal check and date. Never fabricate a portal result or a date field. Missing stays missing.

## Working style expected here

- **Match the local idiom.** Vanilla JS = IIFE namespaces (`FedSpaUI` / `FedSpaSearch` / `FedSpaCrypto`), no modules, no build step. Kotlin = classic views, single activity per module. SwiftUI = one scene, `ObservableObject` state. If your instinct reaches for a framework, the instinct is wrong for this repo.
- **Small, surgical diffs.** One PR, one purpose. Plain imperative commit subjects.
- **Docs travel with code.** If behavior changes, the wiki/docs/CHANGELOG change in the same PR. History is append-only ([ADR-009](ADR.md)) — never rewrite a changelog or log entry.
- **Run the pipeline locally before claiming done:**
  ```
  python3 admin_scripts/validate_schema.py
  python3 admin_scripts/generate_public_files.py && git status --short
  node --check web/js/app.js   # plus every JS file touched
  ```
  Clean `git status` after the fan-out = the same drift-free state CI demands.

## Where the answers already are (check before asking)

| Question | Answer lives in |
|---|---|
| "Why no backend / no libraries?" | [wiki/FAQ.md](wiki/FAQ.md), [ADR.md](ADR.md) |
| "How does the annual refresh run?" | [docs/annual_update_workflow.md](docs/annual_update_workflow.md) |
| "How is the subscriber code handled?" | [docs/password_distribution.md](docs/password_distribution.md) |
| "What's the envelope spec, byte for byte?" | [wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md) |
| "Why is Auto/watch licensed-only?" | [wiki/Platform-surface-map.md](wiki/Platform-surface-map.md) |
| "What does each surface support?" | [wiki/Platform-surface-map.md](wiki/Platform-surface-map.md) |
| "How do I ship a release?" | [DEPLOYMENT.md](DEPLOYMENT.md) |
| "What's the data schema?" | `data/meta/schema.json` |
| "Ready-made prompts for agent tasks?" | [prompts/](prompts/README.md) |

## Claude-specific cautions

- **The helpfulness trap.** Your training wants to offer "a quick npm package for that." In this repo, offering a dependency is the failure mode, not the help. The first-party solution always exists here because the constraints required it to.
- **The liveness trap.** Don't add "nice" freshness features (update checks, timestamps marked "current"). Every surface shows the release's check date and stops there, by design.
- **The data-generosity trap.** Don't invent plausible record fields (phone numbers, hours, ratings). The schema is deliberately minimal; a fabricated field is worse than a missing one.
- **The summary trap.** When asked about the watchlist, describe structure and process — never reproduce contents, even of the empty placeholder, "just to show the format." Show `data/meta/schema.json` or the spec wiki page instead.
- **The refactor trap.** The five crypto implementations and six token blocks look like duplication begging for consolidation. They are deliberate ([ADR-002](ADR.md), [ADR-008](ADR.md)): consolidation would require a shared dependency, which is the one thing forbidden.

## Good first tasks (if asked "what can I do?")

Data-adjacent: draft a record from user-supplied portal evidence ([prompts/verify-a-record.md](prompts/verify-a-record.md)); doc/wiki upkeep; the post-ship checklist in [DEPLOYMENT.md](DEPLOYMENT.md). Code: a bug fix in one surface (keep tokens identical); a sixth-surface port ([prompts/new-surface.md](prompts/new-surface.md)); CI strengthening *within* the GitHub-owned action set. The current work queues are Issues and [ROADMAP.md](ROADMAP.md) — never invent work that the roadmap explicitly declines.
