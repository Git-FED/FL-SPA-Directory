# Welcome to FED-SPA Discussions

This is the community space for **FED-SPA — Florida Establishment Directory, Spa & Parlor Assurance**: the no-backend, once-a-year, no-third-party directory of licensed Florida massage establishments, with a subscriber-only encrypted watchlist of businesses we couldn't find a license for.

Before posting, skim the basics:

- **What FED-SPA is / isn't:** [wiki/FAQ.md](../wiki/FAQ.md)
- **How the data gets here (once a year, by hand):** [docs/annual_update_workflow.md](../docs/annual_update_workflow.md)
- **The three constraints that govern every decision:** [wiki/Home.md](../wiki/Home.md)
- **Data currency:** every record shows its own `as_of` date. The list is a snapshot, not a live feed. **Always re-verify on the [MQA portal](https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders) before acting on anything.**

## Categories and what belongs where

**📣 Announcements** — release notes and data refreshes. Maintainers only. The machine-readable history is `data/meta/changelog.md`; the human history is the [Annual refresh log](../wiki/Annual-refresh-log.md).

**💡 Ideas** — feature requests before they become formal issues. Rough thoughts welcome. Two rules: it must survive the three constraints (no backend, no third-party, annual cadence) and it must not be a scraping demand. "Can you add a reviews section with photos" does not survive; "can you add a county filter" does.

**💬 General** — questions, usage stories, porting questions, and anything that doesn't fit the other buckets. If you're about to ask "why not just use a real backend?" the answer is already in the FAQ — read it first, then come argue with it, which is what this category is for.

**🙋 Q&A** — marked-as-answer questions. Build problems, data oddities, "why is this record yellow." Include your surface (web / extension / Android / Auto / watch / iOS) and the license number if it's data-related.

**🙏 Show and tell** — forks, ports to other states, screenshots, related public-records work. Link your repo freely — but read the ground rule below about pitching.

## Ground rules

1. **Never paste subscriber content into a public thread.** Not the shared code, not decrypted watchlist records, not screenshots of the unlock. The whole point of the encrypted tier is that it isn't casually rehostable. Threads that break this get deleted on sight.
2. **No license-shaming campaigns.** Naming a specific business as "unlicensed" in a public thread is exactly the harm the encryption tier exists to slow down. Watchlist entries go through the data pipeline (Data correction / feature issue with a documented portal check), not the forum.
3. **No scraping demands.** "You should scrape the whole portal" is rejected on constraints and on legal caution. We check records by hand, one at a time, once a year. That's a feature, not a limitation we're embarrassed about.
4. **No third-party pitches.** No "you should use [framework/service/host/analytics]". The no-third-party constraint is a hard project boundary, not an opening bid. If you want to build a version that uses a framework, fork and show us — Show and tell is the right category for that.
5. **Be decent.** The [Code of Conduct](../CODE_OF_CONDUCT.md) applies here the same as everywhere. Zero tolerance for harassment, doxxing, or targeting individuals at any establishment.
6. **Re-verify before you rage.** If a record looks wrong, check the portal first (the date we checked is on every record), then file a Data correction issue with what you saw. Discussions are for talking, not for the correction pipeline.

## Where things actually get done

Discussions are for conversation. The real work queues are:

- **Bugs, data corrections, feature requests** → the repository's [Issues](https://github.com/YOUR_USERNAME/FED-SPA/issues) with the templates in `.github/ISSUE_TEMPLATE/`
- **Pull requests** → the [PR template](../.github/PULL_REQUEST_TEMPLATE.md) — it enforces the three-constraints checklist and, for anything touching crypto, the five-implementation compatibility list
- **The annual refresh** → [docs/annual_update_workflow.md](../docs/annual_update_workflow.md), run once a year by a maintainer

## One more thing

The data in this directory was gathered from a public government portal, by hand, and is offered with no warranty. "No license found" is not a legal determination of anything. Read [docs/legal_disclaimer.md](../docs/legal_disclaimer.md) — it's short, and it's the reason this project can exist at all.
