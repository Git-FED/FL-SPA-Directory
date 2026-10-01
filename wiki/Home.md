# FED-SPA Wiki — Home

Welcome to the wiki. It mirrors (and expands on) `docs/` in the repo, so
if you're reading this on GitHub, the same files live in the repository —
the wiki is the friendly front door.

## What is FED-SPA?

A directory of **licensed massage establishments in Florida**, verified
against the FL DOH MQA portal, available on every surface you own:
desktop and mobile web (a PWA), a browser extension, Android, Android
Auto, Wear OS, and iOS. Plus a subscriber-only **unlicensed watchlist**
that decrypts in your browser — no backend, no accounts.

One number to remember: **data refreshes once a year**. The header of
every surface shows the "Data as of" date.

## Quick links

- **Using FED-SPA** → [usage.md](https://github.com/YOUR_USERNAME/FED-SPA/blob/main/usage.md)
- **How the data is made** → [annual_update_workflow.md](https://github.com/YOUR_USERNAME/FED-SPA/blob/main/docs/annual_update_workflow.md)
- **How the subscriber code works** → [password_distribution.md](https://github.com/YOUR_USERNAME/FED-SPA/blob/main/docs/password_distribution.md)
- **The legal picture** → [legal_disclaimer.md](https://github.com/YOUR_USERNAME/FED-SPA/blob/main/docs/legal_disclaimer.md)
- **Contributing** → [contribution_guidelines.md](https://github.com/YOUR_USERNAME/FED-SPA/blob/main/docs/contribution_guidelines.md)

## Wiki pages

- **[Home](Home.md)** — this page
- **[Data statistics](Data-statistics.md)** — counts per county, per status, per refresh year
- **[FAQ](FAQ.md)** — the questions that come up every release
- **[Platform surface map](Platform-surface-map.md)** — which feature exists where (search, unlock, deep links, offline…)
- **[Crypto envelope spec](Crypto-envelope-spec.md)** — the byte-level contract all five implementations share
- **[Annual refresh log](Annual-refresh-log.md)** — history of every data release

## The three constraints

Everything in FED-SPA flows from these, repeated everywhere because
they're the identity of the project:

1. **No backend** — static files, client-side everything
2. **No third-party anything** — stdlib and platform SDKs only
3. **No tracking** — nothing leaves your device

Proposals that break these are declined, not because we're grumps, but
because the constraints ARE the product.

## Support

- Bug → issue template *Bug report*
- Wrong record → issue template *Data correction*
- Idea → Discussions → 💡 Ideas
- Money → the Ko-fi button in the README / web footer
