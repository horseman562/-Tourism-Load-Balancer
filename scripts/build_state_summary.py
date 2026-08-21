"""Join the extracted DTS tables with the OpenDOSM datasets into one
dashboard-ready row per state, replacing every placeholder column with a
sourced value.

Each output column is tagged REAL (read from an official release) or DERIVED
(arithmetic on REAL columns). Nothing here is invented; columns with no
Malaysian official source are omitted and recorded in data/GAPS.md instead.
"""
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, "data", "processed")
RAW = os.path.join(ROOT, "data", "raw", "opendosm")

# kept identical to the grouping the dashboard already filters on
REGION = {
    "Selangor": "Central", "W.P. Kuala Lumpur": "Central",
    "Negeri Sembilan": "Central", "W.P. Putrajaya": "Central",
    "Perak": "North", "Pulau Pinang": "North", "Kedah": "North", "Perlis": "North",
    "Johor": "South", "Melaka": "South",
    "Pahang": "East Coast", "Kelantan": "East Coast", "Terengganu": "East Coast",
    "Sarawak": "East Malaysia", "Sabah": "East Malaysia", "W.P. Labuan": "East Malaysia",
}


def main():
    key = pd.read_csv(os.path.join(P, "dts_key_statistics_2018_2024.csv"))
    w = key.pivot_table(index=["state", "year"], columns="indicator", values="value").reset_index()

    def yr(y, col):
        return w[w.year == y].set_index("state")[col]

    df = pd.DataFrame(index=sorted(w.state.unique()))
    df.index.name = "state"
    df["region_cluster"] = [REGION[s] for s in df.index]

    # --- DTS Table 1 (REAL) -------------------------------------------------
    df["visitors_2023_millions"] = (yr(2023, "domestic_visitors_thousand") / 1000).round(3)
    df["visitors_2024_millions"] = (yr(2024, "domestic_visitors_thousand") / 1000).round(3)
    df["visitor_growth_pct"] = ((df.visitors_2024_millions / df.visitors_2023_millions - 1) * 100).round(2)
    # DTS 2025 (Malaysia report, Table 9) extends the visitor series one year
    v25 = pd.read_csv(os.path.join(P, "dts_visitors_by_state_2018_2025.csv"))
    v25 = v25[v25.year == 2025].set_index("state")["domestic_visitors_thousand"]
    df["visitors_2025_millions"] = (v25 / 1000).round(3)
    df["visitor_growth_2025_pct"] = ((df.visitors_2025_millions / df.visitors_2024_millions - 1) * 100).round(2)

    df["receipts_2024_rm_million"] = yr(2024, "total_receipts_rm_million")
    df["trips_2024_millions"] = (yr(2024, "domestic_trips_thousand") / 1000).round(3)
    df["alos_nights"] = yr(2024, "avg_length_of_stay_nights")
    df["receipts_per_trip_rm"] = yr(2024, "avg_receipts_per_trip_rm")

    # --- DTS Table 7 (REAL) -------------------------------------------------
    rec = pd.read_csv(os.path.join(P, "dts_receipts_by_component_2023_2024.csv"))
    pv = rec.pivot_table(index="state", columns="component", values="receipts_rm_thousand_2024") / 1000
    df["shopping_spend_rm_m"] = pv["shopping"].round(1)
    df["fnb_spend_rm_m"] = pv["food_and_beverage"].round(1)
    df["accommodation_spend_rm_m"] = pv["accommodation"].round(1)

    # --- DTS Table 13, modal monthly household income class (REAL) ----------
    inc = pd.read_csv(os.path.join(P, "dts_visitor_income_class.csv"))
    df["income_bracket"] = inc.loc[inc.groupby("state").share_pct_2024.idxmax()].set_index("state")["income_class"]

    # --- NAPIC Tables 14/15, accommodation capacity (REAL) ------------------
    hot = pd.read_csv(os.path.join(P, "napic_hotels_rooms_2024.csv"))
    star = hot[hot.breakdown == "star_rating"]
    df["hotels_total"] = star[star.category == "total"].set_index("state")["hotels"]
    df["rooms_total"] = star[star.category == "total"].set_index("state")["rooms"]
    loc = hot[hot.breakdown == "location"]
    df["rooms_beach"] = loc[loc.category == "beach"].set_index("state")["rooms"]
    df["rooms_city_town"] = loc[loc.category == "city_town"].set_index("state")["rooms"]

    # --- OpenDOSM population_state (REAL) -----------------------------------
    pop = pd.read_csv(os.path.join(RAW, "population_state.csv"))
    pop = pop[(pop.date == "2024-01-01") & (pop.sex == "both") &
              (pop.age == "overall") & (pop.ethnicity == "overall")]
    df["population_thousands"] = pop.set_index("state")["population"]

    # --- OpenDOSM hh_income_state (REAL + DERIVED gap) ----------------------
    hh = pd.read_csv(os.path.join(RAW, "hh_income_state.csv"))
    hh = hh[hh.date == "2024-01-01"].set_index("state")
    df["hh_income_median_rm"] = hh["income_median"]
    # gap against Malaysia's own published national median (hh_income), not a
    # median-of-medians: negative means the state is richer than the country
    natdf = pd.read_csv(os.path.join(RAW, "hh_income.csv"))
    nat = float(natdf[natdf.date == "2024-01-01"]["income_median"].iloc[0])
    df["national_hh_income_median_rm"] = nat
    df["income_gap_pct"] = ((nat - hh["income_median"]) / nat * 100).round(2)

    # --- OpenDOSM hh_access_amenities, population-weighted to state (REAL) --
    am = pd.read_csv(os.path.join(RAW, "hh_access_amenities.csv"))
    am = am[(am.date == "2024-01-01") & (am.district != "All Districts")]
    dpop = pd.read_csv(os.path.join(RAW, "population_district.csv"))
    dpop = dpop[(dpop.date == "2024-01-01") & (dpop.sex == "both") &
                (dpop.age == "overall") & (dpop.ethnicity == "overall")]
    # the two releases spell a handful of districts differently
    aliases = {
        "Cameron Highlands": "Cameron Highland", "Larut dan Matang": "Larut Dan Matang",
        "Seberang Perai Selatan": "Sp Selatan", "Seberang Perai Tengah": "Sp Tengah",
        "Seberang Perai Utara": "Sp Utara", "Hulu Langat": "Ulu Langat",
        "Hulu Selangor": "Ulu Selangor",
    }
    am["district"] = am["district"].replace(aliases)
    am = am.merge(dpop[["state", "district", "population"]], on=["state", "district"], how="left")
    if am.population.isna().any():
        miss = am[am.population.isna()][["state", "district"]].values.tolist()
        print(f"  WARNING {len(miss)} districts have no population weight: {miss[:5]}")
    am = am.dropna(subset=["population"])
    for col in ("piped_water", "sanitation", "electricity"):
        g = am.groupby("state").apply(
            lambda x, c=col: (x[c] * x.population).sum() / x.population.sum(), include_groups=False)
        df[f"amenities_{col}_pct"] = g.round(2)

    # --- DERIVED pressure / readiness inputs --------------------------------
    df["visitors_per_capita_2024"] = (df.visitors_2024_millions * 1000 / df.population_thousands).round(2)
    df["visitors_per_room_2024"] = (df.visitors_2024_millions * 1e6 / df.rooms_total).round(0)
    df["beach_room_share_pct"] = (df.rooms_beach / df.rooms_total * 100).round(2)

    out = os.path.join(P, "state_summary_2024.csv")
    df.reset_index().to_csv(out, index=False, encoding="utf-8")
    print(f"wrote {len(df)} states x {len(df.columns)} cols -> {os.path.relpath(out, ROOT)}")
    print(f"\nnulls per column:\n{df.isna().sum()[df.isna().sum() > 0].to_string() or '  none'}")
    return df


if __name__ == "__main__":
    d = main()
    pd.set_option("display.width", 220, "display.max_columns", 40)
    print("\n" + d[["visitors_2024_millions", "population_thousands", "visitors_per_capita_2024",
                    "rooms_total", "visitors_per_room_2024", "alos_nights",
                    "amenities_piped_water_pct", "income_gap_pct"]].to_string())
