# Prompt: Write Release Notes for a Data Refresh

> Copy everything below the line into your assistant. Fill in the bracketed parts before sending.

---

You are helping me write the release announcement for **FED-SPA**'s annual data refresh. FED-SPA is a no-backend static directory of licensed Florida massage establishments with a subscriber-only encrypted watchlist. Release notes go three places, with three different audiences, and I need all three.

**Release facts:**

- Release version: [e.g. 2027.1]
- Ship date: [YYYY-MM-DD]
- Licensed records this release: [N] (was [N] last release)
- New licensed records: [count + list of names/cities, or "none"]
- Watchlist records this release: [N] (was [N])
- Status changes: [e.g. "2 records moved Clear → Delinquent", or "none"]
- Corrections: [what was wrong and what changed, or "none"]
- Coverage added: [new counties/cities, or "none"]
- Anything notable about the workflow itself: [e.g. "first release with the drift check in CI", or "nothing special"]

**What I want from you — three documents:**

**1. The GitHub release notes** (for the tag `data-<year>`). Audience: people watching the repo. Short. Lead with what changed in the data, then the counts, then the "always re-verify on the portal" line. Use the same structure as the wiki's [Annual-refresh-log](../wiki/Annual-refresh-log.md) entries: what shipped, coverage at release, what we learned, deferred to next cycle.

**2. The in-app / site banner text** (audience: users who open the app after months away). One or two sentences, plain language, no jargon. Must include the new `as_of` date and the record count. Must NOT nag, must NOT imply live data, must NOT ask anyone to re-download anything (the surfaces are reinstalled/refreshed like any static app). If the status taxonomy changed, mention it in one clause.

**3. The changelog entries** (machine-readable counterpart, for `data/meta/changelog.md`). Follow the existing entries' format exactly: version, date, counts, and a bullet list of the substantive changes. Do not editorialize in this one.

**Rules for you:**

- Never soften a status downgrade. "Moved from Clear to Expired" is written as exactly that.
- Never imply we did more checking than we did. If coverage didn't grow, say "coverage unchanged."
- Never present a watchlist entry as a legal determination. Use "no license found in a search on [date]" phrasing, never "unlicensed business."
- Keep the three-constraint framing visible where it fits naturally: no backend means the "release" is just new files; annual means "data as of [date]" is the honest freshness claim.
- Don't invent numbers. If a bracket above is still empty or "none," write the document with the gap visible so I catch it before shipping — a release note with a placeholder count is better than one with a made-up count.

**Tone calibration:** factual, plain, quietly proud. The project's voice is "we checked, here's what we found, here's the date." Not hype, not apology. If the release is small, small notes are correct.
