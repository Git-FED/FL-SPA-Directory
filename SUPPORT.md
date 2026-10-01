# Support

How to get help with FED-SPA, and where each kind of request belongs. Following this routing keeps the queues useful — issues stay actionable, Discussions stay conversational, and data corrections reach the person who can actually fix the dataset.

## Routing table

| You have… | Go to… | Use… |
|---|---|---|
| A wrong record (name, address, status, expiry looks off) | **Issues** | the **Data correction** template (`.github/ISSUE_TEMPLATE/custom.md`) — requires what the MQA portal shows now and your re-check date |
| A bug on a surface (crash, broken layout, search misbehaves, unlock fails) | **Issues** | the **bug report** template — include surface, OS/browser, and the license number you were viewing |
| A feature idea | **Issues** | the **feature request** template — it asks the three-constraints question up front |
| A question about using the app | **Discussions — Q&A** | your surface (web / extension / Android / Auto / watch / iOS) and version |
| A question about the project's design ("why no backend?") | **Discussions — General** | read [wiki/FAQ.md](wiki/FAQ.md) first — the answer is there, and the argument belongs in the discussion, not a fresh re-ask |
| A security concern | **Private reporting — do NOT open an issue** | see [SECURITY.md](SECURITY.md) |
| A conduct problem | **Private contact with a maintainer** | see [CODE_OF_CONDUCT.md](#enforcement) |
| A port / fork you want to show off | **Discussions — Show and tell** | a link to your repo |
| A licensing / attribution question | **Discussions — Q&A** | [COPYING.md](COPYING.md) and [CITATIONS.md](CITATIONS.md) first |
| A business wanting its record changed | **Issues — Data correction** | the same template and the same bar: a portal check is the evidence, not a letterhead. We are not a takedown service and not a listing service; the portal is the source of record either way. |

## Before you file anything

1. **Re-check the portal.** Your single most useful debugging step is also free: open [the MQA portal](https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders), search the establishment, and compare what you see with what FED-SPA shows. Half of all "bugs" are stale data with a check date right there on the record.
2. **Check the data version.** Every surface shows `data as of` in its header. If it's older than the current release ([wiki/Annual-refresh-log.md](wiki/Annual-refresh-log.md)), you're looking at a stale copy, not a defect.
3. **Check the FAQ.** [wiki/FAQ.md](wiki/FAQ.md) covers the recurring questions — freshness, tiers, why Auto/watch are licensed-only, how corrections work.

## Response expectations

FED-SPA is maintained by volunteers on an annual-cycle project. There is no SLA. Practical expectations:

- **Data corrections** are reviewed in batches, most likely around the annual refresh window (though corrections to obviously wrong data — a bad street address, a wrong expiry date — get priority whenever a maintainer sees them).
- **Bugs** are triaged as they arrive; fixes ship when they ship, and every surface gets the fix at the next data fan-out.
- **Feature requests** live or die on the three constraints and on maintainer bandwidth. A well-argued request that respects the constraints has a much better shelf life than a popular one that doesn't.
- **Discussions** get answered by maintainers and community members as time permits — often faster than issues, because they're conversations, not work items.

## Unsupportable requests (save yourself the wait)

- "Scrape the whole portal for me" — rejected on constraints and legal caution; see the [FAQ](wiki/FAQ.md).
- "Add a backend / accounts / sync / live updates" — the three constraints are the architecture, not a to-do list.
- "Add [library/service/analytics] to do X" — no third-party, anywhere, any surface. First-party equivalents only.
- "Remove my business from the watchlist" without a portal check showing a license — the watchlist records a documented search; a new documented search that finds a license is the correction. If our search was wrong, show us and we'll fix the record; that's the process working, not failing.
- "The data is wrong because I don't like it" — data disputes run on portal evidence, on the record, with dates.

## Maintainers

See [MAINTAINERS.md](MAINTAINERS.md) for who maintains this project and what each role covers.

## Was this helpful?

If FED-SPA saved you from a bad decision today, the tip jar is in the [README](README.md#funding). If it saved you from a *good* decision, that's a data correction — file the issue.
