#!/usr/bin/env python3
"""Deep analysis of FED_SPA12_merged.xlsx: real row counts, status color distribution, counties, cities, and sample RED/GRAY rows."""
import openpyxl
from collections import Counter

f = "/workspace/FED_SPA12_merged.xlsx"
wb = openpyxl.load_workbook(f, read_only=True, data_only=True)

ws = wb["Spa Directory"]
rows = list(ws.iter_rows(values_only=True))
header = list(rows[0])
idx = {h: i for i, h in enumerate(header)}

real = [r for r in rows[1:] if r[idx["Business Name"]] and str(r[idx["Business Name"]]).strip()]
print(f"REAL DATA ROWS (with business name): {len(real)}")

colors = Counter(str(r[idx["Status Color"]] if r[idx["Status Color"]] is not None else "NONE").strip().upper() for r in real)
print("STATUS COLOR distribution:", dict(colors))

counties = Counter(str(r[idx["County"]]).strip() for r in real)
print("COUNTY distribution:", dict(counties))

lic_status = Counter(str(r[idx["License Status"]] if r[idx["License Status"]] else "None").strip() for r in real)
print("LICENSE STATUS distribution (top):", dict(lic_status.most_common(15)))

# checked vs not
checked = [r for r in real if str(r[idx["License Status"]] or "").strip() not in ("", "Not Checked", "None")]
print(f"CHECKED rows (License Status != Not Checked/None): {len(checked)}")

print("\n=== SAMPLE RED ROWS (first 5) ===")
reds = [r for r in real if str(r[idx["Status Color"]] or "").strip().upper() == "RED"]
print(f"RED count: {len(reds)}")
for r in reds[:5]:
    print("-"*70)
    for h in ["Status Color","County","City","Business Name","Address","Phone","License Status","License Number","Date Verified","Follow-up Notes","Status Reason","Historical/Predecessor Licenses"]:
        v = r[idx[h]]
        if v is not None and str(v).strip():
            print(f"  {h}: {str(v)[:300]}")

print("\n=== SAMPLE GRAY (not checked) count ===")
grays = [r for r in real if str(r[idx["Status Color"]] or "").strip().upper() in ("GRAY","NONE","")]
print(f"GRAY/NONE count: {len(grays)}")

print("\n=== SAMPLE YELLOW rows (2) ===")
yellows = [r for r in real if str(r[idx["Status Color"]] or "").strip().upper() == "YELLOW"]
print(f"YELLOW count: {len(yellows)}")
for r in yellows[:2]:
    print("-"*70)
    for h in ["Business Name","City","License Status","License Number","Follow-up Notes"]:
        v = r[idx[h]]
        if v is not None and str(v).strip():
            print(f"  {h}: {str(v)[:250]}")

print("\n=== GREEN+BLUE licensed count ===")
gb = [r for r in real if str(r[idx["Status Color"]] or "").strip().upper() in ("GREEN","BLUE")]
print(f"GREEN+BLUE count: {len(gb)}")
for r in gb[:3]:
    print("-"*70)
    for h in ["Status Color","Business Name","City","License Number","License Status","Expiration Date","Original Issue Date" ,"Address","Discipline on File","Public Complaint"]:
        v = r[idx[h]]
        if v is not None and str(v).strip():
            print(f"  {h}: {str(v)[:150]}")

wb.close()
