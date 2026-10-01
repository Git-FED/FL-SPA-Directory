# FAQ

The questions that come up every release, answered once, here, so nobody has to ask again.

## What is FED-SPA?

FED-SPA stands for **Florida Establishment Directory — Spa & Parlor Assurance**. It is a directory of licensed massage establishments in the State of Florida, verified against the Florida Department of Health (DOH) Medical Quality Assurance (MQA) online portal. It also carries a subscriber-only watchlist of businesses we could not find a license for. The public licensed list is plaintext JSON anyone can inspect. The watchlist is encrypted at rest and decrypted only in the browser, app, or extension after the subscriber enters the shared code.

## Why "no backend"?

Because a backend would make us a data processor. We would hold subscriber codes, log requests, and become a party to what is fundamentally a public-records lookup. There is no server: the site is static files, the apps read bundled JSON assets, and the encryption happens entirely on the user's device. Once a year a maintainer regenerates the files and re-uploads them. That is the entire operational model.

## How current is the data?

Every record carries a `data_as_of` date — the day that record was last checked against the MQA portal. The directory header and every surface show the release date (`as_of`) and record count. **The data is refreshed once per year.** Between refreshes, a license can expire, be disciplined, or be revoked, and our copy will not know. Always re-verify on the portal before making any decision — every detail view links straight to the MQA search.

## Is this legal advice / a legal determination?

No. See [docs/legal_disclaimer.md](../docs/legal_disclaimer.md). "No license found in a public search" is not the same as "unlicensed." We report what we observed on a specific date against a specific source. A missing record can mean a name mismatch, a recent move, or a lapsed renewal we did not catch. That is why the watchlist exists as a *prompt to ask*, never a verdict.

## Why is the licensed list public but the watchlist encrypted?

Two different data classes. The licensed list is public record — the MQA portal publishes it for anyone. The watchlist contains entities where we found **no** license match. Publishing that as plaintext would let anyone (including the businesses themselves) scrape and rehost it without any of the context or the date-stamping we attach. The shared-code envelope keeps a deliberate speed bump in place: honest people get it for a token price, and it keeps the section from becoming a free ammunition list. It is not strong protection against a determined attacker who has the code — it was never meant to be. That trade-off is documented openly in [docs/password_distribution.md](../docs/password_distribution.md).

## What does the shared code unlock?

Only the watchlist tier. Every surface supports both tiers, except Android Auto and the smart watch, which are licensed-only by deliberate design (see [Platform-surface-map.md](Platform-surface-map.md) for the rationale).

## Can I get the data as a spreadsheet?

Not yet. The licensed list is plaintext JSON, so you can open it in any tool. A CSV export is on the [ROADMAP](../ROADMAP.md) as a maybe. We will not ship anything that requires a backend to generate.

## Where do corrections come from?

From you. If a record is wrong, file a Data correction issue — you must include the MQA re-check date and what the portal shows now. If you're asking us to add an establishment, that's the Feature request template. Both live in `.github/ISSUE_TEMPLATE/`. A correction never lands without a fresh portal check.

## Can I scrape the MQA portal myself and send you a dump?

No. Our collection policy is small, manual, and documented ([docs/annual_update_workflow.md](../docs/annual_update_workflow.md)). We are not a bulk aggregator, and unsolicited dumps carry legal risk we do not want. A single record with a portal screenshot and a date, we'll take. A database, we won't.

## What's the deal with the "no third-party" rule?

It is one of the three non-negotiable project constraints:

1. **No backend** — static files only, updated once a year.
2. **No third-party** — no external libraries, SDKs, services, analytics, or tracking. Every platform uses only its own first-party standard library: Python stdlib, Node's native `crypto`, vanilla JS/CSS, androidx core + appcompat only, SwiftUI + CryptoKit + CommonCrypto with zero SPM dependencies.
3. **Annual cadence** — the data refresh is a once-a-year human workflow, and everything else in the repo respects that.

This rule shapes everything: why the web app is an IIFE and not a framework, why CI uses only GitHub-owned actions, why there is no analytics anywhere, and why the crypto envelope is implemented five times instead of once behind a shared library.

## Why five separate crypto implementations?

Because there is no shared runtime across web, extension, Android, Android Auto, watch, and iOS. Web/extension use Web Crypto (PBKDF2 + AES-256-GCM), Android/auto/watch use `javax.crypto`, iOS uses CommonCrypto for key derivation and CryptoKit for the block cipher. Each is ~60 lines and they must be byte-compatible. The contract they all share is written down in [Crypto-envelope-spec.md](Crypto-envelope-spec.md) — change one, change them all, or the envelope breaks for an entire platform.

## Why is there a warning color on "Delinquent"?

Because delinquent means a renewal fee is past due — the license technically exists, but it is in a grace period that can end in expiration. Yellow = check before you go. Green = clear/active. Red = expired/revoked/no-license-found. Gray = everything else (inactive, or statuses we simply haven't seen yet). The exact mapping lives in [Platform-surface-map.md](Platform-surface-map.md) and is identical on every surface.

## How do I build/run the surfaces?

The short answer is in [BUILD.md](../BUILD.md); the long answer per surface is in [INSTALL.md](../INSTALL.md) and [DEPLOYMENT.md](../DEPLOYMENT.md). Nothing needs a dependency install: the web app runs from a static file server, the extension loads unpacked, the Android modules open in Android Studio, the iOS project opens in Xcode.

## Why is my city / county not covered?

Coverage grows one manual check at a time. The current stats live in [Data-statistics.md](Data-statistics.md). If you want a county prioritized, open a feature request and say which county — that's the actual signal we use to decide next year's checklist.

## Something looks broken. What info should I include?

Use the bug report template. It asks for surface, browser/OS, and the exact license number you were viewing. If it's a data problem, use the Data correction template instead — different pipeline, different maintainers.

## Can I fork this for another state?

Yes — that's the point of the structure. See [USAGE.md](../USAGE.md) for the porting recipe. Keep the three constraints if you want it to stay this cheap to run; they're what keeps a one-person-per-year maintenance burden honest.

## Who pays for this?

Nobody, essentially. Static hosting is free-tier. The optional Ko-fi button in the README is a tip jar, not a business model. [PRICING.md](../PRICING.md) explains what money (if any) ever changes hands: one-time codes for the watchlist tier, priced to cover nothing but the time it takes to do the annual check.
