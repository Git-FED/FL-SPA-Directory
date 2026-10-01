#!/usr/bin/env python3
"""Cross-tab Status Color x License Status; check Halo rows in detail; check ZIP parse-ability of addresses."""
import openpyxl, re
from collections import Counter

wb = openpyxl.load_workbook("/workspace/FED_SPA12_merged.xlsx", read_only=True, data_only=True)
ws = wb["Spa Directory"]
rows = list(ws.iter_rows(values_only=True))
header = list(rows[0]); idx = {h:i for i,h in enumerate(header)}
real = [r for r in rows[1:] if r[idx["Business Name"]] and str(r[idx["Business Name"]]).strip()]

cross = Counter()
for r in real:
    color = str(r[idx["Status Color"]] or "NONE").strip().upper()
    lic = str(r[idx["License Status"]] or "None").strip()
    cross[(color, lic)] += 1
print("=== COLOR x LICENSE STATUS ===")
for (c, l), n in sorted(cross.items()):
    print(f"  {c:8s} | {l:35s} | {n}")

print("\n=== HALO ROWS FULL DETAIL ===")
for r in real:
    if "halo" in str(r[idx["Business Name"]]).lower():
        print("-"*70)
        for h in header:
            v = r[idx[h]]
            if v is not None and str(v).strip():
                print(f"  {h}: {str(v)[:400]}")

print("\n=== ADDRESS ZIP CHECK (checked rows) ===")
checked = [r for r in real if str(r[idx["License Status"]] or "").strip() not in ("","Not Checked")]
zre = re.compile(r"\b(\d{5})(?:-\d{4})?\b")
nozip = 0
for r in checked:
    aor = str(r[idx["Address of Record"]] or "")
    addr = str(r[idx["Address"]] or "")
    if not (zre.search(aor) or zre.search(addr)):
        nozip += 1
        print(f"  NO ZIP: {r[idx['Business Name']]} | AOR={aor[:60]} | addr={addr[:60]}")
print(f"checked={len(checked)}, no-zip-anywhere={nozip}")

print("\n=== Cities with slashes (messy) sample ===")
cities = Counter(str(r[idx["City"]] or "").strip() for r in real)
for c, n in cities.most_common(50):
    if "/" in c or len(c) > 30:
        print(f"  {c!r}: {n}")

wb.close()
