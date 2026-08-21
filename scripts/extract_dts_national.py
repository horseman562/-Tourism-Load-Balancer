"""Extract the Malaysia-level DTS 2025 report and the quarterly DTS bulletins.

Three outputs:
  * dts_visitors_by_state_2018_2025.csv -- Table 9, the 16-state x 8-year panel
    (this is what extends our state series past 2024)
  * dts_origin_destination_2025.csv     -- Table 10, tourists by state of origin
    x state visited: the flow matrix a redistribution model actually needs
  * dts_national_quarterly.csv          -- national quarterly visitors/tourists
    from the bulletins. NOTE: DOSM publishes no state-level quarterly figures.
"""
import csv, os, re

import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "raw", "dosm-publications")
OUT = os.path.join(ROOT, "data", "processed")

# DOSM's Table 9 spelling -> geodata spelling
STATE_FIX = {"W.P. Kuala Lumpur": "W.P. Kuala Lumpur", "W.P. Labuan": "W.P. Labuan",
             "W.P. Putrajaya": "W.P. Putrajaya"}
STATES16 = ["Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang",
            "Pulau Pinang", "Perak", "Perlis", "Selangor", "Terengganu", "Sabah",
            "Sarawak", "W.P. Kuala Lumpur", "W.P. Labuan", "W.P. Putrajaya"]
YEARS = list(range(2018, 2026))
NUMTOK = re.compile(r"^-|^\d[\d,]*(?:\.\d+)?$")


def to_f(t):
    return None if t in ("-", "–", "—") else float(t.replace(",", ""))


def pages_of(name):
    with pdfplumber.open(os.path.join(SRC, name)) as pdf:
        return [(p.extract_text() or "") for p in pdf.pages]


def densest(pages, phrase):
    """The contents page names every table too; take the page that actually
    carries the numbers."""
    hits = [t for t in pages if phrase in t]
    if not hits:
        return None
    return max(hits, key=lambda t: len(re.findall(r"\d[\d,]*\.?\d*", t)))


def table9(pages):
    """16 states x 8 years of domestic visitors ('000)."""
    txt = densest(pages, "Number of Domestic Visitors by State Visited")
    if txt is None:
        raise SystemExit("Table 9 not found in DTS 2025")
    rows = []
    for line in txt.split("\n"):
        for st in STATES16:
            if not line.startswith(st):
                continue
            toks = line[len(st):].split()
            if not all(NUMTOK.match(t) for t in toks) or len(toks) != len(YEARS):
                continue
            for y, v in zip(YEARS, toks):
                rows.append({"state": STATE_FIX.get(st, st), "year": y,
                             "domestic_visitors_thousand": to_f(v)})
            break
    got = {r["state"] for r in rows}
    missing = set(STATES16) - got
    if missing:
        raise SystemExit(f"Table 9 incomplete, missing: {sorted(missing)}")
    return rows


def table10(pages):
    """Tourists ('000) by state of origin x state visited, 2025."""
    txt = densest(pages, "Number of Tourists by State Visited")
    if txt is None:
        raise SystemExit("Table 10 not found in DTS 2025")
    cols = ["Malaysia"] + STATES16
    origins = ["Malaysia"] + STATES16
    lines = txt.split("\n")
    rows = []
    for i, line in enumerate(lines):
        toks = [t for t in line.split() if NUMTOK.match(t)]
        if len(toks) != len(cols):
            continue
        # the label is the text before the numbers, or -- when DOSM wraps a long
        # name like "W.P. Kuala / Lumpur" around the row -- the lines either side
        label = re.sub(r"[\d,.\s]+$", "", line).strip()
        cur = next((o for o in sorted(origins, key=len, reverse=True)
                    if label.startswith(o)), None)
        if cur is None and not label:
            # DOSM wraps "W.P. Kuala Lumpur" as a bare label above and below the
            # numeric row; stitch the neighbouring lines back together
            around = (lines[i - 1].strip() if i else "") + " " + \
                     (lines[i + 1].strip() if i + 1 < len(lines) else "")
            flat = around.replace(" ", "")
            cur = next((o for o in sorted(origins, key=len, reverse=True)
                        if o.replace(" ", "") in flat), None)
        if cur is None:
            continue
        for c, v in zip(cols, toks):
            rows.append({"state_of_origin": cur, "state_visited": c,
                         "tourists_thousand_2025": to_f(v)})
    got = {r["state_of_origin"] for r in rows}
    if set(origins) - got:
        print(f"  WARNING Table 10 missing origin rows: {sorted(set(origins) - got)}")
    return rows


QUARTER_RE = re.compile(
    r"(First|Second|Third|Fourth) Quarter (\d{4})\s*:\s*([\d.]+)\s*million\s*(visitors|tourists)", re.I)
QMAP = {"first": "Q1", "second": "Q2", "third": "Q3", "fourth": "Q4"}


def quarterly():
    """National quarterly visitors/tourists, scraped from every bulletin we hold."""
    seen = {}
    for f in sorted(os.listdir(SRC)):
        if not f.startswith("dts_bulletin"):
            continue
        for txt in pages_of(f):
            for q, y, val, kind in QUARTER_RE.findall(txt):
                key = (int(y), QMAP[q.lower()], kind.lower())
                seen[key] = float(val)
    return [{"year": y, "quarter": q, "measure": k, "value_million": v, "geography": "Malaysia"}
            for (y, q, k), v in sorted(seen.items())]


def write(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"  {len(rows):5d} rows -> {os.path.relpath(path, ROOT)}")


def main():
    p = pages_of("dts_2025_annual.pdf")
    t9 = table9(p)
    write(os.path.join(OUT, "dts_visitors_by_state_2018_2025.csv"), t9,
          ["state", "year", "domestic_visitors_thousand"])
    t10 = table10(p)
    write(os.path.join(OUT, "dts_origin_destination_2025.csv"), t10,
          ["state_of_origin", "state_visited", "tourists_thousand_2025"])
    q = quarterly()
    write(os.path.join(OUT, "dts_national_quarterly.csv"), q,
          ["year", "quarter", "measure", "value_million", "geography"])

    # cross-check Table 9 against the national totals DOSM prints in Table 1
    t1 = densest(p, "Key Statistics of Domestic Tourism, 2018 - 2025")
    # two rows start "Pelawat Domestik"; the counts row is the one not in RM
    nat = []
    for line in t1.split("\n"):
        if line.startswith("Pelawat Domestik") and "RM" not in line:
            toks = [t for t in line.split() if re.fullmatch(r"[\d,]+", t)]
            if len(toks) == len(YEARS):
                nat = [float(t.replace(",", "")) for t in toks]
                break
    print("\ncross-check, sum of Table 9 states vs Table 1 national:")
    for i, y in enumerate(YEARS):
        s = sum(r["domestic_visitors_thousand"] for r in t9 if r["year"] == y)
        n = nat[i] if i < len(nat) else None
        if n is None:
            print(f"  {y}  states {s:>10,.0f}   national          ?   NO REFERENCE")
            continue
        flag = "OK" if abs(s - n) / n < 0.001 else "DIFF"
        print(f"  {y}  states {s:>10,.0f}   national {n:>10,.0f}   {flag}")


if __name__ == "__main__":
    main()
