"""Extract the statistical tables from the DOSM Domestic Tourism Survey 2024
state publications into tidy CSVs.

Every value written here is read out of an official DOSM PDF. Nothing is
imputed: a cell DOSM prints as "-" (nil) becomes 0 for counts and empty for
rates, and a table that cannot be located is reported, never guessed.

Tables covered (numbering is DOSM's, identical across all 16 reports):
   1  Key Statistics 2018-2024 (receipts, visitors, trips, ALOS, per-capita)
   2  Domestic visitors by type (excursionist / tourist)
   3  Domestic tourism trips (same day / overnight)
   6  Average length of stay
   7  Total receipts by component  <- shopping / F&B spend
  12  Tourist arrivals by type of accommodation
  13  Social & demographic profiles  <- monthly household income class
  14  Hotels and rooms by star rating   (source: NAPIC)
  15  Hotels and rooms by location      (source: NAPIC)
"""
import csv, json, os, re, sys

import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDF_DIR = os.path.join(ROOT, "dosm-tourism-data", "2024-states")
OUT_DIR = os.path.join(ROOT, "data", "processed")
CACHE_DIR = os.path.join(ROOT, "data", "_tmp", "pdftext")

# filename stem -> geodata spelling (dashboard/geo_state.json)
STATES = {
    "Johor": "Johor",
    "Kedah": "Kedah",
    "Kelantan": "Kelantan",
    "Melaka": "Melaka",
    "Negeri_Sembilan": "Negeri Sembilan",
    "Pahang": "Pahang",
    "Perak": "Perak",
    "Perlis": "Perlis",
    "Pulau_Pinang": "Pulau Pinang",
    "Sabah": "Sabah",
    "Sarawak": "Sarawak",
    "Selangor": "Selangor",
    "Terengganu": "Terengganu",
    "Wilayah_Persekutuan_Kuala_Lumpur": "W.P. Kuala Lumpur",
    "Wilayah_Persekutuan_Labuan": "W.P. Labuan",
    "Wilayah_Persekutuan_Putrajaya": "W.P. Putrajaya",
}

YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
NUM = r"-|\d[\d,]*(?:\.\d+)?"


def num(tok):
    """DOSM prints nil as '-'. Return None for nil so callers decide."""
    tok = tok.strip()
    if tok in ("-", "–", "—", ""):
        return None
    return float(tok.replace(",", ""))


