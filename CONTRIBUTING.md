# Contributing to FED-SPA

The short version of the rules. The long version — with surface-specific notes, the crypto contract, and the data pipeline details — is [docs/contribution_guidelines.md](docs/contribution_guidelines.md). This file tells you how to get a PR merged; that file tells you how to be right while doing it.

## The three constraints (read twice, they are enforced)

1. **No backend.** Static files only, updated once a year. If your change needs a server, an API, a cron job, or a service — it will not merge, no matter how good it is.
2. **No third-party.** No external libraries, SDKs, fonts, CDNs, analytics, or icon packs on any surface. Allowed: Python stdlib, Node's native `crypto`, vanilla JS/CSS, androidx core-ktx + appcompat only, SwiftUI + CryptoKit + CommonCrypto with zero SPM dependencies. CI (`.github/workflows/build.yml`) uses only GitHub-owned actions — that's also the rule for anything you add there.
3. **Annual cadence.** The data refreshes once a year. No auto-refresh, no polling, no "check for updates" pings, no freshness nagware that pretends otherwise.

If you want to argue with the constraints, do it in Discussions — General, with your best case. History says the answer is in the [FAQ](wiki/FAQ.md), but the argument is welcome; the violation is not.

## What we need most (in order)

1. **Data corrections with portal evidence.** The highest-value contribution is a record fixed against a fresh MQA check. Use the Data correction issue template; include what the portal shows now and your check date.
2. **Coverage.** New records from counties we don't cover yet, each with its own portal check. One verified record beats ten proposed features.
3. **Surface polish and bug fixes.** Layout breaks, contrast issues, search edge cases — small, surgical, reproducible.
4. **Documentation and translations.** The wiki and docs are part of the product; keeping them honest is real work.
5. **New surface ports.** Ambitious but welcome — read `prompts/new-surface.md` first; it encodes the whole checklist.

## The fast path to a merged PR

1. **Issue first** for anything non-trivial, so you don't build the wrong thing. Link the issue in your PR.
2. **Branch from `main`.** Don't stack PRs.
3. **One PR, one purpose.** A data correction, a bug fix, a docs update — not a combination platter.
4. **If you touched source data** (`data/public/licensed.json` or the watchlist plaintext): re-run `python3 admin_scripts/generate_public_files.py` and commit the fan-out. CI's drift check fails the build if you don't. Never commit `data/private/unlicensed.plain.json` — it's gitignored, and that's load-bearing.
5. **If you touched crypto** (any of the five implementations: `admin_scripts/encrypt_unlicensed.js`, `web/js/crypto.js`, the extension's crypto, `CryptoHelper.kt`, `ios/CryptoManager.swift`): all five change together, per the frozen spec in [wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md). The PR template's crypto checklist is not optional.
6. **If you touched UI:** the design tokens (colors, spacing, status-color mapping) are a cross-surface contract, documented in [wiki/Platform-surface-map.md](wiki/Platform-surface-map.md) and `styles.css`. "Improved on one surface" by breaking the token = a defect.
7. **Docs travel with behavior.** If behavior changed and the wiki/docs don't mention it, the PR isn't done.

## What never merges

- A dependency of any kind (see constraint 2). "It's tiny and everywhere" is how every bundle starts.
- Plaintext watchlist content in a diff, an issue, a screenshot, or a Discussion post. Instant close, no debate — see the [PR template](.github/PULL_REQUEST_TEMPLATE.md) and [SECURITY.md](SECURITY.md).
- Scraped bulk data. Records enter one verified check at a time, or not at all.
- A "backend-lite" — remote config, a hosted JSON, a serverless function, a third-party data feed. Static files means static files.
- Silent data rewrites. History is never edited — corrections append, per [wiki/Annual-refresh-log.md](wiki/Annual-refresh-log.md).

## Setup

Nothing to install beyond platform toolchains — that's the point of the constraints. Clone the repo, run `python3 admin_scripts/validate_schema.py` to confirm your checkout is sound, and open the surface you're working on. Surface-specific setup (Android Studio, Xcode, extension unpacked-load) is in [INSTALL.md](INSTALL.md); CI's exact checks are in [BUILD.md](BUILD.md).

## Commit style

Plain, imperative, boring: `Fix county line in parlor card on watch`, `Add MM41109 re-check to licensed data`, `Correct delinquent status color token on iOS`. No emoji commits, no chore-and-rewrite histories. Small commits that each make sense alone review faster than one perfect monolith.

## Code of conduct

The [Code of Conduct](CODE_OF_CONDUCT.md) applies to every interaction here. The one project-specific addition that matters most: never target a listed establishment or its people — contributions and conversations alike. The directory exists to inform decisions, not to organize pressure campaigns.

## Where to get help while contributing

- **Discussions — Q&A** for build/setup questions
- **Issues** on the relevant record/surface for data questions
- **[SUPPORT.md](SUPPORT.md)** for the full routing table
- **[docs/contribution_guidelines.md](docs/contribution_guidelines.md)** for the deep version of everything on this page
