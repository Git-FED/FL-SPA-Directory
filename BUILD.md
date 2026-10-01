# BUILD — CI and the Build Pipeline

FED-SPA's "build" is deliberately boring: there is nothing to compile for the web, nothing to bundle for the extension, and the three Android modules plus the iOS app use only their platform toolchains with zero added dependencies. What this project calls *building* is three things: **validating the data**, **regenerating the fan-out**, and **packaging the release**. CI automates exactly that and refuses exactly the violations that matter.

The workflow file is [.github/workflows/build.yml](.github/workflows/build.yml). It uses **only GitHub-owned actions** — `actions/checkout`, `actions/setup-python`, `actions/setup-node`, `actions/upload-artifact` — because the no-third-party constraint applies to CI like everywhere else. There is no marketplace action in this project's pipeline, and a PR that adds one will be declined on that ground alone.

## What CI does, in order

**1. Validate the dataset.** `python3 admin_scripts/validate_schema.py` runs against `data/meta/schema.json` — every licensed record must carry the required fields with valid ISO dates, a status from the taxonomy, the `verified_by` portal URL, and `last_checked`. It also checks the envelope's structural shape (`v`, `kdf`, `iterations`, `salt`, `iv`, `data` fields, base64 lengths). A failure here means the source data itself is malformed: fix the data, never the schema, unless the schema change is the point of the PR.

**2. Regenerate the fan-out and check for drift.** `python3 admin_scripts/generate_public_files.py` rewrites the bundled copies in `web/data/`, `extension/data/`, `android/app/src/main/assets/data/`, `android_auto/app/src/main/assets/data/`, `watch/app/src/main/assets/data/`, and `ios/Resources/Data/` from the single source. Then `git diff --exit-code` on those paths: if anything changed, someone edited source data (or a bundled copy) without re-running the fan-out — the build fails until the drift is committed. This is the check that keeps six surfaces from silently disagreeing about reality.

**3. Smoke-test the web app.** The JS files get `node --check` (syntax), and the extension's `manifest.json` gets its MV3 shape verified (background service worker, no remote code, no network permissions beyond the portal link). The web app itself has no framework to typecheck — `node --check` plus the schema validation is the honest level of automation for vanilla JS.

**4. Crypto envelope round-trip self-test.** This is the one test that matters most, so it runs on every push: derive a key with `crypto.pbkdf2Sync` at the envelope's own iteration count, encrypt sample plaintext with `createCipheriv('aes-256-gcm')`, append the auth tag exactly as the spec says, then decrypt by splitting `data` into ciphertext and trailing 16-byte tag, `setAuthTag`, and compare. It proves the **appended-tag layout** — the single most load-bearing byte-level decision in [wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md) — still behaves the way all five implementations assume.

**5. Package and upload.** The release zip is assembled **excluding `data/private/unlicensed.plain.json`** (belt and suspenders — it's gitignored, never in the checkout CI sees, and excluded from the zip step anyway) and uploaded as an artifact via `actions/upload-artifact`.

## Running everything locally

Every CI check is a plain script you can run yourself, in the same order:

```
python3 admin_scripts/validate_schema.py
python3 admin_scripts/generate_public_files.py && git status --short   # must be clean
node --check web/js/app.js && node --check web/js/crypto.js            # etc.
node admin_scripts/encrypt_unlicensed.js /tmp/t.json /tmp/e.json      # envelope round-trip
#   (with FEDSPA_PASSWORD set; encrypts a scratch document to scratch paths,
#    then self-checks the round-trip without touching the repo's real files)
```

If all four pass locally, CI will pass. There is no CI-only magic in this project — a design decision, so contributors can reproduce the pipeline exactly.

## The Android modules

Each module (`android/`, `android_auto/`, `watch/`) builds with the platform's own toolchain:

```
cd android && ./gradlew assembleDebug
```

- AGP 8.2.2, Kotlin 1.9.22, compileSdk 34, minSdk 26, Java 17 — pinned in each module's `build.gradle` and `gradle.properties`.
- Exactly two first-party dependencies per module: `androidx.core:core-ktx` and `androidx.appcompat:appcompat`. CI does not build the Android modules (no third-party runner actions are allowed, and GitHub's own runners can hold Android builds only via actions we won't take a chance on for this project); local builds and Play-side review are the build path for APKs.
- The manifest declares **no INTERNET permission** — if your build ever requests network, the checkout is wrong.
- Release packaging (signing) is a maintainer-local step, documented in [DEPLOYMENT.md](DEPLOYMENT.md).

## The iOS app

Xcode builds it; there is nothing else. The committed `project.json` is a structural placeholder — the first-open recipe in `ios/README.md` generates the real `.xcodeproj` and takes about two minutes. Zero SPM dependencies: CryptoKit and CommonCrypto ship with the SDK, so `xcodebuild` needs no resolve step at all.

## The web app and extension

There is no build step. What's committed is what runs. The "build" for these surfaces is the fan-out regenerating their `data/` directories, and CI's drift check is their packaging gate.

## What CI deliberately does not do

- **No deployment step.** Shipping is a maintainer action, documented in [DEPLOYMENT.md](DEPLOYMENT.md) — no CD, no auto-push, no tokens in the workflow.
- **No test matrix beyond the envelope.** The surfaces' UIs are exercised by humans on the annual cycle; automating UI testing would require third-party frameworks, which is the constraint saying no. The honest coverage is: data validated, fan-out consistent, JS syntactically sound, envelope byte-layout proven.
- **No Android/iOS compilation in CI**, for the runner-action reasons above. If GitHub ships first-party mobile build actions, the door is open — that would fit the constraint (GitHub-owned tooling, like the four actions already used).

## The release artifact

The zip CI attaches contains the full tree minus the plaintext watchlist: all six surfaces' sources, the public dataset, the encrypted envelope, docs, wiki, prompts, and admin scripts. It is the "single artifact anyone can verify" distribution — see [DEPLOYMENT.md](DEPLOYMENT.md) for where it goes and how it's tagged.

## When the build fails

| Failure | Meaning | Fix |
|---|---|---|
| Schema validation | A record is malformed or missing a required honest field (`last_checked`, `verified_by`, dates) | Fix the data in `data/public/licensed.json` (or the watchlist plaintext), not the validator |
| Drift check | Source data and bundled copies disagree | Run the fan-out script, commit the result |
| `node --check` | A JS file has a syntax error | Fix the JS — there's no transpiler to blame |
| MV3 shape check | The extension manifest lost its offline-only shape | Restore the committed shape; any network permission is a constraints violation |
| Envelope round-trip | The appended-tag layout broke | Stop. All five crypto implementations must be checked against [wiki/Crypto-envelope-spec.md](wiki/Crypto-envelope-spec.md) before anything merges |
