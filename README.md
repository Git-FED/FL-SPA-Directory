# FED-SPA

**Florida Establishment Directory — Spa & Parlor Assurance**

A no-backend, once-a-year directory of licensed massage establishments in the State of Florida — verified against the Florida DOH Medical Quality Assurance (MQA) portal — plus a subscriber-only, client-side-encrypted watchlist of businesses we could not find a license for.

> **Data as of 2026-09-07 · 1 licensed record · Release `2026.1`**
> The data is a snapshot, not a live feed. **Always re-verify on the [MQA portal](https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders) before making any decision.** See [docs/legal_disclaimer.md](docs/legal_disclaimer.md).

## The one-line pitch

You should never have to wonder whether the spa you're standing in front of is licensed. FED-SPA puts the verified answer on every screen you own — desktop, phone, tablet, browser, car, and wrist — with zero servers, zero trackers, and zero third-party code.

## The three constraints

Every decision in this repo traces back to three rules. They are not preferences; they are the architecture:

1. **No backend.** Static files only, updated once a year. There is no server, no API, no database, no account system. The "deployment" is copying files.
2. **No third-party.** No external libraries, SDKs, services, analytics, or tracking on any surface. Python stdlib. Node's native `crypto`. Vanilla JS and CSS. androidx core + appcompat only. SwiftUI + CryptoKit + CommonCrypto only. If it isn't first-party platform code, it isn't in the repo.
3. **Annual cadence.** The data refresh is a once-a-year human workflow. Everything downstream — UI, search, the "data as of" label, the absence of auto-refresh — respects that.

## What's in it

**Two tiers of data.** The licensed list is public record and ships as plaintext JSON — anyone can audit it, fork it, or load it into anything. The watchlist tier contains establishments where a documented search of the MQA portal found no license match; it is encrypted at rest (PBKDF2-SHA256 → AES-256-GCM) and decrypts only in the app after a subscriber enters the shared code. "No license found" is a prompt to ask questions, never a verdict — every watchlist entry carries the exact search terms and date in its `status_note`.

**Six surfaces, one dataset.** A single source (`data/public/licensed.json` + the encrypted envelope) is fanned out by `admin_scripts/generate_public_files.py` to every platform, so nothing can drift:

| Surface | Tier support | Notes |
|---|---|---|
| [web/](web/) — PWA | licensed + watchlist | installable, offline-capable, code kept in sessionStorage only |
| [extension/](extension/) — Chrome MV3 | licensed + watchlist | domain badge + quick popup, opt-in remember-code |
| [android/](android/) | licensed + watchlist | classic views, deep link `fedspa://parlor/MM41109`, home-screen widget |
| [android_auto/](android_auto/) | licensed only | glanceable rows, voice-search entry — deliberate data minimization |
| [watch/](watch/) | licensed only | glanceable list, readable at arm's length — deliberate data minimization |
| [ios/](ios/) | licensed + watchlist | SwiftUI, zero SPM dependencies |

The full capability matrix, including the reasoning behind every "licensed only" decision, is in [wiki/Platform-surface-map.md](wiki/Platform-surface-map.md).

## Repository layout

```
FED-SPA/
├── data/                    # the dataset — public licensed list + encrypted watchlist
│   ├── public/licensed.json     # single source of truth (plaintext, auditable)
│   ├── private/unlicensed.encrypted.json   # subscriber envelope (committed)
│   └── private/unlicensed.plain.json       # NEVER committed — in .gitignore
├── admin_scripts/           # annual data workflow: scrape_mqa.py, encrypt_unlicensed.js,
│                            # validate_schema.py, generate_public_files.py, merge_and_encrypt.sh
├── web/                     # installable PWA (no framework)
├── extension/               # Chrome extension, Manifest V3
├── android/  android_auto/  watch/   # three Kotlin modules (classic views only)
├── ios/                     # SwiftUI app, zero SPM dependencies
├── .github/                 # CI (GitHub-owned actions only), issue templates, PR template
├── docs/                    # annual workflow, code distribution, legal, contributing
├── wiki/                    # Home, Data-statistics, Platform-surface-map, FAQ,
│                            # Crypto-envelope-spec, Annual-refresh-log
├── discussion/              # welcome.md — the discussions landing page
├── prompts/                 # ready-to-use AI-assistant prompts (constraints baked in)
└── social-image.png         # repo social preview
```

