"""Build a MODELLED quarterly seasonality series per state.

DOSM publishes domestic visitors quarterly for Malaysia and annually by state,
but never quarterly by state (see data/GAPS.md §1). This script combines the
two REAL series into one DERIVED one:

    state_visitors[s, q] = state_annual[s] * (national[q] / national_annual)

Both inputs are real published figures, and the national quarterly values sum
to the published national annual total exactly, so the shares are exact.

The ASSUMPTION -- and it is a strong one -- is that every state shares the
national seasonal profile. It is certainly wrong in detail: beach states such as
Terengganu and Pahang are far more seasonal than W.P. Kuala Lumpur or Putrajaya.
Output is therefore labelled MODELLED in the data itself, in every row, and must
never be presented as observed. No monthly version is produced: interpolating
quarters into months would add a second layer of invention on top of this one.
"""
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, "data", "processed")
YEAR = 2025
QSTART = {"Q1": f"{YEAR}-01-01", "Q2": f"{YEAR}-04-01",
          "Q3": f"{YEAR}-07-01", "Q4": f"{YEAR}-10-01"}


def main():
    nat = pd.read_csv(os.path.join(P, "dts_national_quarterly.csv"))
    nat = nat[(nat.measure == "visitors") & (nat.year == YEAR)]
    if len(nat) != 4:
        raise SystemExit(f"need 4 national quarters for {YEAR}, found {len(nat)}")
    total_q = nat.value_million.sum()

    st = pd.read_csv(os.path.join(P, "dts_visitors_by_state_2018_2025.csv"))
    st = st[st.year == YEAR][["state", "domestic_visitors_thousand"]]
    st["annual_millions"] = st.domestic_visitors_thousand / 1000

    # sanity: the published quarters should reconstruct the published annual total
    gap = abs(total_q - st.annual_millions.sum()) / total_q * 100
    print(f"national quarters sum {total_q:.1f}M vs sum of state annuals "
          f"{st.annual_millions.sum():.1f}M  ({gap:.2f}% apart)")
    if gap > 1.0:
        raise SystemExit("national quarterly and annual series disagree by >1%; "
                         "do not model on top of that")

    shares = {r.quarter: r.value_million / total_q for r in nat.itertuples()}
    print("national quarterly shares: " +
          ", ".join(f"{q} {s*100:.1f}%" for q, s in sorted(shares.items())))

    rows = []
    for r in st.itertuples():
        for q, share in sorted(shares.items()):
            rows.append({
                "state": r.state, "year": YEAR, "quarter": q,
                "quarter_start": QSTART[q],
                "visitors_millions": round(r.annual_millions * share, 4),
                "basis": "MODELLED",
                "method": "state annual (DTS 2025 Table 9) x national quarterly share "
                          "(DTS bulletins); assumes the national seasonal profile applies "
                          "to every state",
            })
    out = pd.DataFrame(rows)
    path = os.path.join(P, "state_quarterly_visitors_2025_MODELLED.csv")
    out.to_csv(path, index=False, encoding="utf-8")
    print(f"wrote {len(out)} rows ({out.state.nunique()} states x 4 quarters) -> "
          f"{os.path.relpath(path, ROOT)}")

    chk = out.groupby("state").visitors_millions.sum().round(3)
    ann = st.set_index("state").annual_millions.round(3)
    worst = (chk - ann).abs().max()
    print(f"reconstruction check: max |sum(quarters) - annual| = {worst:.4f}M")


if __name__ == "__main__":
    main()
