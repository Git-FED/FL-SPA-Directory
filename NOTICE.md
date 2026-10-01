# NOTICE

FED-SPA — Florida Establishment Directory, Spa & Parlor Assurance.

## What this project is

An independent, non-commercial directory of licensed massage establishments in the State of Florida, compiled from public records and offered as static files. It is maintained by volunteers. It is **not** a government service, **not** affiliated with, endorsed by, or connected to the State of Florida, the Florida Department of Health, or the Medical Quality Assurance division, and it carries no authority of any kind.

## Data source

All license facts come from the Florida DOH Medical Quality Assurance public search portal:

https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders

The project's use of that portal is small-scale, manual, and documented in [docs/annual_update_workflow.md](docs/annual_update_workflow.md). Each record stores the URL it was verified against (`verified_by`), the date of the check (`last_checked`), and the release it shipped in (`data_as_of`). The portal is the authoritative source; this directory is a snapshot of observations made on specific dates.

## No warranty

The data is provided as-is, with no warranty of accuracy, completeness, or fitness for any purpose. License statuses change between our annual checks — a license can expire, be disciplined, or be revoked the day after we record it. **Before relying on any record, re-verify it on the portal directly.** Every surface in this project links to the portal for exactly that reason. The full disclaimer is [docs/legal_disclaimer.md](docs/legal_disclaimer.md).

## Not a legal determination

The subscriber watchlist lists establishments for which a documented search of the portal found no license match. "No license found in a search on a given date" is an observation about a search, not a legal conclusion about a business. It can reflect a name mismatch, a recent relocation, a renewal lapsed after our check, or an error in our search terms. The project does not accuse any business of operating unlawfully, and no watchlist record should be presented as if it does.

## No relationship to listed establishments

Listing in this directory — in either tier — is not an endorsement, a review, a rating, or a recommendation. Absence from the directory means nothing: coverage is partial by design and grows a few records at a time.

## Trademarks

"FED-SPA" and the project's emblem are the project's own marks. "Florida," state agency names, and any product names referenced in build files (Android, Android Auto, Chrome, Xcode, and so on) are trademarks of their respective owners; their appearance here is descriptive of build targets only and implies no affiliation.

## Licensing

Code is MIT ([LICENSE](LICENSE)). The dataset is ODbL 1.0 ([COPYING.md](COPYING.md)). Attribution norms for the dataset are described in [CITATIONS.md](CITATIONS.md). This file is part of the distribution under those terms.