## Getting the data on your screen

Nothing here needs an install step beyond the platform's own tooling. The web app runs from any static file server (or `python3 -m http.server` in `web/`). The extension loads unpacked from `chrome://extensions`. The Android modules open in Android Studio. The iOS project opens in Xcode. Step-by-step for every surface lives in [INSTALL.md](INSTALL.md), and the deeper operational details are in [BUILD.md](BUILD.md) and [DEPLOYMENT.md](DEPLOYMENT.md).

## The annual refresh

Once a year, a maintainer: re-checks every record against the MQA portal, edits the source JSON, validates against the schema, re-encrypts the watchlist, re-runs the fan-out script, and tags the release `data-<year>`. It is a one-command workflow (`admin_scripts/merge_and_encrypt.sh`) with human verification at every step. The full procedure — including what happens when a record's status changes — is [docs/annual_update_workflow.md](docs/annual_update_workflow.md), and every release is logged in [wiki/Annual-refresh-log.md](wiki/Annual-refresh-log.md).

## Verification policy

Every record carries three honest fields: `verified_by` (the portal URL), `last_checked` (the date we looked), and `data_as_of` (the release date). No record enters the licensed list without a maintainer's eyes on the portal that day. No record enters the watchlist without a documented zero-match search recorded in `status_note`. Corrections are welcome and expected — use the **Data correction** issue template, and include what the portal shows now and your check date.

## Security and privacy

There is nothing to breach. No server, no accounts, no analytics, no collection. The subscriber code is never transmitted anywhere — it exists only in the user's browser session, opt-in local storage, or device keychain-equivalent. The crypto envelope spec is public and frozen: [wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md). Reporting a vulnerability? [SECURITY.md](SECURITY.md).

## Contributing

Corrections, translations, new-surface ports, and documentation fixes are welcome. The three constraints are non-negotiable in PRs — the [PR template](.github/PULL_REQUEST_TEMPLATE.md) enforces the checklist, and crypto changes must update all five implementations in lockstep. Start at [CONTRIBUTING.md](CONTRIBUTING.md) (quick rules) or [docs/contribution_guidelines.md](docs/contribution_guidelines.md) (the full version).

## Support

Data problems go to Issues with the right template; questions go to Discussions; the full routing table is in [SUPPORT.md](SUPPORT.md). If you're about to ask why there's no backend — the [FAQ](wiki/FAQ.md) has your answer, and then the argument you'll want to have.

## Funding

FED-SPA is a spare-time project. Static hosting sits in a free tier, and the annual refresh costs a maintainer a weekend. If it's useful to you, the tip jar is open:

<a href='https://ko-fi.com/YOUR_USERNAME' target='_blank' rel='noopener noreferrer'>
  <img height='36' style='border:0px;height:36px;' src='https://ko-fi.com/img/githubbutton_sm.svg' border='0' alt='Buy Me a Coffee at ko-fi.com' />
</a>

*(Replace `YOUR_USERNAME` with your Ko-fi handle. The same button appears in the web app footer — keep the two in sync.)*

The subscriber tier has a one-time code rather than a subscription; what that means, and why, is laid out plainly in [PRICING.md](PRICING.md).

## License

Data and code are released under the licenses in [LICENSE](LICENSE) (code, MIT) and [COPYING.md](COPYING.md) (dataset, ODbL 1.0). Attribution norms for the dataset are in [CITATIONS.md](CITATIONS.md). The project is independent and unaffiliated with the State of Florida or any agency — see [NOTICE.md](NOTICE.md).

---

**FED-SPA is an independent public-records project.** It is not a government service, not a live feed, and not a legal determination of anything. Verify before you act: [https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders](https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders)
