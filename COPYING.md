# COPYING — Dataset License (ODbL 1.0)

The **FED-SPA dataset** — the contents of `data/public/licensed.json`, the decrypted form of the subscriber watchlist, and the derived data files fanned out to the six platform surfaces (`web/data/`, `extension/data/`, `android*/app/src/main/assets/data/`, `ios/Resources/Data/`) — is licensed under the **Open Database License 1.0** (ODbL-1.0).

The **code** in this repository is separately licensed under the MIT License — see [LICENSE](LICENSE). If you are copying code, that is the file that governs you. This file governs the *data*.

## Why ODbL for the data

The dataset is a collection of factual records assembled from a public government source through individual, dated, manual verification. ODbL is the standard share-alike license for databases of this shape: it lets anyone use, extend, and even commercialize the data, while requiring that improved versions of the *database itself* stay open under the same terms. The facts themselves are free; the compiled database carries the obligation forward.

## The short version (not a substitute for the license text)

- **You may** copy, redistribute, and build on the dataset, commercially or not.
- **You must** attribute FED-SPA as the source (see [CITATIONS.md](CITATIONS.md) for the recommended form).
- **You must** keep any *Derivative Database* you distribute under ODbL 1.0, and make it available to recipients.
- **You may** ship the data inside a larger collective work under other terms, but the dataset portion remains ODbL and its attribution and share-alike obligations travel with it.
- **You may not** represent the data as live, official, or government-issued, and you must preserve the `last_checked` / `data_as_of` fields or otherwise carry the observation dates forward — the freshness dates are part of what makes the database honest, and stripping them misrepresents it.

## Where to get the license text

The canonical ODbL 1.0 text is published by Open Data Commons:

https://opendatacommons.org/licenses/odbl/1-0/

The project does not bundle the full license text (it is long, canonical, and better served from its canonical home). The committed file that matters for day-to-day use is this one plus [LICENSE](LICENSE).

## The subscriber watchlist, specifically

The *encrypted* envelope (`data/private/unlicensed.encrypted.json`) is a machine artifact of this repository and is covered by the repository's code license (MIT) like any other build output. The *decrypted contents* — the actual watchlist records — are part of the ODbL database, like any other records. The shared-code distribution model described in [docs/password_distribution.md](docs/password_distribution.md) is an access mechanism, not a data license: once you have the data, ODbL applies to it the same as to the licensed list. Nothing in the encryption is a technical protection measure intended to override the license; it is an access-tier implementation.

## Notices you must keep

If you redistribute the dataset, carry this notice forward:

> Contains FED-SPA data (https://github.com/YOUR_USERNAME/FED-SPA), licensed under ODbL 1.0. Data compiled from the Florida DOH MQA public portal; observation dates recorded per record. Not affiliated with the State of Florida. No warranty — verify on the portal before relying on any record.
