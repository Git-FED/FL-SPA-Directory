#!/usr/bin/env python3
"""Field availability check for licensed-tier candidates (GREEN/BLUE + YELLOW-with-Clear-license, establishment rows with addresses)."""
import openpyxl, re
from collections import Counter

wb = openpyxl.load_workbook("/workspace/FED_SPA12_merged.xlsx", read_only=True, data_only=True)
ws = wb["Spa Directory"]
rows = list(ws.iter_rows(values_only=True))
header = list(rows[0]); idx = {h: i for i, h in enumerate(header)}
real = [r for r in rows[1:] if r[idx["Business Name"]] and str(r[idx["Business Name"]]).strip()]

# establishment rows = have a street address
est = [r for r in real if str(r[idx["Address"]] or "").strip()]
ev = [r for r in real if not str(r[idx["Address"]] or "").strip()]
print(f"establishment rows: {len(est)}, evidence rows (no address): {len(ev)}")
print(f"evidence row colors: {Counter(str(r[idx['Status Color']] or 'NONE').strip().upper() for r in ev)}")
print(f"evidence row license statuses: {Counter(str(r[idx['License Status']] or '') for r in ev).most_common(10)}")

lic_cand = [r for r in est if str(r[idx["Status Color"]] or "").strip().upper() in ("GREEN", "BLUE")]
yellow_clear = [r for r in est if str(r[idx["Status Color"]] or "").strip().upper() == "YELLOW"
                and str(r[idx["License Status"]] or "").strip().startswith("Clear")]
print(f"\nlicensed candidates G/B: {len(lic_cand)}, Y-Clear: {len(yellow_clear)}")

def has(r, h): return str(r[idx[h]] or "").strip()

print("\n=== field gaps among all licensed candidates (G/B + Y-Clear) ===")
cands = lic_cand + yellow_clear
gaps = Counter()
for r in cands:
    for h in ["Expiration Date", "License Original Issue Date", "Address of Record", "License Number",
              "Discipline on File", "Public Complaint", "Date Verified", "License Profession", "Phone", "City", "County"]:
        if not has(r, h):
            gaps[h] += 1
print("gaps:", dict(gaps))

print("\n=== Date formats seen ===")
print("Expiration:", Counter(has(r, "Expiration Date") for r in cands).most_common(8))
print("IssueDate:", Counter(has(r, "License Original Issue Date") for r in cands).most_common(8))
print("DateVerified:", Counter(has(r, "Date Verified") for r in cands).most_common(8))
print("DataAsOf:", Counter(has(r, "Verification Data As Of") for r in cands).most_common(8))

print("\n=== Discipline/PublicComplaint values (licensed candidates) ===")
print("disc:", Counter(has(r, "Discipline on File") for r in cands))
print("compl:", Counter(has(r, "Public Complaint") for r in cands))

print("\n=== Y-Clear rows: why yellow? (Status Reason) ===")
for r in yellow_clear:
    print(f"  - {r[idx['Business Name']]} ({r[idx['City']]}): {str(r[idx['Status Reason']] or '')[:160]}")

print("\n=== counties raw values among candidates ===")
print(Counter(str(r[idx['County']] or 'NONE') for r in cands))

print("\n=== duplicate license numbers among candidates? ===")
nums = [has(r, "License Number") for r in cands]
dup = [n for n, c in Counter(nums).items() if c > 1]
print("dups:", dup)
for r in cands:
    if has(r, "License Number") in dup:
        print(f"  {has(r,'License Number')} | {r[idx['Business Name']]} | {r[idx['City']]} | {r[idx['Address']]}")

# also check phone format and notes
print("\n=== sample full licensed candidate (BLUE) ===")
r = [r for r in lic_cand if str(r[idx['Status Color']]).upper()=='BLUE'][1]
for h in header:
    v = r[idx[h]]
    if v is not None and str(v).strip():
        print(f"  {h}: {str(v)[:200]}")

wb.close()
