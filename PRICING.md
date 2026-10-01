# PRICING

What money changes hands in FED-SPA, in full. It's a short document because the answer is short: **almost none, by design.**

## The free tier: everything except the watchlist

The licensed directory — every verified record, every surface, search, filters, detail views, offline support, the PWA, the extension, the apps — is **free, forever, no account, no ads, no tracking**. There is nothing to upsell because there is nothing to gate: the licensed list is public record, and the whole project exists to make it legible.

The data itself is downloadable as plaintext JSON ([COPYING.md](COPYING.md) — ODbL) — even the "product" is free to take.

## The paid tier: the watchlist code

The subscriber tier is the encrypted watchlist. Access is a **one-time code** that decrypts the current release's envelope on your device.

- **Price:** set by the maintainer at release time, targeted at "covers a coffee and some of the checking weekend." Think single-digit dollars, not subscriptions.
- **What it's for:** a deliberate access tier (ADR-003) — not a paywall around public record, but friction against the watchlist becoming a free, context-free, scrapeable list of named businesses.
- **What it is not:** a subscription, a license to redistribute (the data is ODbL once you have it — see [COPYING.md](COPYING.md)), or a security boundary ([SECURITY.md](SECURITY.md) explains honestly what the encryption is).

A code from a prior release dies with that release — the code rotates annually with the data ([docs/password_distribution.md](docs/password_distribution.md)), and the new envelope + new code ship together. Buy once per year you want the watchlist; skip years freely.

## Where the money goes

Nowhere, structurally. Static hosting lives in free tiers. No services, no dependencies, no infrastructure — the three constraints make the cost structure nearly flat. Contributions to the tip jar (Ko-fi, in the [README](README.md)) fund exactly the kind of expenses a volunteer project has: essentially none, occasionally a domain.

The watchlist code revenue is the same story: it's a priced thank-you that partially funds the annual checking weekend, not revenue that scales, and not a business model pretending to be one.

## Why not free-everything?

Because the watchlist is the one tier where free costs something. A plaintext, freely-scrapable list of "no license found" businesses — stripped of check dates and search notes by whoever rehosts it — is the harm scenario the tier's design exists to prevent. The one-time code keeps access honest (paid, deliberate, context-carried) without pretending secrecy that a shared code can't provide. That trade-off is argued in full at [docs/password_distribution.md](docs/password_distribution.md) and [SECURITY.md](SECURITY.md).

## Why not subscriptions / ads / sponsorships?

- **Subscriptions** require accounts, accounts require a backend, and a backend violates the first constraint — that's the whole syllogism.
- **Ads** mean trackers, trackers mean third-party code, third-party code violates the second constraint — and would make a *directory of trust* monetized by untrustworthy intermediaries.
- **Sponsorships** are fine in principle (a "built with the support of" credit), but nothing in the project needs sponsorship to run, and sponsor relationships create pressure the annual-cadence, no-backend design doesn't need.

If the project ever needs real money, the honest paths are grants for public-records tooling or nothing. It has never needed real money.

## The tip jar

The Ko-fi button in the README (and the web footer) is the voluntary path. It changes nothing about access, ships no perks, and creates no obligation — including no obligation for maintainers to prioritize anything. See [FUNDING expectations in GOVERNANCE.md](GOVERNANCE.md) for the one rule that matters: money never buys data decisions.

## Forks and pricing

Forks are MIT + ODbL and free to set their own pricing — including free. The only request (not requirement): keep the licensed tier free in spirit. Public record behind a paywall is the one move this project's structure argues against.
