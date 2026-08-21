"""Extract the SDG 14 (Life Below Water) state tables from the DOSM
Compendium of Environment Statistics, Malaysia 2025.

The compendium is used in preference to the 12 separate state Environment
Statistics reports because it covers all states in one place -- including Johor
and Sabah, which DOSM did not publish state volumes for in the 2025 round.

Tables extracted (DOSM numbering):
  1.11  Coastal length by state
  1.20  Area of mangrove forest by state, 2019-2022
  1.36  Marine water quality, COASTAL areas, by state, 2020-2024
  1.37  Marine water quality, ESTUARY areas, by state, 2020-2024
  1.38  Marine water quality, ISLAND areas, by state, 2020-2024
  2.24  Landings of marine fish by state, 2020-2024
  4.15  Distribution of coastal erosion areas, 2024

Originating agencies (cite these, not DOSM, for the underlying measurements):
Department of Environment (marine water quality), Department of Irrigation and
Drainage (coastal length and erosion), Department of Fisheries (landings).
"""
import csv, json, os, re

import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDF = os.path.join(ROOT, "data", "raw", "dosm-publications",
                   "envstats_compendium_malaysia_2025.pdf")
CACHE = os.path.join(ROOT, "data", "_tmp", "compendium_pages.json")
OUT = os.path.join(ROOT, "data", "processed")

STATES = ["Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang",
          "Perak", "Perlis", "Pulau Pinang", "Sabah", "Sarawak", "Selangor",
          "Terengganu", "W.P. Kuala Lumpur", "W.P. Labuan", "W.P. Putrajaya"]
MWQ_CATS = ["excellent", "good", "moderate", "poor"]
YEARS5 = [2020, 2021, 2022, 2023, 2024]
TOK = re.compile(r"^(?:-|–|—|\d[\d,]*(?:\.\d+)?)$")


def num(t):
    return None if t in ("-", "–", "—") else float(t.replace(",", ""))


def pages():
    if os.path.exists(CACHE):
        return json.load(open(CACHE, encoding="utf-8"))
    with pdfplumber.open(PDF) as pdf:
        out = [(p.extract_text() or "") for p in pdf.pages]
    json.dump(out, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    return out


def find(pgs, caption):
    """Page text for an English table caption.

    The 486-page compendium lists every caption in its contents as well, and
    that listing is dense with page numbers -- so rank by how many lines
    actually begin with a state name, not by digit count.
    """
    hits = [t for t in pgs if caption in t]
    if not hits:
        return None

    def score(t):
        return sum(1 for l in t.split("\n")
                   if any(l.strip().startswith(s) for s in STATES))
    best = max(hits, key=score)
    return best if score(best) else None


def state_rows(text, ncols, stop=None):
    """Rows keyed by state name, each with `ncols` numeric/nil tokens.

    DOSM wraps long names like 'Negeri Sembilan' across lines, sometimes above
    the numeric row and sometimes straddling it ('Negeri' / numbers /
    'Sembilan'), so both stitchings are tried.
    """
    if stop:
        text = text.split(stop)[0]
    lines = [l.strip() for l in text.split("\n")]
    joined = (lines
              + [f"{lines[i]} {lines[i+1]}" for i in range(len(lines) - 1)]
              + [f"{lines[i]} {lines[i+2]} {lines[i+1]}" for i in range(len(lines) - 2)])
    out = {}
    for line in joined:
        st = next((s for s in sorted(STATES, key=len, reverse=True)
                   if line.startswith(s)), None)
        if not st or st in out:
            continue
        toks = [t for t in line[len(st):].split() if TOK.match(t)]
        if len(toks) == ncols:
            out[st] = [num(t) for t in toks]
    return out


def mwq(pgs, caption, area, rows):
    txt = find(pgs, caption)
    if txt is None:
        print(f"  MISS {caption}")
        return
    got = state_rows(txt, 20)
    for st, v in got.items():
        for yi, y in enumerate(YEARS5):
            for ci, cat in enumerate(MWQ_CATS):
                rows.append({"state": st, "area": area, "year": y, "category": cat,
                             "stations": v[yi * 4 + ci]})
    print(f"  {caption[:46]:48s} {len(got):2d} states")


def write(name, rows, fields):
    p = os.path.join(OUT, name)
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"  {len(rows):5d} rows -> {os.path.relpath(p, ROOT)}")


def main():
    pgs = pages()
    print(f"compendium: {len(pgs)} pages")

    # --- marine water quality, three area types ------------------------------
    mrows = []
    mwq(pgs, "Status of marine water quality in coastal areas", "coastal", mrows)
    mwq(pgs, "Status of marine water quality in estuary areas", "estuary", mrows)
    mwq(pgs, "Status of marine water quality in island areas", "island", mrows)
    write("sdg14_marine_water_quality_2020_2024.csv", mrows,
          ["state", "area", "year", "category", "stations"])

    # --- coastal length ------------------------------------------------------
    t = find(pgs, "Coastal length by state")
    rows = [{"state": s, "coastal_length_km": v[0], "share_of_malaysia_pct": v[1]}
            for s, v in state_rows(t, 2).items()]
    write("sdg14_coastal_length.csv", rows, ["state", "coastal_length_km", "share_of_malaysia_pct"])

    # --- coastal erosion -----------------------------------------------------
    t = find(pgs, "Distribution of coastal erosion areas")
    rows = []
    for s, v in state_rows(t, 9).items():
        rows.append({"state": s, "coastal_length_km": v[0],
                     "cat1_sites": v[1], "cat1_km": v[2], "cat2_sites": v[3], "cat2_km": v[4],
                     "cat3_sites": v[5], "cat3_km": v[6],
                     "total_eroding_km": v[7], "eroding_share_of_coast_pct": v[8]})
    write("sdg14_coastal_erosion_2024.csv", rows,
          ["state", "coastal_length_km", "cat1_sites", "cat1_km", "cat2_sites", "cat2_km",
           "cat3_sites", "cat3_km", "total_eroding_km", "eroding_share_of_coast_pct"])

    # --- mangrove forest -----------------------------------------------------
    t = find(pgs, "Area of mangrove forest by state")
    if t:
        rows = []
        for s, v in state_rows(t, 4).items():
            for y, val in zip([2019, 2020, 2021, 2022], v):
                rows.append({"state": s, "year": y, "mangrove_hectares": val})
        write("sdg14_mangrove_area.csv", rows, ["state", "year", "mangrove_hectares"])

    # --- marine fish landings ------------------------------------------------
    # each year contributes two columns: thousand tonnes, then % of Malaysia
    t = find(pgs, "Landings of marine fish by state")
    if t:
        rows = []
        for s, v in state_rows(t, 10).items():
            for i, y in enumerate(YEARS5):
                rows.append({"state": s, "year": y,
                             "landings_thousand_tonnes": v[i * 2],
                             "share_of_malaysia_pct": v[i * 2 + 1]})
        write("sdg14_marine_fish_landings.csv", rows,
              ["state", "year", "landings_thousand_tonnes", "share_of_malaysia_pct"])


if __name__ == "__main__":
    main()