def page_texts(path, state):
    """Extract per-page text once, then cache -- these are 14-86 MB files."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache = os.path.join(CACHE_DIR, f"{state}.json")
    if os.path.exists(cache):
        return json.load(open(cache, encoding="utf-8"))
    with pdfplumber.open(path) as pdf:
        pages = [(p.extract_text() or "") for p in pdf.pages]
    json.dump(pages, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    return pages


def find_table(pages, n, cont=False):
    """Return the text of the page holding 'Table <n>:', excluding the technical
    notes appendix (which restarts its own Table 1)."""
    hits = []
    pat = re.compile(rf"^Table {n}:", re.M)
    for i, t in enumerate(pages):
        if pat.search(t) and "TECHNICAL NOTES" not in t.upper():
            hits.append((i, t))
    if not hits:
        return None
    # statistical tables live in Part 2, before the appendix; take the first run
    if cont:
        return hits[1][1] if len(hits) > 1 else None
    return hits[0][1]


TOKEN_RE = re.compile(r"^(?:-|–|—|\d[\d,]*(?:\.\d+)?)$")


def numeric_tail(s):
    """Trailing run of numeric/nil tokens on a line, e.g. '... 2 150' -> ['2','150']."""
    toks = s.split()
    tail = []
    for t in reversed(toks):
        if TOKEN_RE.match(t):
            tail.insert(0, t)
        else:
            break
    return tail


def row_after(text, label_re, count):
    """Find the line matching `label_re` and take the last `count` numbers on it.

    Labels are matched then sliced off, because several of them contain digits
    themselves ('5-Bintang/ 5-Star', '1,001 - 3,000').
    """
    pat = re.compile(label_re)
    for line in text.split("\n"):
        m = pat.search(line)
        if not m:
            continue
        tail = numeric_tail(line[m.end():])
        if len(tail) >= count:
            return [num(t) for t in tail[-count:]]
    return None


# ---------------------------------------------------------------- table 1
T1_ROWS = [
    ("total_receipts_rm_million", r"Jumlah Terimaan \(RM juta\)"),
    ("domestic_visitors_thousand", r"Pelawat Domestik \('000\)"),
    ("domestic_trips_thousand", r"Perjalanan Pelancongan Domestik \('000\)"),
    ("avg_receipts_per_capita_rm", r"Purata Terimaan per Kapita \(RM\)"),
    ("avg_receipts_per_trip_rm", r"Purata Terimaan per Perjalanan \(RM\)"),
    ("avg_length_of_stay_nights", r"Purata Bilangan Hari Menginap"),
]


def parse_t1(pages, state, problems):
    t = find_table(pages, 1)
    out = []
    if not t:
        problems.append((state, "table_1", "page not found"))
        return out
    for ind, lab in T1_ROWS:
        vals = row_after(t, lab, 7)
        if vals is None:
            problems.append((state, "table_1", f"row not matched: {ind}"))
            continue
        for y, v in zip(YEARS, vals):
            out.append({"state": state, "year": y, "indicator": ind, "value": v})
    return out


# ---------------------------------------------------------------- table 7
T7_ROWS = [
    ("expenditure_by_visitors", r"A\. Perbelanjaan oleh pelawat"),
    ("shopping", r"Membeli-belah"),
    ("automotive_fuel", r"Pembelian bahan api kenderaan"),
    ("transportation", r"^Pengangkutan\b"),
    ("food_and_beverage", r"Makanan & minuman"),
    ("accommodation", r"^Penginapan\b"),
    ("pre_trip_package_entrance_tickets", r"Perbelanjaan sebelum perjalanan"),
    ("other_activities", r"Aktiviti-aktiviti lain"),
    ("expenditure_by_visited_households", r"B\. Perbelanjaan oleh isi rumah"),
]


def parse_t7(pages, state, problems):
    t = find_table(pages, 7)
    out = []
    if not t:
        problems.append((state, "table_7", "page not found"))
        return out
    for ind, lab in T7_ROWS:
        vals = row_after(t, lab, 4)
        if vals is None:
            problems.append((state, "table_7", f"row not matched: {ind}"))
            continue
        r23, r24, s23, s24 = vals
        out.append({"state": state, "component": ind, "receipts_rm_thousand_2023": r23,
                    "receipts_rm_thousand_2024": r24, "share_pct_2023": s23, "share_pct_2024": s24})
    # the A+B total row prints its numbers on the line *after* the label
    m = re.search(r"Jumlah Terimaan \(A\+B\)[\s\S]{0,80}?\n\s*(" + NUM + r")\s+(" + NUM + r")\s+100\.0\s+100\.0", t)
    if m:
        out.append({"state": state, "component": "total_receipts",
                    "receipts_rm_thousand_2023": num(m.group(1)),
                    "receipts_rm_thousand_2024": num(m.group(2)),
                    "share_pct_2023": 100.0, "share_pct_2024": 100.0})
    else:
        problems.append((state, "table_7", "total row not matched"))
    return out


# ------------------------------------------------------------ tables 14/15
STAR_ROWS = [("5_star", r"5-Bintang/ ?5-Star"), ("4_star", r"4-Bintang/ ?4-Star"),
             ("3_star", r"3-Bintang/ ?3-Star"), ("2_star", r"2-Bintang/ ?2-Star"),
             ("1_star", r"1-Bintang/ ?1-Star"), ("3_orchid", r"3 Orkid/ ?3 Orchid"),
             ("2_orchid", r"2 Orkid/ ?2 Orchid"), ("1_orchid", r"1 Orkid/ ?1 Orchid"),
             ("unrated", r"Unrated")]
LOC_ROWS = [("city_town", r"Bandar/ ?Pekan"), ("beach", r"Pantai/ ?Beach"),
            ("hill", r"Gunung/ ?Hill"), ("other_location", r"Lain-lain/ ?Others")]


def parse_hotels(pages, state, problems):
    """Tables 14 and 15 usually share a page; split on the Table 15 header."""
    t = find_table(pages, 14)
    out = []
    if not t:
        problems.append((state, "table_14_15", "page not found"))
        return out
    parts = re.split(r"Jadual 15:", t)
    t14 = parts[0]
    t15 = parts[1] if len(parts) > 1 else (find_table(pages, 15) or "")
    for kind, rows, blob in (("star_rating", STAR_ROWS, t14), ("location", LOC_ROWS, t15)):
        for ind, lab in rows:
            vals = row_after(blob, lab, 2)
            if vals is None:
                problems.append((state, f"table_{'14' if kind=='star_rating' else '15'}",
                                 f"row not matched: {ind}"))
                continue
            out.append({"state": state, "breakdown": kind, "category": ind,
                        "hotels": 0 if vals[0] is None else int(vals[0]),
                        "rooms": 0 if vals[1] is None else int(vals[1])})
        tot = row_after(blob, r"Jumlah/ ?Total", 2)
        if tot:
            out.append({"state": state, "breakdown": kind, "category": "total",
                        "hotels": 0 if tot[0] is None else int(tot[0]),
                        "rooms": 0 if tot[1] is None else int(tot[1])})
    return out


# ---------------------------------------------------------------- table 13
INCOME_ROWS = [("le_1000", r"≤ ?1,000"), ("1001_3000", r"1,001 - 3,000"),
               ("3001_5000", r"3,001 - 5,000"), ("5001_10000", r"5,001 - 10,000"),
               ("ge_10001", r"≥ ?10,001")]
INCOME_LABEL = {"le_1000": "≤RM1,000", "1001_3000": "RM1,001-3,000",
                "3001_5000": "RM3,001-5,000", "5001_10000": "RM5,001-10,000",
                "ge_10001": "≥RM10,001"}


def parse_income(pages, state, problems):
    # the phrase also appears in the Part 1 narrative; take the page that
    # actually carries the Table 13 income rows
    t = None
    for txt in pages:
        if "Pendapatan Bulanan Isi Rumah" in txt and re.search(r"5,001 - 10,000", txt):
            t = txt
            break
    out = []
    if not t:
        problems.append((state, "table_13_income", "section not found"))
        return out
    for ind, lab in INCOME_ROWS:
        vals = row_after(t, lab, 2)
        if vals is None:
            problems.append((state, "table_13_income", f"row not matched: {ind}"))
            continue
        out.append({"state": state, "income_class": INCOME_LABEL[ind],
                    "share_pct_2023": vals[0], "share_pct_2024": vals[1]})
    return out


# ---------------------------------------------------------------- table 12
# the accommodation list varies by state (no chalets in Putrajaya, etc.), so
# rows are read generically and only the label is normalised
ACC_SLUG = [
    (r"Rumah saudara", "relatives_friends_house"), (r"^Hotel", "hotel"),
    (r"^Chalet", "chalet"), (r"Apartmen", "apartment"),
    (r"Inap desa|Homestay", "homestay_vacation_home"), (r"Rumah rehat", "rest_house"),
    (r"Tapak perkhemahan|Camp", "campsite"), (r"Rumah tetamu|Guest", "guest_house"),
    (r"Resort", "resort"), (r"Motel", "motel"), (r"Lain-lain", "other_accommodation"),
]


def slug_acc(label):
    for pat, s in ACC_SLUG:
        if re.search(pat, label, re.I):
            return s
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")


def parse_accommodation(pages, state, problems):
    t = find_table(pages, 12)
    out = []
    if not t:
        problems.append((state, "table_12", "page not found"))
        return out
    body = re.split(r"Jadual 12:", t)
    body = re.split(r"Jadual 13:", body[-1])[0]
    for line in body.split("\n"):
        tail = numeric_tail(line)
        label = line[: len(line) - len(" ".join(tail))].strip() if tail else ""
        if len(tail) != 2 or not label or "Total" in label or "Table 12" in label:
            continue
        out.append({"state": state, "accommodation_type": slug_acc(label),
                    "share_pct_2023": num(tail[0]), "share_pct_2024": num(tail[1])})
    if not out:
        problems.append((state, "table_12", "no rows matched"))
    return out


def write_csv(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {len(rows):5d} rows -> {os.path.relpath(path, ROOT)}")


def main():
    only = sys.argv[1:] or None
    t1, t7, hot, inc, acc = [], [], [], [], []
    problems = []
    for stem, state in STATES.items():
        if only and state not in only and stem not in only:
            continue
        path = os.path.join(PDF_DIR, f"publication_{stem}_2024.pdf")
        if not os.path.exists(path):
            problems.append((state, "pdf", "file missing"))
            continue
        pages = page_texts(path, stem)
        t1 += parse_t1(pages, state, problems)
        t7 += parse_t7(pages, state, problems)
        hot += parse_hotels(pages, state, problems)
        inc += parse_income(pages, state, problems)
        acc += parse_accommodation(pages, state, problems)
        print(f"{state:22s} pages={len(pages):3d} t1={len([r for r in t1 if r['state']==state]):2d} "
              f"t7={len([r for r in t7 if r['state']==state]):2d} "
              f"hotels={len([r for r in hot if r['state']==state]):2d} "
              f"income={len([r for r in inc if r['state']==state]):2d} "
              f"accom={len([r for r in acc if r['state']==state]):2d}")

    write_csv(os.path.join(OUT_DIR, "dts_key_statistics_2018_2024.csv"), t1,
              ["state", "year", "indicator", "value"])
    write_csv(os.path.join(OUT_DIR, "dts_receipts_by_component_2023_2024.csv"), t7,
              ["state", "component", "receipts_rm_thousand_2023", "receipts_rm_thousand_2024",
               "share_pct_2023", "share_pct_2024"])
    write_csv(os.path.join(OUT_DIR, "napic_hotels_rooms_2024.csv"), hot,
              ["state", "breakdown", "category", "hotels", "rooms"])
    write_csv(os.path.join(OUT_DIR, "dts_visitor_income_class.csv"), inc,
              ["state", "income_class", "share_pct_2023", "share_pct_2024"])
    write_csv(os.path.join(OUT_DIR, "dts_accommodation_type.csv"), acc,
              ["state", "accommodation_type", "share_pct_2023", "share_pct_2024"])

    if problems:
        print(f"\n{len(problems)} PROBLEMS (these become GAPS.md entries):")
        for s, tb, why in problems:
            print(f"  {s:22s} {tb:18s} {why}")
    else:
        print("\nno extraction problems")


if __name__ == "__main__":
    main()
