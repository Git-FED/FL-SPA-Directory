# Changelog

All notable changes to FED-SPA. Data releases are tagged `data-<year>`; code changes ride `main` between them. The human-readable data history lives in [wiki/Annual-refresh-log.md](wiki/Annual-refresh-log.md); this file is the full engineering record. Format follows Keep-a-Changelog; the project does not bump semver for data — data releases carry year-prefixed versions (`2026.1`) that match the version shown on every surface.

## [Unreleased]

Nothing pending.

## [2026.1] — 2026-09-07

The first public release.

### Added

- **The dataset.** Public licensed list with the seed record — Halo Asian Spa, Inc (MM41109, Clear, issued 2020-12-14, expires 2027-08-31, Boynton Beach FL) — verified against the Florida DOH MQA portal on 2026-09-07. Every record carries `verified_by`, `last_checked`, and `data_as_of`.
- **The watchlist tier.** Encrypted envelope (`data/private/unlicensed.encrypted.json`), v1: PBKDF2-SHA256 @ 310,000 iterations, AES-256-GCM, appended auth tag. Ships with zero records by design — the unlock path is exercised end-to-end on every surface with an empty plaintext document.
- **Six surfaces** from one fan-out (`admin_scripts/generate_public_files.py`):
  - `web/` — installable PWA, offline-capable, no framework; search, status filters, tier unlock, detail views with portal links. Code kept in sessionStorage only.
  - `extension/` — Chrome MV3; domain badge, quick popup, options with opt-in remember-code, no network permissions.
  - `android/` — classic views, deep link `fedspa://parlor/<license>`, home-screen widget, opt-in remember-code in private prefs, no INTERNET permission.
  - `android_auto/` — licensed-only glanceable rows, voice-search entry (ADR-007).
  - `watch/` — licensed-only glanceable list, readable at arm's length (ADR-007).
  - `ios/` — SwiftUI, zero SPM dependencies, CommonCrypto + CryptoKit envelope reader.
- **The annual workflow** (`admin_scripts/`): portal fetch helper (`scrape_mqa.py`, manual-first), schema validator (`validate_schema.py`), Node-native encryptor (`encrypt_unlicensed.js`), the fan-out generator, and the one-command orchestrator (`merge_and_encrypt.sh`, `SCRAPE=0`/`SCRAPE=1`).
- **The crypto envelope spec**, frozen at v1: [wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md) — the byte-level contract shared by five implementations.
- **CI** (`.github/workflows/build.yml`): schema validation → fan-out drift check → web smoke tests (`node --check`, MV3 shape) → envelope round-trip self-test → release zip (plaintext watchlist excluded) → artifact upload. GitHub-owned actions only.
- **The community layer**: issue templates (bug / feature / data correction), PR template with the constraints + five-implementation crypto checklist, discussions welcome page, the six-page wiki, the prompts library (`prompts/`), docs/ (annual workflow, password distribution, legal, contributing).
- **The root documentation set**: README, USAGE, INSTALL, BUILD, DEPLOYMENT, ROADMAP, ADR (nine records), SUPPORT, SECURITY, CODE_OF_CONDUCT, PRICING, CITATIONS, COPYING (ODbL for data), NOTICE, FAQ, GOVERNANCE, MAINTAINERS, AUTHORS, AGENTS, CLAUDE, SUMMARY.
- **Design tokens** as a cross-surface contract (ADR-008): dark palette, single status-color mapping, mirrored on all six surfaces and documented in `styles.css`.

### Decisions

- Three constraints locked as permanent architecture: no backend, no third-party, annual cadence (ADR-001, ADR-002, ADR-006).
- Two-tier model with client-side encryption as an access tier, not a security system (ADR-003).
- Appended auth tag chosen as the cross-platform ciphertext layout because Web Crypto's native format is ciphertext-then-tag and the other four platforms can match it exactly (ADR-004).
- Auto/watch ship licensed-only: data minimization on constrained surfaces (ADR-007).
- Append-only data history: corrections add entries, never rewrite (ADR-009).

### Known limitations (honest ones)

- Coverage is one record. The directory is a working pipeline around a seed dataset, by design.
- The watchlist is empty. The unlock machinery is live and tested; entries land when the documented-search bar is met.
- The iOS `.xcodeproj` is a structural placeholder (`project.json`) — the real project file is generated on first open per `ios/README.md`; committing Xcode's generated bundle was judged worse than a two-minute documented recipe.
- CI does not compile the Android/iOS apps (no first-party actions for it yet); local builds are the compile path.
- `android_auto/` and `watch/` carry byte-compatible crypto helpers that are deliberately unused until those surfaces gain a subscriber tier.

## Earlier history

- Project structure and the three constraints established.
- Logo, emblem, and per-surface icon sets generated (`admin_scripts/generate_icons.py`, `generate_android_icons.py`).
- Schema (`data/meta/schema.json`) and the raw seed evidence (`data/meta/raw/halo_mm41109.md`) committed.
