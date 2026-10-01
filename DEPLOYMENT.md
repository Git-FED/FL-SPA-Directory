# DEPLOYMENT — Shipping FED-SPA

There is no infrastructure. That is the deployment story, and it's worth internalizing before reading further: "deploying" FED-SPA means **regenerating static files and putting them places** — a static web host, the Chrome Web Store, an APK you sign, an Xcode archive you export. No servers to provision, no containers to build, no environment variables, no rollback plans longer than "put the previous files back."

Everything here is a maintainer action on the annual cycle. The data-side procedure is [docs/annual_update_workflow.md](docs/annual_update_workflow.md); CI's checks are [BUILD.md](BUILD.md); this page covers shipping each surface and the release ritual that ties them together.

## The release ritual (once a year)

A release is **one commit, one tag, one upload pass**, in this order:

1. **Data is regenerated and validated** — the annual workflow's fan-out step has run; the tree is drift-clean (`python3 admin_scripts/generate_public_files.py && git status --short` comes back empty).
2. **The commit lands** with everything the release contains: source data, all six surfaces' regenerated bundled copies, the changelog entry, the wiki refresh-log row.
3. **Tag `data-<year>`** (e.g. `data-2026`). Data releases are the tags that matter; code fixes ride `main` between them and get noted in [CHANGELOG.md](CHANGELOG.md).
4. **Ship every surface** (sections below) from that exact tag.
5. **Write the release notes** — the three-audience ritual documented in `prompts/release-notes.md`: GitHub release, site banner text, changelog entry.
6. **Rotate the subscriber code** with the release, per [docs/password_distribution.md](docs/password_distribution.md) — new code, re-encrypted envelope, both ship together.

**Rule: no partial releases.** If the web app ships release 2027.1, every surface ships 2027.1 from the same tag. The `as_of` date shown on every surface is the contract with the user; surfaces disagreeing about reality is the failure mode the whole fan-out exists to prevent.

## Web (PWA)

Any static host. The committed truth is the `web/` directory after the fan-out — upload it as-is.

- **GitHub Pages**: branch deploy from the repo, or the gh-pages workflow — files in, URL out. Free tier fits this project forever.
- **Object storage static hosting** (S3 + web hosting, or any equivalent): sync `web/`, serve `index.html` at the root, done.
- **Any file server**: the PWA is vanilla HTML/CSS/JS; it only needs to be served over HTTP(S) — fetches of `data/*.json` don't work over `file://` (see [INSTALL.md](INSTALL.md)).

Service worker caching: the SW precaches the shell and the release's data files, versioned by the data version — a new release means a new SW version, and returning visitors pick it up on their next load. There is no "update available" nag by design; the annual cadence is stated plainly on every surface instead.

Cache rules if your host lets you set them: the JSON under `data/` can be short-cache (they change once a year anyway), the shell files can be long-cache — but the SW controls freshness for installed users regardless, so host caching is a performance knob, not a correctness one.

## Browser extension

Chrome Web Store (and equivalents that accept MV3 unpacked-equivalent packages):

1. `cd extension && zip -r ../fedspa-extension.zip . -x ".*"` from a clean checkout of the release tag.
2. Upload to the Chrome Web Store developer dashboard; the store review is the only gate between commit and users.
3. The store version is the data release (`2026.1` style) plus a build suffix if a code-only fix needed to reship.

The manifest requests **no network permissions** and loads no remote code — review-friendly by construction. The bundled `data/` directory ships inside the package; the store update *is* the data update, which is the entire mechanism.

## Android, Android Auto, Watch

Maintainer-local builds, signed with a private keystore that never enters the repo (`.gitignore` covers `*.keystore` / `*.jks`):

```
cd android      && ./gradlew assembleRelease
cd android_auto && ./gradlew assembleRelease
cd watch        && ./gradlew assembleRelease
```

Sign, then ship the APKs the way you ship APKs: a releases page attachment, an F-Droid submission (their build-from-source pipeline fits a stdlib-only project well), or sideload distribution — the choice is a maintainer policy decision, not a technical one. All three modules are self-contained Gradle projects, so any of those paths works from the same tagged commit.

- Bundle IDs: `ai.ninjatech.fedspa`, `ai.ninjatech.fedspa.auto`, `ai.ninjatech.fedspa.watch`.
- The Android module declares **no INTERNET permission** — stores review that as a feature; keep it that way.
- Version codes bump with each data release; `versionName` carries the data release string so users can see which snapshot they hold.

## iOS

Xcode → Product → Archive → export or upload to the App Store, following the first-open recipe in `ios/README.md` once (the committed `project.json` is the placeholder; the real `.xcodeproj` is generated on first open and lives locally thereafter). Zero SPM dependencies means zero resolve steps — archive works from a clean checkout with nothing but Xcode installed.

App Store review notes worth carrying in the submission: the app makes **no network requests of its own** (the only external link is a user-tapped portal URL), stores nothing in the cloud, and its data is a dated public-records snapshot — reviewers tend to ask "is this official?" and the answer is "no, and it says so in the app, the store listing, and [NOTICE.md](NOTICE.md)."

## The release zip

CI attaches the full-tree artifact (everything except the plaintext watchlist). It is the verifiable distribution: anyone can download the exact release, run `python3 admin_scripts/validate_schema.py` on it, and confirm the tree they're being asked to trust. Post it on the GitHub release for the `data-<year>` tag.

## Rollback

The previous tag. That's the whole plan: check out `data-2025` (when it exists), re-run the fan-out, re-upload the static files, re-submit the store packages. No database to restore, no migrations to reverse — static files make rollback a file copy, which is one of the quiet reasons the no-backend constraint is load-bearing.

## Post-ship checklist

- [ ] All surfaces show the same `as_of` and record count (spot-check each: web, extension options, Android, Auto, watch, iOS)
- [ ] The GitHub release for `data-<year>` exists with notes and the zip attached
- [ ] [wiki/Annual-refresh-log.md](wiki/Annual-refresh-log.md) and `data/meta/changelog.md` both carry the release entry
- [ ] The new subscriber code has been distributed through the channels in [docs/password_distribution.md](docs/password_distribution.md)
- [ ] Store listings updated (version numbers, "data as of" dates in the descriptions)
- [ ] `git status` run with human eyes during data season — no plaintext watchlist anywhere in the tree ([SECURITY.md](SECURITY.md))
