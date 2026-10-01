# CITATIONS — How to Cite FED-SPA

FED-SPA is a dataset plus code. If you use the dataset — in research, journalism, a product, or another open-data project — cite it. Citation is also the attribution required by the ODbL 1.0 dataset license (see [COPYING.md](COPYING.md)).

## Recommended citation formats

**BibTeX:**

{% raw %}
```bibtex
@dataset{fedspa_2026,
  author  = {FED-SPA contributors},
  title   = {{FED-SPA}: Florida Establishment Directory — Spa \& Parlor Assurance},
  year    = {2026},
  version = {2026.1},
  note    = {Data as of 2026-09-07. Licensed massage establishments in Florida, verified
             against the Florida DOH MQA portal. Dataset under ODbL 1.0; code under MIT.},
  url     = {[https://github.com/YOUR_USERNAME/FED-SPA](https://github.com/YOUR_USERNAME/FED-SPA)}
}
```
{% endraw %}

**Plain text:**

> FED-SPA contributors (2026). *FED-SPA: Florida Establishment Directory — Spa & Parlor Assurance*, release 2026.1 (data as of 2026-09-07). Dataset of licensed Florida massage establishments verified against the Florida DOH MQA portal. [https://github.com/YOUR_USERNAME/FED-SPA](https://github.com/YOUR_USERNAME/FED-SPA) — data under ODbL 1.0, code under MIT.

**A footnote for articles / reports:**

> Directory data from FED-SPA (release 2026.1, records checked as of 2026-09-07), an independent compilation of Florida DOH MQA public records.

## The three things a citation must carry

Whatever format you use, keep these three facts attached to the data:

1. **The release version and its date.** The dataset is a snapshot, not a live source. Cite the release you actually used (`2026.1`, data as of 2026-09-07), not the project generally. Every release is listed in [wiki/Annual-refresh-log.md](wiki/Annual-refresh-log.md).

2. **The upstream authority.** The Florida DOH MQA portal is the source of record. FED-SPA organizes and date-stamps observations; it does not originate license facts. A citation that implies FED-SPA is the authority misrepresents the chain of provenance.

3. **The license.** Dataset: ODbL 1.0. Code: MIT. A link is fine; silence is not, if you are redistributing.

## Using the data downstream

- **Redistribution / derivative databases:** ODbL 1.0 applies — see [COPYING.md](COPYING.md). Keep the observation dates (`last_checked` / `data_as_of`) attached or carried forward; they are part of what the database *is*.

- **Software built on the data:** cite the dataset in your About/credits. If your software's value is the verification layer, say so in your own words — don't imply partnership.

- **Academic work:** cite the dataset release, and if FED-SPA's structure informed your methodology, the [wiki/](wiki/) pages (especially [Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md) and [docs/annual_update_workflow.md](docs/annual_update_workflow.md)) are citable as project documentation.

## What not to cite FED-SPA as

- A government source. It isn't one — see [NOTICE.md](NOTICE.md).

- A live or current-status feed. It refreshes annually; any status can have changed since the check date.

- A legal determination. Watchlist records are documented zero-match searches, not findings of unlawful operation.

## Contact for citation questions

For citation, attribution, licensing, or data-provenance questions, open an issue in this repository.

Open a Discussions thread in the Q&A category — see [SUPPORT.md](SUPPORT.md) for routing. Citation corrections (wrong dates, wrong release) are treated as data corrections and go through the issue templates.
