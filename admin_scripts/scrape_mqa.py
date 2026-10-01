#!/usr/bin/env python3
"""
FED-SPA MQA Scraper - pure standard library, no third-party packages.

Talks directly to the Florida DOH MQA verification portal:
  https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders

Two modes:

  discover    Fetch the search page and list every <select>/<input> field name
              it exposes, so you can fill in SEARCH_FORM below (one-time setup).

  scrape      Run the configured search, walk the result rows, open each
              detail page, and extract the labeled fields with regex.
              Writes raw output to data/meta/raw/scrape_<date>.json for human
              review. Nothing is merged into licensed.json automatically.

Usage:
  python3 scrape_mqa.py discover
  python3 scrape_mqa.py scrape "Halo Asian Spa"
  python3 scrape_mqa.py scrape --file my_names.txt        # one query per line

The state portal occasionally changes its form field names. If scrape mode
returns zero results, run discover mode again and update SEARCH_FORM.
"""

import json
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PORTAL_URL = (
    "https://mqa-internet.doh.state.fl.us"
    "/MQASearchServices/HealthCareProviders"
)

# Fields the portal's search form expects. VERIFY with `discover` mode.
# These names mirror the visible form on the search page; if the portal
# renames them, `discover` will tell you the new names in seconds.
SEARCH_FORM = {
    "Profession": "Massage Establishment",   # establishment search (business)
    "LicenseType": "",                       # leave blank unless discover says otherwise
    "SearchType": "Business",                # Business search (vs. Person)
    "SearchValue": "",                       # filled in per query at runtime
    "County": "",                            # optional filter, e.g. "MIAMI-DADE"
}

# SSL context: state portals sometimes run with dated certificates.
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE  # scrape only; no secrets cross the wire

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 FED-SPA/1.0"
    ),
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": PORTAL_URL,
}

# Label -> regex used on the DETAIL page. MQA renders simple label/value
# markup, so we anchor on the label text and grab the following cell/text.
# Patterns are tolerant of extra tags and whitespace.
DETAIL_PATTERNS = {
    "profession": r"Profession(?:</[^>]+>|[^<])*>\s*([^<]+?)\s*<",
    "license_number": r"License(?:\s*Number)?(?:</[^>]+>|[^<])*>\s*([A-Z]{2}[0-9]{4,8})\s*<",
    "status": r"License\s*Status(?:</[^>]+>|[^<])*>\s*([A-Za-z/ ]+?)\s*<",
    "expiration_date": r"License\s*Expiration\s*Date(?:</[^>]+>|[^<])*>\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})\s*<",
    "original_issue_date": r"License\s*Original\s*Issue\s*Date(?:</[^>]+>|[^<])*>\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})\s*<",
    "discipline_on_file": r"Discipline\s*on\s*File(?:</[^>]+>|[^<])*>\s*(Yes|No)\s*<",
    "public_complaint": r"Public\s*Complaint(?:</[^>]+>|[^<])*>\s*(Yes|No)\s*<",
}

ADDRESS_RE = re.compile(
    r"Address\s*of\s*Record(?:</[^>]+>|[^<])*>\s*([^<]+?)\s*<",
    re.IGNORECASE,
)

# Result-row link pattern on the search results page: detail links usually
# carry a license number or provider id in the query string.
RESULT_LINK_RE = re.compile(
    r'href=["\']([^"\']*?(?:Lic|Provider|Details?)[^"\']*?)["\'][^>]*>([^<]+)<',
    re.IGNORECASE,
)

TODAY = date.today().isoformat()
ROOT = Path(__file__).resolve().parent.parent          # FED-SPA/
RAW_DIR = ROOT / "data" / "meta" / "raw"


# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only)
# ---------------------------------------------------------------------------

