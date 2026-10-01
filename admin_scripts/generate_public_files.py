#!/usr/bin/env python3
"""
FED-SPA public file generator.

Fans the single source of truth out to every platform that bundles or fetches
data. Run after editing data/public/licensed.json:

  python3 admin_scripts/generate_public_files.py

What it does:
  1. web/data/licensed.json          full list (fetched at runtime by the PWA)
  2. web/data/unlicensed.encrypted.json  subscriber blob for the PWA
  3. extension/data/*                same two files, bundled into the zip
  4. android/app/src/main/assets/data/*        full list + encrypted blob
  5. android_auto/app/src/main/assets/data/licensed.json   licensed only
  6. watch/app/src/main/assets/data/licensed.json          licensed only
  7. ios/Resources/Data/*             full list + encrypted blob

Admin-only fields (verified_by, raw source notes) are stripped from the
generated copies; the repo originals keep everything.
"""

import json
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STRIP_FIELDS = ["verified_by"]
ADMIN_ONLY_NOTE = "Do not edit generated files. Edit data/public/licensed.json and run generate_public_files.py."

SOURCE_LIC = ROOT / "data" / "public" / "licensed.json"
SOURCE_ENC = ROOT / "data" / "private" / "unlicensed.encrypted.json"

DESTS = [
    # (target dir, licensed, encrypted unlicensed)
    (ROOT / "web" / "data", True, True),
    (ROOT / "extension" / "data", True, True),
    (ROOT / "android" / "app" / "src" / "main" / "assets" / "data", True, True),
    (ROOT / "android_auto" / "app" / "src" / "main" / "assets" / "data", True, False),
    (ROOT / "watch" / "app" / "src" / "main" / "assets" / "data", True, False),
    (ROOT / "ios" / "Resources" / "Data", True, True),
]


def main() -> int:
    if not SOURCE_LIC.exists():
        print(f"[x] Missing {SOURCE_LIC}")
        return 1
    doc = json.loads(SOURCE_LIC.read_text())

    # Strip admin-only fields from the distribution copy.
    parlors = []
    for p in doc.get("parlors", []):
        q = {k: v for k, v in p.items() if k not in STRIP_FIELDS}
        parlors.append(q)
    public = {
        "version": doc.get("version", 1),
        "as_of": doc.get("as_of", date.today().isoformat()),
        "update_frequency": doc.get("update_frequency", "annual"),
        "source_url": doc.get("source_url", ""),
        "parlors": parlors,
        "generated_note": ADMIN_ONLY_NOTE,
    }

    enc_exists = SOURCE_ENC.exists()
    enc_is_placeholder = False
    envelope = None
    if enc_exists:
        envelope = json.loads(SOURCE_ENC.read_text())
        enc_is_placeholder = not envelope.get("data")

    written = 0
    for dest, want_lic, want_enc in DESTS:
        if want_lic:
            dest.mkdir(parents=True, exist_ok=True)
            (dest / "licensed.json").write_text(json.dumps(public, indent=2) + "\n")
            written += 1
        if want_enc:
            dest.mkdir(parents=True, exist_ok=True)
            if enc_exists and not enc_is_placeholder:
                shutil.copyfile(SOURCE_ENC, dest / "unlicensed.encrypted.json")
                written += 1
            else:
                # Keep a placeholder so every consumer can code against the
                # same filename before the first real blob exists.
                (dest / "unlicensed.encrypted.json").write_text(
                    json.dumps(
                        {"v": 1, "kdf": "PBKDF2-SHA256", "iterations": 310000,
                         "salt": "", "iv": "", "data": "",
                         "note": "placeholder - run admin_scripts/encrypt_unlicensed.js"},
                        indent=2,
                    )
                    + "\n"
                )
                written += 1

    print(f"[+] Generated {written} file(s) across {len(DESTS)} platform destinations.")
    print("    Admin-only fields stripped from distribution copies.")
    if enc_is_placeholder:
        print("    NOTE: unlicensed blob is still the placeholder -")
        print("    run admin_scripts/encrypt_unlicensed.js once you have entries.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
