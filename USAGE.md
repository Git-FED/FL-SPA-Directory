# USAGE — Using FED-SPA on Every Surface

FED-SPA is a lookup tool, not an app you live in. You open it when you're standing somewhere, or about to book somewhere, and you want to know one thing: **does this establishment hold a Florida massage license, and what's its status?** This page explains how to use it on each surface, what the tier split means, and how to read a record honestly.

Installation per surface is covered in [INSTALL.md](INSTALL.md). This page assumes it's already on your screen.

## The two tiers

**The licensed list (public, free, always available).** Every establishment in it was verified against the Florida DOH MQA portal. Each record shows the license number, current status, issue and expiry dates, the full address, and the date we last checked. This is the tier Auto and the watch ship.

**The watchlist (subscriber-only, encrypted).** Establishments for which a documented search of the portal found **no license match**. It decrypts on your device only, after you enter the shared code. Records here show what we searched, when, and what came back — never a verdict. "No license found in a search on 2026-09-07" is an observation about a search, not a claim about a business.

**Reading status colors** — the same on every surface:

| Color | Meaning | Statuses |
|---|---|---|
| 🟩 Green | Licensed and in good standing | Clear, Active |
| 🟨 Yellow | Exists but needs attention | Delinquent, Probation |
| 🟥 Red | Don't rely on it | Expired, Revoked, No-license-found (watchlist) |
| ⬜ Gray | Everything else | Inactive, or a status not in our taxonomy |

Yellow on "Delinquent" means a renewal is past due — the license still exists but is in a grace period that can end in expiration. Check before you go.

## Web (PWA)

Open the site. Search by name, city, ZIP, license number, or street — the search box matches all terms across all fields. The status filter chips narrow by status. Tap any card to open the detail view with the full record, including **Data as of** and a **Verify on MQA portal** link — use it; it opens the authoritative source in a new tab.

Install it as an app (browser menu → Install / Add to Home Screen) and it works offline — the current release's data is cached with the page. The unlock code, if you use the watchlist tier, lives in `sessionStorage` only: close the tab and it's gone. That's deliberate — see [docs/password_distribution.md](docs/password_distribution.md).

## Browser extension

The extension watches your browsing and shows a small badge when you land on a domain that matches a listed establishment — green for clear/active, yellow for delinquent/probation, red for expired/revoked/watchlist. Click the badge for the popup: the record's summary, the search box, and a link to the options page.

In **options**, you can save the subscriber code (opt-in, masked, one-click wipe) and see the bundled data's version and record count. The badge only ever reflects the bundled annual data — it does not fetch anything.

## Android

Open the app: the list, a search field, a status filter, and a tier switch. Tap a card for the detail dialog with the full record and the portal link. Deep links work: `fedspa://parlor/MM41109` opens the record directly from anywhere on the device.

**Settings** offers opt-in "remember code" — stored in the app's private preferences, wiped by unchecking. The **home-screen widget** shows the record count and the data-as-of date at a glance. Data is bundled in the APK; there is no network permission in the manifest at all.

## Android Auto

Licensed-only, by design — a car is not the place to decrypt a subscriber tier or read fine print. Rows are glanceable: name, city, license, status chip. Voice search is the entry point: the assistant's query lands on the list filtered to your terms. Nothing else. Eyes on the road; the directory answers the one question a driver actually has.

## Smart watch

Licensed-only, same rationale: constrained surface, data minimization. A scrollable list of big, high-contrast rows — name, city, status color — readable at arm's length. Tap a row for a compact detail. It's the "is this place licensed, yes or no" surface; anything deeper is what the phone in your pocket is for.

## iOS

Same two-tier experience as Android: list, search, status filter, tier switch, detail view, portal link. The unlock code is opt-in "remember" via the app's private defaults, same trade-off as Android. SwiftUI, zero third-party dependencies, works fully offline.

## The honest way to read any record

1. **Check `Data as of` first.** Every surface shows the release date. Our copy of reality is a year old at most, and possibly older than the license's reality by a day — statuses change without our knowledge.
2. **Trust the date fields, not the vibe.** "Clear" on a record checked 2026-09-07 means clear *on that date*. An expiry in the past means it's expired *now* regardless of what the record's status field still says — the app surfaces "expiring soon" for records within 180 days of expiry.
3. **Click through to the portal** for anything that matters. The link is on every detail view. FED-SPA organizes public records; the portal is the authority.
4. **Never treat watchlist red as a verdict.** It's a documented zero-match search. Name mismatches, relocations, and lapsed renewals we didn't catch all read the same on our end. Ask the business, check the portal yourself, or file a Data correction if you find the license we missed — that's the pipeline working.

## Refreshing your copy

There is no update button on any surface, by design. The web app picks up the new release when you next load it; installed apps and extensions get the new data when you reinstall or update them like any other static app. Annual cadence, honest about it — see [wiki/Annual-refresh-log.md](wiki/Annual-refresh-log.md) for what shipped when.

## For maintainers and forkers

Running the annual refresh is documented in [docs/annual_update_workflow.md](docs/annual_update_workflow.md). Porting FED-SPA to another state (or another platform) is covered in [docs/contribution_guidelines.md](docs/contribution_guidelines.md) and `prompts/new-surface.md`. The dataset license for downstream use is [COPYING.md](COPYING.md); citation norms are [CITATIONS.md](CITATIONS.md).