def http_get(url: str) -> str:
    req = urllib.request.Request(url, headers={k: v for k, v in HEADERS.items() if k != "Content-Type"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def http_post(url: str, form: dict) -> str:
    body = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=HEADERS)
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# discover mode
# ---------------------------------------------------------------------------

def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def discover() -> None:
    """Print every form control name the search page exposes."""
    html = http_get(PORTAL_URL)
    controls = re.findall(
        r'<(select|input)\b[^>]*?\bname=["\']([^"\']+)["\'][^>]*>', html, re.IGNORECASE
    )
    if not controls:
        print("No named form controls found. The page may render its form via")
        print("script. Save the page source and inspect it manually:")
        print("  view-source: " + PORTAL_URL)
        return
    print(f"Form controls discovered on {PORTAL_URL}:\n")
    for kind, name in controls:
        print(f"  [{kind:>6}]  {name}")
    print("\nCopy any changed names into SEARCH_FORM at the top of this script.")


# ---------------------------------------------------------------------------
# scrape mode
# ---------------------------------------------------------------------------

def absolute(link: str) -> str:
    if link.startswith("http"):
        return link
    if link.startswith("/"):
        return "https://mqa-internet.doh.state.fl.us" + link
    return PORTAL_URL.rsplit("/", 1)[0] + "/" + link


def parse_detail(html: str, name_hint: str) -> dict:
    """Extract labeled fields from a provider detail page."""
    record = {"query": name_hint, "captured": TODAY}
    for key, pattern in DETAIL_PATTERNS.items():
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            record[key] = m.group(1).strip()
    m = ADDRESS_RE.search(html)
    if m:
        record["address_raw"] = m.group(1).strip()
    return record


def parse_address(raw: str) -> dict:
    """Split a one-line address of record into structured parts."""
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    addr = {"street": "", "street2": "", "city": "", "state": "FL", "zip": ""}
    if not parts:
        return addr
    addr["street"] = parts[0]
    if len(parts) >= 4:
        addr["street2"] = parts[1]
        addr["city"] = parts[-2].title()
        state_zip = parts[-1]
    elif len(parts) >= 3:
        addr["city"] = parts[-2].title()
        state_zip = parts[-1]
    else:
        state_zip = parts[-1] if len(parts) == 2 else ""
    m = re.match(r"([A-Z]{2})\s+([0-9]{5}(?:-[0-9]{4})?)", state_zip)
    if m:
        addr["state"], addr["zip"] = m.group(1), m.group(2)
    return addr


def mdy_to_iso(value: str) -> str:
    m = re.match(r"([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})", value or "")
    if not m:
        return ""
    return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"


def scrape_one(name: str) -> dict:
    form = dict(SEARCH_FORM)
    form["SearchValue"] = name
    html = http_post(PORTAL_URL, form)
    links = RESULT_LINK_RE.findall(html)
    if not links:
        return {"query": name, "found": False, "captured": TODAY}
    # Take the first detail link that matches the query loosely.
    for href, label in links:
        if name.lower().split(",")[0] in label.lower():
            detail_html = http_get(absolute(href))
            rec = parse_detail(detail_html, name)
            rec["found"] = True
            rec["detail_url"] = absolute(href)
            if rec.get("address_raw"):
                rec["address"] = parse_address(rec["address_raw"])
            return rec
    # Fallback: first link on the page.
    href, label = links[0]
    detail_html = http_get(absolute(href))
    rec = parse_detail(detail_html, name)
    rec["found"] = True
    rec["detail_url"] = absolute(href)
    if rec.get("address_raw"):
        rec["address"] = parse_address(rec["address_raw"])
    return rec


def classify(rec: dict) -> str:
    """Rough triage only - human review is always the final word."""
    if not rec.get("found"):
        return "no_license_found"
    status = (rec.get("status") or "").lower()
    exp = mdy_to_iso(rec.get("expiration_date", ""))
    if "clear" in status or "active" in status:
        if exp and exp < TODAY:
            return "expired"
        return "licensed"
    if "delinquent" in status:
        return "delinquent"
    if "inactive" in status:
        return "inactive"
    if "probation" in status:
        return "probation"
    return "review_needed"


def scrape(names: list) -> None:
    results = []
    for name in names:
        name = name.strip()
        if not name:
            continue
        print(f"  -> searching: {name}")
        try:
            rec = scrape_one(name)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            rec = {"query": name, "found": False, "error": str(exc), "captured": TODAY}
        rec["triage"] = classify(rec)
        results.append(rec)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out = RAW_DIR / f"scrape_{TODAY}.json"
    out.write_text(json.dumps({"scraped_on": TODAY, "results": results}, indent=2))
    print(f"\nWrote {len(results)} record(s) to {out}")
    print("Review them, then merge into data/public/licensed.json or")
    print("data/private/unlicensed.plain.json by hand. Triage summary:")
    for rec in results:
        print(f"  {rec.get('triage'):>16}  {rec.get('query')}")


# ---------------------------------------------------------------------------
# entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] not in ("discover", "scrape"):
        print(__doc__)
        sys.exit(0)
    if args[0] == "discover":
        discover()
        return
    if len(args) < 2:
        print("scrape mode needs a name: python3 scrape_mqa.py scrape \"Halo Asian Spa\"")
        sys.exit(1)
    if args[1] == "--file":
        path = Path(args[2])
        names = path.read_text().splitlines()
        scrape(names)
    else:
        scrape([" ".join(args[1:])])


if __name__ == "__main__":
    main()
