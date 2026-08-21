"""Extract sheets 8A and 8B of tourism_domestic_2025.xlsx (DTS 2025, OpenDOSM).

  8A  Top Five Destinations Most Visited by Domestic Visitors, 2025  (16 states)
  8B  Top Five Administrative Districts Most Visited by Domestic Visitors, 2025
      (12 states; Perlis, W.P. Kuala Lumpur, W.P. Labuan and W.P. Putrajaya have
      no administrative districts)

8B is the only district-level tourism *demand* statistic DOSM publishes. It is a
rank with no counts -- it can name and order districts, it cannot size them.

Layout: two side-by-side column blocks, each 'state | newline-separated list of
five'. Rows are read generically so the block positions do not matter.
"""
import csv, os, re, unicodedata

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "raw", "opendosm-tourism", "tourism_domestic_2025.xlsx")
OUT = os.path.join(ROOT, "data", "processed")

STATES = ["Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang",
          "Perak", "Perlis", "Pulau Pinang", "Sabah", "Sarawak", "Selangor",
          "Terengganu", "W.P. Kuala Lumpur", "W.P. Labuan", "W.P. Putrajaya"]


def clean(s):
    # the workbook uses non-breaking spaces inside several destination names
    s = unicodedata.normalize("NFKC", str(s)).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def read_sheet(ws):
    """Pair each state cell with the next non-empty cell on its row."""
    out = []
    for row in ws.iter_rows(values_only=True):
        cells = [(i, c) for i, c in enumerate(row) if c not in (None, "")]
        for pos, (i, c) in enumerate(cells):
            name = clean(c)
            if name not in STATES:
                continue
            if pos + 1 >= len(cells):
                continue
            items = [clean(x) for x in str(cells[pos + 1][1]).split("\n")]
            items = [x for x in items if x]
            for rank, item in enumerate(items, 1):
                out.append((name, rank, item))
    return out


def write(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(fields)
        w.writerows(rows)
    print(f"  {len(rows):4d} rows -> {os.path.relpath(path, ROOT)}")


def main():
    wb = openpyxl.load_workbook(SRC, data_only=True)

    a = read_sheet(wb["8A"])
    write(os.path.join(OUT, "dts_top_destinations_2025.csv"), a,
          ["state", "rank", "destination"])
    print(f"    8A: {len({r[0] for r in a})} states")

    b = read_sheet(wb["8B"])
    write(os.path.join(OUT, "dts_top_districts_visited_2025.csv"), b,
          ["state", "rank", "district"])
    got = {r[0] for r in b}
    print(f"    8B: {len(got)} states, {len({r[2] for r in b})} distinct districts")
    missing = [s for s in STATES if s not in got]
    print(f"    8B states absent (no administrative districts): {missing}")
    wb.close()

    for label, rows in (("8A", a), ("8B", b)):
        bad = {s: n for s, n in
               ((s, sum(1 for r in rows if r[0] == s)) for s in {r[0] for r in rows})
               if n != 5}
        print(f"    {label} states without exactly 5 entries: {bad or 'none'}")


if __name__ == "__main__":
    main()
