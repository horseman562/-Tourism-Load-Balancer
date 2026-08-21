"""Extract Table 10.9 of My Local Stats 2024 (doc 18191): registered homestay
clusters, accommodation premises and rooms BY STATE, 2022-2024.
Originating agency: Ministry of Tourism, Arts and Culture Malaysia (MOTAC).

Why this matters: our district-level supply (GDP-by-District Table 72) is
2020-2022 with 2022 unusable, so the newest district figure is 2021, while the
demand rank it is joined to is 2025. This table is the same MOTAC series at state
level and runs to 2024, so it cannot fix the district vintage but it can measure
how much the series moved over the gap -- which tells us whether the 2021
district split is likely to still be roughly right.

Note: DOSM's own English caption on this table reads "2021-2023" while the Malay
caption and the data rows both read 2022-2024. The data rows are taken as
authoritative.
"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, "data", "_tmp", "mylocalstats_pages.json")
OUT = os.path.join(ROOT, "data", "processed", "motac_accommodation_by_state_2022_2024.csv")

STATES = ["Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang",
          "Perak", "Perlis", "Pulau Pinang", "Sabah", "Sarawak", "Selangor",
          "Terengganu", "W.P. Kuala Lumpur", "W.P. Labuan", "W.P. Putrajaya",
          "MALAYSIA"]
ROW = re.compile(r"^(?P<name>[A-Za-z. ]+?)\s*(?P<year>20\d\d)\s+(?P<a>-|[\d,]+)\s+"
                 r"(?P<b>-|[\d,]+)\s+(?P<c>-|[\d,]+)\s*$")
CONT = re.compile(r"^(?P<year>20\d\d)\s+(?P<a>-|[\d,]+)\s+(?P<b>-|[\d,]+)\s+"
                  r"(?P<c>-|[\d,]+)\s*$")


def val(t):
    return None if t.strip() in ("-", "–", "—") else int(t.replace(",", ""))


def main():
    pgs = json.load(open(CACHE, encoding="utf-8"))
    page = next(t for i, t in enumerate(pgs)
                if "kluster homestay" in t.lower() and i > 100)
    rows, cur = [], None
    for line in page.split("\n"):
        line = " ".join(line.split())
        m = ROW.match(line)
        if m:
            name = m.group("name").strip()
            cur = next((s for s in STATES if s.lower() == name.lower()), cur)
        else:
            m = CONT.match(line)
            if not m or cur is None:
                continue
        rows.append({
            "state": "Malaysia" if cur == "MALAYSIA" else cur,
            "year": int(m.group("year")),
            "homestay_clusters": val(m.group("a")),
            "accommodation_premises": val(m.group("b")),
            "rooms": val(m.group("c")),
        })

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["state", "year", "homestay_clusters",
                                          "accommodation_premises", "rooms"])
        w.writeheader()
        w.writerows(rows)
    got = {r["state"] for r in rows}
    print(f"wrote {len(rows)} rows, {len(got)} areas -> {os.path.relpath(OUT, ROOT)}")
    missing = [s for s in STATES if (s if s != "MALAYSIA" else "Malaysia") not in got]
    print(f"  missing: {missing or 'none'}")

    # the printed Malaysia row must equal the sum of the states
    for y in (2022, 2023, 2024):
        tot = next((r for r in rows if r["state"] == "Malaysia" and r["year"] == y), None)
        s = sum(r["accommodation_premises"] or 0 for r in rows
                if r["state"] != "Malaysia" and r["year"] == y)
        if tot:
            ok = s == tot["accommodation_premises"]
            print(f"  {y}: states sum {s:,} vs printed Malaysia "
                  f"{tot['accommodation_premises']:,}  {'OK' if ok else 'DIFF'}")


if __name__ == "__main__":
    main()
