"""Extract Table 72 of 'GDP by Administrative District, 2015-2020' (DOSM,
published 2 Nov 2024, doc 11782): registered homestay clusters and
accommodation premises **by administrative district**, 2020-2022.

This is the only district-level tourism statistic found anywhere in DOSM's
3,065-publication catalogue (see data/GAPS.md section 2). It is tourism
*supply*, not demand -- there is still no district-level visitor count.

Layout: a state name in CAPITALS or a district name in Title Case, followed by
three yearly rows. DOSM prints '-' for nil and 'n.a' for not available; both are
preserved as distinct outcomes rather than being collapsed to zero.
"""
import csv, json, os, re

import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDF = os.path.join(ROOT, "data", "raw", "dosm-publications", "gdp_by_district_2015_2020.pdf")
CACHE = os.path.join(ROOT, "data", "_tmp", "gdp_district_pages.json")
OUT = os.path.join(ROOT, "data", "processed", "district_homestay_accommodation_2020_2022.csv")

CAPTION = "Number of registered homestay clusters and accommodation premises by administrative"
VAL = r"(?:-|n\.a\.?|\d[\d,]*)"
HEAD = re.compile(rf"^(?P<name>[A-Za-z][A-Za-z .'/()-]*?)\s+(?P<year>20(?:20|21|22))\s+"
                  rf"(?P<a>{VAL})\s+(?P<b>{VAL})\s*$")
CONT = re.compile(rf"^(?P<year>20(?:20|21|22))\s+(?P<a>{VAL})\s+(?P<b>{VAL})\s*$")


def val(t):
    t = t.strip()
    if t in ("-", "–", "—"):
        return 0, "nil"
    if t.lower().rstrip(".") == "n.a":
        return None, "not_available"
    return int(t.replace(",", "")), "reported"


def pages():
    if os.path.exists(CACHE):
        return json.load(open(CACHE, encoding="utf-8"))
    with pdfplumber.open(PDF) as pdf:
        out = [(p.extract_text() or "") for p in pdf.pages]
    json.dump(out, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    return out


def main():
    pgs = pages()
    idx = [i for i, t in enumerate(pgs) if CAPTION in t]
    # drop the contents listing: keep only pages that carry data rows
    idx = [i for i in idx
           if any(CONT.match(l.strip()) for l in pgs[i].split("\n"))]
    print(f"Table 72 spans pages {[i+1 for i in idx]}")

    rows, current, state = [], None, None
    for i in idx:
        for line in pgs[i].split("\n"):
            line = line.strip()
            m = HEAD.match(line)
            if m and m.group("name").lower() not in ("table", "jadual"):
                current = m.group("name").strip()
                if current.isupper():
                    state = current
                keep = m
            else:
                keep = CONT.match(line)
                if not keep or current is None:
                    continue
            clusters, cflag = val(keep.group("a"))
            premises, pflag = val(keep.group("b"))
            is_state = current.isupper()
            rows.append({
                "state": state.title() if state else "",
                "district": "" if is_state else current,
                "level": "state" if is_state else "district",
                "year": int(keep.group("year")),
                "homestay_clusters": clusters,
                "homestay_clusters_flag": cflag,
                "accommodation_premises": premises,
                "accommodation_premises_flag": pflag,
            })

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    d = [r for r in rows if r["level"] == "district"]
    s = [r for r in rows if r["level"] == "state"]
    print(f"wrote {len(rows)} rows -> {os.path.relpath(OUT, ROOT)}")
    print(f"  {len({r['district'] for r in d})} districts, "
          f"{len({r['state'] for r in s})} state totals, years "
          f"{sorted({r['year'] for r in rows})}")

    # districts should sum to their printed state total, per state per year
    print("\ncheck: sum of districts vs printed state total (2021 premises)")
    bad = 0
    for st in sorted({r["state"] for r in s}):
        tot = next((r["accommodation_premises"] for r in s
                    if r["state"] == st and r["year"] == 2021), None)
        got = sum(r["accommodation_premises"] or 0 for r in d
                  if r["state"] == st and r["year"] == 2021)
        if tot is None:
            continue
        ndist = len({r["district"] for r in d if r["state"] == st})
        if ndist == 0:
            # DOSM reports these as a single undivided figure, so there is
            # nothing to sum -- not an extraction failure
            print(f"  {st:18s} state-only in this table (no district rows)")
            continue
        ok = got == tot
        bad += not ok
        print(f"  {st:18s} districts {got:5d}   printed {tot:5d}   {'OK' if ok else 'DIFF'}")
    print(f"{bad} states disagree")


if __name__ == "__main__":
    main()
