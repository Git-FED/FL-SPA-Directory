#!/usr/bin/env python3
"""
FED-SPA xlsx_to_fedspa.py - converts the county-sweep working spreadsheet
(FED_SPA12_merged.xlsx, the master of the FED_SPA2..12 series) into the two
repo data files:

  data/public/licensed.json          public tier  (verified licensed records)
  data/private/unlicensed.plain.json subscriber tier (NEVER committed)

Tier mapping (from the sweep's Status Color + License Status columns):

  Licensed tier - a maintainer verified a CURRENT, ACTIVE license on the
  MQA portal, with license number, expiration, issue date, and address of
  record on file:
    GREEN / BLUE establishment rows  (clean / zero-issue history)
    YELLOW rows whose license status is Clear* (license is real and active;
        the yellow is about predecessor-license history, carried in notes)
    GREEN evidence rows (DOH license records surfaced during verification,
        with Address of Record, no separate directory listing)

  Watchlist tier - a documented portal search found NO ACTIVE license for
  the listed business at the listed address:
    RED rows    (license revoked / null-and-void / relinquished / pending
                 board action - documented case numbers where present)
    YELLOW 'No Match Found' rows (documented zero-match searches)
    YELLOW 'Multiple Candidates - Unconfirmed' (documented search, no
                 address-confirmed match - ambiguity recorded verbatim)
    YELLOW 'Closed' (DOH status Closed, name-matched)

  EXCLUDED from both tiers (honesty over volume):
    Not Checked / GRAY rows (~265) - nobody has looked at them yet
    Evidence rows that are predecessor-license documentation (their content
        already lives in the parent record's notes/history fields)
    YELLOW 'Not Checked' (colored but unchecked - inconsistent, excluded)

Field notes:
  - address uses the DOH Address of Record when present (authoritative),
    else the directory listing address; ZIP is carried only when the
    source shows one - never guessed (schema allows zip: null).
  - dates normalize M/D/YYYY -> YYYY-MM-DD.
  - phone is carried into notes for the licensed tier (schema has no phone
    field; losing it would be worse than a note).
  - verified_by carries the portal URL or "FL DOH MQA License Verification"
    provenance from the sweep.

Usage:
  python3 admin_scripts/xlsx_to_fedspa.py [path-to-xlsx]
    (default: /workspace/FED_SPA12_merged.xlsx)

Outputs are written to the repo root it sits in (../data/...).
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_XLSX = Path("/workspace/FED_SPA12_merged.xlsx")

RELEASE = "2026.2"
AS_OF = "2026-09-11"          # latest Date Verified in the sweep
SOURCE = "Florida Department of Health - MQA Verification Portal"
SOURCE_URL = "https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders"

# DOH license status -> repo licensed-tier status enum
LIC_STATUS_MAP = {
    "Clear": "Clear",
    "Clear/Active": "Clear",
}

# DOH license status -> repo watchlist status enum + human label
WATCH_STATUS_MAP = {
    "Revoked": ("revoked", "License REVOKED by the Florida Board of Massage Therapy"),
    "Disc Relinquish": ("revoked", "License relinquished in the face of discipline (Disc Relinquish)"),
    "Null And Void": ("expired", "License NULL AND VOID (no longer valid)"),
    "Vol Relinquish": ("inactive", "License voluntarily relinquished"),
    "VR Pend Bd Act": ("inactive", "License relinquishment pending Board action"),
    "No Match Found": ("no_license_found", "No matching license found in the DOH database"),
    "Multiple Candidates - Unconfirmed": ("no_license_found", "Same-named licenses exist but none can be address-confirmed"),
    "Closed": ("inactive", "DOH license status: Closed"),
}

ZIP_RE = re.compile(r"\b(\d{5})(?:-(\d{4}))?\b")
LICENSE_RE = re.compile(r"\b(M[A-Z]\d{4,6})\b")
AOR_TAIL_RE = re.compile(r"[,\s]+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\s*$")
AOR_STATE_ONLY_RE = re.compile(r"[,\s]+([A-Z]{2})\s*$")

# portal spellings -> official municipality name (pure spelling normalization
# of unambiguous places - NOT municipal-boundary assertions). LAKE WORTH ->
# Lake Worth Beach follows the 2019 rename documented in wiki/locations.md.
CITY_ALIASES = {
    "GREEN ACRES": "Greenacres",      # the city's official name is one word
    "PORT SAINT LUCIE": "Port St. Lucie",
    "PORT ST LUCIE": "Port St. Lucie",
    "PORT ST. LUCIE": "Port St. Lucie",
    "FT LAUDERDALE": "Fort Lauderdale",
    "LAKE WORTH": "Lake Worth Beach",  # renamed 2019; project wiki documents it
}


def norm_date(v) -> str | None:
    """M/D/YYYY or MM/DD/YYYY or YYYY-MM-DD -> YYYY-MM-DD (None if empty)."""
    s = str(v or "").strip()
    if not s:
        return None
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}-{mo:02d}-{d:02d}"
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
    if m:
        return s
    return None


def norm_zip(v) -> str | None:
    s = str(v or "").strip()
    if not s:
        return None
    m = ZIP_RE.search(s)
    return m.group(0) if m else None


def clean(v) -> str:
    return str(v or "").strip()


def split_aor(aor: str) -> tuple[str, str, str, str | None]:
    """Parse an MQA Address-of-Record from the END.

    Portal AORs come in two shapes:
      '4720 SOUTH 25TH ST, FORT PIERCE, FL 34981'                  (3 parts)
      '131 North 2nd St, Ste# 220-222, Fort Pierce, FL 34950'      (4 parts -
        the suite sits in its own comma part, which is why positional
        parsing put 'Suite 7' in the city slot for 7 records)

    Anchoring on the ', ST ZIP' tail (instead of parts[1]/parts[2]) makes
    both shapes parse identically: whatever commas remain in front of the
    tail are street (+ optional embedded suite); the comma part directly
    before the tail is the city.
    """
    aor = clean(aor)
    if not aor:
        return "", "", "", None

    zipc = norm_zip(aor)
    m = AOR_TAIL_RE.search(aor)
    if not m:
        # no 'STATE ZIP' tail - fall back to state-only tail, then positional
        m2 = AOR_STATE_ONLY_RE.search(aor)
        if m2:
            head, state = aor[: m2.start()], m2.group(1)
        else:
            head, state = aor, "FL"
        parts = [p.strip() for p in head.split(",") if p.strip()]
        if len(parts) >= 2:
            return parts[0], title_city(parts[-1]), state, zipc
        if len(parts) == 1:
            return parts[0], "", state, zipc
        return aor, "", "FL", zipc

    state, head = m.group(1), aor[: m.start()]
    parts = [p.strip() for p in head.split(",") if p.strip()]
    if len(parts) >= 2:
        street = parts[:-1]          # all but the last comma part
        city = parts[-1]             # the comma part right before the tail
    elif len(parts) == 1:
        street, city = [parts[0]], ""
    else:
        street, city = [aor], ""

    # an embedded suite comma part (starts with a suite word) folds into the
    # street so suite_from_street() can split it off cleanly below
    if len(street) > 1:
        folded = [street[0]]
        for extra in street[1:]:
            if re.match(r"^(Suite|Ste\.?|Ste#?|Unit|Apt\.?|Bldg|Rm\.?|Room|#)", extra, re.IGNORECASE):
                folded[-1] = folded[-1].rstrip(",") + ", " + extra
            else:
                folded.append(extra)
        street = folded
    if len(street) == 1 and not city and looks_like_city(street[0]):
        # 'GREENACRES, FL 33467' - the lone head part is the city, not a street
        return "", title_city(street[0]), state, zipc
    return street[0], title_city(city), state, zipc


def looks_like_city(part: str) -> bool:
    """True for head parts that are clearly a municipality, not a street.

    'GREENACRES' -> True; '4720 SOUTH 25TH ST' -> False (house number);
    'Ste# 220-222' -> False (suite). Used only for the rare city-only AOR.
    """
    p = clean(part)
    if not p:
        return False
    if re.match(r"^(Suite|Ste\.?|Ste#?|Unit|Apt\.?|Bldg|Rm\.?|Room|#)", p, re.IGNORECASE):
        return False
    if re.match(r"^\d", p):  # streets start with a house number
        return False
    return True


def title_city(city: str) -> str:
    """Normalize ALL-CAPS portal city spellings to official municipality names.

    'FORT PIERCE' -> 'Fort Pierce'; 'OPA-LOCKA' -> 'Opa-Locka' (hyphenated
    compounds keep the capital after the hyphen, matching FL convention);
    known one-off portal spellings are aliased first. Empty stays empty.
    """
    c = clean(city)
    if not c:
        return c
    if c.upper() in CITY_ALIASES:
        return CITY_ALIASES[c.upper()]
    if c.isupper():
        words = []
        for w in c.split():
            if "-" in w:
                words.append("-".join(seg.capitalize() for seg in w.split("-")))
            else:
                words.append(w.capitalize())
        return " ".join(words)
    return c


def suite_from_street(street: str) -> tuple[str, str | None]:
    """Split '975 West Gateway Blvd Suite 105' -> ('975 West Gateway Blvd', 'Suite 105').

    Also handles portal shapes like 'Rm #118', 'Ste# 220-222', and a suite
    carried in its own comma part ('131 North 2nd St, Ste# 220-222') - the
    comma was already folded into the street by split_aor(), so it is split
    back off here.
    """
    if not street:
        return street, None
    # embedded comma-part suite folded by split_aor() - split it back off.
    # 'Ste#' keeps its hash verbatim ('Ste# 220-222', not 'Ste # 220-222').
    m = re.search(r",\s*(Suite|Ste\.?|Ste#?|Unit|Apt|Bldg|Rm\.?|Room|#)\s*([^,]+)$", street)
    if m:
        suite = (m.group(1).rstrip(".") + " " + m.group(2).strip()).strip()
        if m.group(1).lower() in ("ste#", "ste") and m.group(2).strip().startswith("#"):
            suite = m.group(1).rstrip(".") + m.group(2).strip()  # 'Ste# 220-222'
        return street[: m.start()].strip(), suite
    # space-separated suffix on the street line. (?<![\w#]) anchors on word
    # or '#' boundaries so '#03A' attaches correctly after a space.
    m = re.search(r"(?<![\w#])(Suite|Ste\.?|Ste#?|Unit|Apt|Bldg|Rm\.?|Room)(?![\w#])\s*([A-Za-z0-9\-#]+)\s*$", street, re.IGNORECASE)
    if m:
        return street[: m.start()].strip().rstrip(","), street[m.start():].strip()
    m = re.search(r"\s#([A-Za-z0-9\-]+)\s*$", street)  # '5891 S Military Trail #03A'
    if m:
        return street[: m.start()].strip(), "#" + m.group(1)
    return street, None


def main() -> int:
    xlsx = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_XLSX
    print(f"[i] Reading {xlsx}")
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    ws = wb["Spa Directory"]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    header = list(rows[0])
    idx = {h: i for i, h in enumerate(header)}

    def g(r, h):
        return r[idx[h]] if h in idx else None

    real = [r for r in rows[1:] if clean(g(r, "Business Name"))]
    est = [r for r in real if clean(g(r, "Address"))]
    evidence = [r for r in real if not clean(g(r, "Address"))]

    def color(r):
        return clean(g(r, "Status Color")).upper()

    def lic_status(r):
        return clean(g(r, "License Status"))

    # ---------------- classify ----------------
    lic_rows = []       # (row, why)
    watch_rows = []     # (row, why)
    excluded = []

    for r in est:
        c, ls = color(r), lic_status(r)
        if c in ("GREEN", "BLUE") and ls in LIC_STATUS_MAP:
            lic_rows.append((r, f"{c} + {ls}"))
        elif c == "YELLOW" and ls in LIC_STATUS_MAP:
            lic_rows.append((r, f"YELLOW + {ls} (predecessor caveats in notes)"))
        elif c == "RED" and ls in WATCH_STATUS_MAP:
            watch_rows.append((r, f"RED + {ls}"))
        elif c == "YELLOW" and ls in WATCH_STATUS_MAP:
            watch_rows.append((r, f"YELLOW + {ls}"))
        else:
            excluded.append((r, f"{c or 'NONE'} + {ls or 'Not Checked'}"))

    # Evidence rows: only GREEN + Clear with an Address of Record become
    # licensed records (a verified active license with a real location).
    # All other evidence rows are predecessor/license-history documentation
    # whose content already lives inside the parent record's notes.
    evidence_included = []
    for r in evidence:
        c, ls = color(r), lic_status(r)
        if c == "GREEN" and ls in LIC_STATUS_MAP and clean(g(r, "Address of Record")):
            lic_rows.append((r, "GREEN evidence row (DOH record w/ Address of Record)"))
            evidence_included.append(clean(g(r, "Business Name")))
        else:
            excluded.append((r, f"evidence row {c or 'NONE'} + {ls} (documentation only)"))

    print(f"[i] {len(real)} real rows: {len(est)} establishment + {len(evidence)} evidence")
    print(f"[+] licensed tier : {len(lic_rows)} records")
    print(f"[+] watchlist tier: {len(watch_rows)} entries")
    print(f"[-] excluded      : {len(excluded)} rows (not checked / documentation-only)")

    # ---------------- licensed tier ----------------
    parlors = []
    for r, why in lic_rows:
        aor = clean(g(r, "Address of Record"))
        if aor:
            street, city, state, zipc = split_aor(aor)
            street, street2 = suite_from_street(street)
            # normalize the ALL-CAPS portal formatting to title-ish case is
            # skipped deliberately: portal text is carried verbatim (honesty).
        else:
            street, street2 = clean(g(r, "Address")), None
            city, state, zipc = clean(g(r, "City")), "FL", None
        county = clean(g(r, "County")).replace(" County", "").split("\u2014")[0].strip()
        if not county:
            county = "Unknown"

        exp = norm_date(g(r, "Expiration Date"))
        issued = norm_date(g(r, "License Original Issue Date"))
        checked = norm_date(g(r, "Date Verified")) or AS_OF
        data_as_of = norm_date(g(r, "Verification Data As Of")) or checked

        disc = clean(g(r, "Discipline on File")).lower().startswith("yes")
        compl = clean(g(r, "Public Complaint")).lower().startswith("yes")

        notes_bits = []
        phone = clean(g(r, "Phone"))
        if phone:
            notes_bits.append(f"Phone: {phone}")
        fu = clean(g(r, "Follow-up Notes"))
        if fu and not fu.startswith("Discipline on File"):
            notes_bits.append(fu)
        elif fu:
            notes_bits.append(fu)
        hist = clean(g(r, "Historical/Predecessor Licenses"))
        if hist and hist.lower() not in ("none found.", "none found"):
            notes_bits.append(f"License history: {hist}")
        sr = clean(g(r, "Status Reason"))
        if sr:
            notes_bits.append(f"Sweep status: {sr}")
        vurl = clean(g(r, "Verification URL"))
        if vurl:
            notes_bits.append(f"Portal record: {vurl}")
        notes = " | ".join(notes_bits)

        parlors.append({
            "license_number": clean(g(r, "License Number")),
            "business_name": clean(g(r, "Business Name")),
            "profession": "Massage Establishment",
            "status": LIC_STATUS_MAP[lic_status(r)],
            "expiration_date": exp,
            "original_issue_date": issued,
            "address": {
                "street": street,
                "street2": street2,
                "city": city,
                "state": "FL",
                "zip": zipc,
            },
            "county": county,
            "discipline_on_file": disc,
            "public_complaint": compl,
            "data_as_of": data_as_of,
            "last_checked": checked,
            "verified_by": clean(g(r, "Verification Source")) or "FL DOH License Verification (mqa-internet.doh.state.fl.us)",
            "notes": notes,
        })

    # dedupe by license number (keep first, log collisions)
    seen = {}
    deduped = []
    for p in parlors:
        key = p["license_number"]
        if key in seen:
            print(f"[!] duplicate license {key}: {p['business_name']} vs {seen[key]['business_name']} - keeping first")
            continue
        seen[key] = p
        deduped.append(p)
    parlors = deduped

    licensed_doc = {
        "version": 2,
        "as_of": AS_OF,
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "update_frequency": "annual",
        "parlors": parlors,
    }

    # ---------------- watchlist tier ----------------
    watch = []
    for r, why in watch_rows:
        street = clean(g(r, "Address"))
        city = clean(g(r, "City"))
        county = clean(g(r, "County")).replace(" County", "").split("\u2014")[0].strip() or "Unknown"

        ls = lic_status(r)
        wstatus, label = WATCH_STATUS_MAP[ls]

        # last-known license numbers (RED rows carry the dead license; the
        # Multiple-Candidates row carries its candidate numbers)
        lic_raw = clean(g(r, "License Number"))
        last_known = None
        if ls == "No Match Found":
            last_known = None
        elif lic_raw:
            nums = LICENSE_RE.findall(lic_raw)
            last_known = "; ".join(nums) if nums else lic_raw

        reason_bits = [label + "."]
        fu = clean(g(r, "Follow-up Notes"))
        if fu:
            reason_bits.append(fu)
        sr = clean(g(r, "Status Reason"))
        if sr:
            reason_bits.append(f"Sweep status: {sr}")
        hist = clean(g(r, "Historical/Predecessor Licenses"))
        if hist and hist.lower() not in ("none found.", "none found"):
            reason_bits.append(f"License history: {hist}")
        reason = " | ".join(reason_bits)

        watch.append({
            "business_name": clean(g(r, "Business Name")),
            "address": {
                "street": street,
                "street2": None,
                "city": city,
                "state": "FL",
                "zip": None,
            },
            "status": wstatus,
            "license_number_last_known": last_known,
            "reason": reason,
            "last_checked": norm_date(g(r, "Date Verified")) or AS_OF,
            "source": clean(g(r, "Verification Source")) or "FL DOH License Verification (mqa-internet.doh.state.fl.us)",
            "notes": clean(g(r, "Phone")) and f"Phone: {clean(g(r, 'Phone'))}" or "",
        })

    # dedupe by business_name (validator requires unique names).
    # Same-name entries at DIFFERENT addresses are distinct locations, not
    # duplicates - they are kept and disambiguated with their street address
    # (standard directory convention; the full address ships either way).
    seen = {}
    deduped = []
    for w in watch:
        key = w["business_name"].lower()
        if key in seen and seen[key]["address"]["street"] == w["address"]["street"]:
            print(f"[!] true duplicate (same name+street): {w['business_name']} - keeping first")
            continue
        if key in seen:
            suffix = f" ({w['address']['street']})"
            w["business_name"] = w["business_name"] + suffix
            print(f"[!] same name, different address - disambiguated to: {w['business_name']}")
        seen[w["business_name"].lower()] = w
        deduped.append(w)
    watch = deduped

    plain_doc = {
        "version": 2,
        "as_of": AS_OF,
        "parlors": watch,
    }

    # ---------------- write ----------------
    out_lic = ROOT / "data" / "public" / "licensed.json"
    out_plain = ROOT / "data" / "private" / "unlicensed.plain.json"
    out_lic.write_text(json.dumps(licensed_doc, indent=2) + "\n")
    out_plain.write_text(json.dumps(plain_doc, indent=2) + "\n")
    print(f"[+] wrote {out_lic.relative_to(ROOT)}  ({len(parlors)} records)")
    print(f"[+] wrote {out_plain.relative_to(ROOT)}  ({len(watch)} entries)  [NEVER commit this file]")
    if evidence_included:
        print(f"[i] evidence rows promoted to licensed tier: {evidence_included}")

    # summary table for docs
    from collections import Counter
    print("\n== tier summary ==")
    print("licensed by county:", dict(Counter(p["county"] for p in parlors)))
    print("watchlist by status:", dict(Counter(w["status"] for w in watch)))
    print("watchlist by county:", dict(Counter((w["address"]["city"] or "?").split("/")[0].strip() for w in watch)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
