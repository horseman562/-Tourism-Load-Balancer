"""Join district tourism DEMAND (rank) to district tourism SUPPLY and context.

Demand : DTS 2025 sheet 8B -- top five most-visited administrative districts per
         state. A rank, not a count: it orders districts, it cannot size them.
Supply : registered homestay clusters and accommodation premises per district
         (GDP-by-District Table 72, 2020-2022).
Context: resident population and basic-amenities access per district.

This is the first claim in the project that is genuinely at district level on
both sides. It supports statements of the form "district X is among the five
most-visited in its state yet holds only N accommodation premises", and it
supports naming under-visited districts that already have supply.

TWO LIMITS ARE BUILT INTO THE OUTPUT AS COLUMNS, because both are easy to
forget once the file is downstream:

1. VINTAGE MISMATCH. Demand is 2025; supply is 2021 (the source table runs
   2020-2022 but its 2022 column is 'n.a' throughout). That is a four-year gap
   on two halves of one claim. No district-level accommodation count exists for
   2023, 2024 or 2025 anywhere in DOSM -- checked My Local Stats 2024 (state
   only), GDP-by-District (no newer edition), and the Economic Census
   accommodation volume (dead link, and 2022 reference year regardless).
   Mitigation, not a fix: the same MOTAC series at state level runs to 2024, and
   over 2021-2024 it moved +0.5% nationally with a Spearman rank correlation of
   0.977, so the 2021 district split is probably still close. The per-state
   drift is attached to every row so the risk is visible where it bites.

2. RANK IS ORDINAL. Sheet 8B gives position within a state, not a quantity.
   Rank 3 in Kelantan and rank 3 in Melaka are not comparable, no
   demand-to-supply ratio can be computed from it, and differences between ranks
   have no magnitude.
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from district_names import dkey, skey  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, "data", "processed")
RAW = os.path.join(ROOT, "data", "raw", "opendosm")


def keyed(df, state_col="state", dist_col="district"):
    df = df.copy()
    df["_sk"] = df[state_col].map(skey)
    df["_dk"] = df[dist_col].map(dkey)
    return df


def main():
    dem = keyed(pd.read_csv(os.path.join(P, "dts_top_districts_visited_2025.csv")))

    sup = pd.read_csv(os.path.join(P, "district_homestay_accommodation_2020_2022.csv"))
    sup = keyed(sup[(sup.level == "district") & (sup.year == 2021)])
    sup = sup[["_sk", "_dk", "homestay_clusters", "accommodation_premises"]]

    pop = pd.read_csv(os.path.join(RAW, "population_district.csv"))
    pop = pop[(pop.date == "2024-01-01") & (pop.sex == "both") &
              (pop.age == "overall") & (pop.ethnicity == "overall")]
    pop = keyed(pop)[["_sk", "_dk", "population"]].rename(
        columns={"population": "population_thousands"})

    am = pd.read_csv(os.path.join(RAW, "hh_access_amenities.csv"))
    am = am[(am.date == "2024-01-01") & (am.district != "All Districts")]
    am = keyed(am)[["_sk", "_dk", "piped_water", "sanitation", "electricity"]]

    out = (dem.merge(sup, on=["_sk", "_dk"], how="left")
              .merge(pop, on=["_sk", "_dk"], how="left")
              .merge(am, on=["_sk", "_dk"], how="left"))

    for col, label in (("accommodation_premises", "supply"),
                       ("population_thousands", "population"),
                       ("piped_water", "amenities")):
        n = out[col].isna().sum()
        print(f"  unmatched against {label:11s}: {n}")
        if n:
            print("    ", out[out[col].isna()][["state", "district"]].values.tolist())

    # per-state drift in the same MOTAC series over the vintage gap, so the
    # staleness risk travels with each row instead of living in a footnote
    mot = pd.read_csv(os.path.join(P, "motac_accommodation_by_state_2022_2024.csv"))
    mot = mot[(mot.state != "Malaysia") & (mot.year == 2024)][
        ["state", "accommodation_premises"]].rename(
        columns={"accommodation_premises": "_p24"})
    s21 = pd.read_csv(os.path.join(P, "district_homestay_accommodation_2020_2022.csv"))
    s21 = s21[(s21.level == "state") & (s21.year == 2021)][
        ["state", "accommodation_premises"]].rename(
        columns={"accommodation_premises": "_p21"})
    drift = mot.merge(s21, on="state")
    drift["state_supply_change_2021_2024_pct"] = (
        (drift._p24 / drift._p21 - 1) * 100).round(1)
    out = out.merge(drift[["state", "state_supply_change_2021_2024_pct"]],
                    on="state", how="left")

    out = out.drop(columns=["_sk", "_dk"])
    out["demand_year"] = 2025
    out["demand_measure"] = "rank within state (ORDINAL - not a count, not comparable across states)"
    out["supply_year"] = 2021
    out["supply_vintage_gap_years"] = 4
    out["caveat"] = ("demand rank 2025 vs supply 2021; no district accommodation "
                     "count published for 2023-2025. See data/GAPS.md section 2.")

    path = os.path.join(P, "district_demand_supply_2025.csv")
    out.to_csv(path, index=False, encoding="utf-8")
    print(f"\nwrote {len(out)} rows x {len(out.columns)} cols -> "
          f"{os.path.relpath(path, ROOT)}")

    # the interesting cases: top-ranked districts with thin accommodation supply
    o = out.dropna(subset=["accommodation_premises"]).copy()
    o["premises_per_100k"] = (o.accommodation_premises /
                              (o.population_thousands / 100)).round(1)
    print("\nMost-visited district per state (rank 1), by accommodation supply:")
    r1 = o[o["rank"] == 1].sort_values("accommodation_premises")
    print(r1[["state", "district", "accommodation_premises", "homestay_clusters",
              "population_thousands", "premises_per_100k"]].to_string(index=False))
    print("\nThinnest supply among all 58 top-five districts")
    print("(state_drift = how much that state's total supply moved 2021->2024;")
    print(" a large drift means the 2021 district figure is the least reliable):")
    t = o.nsmallest(8, "accommodation_premises").rename(
        columns={"state_supply_change_2021_2024_pct": "state_drift_pct"})
    print(t[["state", "district", "rank", "accommodation_premises",
             "homestay_clusters", "premises_per_100k",
             "state_drift_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()
