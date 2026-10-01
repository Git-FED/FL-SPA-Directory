# SUMMARY — FED-SPA in One Page

**Florida Establishment Directory — Spa & Parlor Assurance.** An independent, volunteer-run directory of licensed massage establishments in Florida, verified against the state's DOH MQA portal, shipped to six platforms with no backend, no third-party code, and an annual refresh cadence.

## What it does

You're standing in front of a spa, or about to book one. You want one fact: **is it licensed, and what's the status?** FED-SPA answers that on every screen you own — web, browser extension, Android phone, Android Auto, smart watch, iOS — with the license number, status, dates, address, and the day we last checked, plus a one-tap link to the authoritative portal.

Alongside the public licensed list sits a **subscriber-only watchlist**: establishments where a documented portal search found no license match. It's encrypted at rest, decrypts on the user's device with a shared code, and every record carries its search terms and date — an observation, never a verdict.

## The three constraints (the architecture)

1. **No backend** — static files only, refreshed once a year. No server, no API, no accounts, no logs, no bill.
2. **No third-party** — first-party platform code only: Python stdlib, Node native crypto, vanilla JS/CSS, androidx core + appcompat, SwiftUI + CryptoKit + CommonCrypto. CI uses only GitHub-owned actions.
3. **Annual cadence** — one human-verified data release per year, tagged `data-<year>`, with check dates on every record and no pretense of liveness.

Everything else in the project is downstream of these. The [ADR](ADR.md) records the reasoning; the [wiki FAQ](wiki/FAQ.md) hosts the arguments.

## The shape of the repo

- **`data/`** — the single source of truth: public licensed list (plaintext, auditable) + encrypted watchlist envelope + schema + raw evidence.
- **`admin_scripts/`** — the annual workflow: portal fetch helper, schema validator, Node-native encryptor, six-way fan-out generator, one-command orchestrator.
- **`web/` · `extension/` · `android/` · `android_auto/` · `watch/` · `ios/`** — six surfaces, all fed from the one source so they can't disagree about reality.
- **`.github/` · `docs/` · `wiki/` · `discussion/` · `prompts/`** — CI (GitHub-owned actions only), the annual workflow docs, the six-page wiki, the discussions landing page, and a prompt library with the constraints baked in.
- **Root docs** — README, USAGE, INSTALL, BUILD, DEPLOYMENT, ROADMAP, ADR, SUPPORT, SECURITY, CODE_OF_CONDUCT, PRICING, CITATIONS, COPYING, NOTICE, FAQ, GOVERNANCE, MAINTAINERS, AUTHORS, AGENTS, CLAUDE, CHANGELOG, this file.

## The current release — `2026.1` (data as of 2026-09-07)

One licensed record — the seed: **Halo Asian Spa, Inc**, license MM41109, status Clear, Boynton Beach FL — and a deliberately empty watchlist envelope, so the entire subscriber machinery is live and tested without a single business exposed to a first-release bug. Coverage grows county by county from here, one documented portal check at a time ([wiki/Data-statistics.md](wiki/Data-statistics.md)).

## What's honest about it

The project's value is auditability, so its claims are built to be checked: every record carries `verified_by`, `last_checked`, and `data_as_of`; every watchlist entry documents its zero-match search; the changelog and refresh log append and never rewrite; and the security policy describes the shared-code encryption as exactly what it is — an access tier, not a vault. "No license found" is never softened into "unlicensed," and no data decision is ever sold ([PRICING.md](PRICING.md), [GOVERNANCE.md](GOVERNANCE.md)).

## Where to go next

- **Use it** → [USAGE.md](USAGE.md) · **Install it** → [INSTALL.md](INSTALL.md)
- **Understand the design** → [README.md](README.md) · [ADR.md](ADR.md) · [wiki/Home.md](wiki/Home.md)
- **Contribute a correction** → [CONTRIBUTING.md](CONTRIBUTING.md) and the issue templates
- **Run the annual refresh** → [docs/annual_update_workflow.md](docs/annual_update_workflow.md)
- **Fork it for another state** → [COPYING.md](COPYING.md) · `prompts/new-surface.md`

**Verify before you act:** https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders
