# ROADMAP

What FED-SPA intends to do, in the order it intends to do it — with the honesty the project runs on: **the roadmap is subordinate to the three constraints** (no backend, no third-party, annual cadence). Anything that can't be built inside them doesn't get built, no matter how good it looks. Every item below has already passed that filter.

## Now — the annual cycle (every year, forever)

The heart of the project is not a feature; it's a habit. Once a year:

- Re-check every record against the MQA portal; record statuses, expiries, and check dates.
- Add coverage where the checklist (and the feature-request signal in Issues) points.
- Re-encrypt the watchlist, rotate the subscriber code, re-run the fan-out, tag `data-<year>`.

Everything else on this page happens *around* that cycle, never in place of it. The refresh procedure is [docs/annual_update_workflow.md](docs/annual_update_workflow.md); the history is [wiki/Annual-refresh-log.md](wiki/Annual-refresh-log.md).

## Near term — the next release window

**Coverage growth, county by county.** Current coverage is intentionally tiny (see [wiki/Data-statistics.md](wiki/Data-statistics.md)) — the seed record plus whatever the checklist adds. The near-term goal is the high-traffic counties first, prioritized by the feature requests that name them. This is the single most valuable work in the project and it is almost entirely a data problem, not a code problem.

**First watchlist entries.** The tier is built, tested, and shipping empty on purpose (the unlock path is exercised end-to-end with a zero-record envelope). Entries land when the bar is met: a documented zero-match search, terms and date recorded in `status_note`. The bar is deliberately high — see the [FAQ](wiki/FAQ.md).

**Expiry-awareness pass.** The seed record's license expires 2027-08-31, inside the "expiring soon" window the apps already compute. The first real expiry event is a chance to prove the pipeline handles a status transition correctly (Clear → Expired, or renewed → new expiry date) and to document that story in the refresh log.

**CI strengthening, within the allowed action set.** If GitHub ships first-party mobile build actions, Android/iOS compilation joins the pipeline — the constraint is GitHub-owned tooling only, same as the four actions the workflow already uses. Tracked as a watch item, not a promise.

## Mid term — the next two to three cycles

**CSV export of the licensed list.** The most-requested "give me the data" format. Fits every constraint: it's a generated static file, produced by the fan-out script from the same single source. Not a priority until someone asks with a use case — Issues signal decides.

**Translation pass.** The surfaces' strings are centralized per-platform (strings.xml, SwiftUI text, web JS) which makes a second language tractable. Candidate languages come from user signal, not guesswork. No translation *service* — ever — that's a third-party dependency; it's human translations or nothing.

**Surface depth polish.** The web app's filters, the extension's badge rules, and the watch's glance layouts all have small known-polish items in Issues. Nothing structural; the surfaces work, they can work nicer.

**Fork kit for other states.** The structure (schema, workflow, envelope, six surfaces) is designed to be portable. A short "port this to your state" guide — essentially `prompts/new-surface.md` adapted for a full fork — would make the porting path official. The dataset license ([COPYING.md](COPYING.md)) already permits it.

## Long term — the horizon

**Watchlist tooling maturity.** As the tier grows, the annual workflow may need better-than-manual tooling for recording zero-match searches — still stdlib-only, still human-verified, never a scraper. The line stays: no bulk collection, no automation of the judgment call.

**Second data source integration.** If Florida publishes an official open-data export of licensed establishments, importing it (manually, annually, validated against the portal) could scale coverage dramatically while staying inside the constraints — a static file is a static file. Watch item, contingent entirely on the state publishing it.

**Community coverage program.** If the project grows contributors, the annual checklist could become a distributed effort — each contributor takes a county, checks it with the documented workflow, PRs the results. The workflow docs and the verify-a-record prompt (`prompts/verify-a-record.md`) are already written as if for this future.

## Explicitly not on the roadmap

Honesty section — things that get proposed and will not happen:

- **A backend / API / accounts / sync.** The constraint is the architecture. See the [FAQ](wiki/FAQ.md) for the full argument.
- **Live data / auto-refresh.** The annual cadence is the honest model; pretending to be live would misrepresent what the data is.
- **Reviews, ratings, photos, or user-generated content.** Anything that makes us a platform rather than a directory also makes us a data processor — the thing the no-backend constraint exists to avoid. Also outside the Code of Conduct's scope by design.
- **Any third-party library, on any surface, for any reason.** Not a shortcut we take once.
- **Bulk scraping of the MQA portal.** Manual, documented, per-record verification is the entire integrity of the dataset — and the legal caution is real.
- **Push notifications / "update available" nudges.** Static files don't nag; the surfaces state the data date plainly and that's the whole freshness story.

## How the roadmap changes

Items move when the annual cycle and Issues signal say so, not when a roadmap document gets rewritten. The three constraints are permanent — they are the constitution, and this roadmap is just legislation.
