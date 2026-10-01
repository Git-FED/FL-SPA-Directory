# GOVERNANCE

How decisions get made in FED-SPA. The project is small and volunteer-run; the governance is correspondingly light — but written down, because "small project, unwritten rules" is how good projects die when a founder steps back.

## The constitution: three constraints

The three constraints are not policy — they're the constitution, and they bind every decision-maker including founders:

1. **No backend.** Static files only, refreshed annually.
2. **No third-party.** First-party platform code only, on every surface, including CI.
3. **Annual cadence.** One human-verified data release per year, check dates attached, no liveness pretense.

Changing a constraint requires... not happening, functionally: it would be a different project. Everything else — features, surface designs, tooling, docs — is ordinary policy beneath them.

## Who decides what

| Decision | Made by | Process |
|---|---|---|
| Data records (add / correct / status change) | any maintainer | portal evidence required; the Data correction pipeline ([CONTRIBUTING.md](CONTRIBUTING.md)) is the only path in |
| Annual release (what ships, when) | the maintainer running the refresh | the workflow in [docs/annual_update_workflow.md](docs/annual_update_workflow.md) |
| Bug fixes, docs, translations | any maintainer or contributor | PR + review per [CONTRIBUTING.md](CONTRIBUTING.md) |
| New surface / major feature | consensus of maintainers | issue-first, ADR appended ([ADR.md](ADR.md)) if architectural |
| Crypto envelope changes | **all five implementations' owners** — functionally, the maintainer set | spec bump in [wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md), envelope `v` bumped, CI round-trip green, all surfaces updated in one PR |
| Subscriber code rotation / pricing | the maintainer running the release | per [docs/password_distribution.md](docs/password_distribution.md) and [PRICING.md](PRICING.md) |
| Conduct enforcement | any maintainer, escalating for conflicts | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |

**The one money rule:** no payment, tip, sponsorship, or relationship ever buys a data decision — a record changes on portal evidence or not at all. This is stated in [PRICING.md](PRICING.md) and enforced here as governance, not preference.

## Roles

**Maintainer.** Runs the annual cycle (or shares it), merges PRs, owns the constraint checks in review, holds the signing keys for app store surfaces, and rotates the subscriber code. Maintainers are named in [MAINTAINERS.md](MAINTAINERS.md). A maintainer who stops participating for two full annual cycles is moved to emeritus by consensus of the rest (no shame — the cadence is deliberately survivable).

**Contributor.** Anyone whose PR merges. Corrections-with-evidence are the highest-value contribution class; the pipeline treats them with priority (see [CONTRIBUTING.md](CONTRIBUTING.md)).

**Reporter.** Anyone who files an issue or Discussion thread. No code commitment required; good reports (surface, version, license number, portal re-check) are first-class contributions.

**Emeritus.** Former maintainers, credited in [AUTHORS.md](AUTHORS.md), consulted at their pleasure, holding no obligations.

## How a decision actually flows

1. **Issue or Discussion first** for anything non-trivial — the project's habit of "argue the design, then build" is governance, not etiquette.
2. **Constraints check** happens before any technical debate: a proposal that violates the constitution ends at this step, politely, with a pointer to the [FAQ](FAQ.md) argument.
3. **PRs get review** from at least one maintainer who did not write them. Data PRs get *evidence* review (the portal check) in addition to code review.
4. **Architectural decisions append an ADR** ([ADR.md](ADR.md)) — the record exists so the decision can be *found* later, not just made now.
5. **Disagreements** between maintainers get talked out in the PR/issue thread; if a stalemate persists across an annual cycle, the tie-breaker is the maintainer who will be doing the work. Voluntary projects don't run on override power; they run on whoever's actually carrying the load.

## Succession

The bus-factor problem is solved structurally, not heroically: everything needed to run the project is in the repo — the workflow docs, the prompts, the ADRs, the annual log. A successor maintainer needs the repo, the MQA portal, a signing keystore (transferred privately), and the subscriber-code distribution channel. [MAINTAINERS.md](MAINTAINERS.md) tracks the handoff checklist. If nobody steps up in a cycle, the project rests gracefully: the static sites stay up, the data stays honest with its old dates, and "unmaintained since <year>" gets added to the README. A directory with honest dates needs no apology for being stale — that's the design.

## Changes to this page

Governance changes follow the ordinary PR process with maintainer consensus. The constitution is exempt from ordinary change: a PR that alters the three constraints will be closed with a pointer here and an invitation to fork — forks are explicitly welcome ([COPYING.md](COPYING.md)), and a fork with a backend is someone else's honest project, not this one's betrayal.
