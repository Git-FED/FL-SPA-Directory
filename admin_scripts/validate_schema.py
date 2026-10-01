#!/usr/bin/env python3
"""
FED-SPA schema validator - pure standard library.

Validates data/public/licensed.json and data/private/unlicensed.plain.json
against the rules declared in data/meta/schema.json. Deliberately hand-rolled
(no jsonschema package) so it runs anywhere Python 3 exists.

Exits non-zero on the first file that fails, printing every problem found.

Usage:
  python3 admin_scripts/validate_schema.py
  python3 admin_scripts/validate_schema.py --quiet
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUIET = "--quiet" in sys.argv

REQUIRED_LIC = [
    "license_number", "business_name", "profession", "status",
    "expiration_date", "original_issue_date", "address", "county",
    "discipline_on_file", "public_complaint", "data_as_of", "last_checked",
]
STATUS_ENUM = {"Clear", "Active", "Delinquent", "Expired", "Inactive", "Probation"}
UNLIC_STATUS_ENUM = {"no_license_found", "expired", "inactive", "revoked", "delinquent"}
ZIP_RE = re.compile(r"^[0-9]{5}(-[0-9]{4})?$")
LIC_RE = re.compile(r"^[A-Z]{2}[0-9]{4,8}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

problems: list = []


def err(msg: str) -> None:
    problems.append(msg)
    if not QUIET:
        print(f"  [x] {msg}")


def ok(msg: str) -> None:
    if not QUIET:
        print(f"  [ok] {msg}")


def is_date(value) -> bool:
    if not isinstance(value, str) or not DATE_RE.match(value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def check_address(where: str, addr) -> None:
    if not isinstance(addr, dict):
        err(f"{where}: address must be an object, got {type(addr).__name__}")
        return
    for key in ("street", "city", "state", "zip"):
        if key not in addr or not isinstance(addr[key], str) or not addr[key].strip():
            err(f"{where}: address.{key} missing or empty")
    if isinstance(addr.get("state"), str) and addr["state"] != "FL":
        err(f"{where}: address.state must be 'FL' (FL-only dataset)")
    if isinstance(addr.get("zip"), str) and not ZIP_RE.match(addr["zip"]):
        err(f"{where}: address.zip '{addr['zip']}' is not a FL zip format")


def validate_licensed(path: Path) -> bool:
    print(f"Validating {path.relative_to(ROOT)}")
    if not path.exists():
        err("file does not exist")
        return False
    doc = json.loads(path.read_text())
    for field in ("version", "as_of", "source", "source_url", "parlors"):
        if field not in doc:
            err(f"top-level field '{field}' missing")
    if not is_date(doc.get("as_of")):
        err("top-level 'as_of' must be an ISO date (YYYY-MM-DD)")
    parlors = doc.get("parlors", [])
    if not isinstance(parlors, list):
        err("'parlors' must be an array")
        return False
    seen = set()
    for i, p in enumerate(parlors):
        where = f"parlors[{i}] ({p.get('business_name', '?')})"
        for field in REQUIRED_LIC:
            if field not in p:
                err(f"{where}: required field '{field}' missing")
        if not LIC_RE.match(p.get("license_number", "")):
            err(f"{where}: license_number '{p.get('license_number')}' doesn't match FL format (e.g. MA123456)")
        if p.get("license_number") in seen:
            err(f"{where}: duplicate license_number")
        seen.add(p.get("license_number"))
        if p.get("profession") != "Massage Establishment":
            err(f"{where}: profession must be 'Massage Establishment'")
        if p.get("status") not in STATUS_ENUM:
            err(f"{where}: status '{p.get('status')}' not in {sorted(STATUS_ENUM)}")
        for dfield in ("expiration_date", "original_issue_date", "data_as_of", "last_checked"):
            if not is_date(p.get(dfield)):
                err(f"{where}: {dfield} must be an ISO date, got '{p.get(dfield)}'")
        for bfield in ("discipline_on_file", "public_complaint"):
            if not isinstance(p.get(bfield), bool):
                err(f"{where}: {bfield} must be true/false")
        check_address(where, p.get("address"))
    if not problems:
        ok(f"{len(parlors)} licensed establishment(s) pass")
    return not problems


def validate_unlicensed(path: Path) -> bool:
    print(f"Validating {path.relative_to(ROOT)}")
    if not path.exists():
        err("file does not exist")
        return False
    doc = json.loads(path.read_text())
    parlors = doc.get("parlors", [])
    if not isinstance(parlors, list):
        err("'parlors' must be an array")
        return False
    seen = set()
    for i, p in enumerate(parlors):
        where = f"parlors[{i}] ({p.get('business_name', '?')})"
        for field in ("business_name", "address", "status", "last_checked", "reason"):
            if field not in p:
                err(f"{where}: required field '{field}' missing")
        if p.get("business_name") in seen:
            err(f"{where}: duplicate business_name")
        seen.add(p.get("business_name"))
        if p.get("status") not in UNLIC_STATUS_ENUM:
            err(f"{where}: status '{p.get('status')}' not in {sorted(UNLIC_STATUS_ENUM)}")
        if not is_date(p.get("last_checked")):
            err(f"{where}: last_checked must be an ISO date")
        if not isinstance(p.get("reason"), str) or not p["reason"].strip():
            err(f"{where}: reason must be a non-empty string")
        check_address(where, p.get("address"))
    if not problems:
        ok(f"{len(parlors)} unlicensed entr(ies) pass")
    return not problems


def main() -> int:
    global problems
    base = len(problems)
    a = validate_licensed(ROOT / "data" / "public" / "licensed.json")
    b = validate_unlicensed(ROOT / "data" / "private" / "unlicensed.plain.json")
    if problems:
        print(f"\nFAILED with {len(problems)} problem(s). Fix the data and re-run.")
        return 1
    print("\nAll data files conform to data/meta/schema.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
