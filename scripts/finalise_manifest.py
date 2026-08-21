"""Complete data/manifest.json: every raw file we hold and every processed CSV
we produced, each with source URL, retrieval date, licence, DOSM release name
and a REAL / DERIVED / MISSING status.

Rule 10 of the competition requires every dataset to be cited; this file is the
machine-readable half of that, data/SOURCES.md is the human half.
"""
import csv, hashlib, json, os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFEST = os.path.join(ROOT, "data", "manifest.json")
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")

DOSM_LICENCE = ("Open Data Terms of Use, https://www.data.gov.my/terms-of-use "
                "-- free to use with attribution to the Department of Statistics Malaysia")

# raw CSVs pulled from the OpenDOSM / data.gov.my machine-readable catalogue
OPENDOSM = {
    "population_state.csv": ("population_state", "Population Table: States",
                             "https://storage.dosm.gov.my/population/population_state.csv"),
    "population_district.csv": ("population_district", "Population Table: Administrative Districts",
                                "https://storage.dosm.gov.my/population/population_district.csv"),
    "hh_income.csv": ("hh_income", "Household Income",
                      "https://storage.dosm.gov.my/hies/hh_income.csv"),
    "hh_income_state.csv": ("hh_income_state", "Household Income by State",
                            "https://storage.dosm.gov.my/hies/hh_income_state.csv"),
    "hh_income_district.csv": ("hh_income_district", "Household Income by Administrative District",
                               "https://storage.dosm.gov.my/hies/hh_income_district.csv"),
    "hh_inequality_state.csv": ("hh_inequality_state", "Income Inequality by State",
                                "https://storage.dosm.gov.my/hies/hh_inequality_state.csv"),
    "hh_poverty_state.csv": ("hh_poverty_state", "Poverty by State",
                             "https://storage.dosm.gov.my/hies/hh_poverty_state.csv"),
    "hh_access_amenities.csv": ("hh_access_amenities", "Access to Basic Amenities by State & District",
                                "https://storage.dosm.gov.my/hies/hh_access_amenities.csv"),
    "water_access.csv": ("water_access", "Access to Treated Water by State & Strata",
                         "https://storage.data.gov.my/water/water_access.csv"),
    "water_pollution_basin.csv": ("water_pollution_basin", "River Basin Pollution Monitoring",
                                  "https://storage.data.gov.my/environment/water_pollution_basin.csv"),
    "fish_landings.csv": ("fish_landings", "Monthly Landings of Marine Fish by State",
                          "https://storage.data.gov.my/agriculture/fish_landings.csv"),
    "gdp_state_real_supply.csv": ("gdp_state_real_supply", "Annual Real GDP by State & Economic Sector",
                                  "https://storage.dosm.gov.my/gdp/gdp_state_real_supply.csv"),
}

# processed outputs -> (status, derived-from, one-line description)
PROCESSED = {
    "dts_key_statistics_2018_2024.csv": (
        "REAL", "DTS 2024 state reports, Table 1",
        "Receipts, visitors, trips, per-capita/per-trip receipts and ALOS, 16 states x 2018-2024."),
    "dts_receipts_by_component_2023_2024.csv": (
        "REAL", "DTS 2024 state reports, Table 7",
        "Tourism receipts split by shopping, fuel, transport, F&B, accommodation, pre-trip and other."),
    "napic_hotels_rooms_2024.csv": (
        "REAL", "DTS 2024 state reports, Tables 14 & 15 (source: NAPIC)",
        "Hotels and rooms by star rating and by location (city/town, beach, hill, other)."),
    "dts_visitor_income_class.csv": (
        "REAL", "DTS 2024 state reports, Table 13",
        "Percentage of domestic visitors by monthly household income class."),
    "dts_accommodation_type.csv": (
        "REAL", "DTS 2024 state reports, Table 12",
        "Percentage of tourist arrivals by type of accommodation used."),
    "dts_visitors_by_state_2018_2025.csv": (
        "REAL", "DTS 2025 Malaysia report, Table 9",
        "Domestic visitors by state visited, 16 states x 2018-2025. Sums to DOSM's published national totals."),
    "dts_origin_destination_2025.csv": (
        "REAL", "DTS 2025 Malaysia report, Table 10",
        "Origin-destination matrix: tourists by state of origin x state visited, 2025."),
    "dts_national_quarterly.csv": (
        "REAL", "DTS quarterly bulletins Q2-Q4 2025 and Q1 2026",
        "National quarterly domestic visitors and tourists. NO state breakdown is published."),
    "sdg14_marine_water_quality_2020_2024.csv": (
        "REAL", "Compendium of Environment Statistics Malaysia 2025, Tables 1.36/1.37/1.38 "
                "(originating agency: Department of Environment)",
        "Marine Water Quality Index station counts by state, area (coastal/estuary/island), "
        "year and category (excellent/good/moderate/poor)."),
    "sdg14_coastal_length.csv": (
        "REAL", "Compendium of Environment Statistics Malaysia 2025, Table 1.11 "
                "(originating agency: Department of Irrigation and Drainage)",
        "Coastal length in km by state; sums to DOSM's published 8,840.0 km national total."),
    "sdg14_coastal_erosion_2024.csv": (
        "REAL", "Compendium of Environment Statistics Malaysia 2025, Table 4.15 "
                "(originating agency: Department of Irrigation and Drainage)",
        "Eroding coastline by state and severity category, 2024."),
    "sdg14_mangrove_area.csv": (
        "REAL", "Compendium of Environment Statistics Malaysia 2025, Table 1.20",
        "Mangrove forest area in hectares by state, 2019-2022."),
    "sdg14_marine_fish_landings.csv": (
        "REAL", "Compendium of Environment Statistics Malaysia 2025, Table 2.24",
        "Marine fish landings by state, 2020-2024, in thousand tonnes and share of Malaysia."),
    "motac_accommodation_by_state_2022_2024.csv": (
        "REAL", "My Local Stats 2024 (doc 18191), Table 10.9 "
                "(originating agency: Ministry of Tourism, Arts and Culture Malaysia)",
        "Registered homestay clusters, accommodation premises and rooms by state, 2022-2024. "
        "Used to measure supply drift across the district-data vintage gap; state sums match "
        "the printed Malaysia row in all three years."),
    "dts_national_urban_rural_2024_2025.csv": (
        "REAL", "DTS 2025 (OpenDOSM XLSX), sheets 2&3 and 4&5",
        "National visitors, trips, expenditure, ALOS and overnight spend split by urban / "
        "rural strata, 2024 and 2025. Malaysia level only; no state breakdown is published."),
    "dts_top_destinations_2025.csv": (
        "REAL", "DTS 2025 (OpenDOSM XLSX), sheet 8A",
        "Top five named destinations most visited by domestic visitors, 2025, all 16 states."),
    "dts_top_districts_visited_2025.csv": (
        "REAL", "DTS 2025 (OpenDOSM XLSX), sheet 8B",
        "Top five most-visited administrative districts per state, 2025 (12 states). "
        "The only district-level tourism DEMAND statistic DOSM publishes; a rank, not a count."),
    "district_demand_supply_2025.csv": (
        "REAL", "join of DTS 2025 sheet 8B with district homestay/accommodation, "
                "population_district and hh_access_amenities",
        "58 top-five districts: 2025 demand RANK (ordinal, within-state only) joined to 2021 "
        "supply, population and amenities. Carries explicit vintage-gap and ordinality columns "
        "plus per-state supply drift 2021-2024. All 58 matched across all four sources."),
    "state_panel_2017_2025.csv": (
        "REAL", "DTS 2023 state XLSX (2017-2023), DTS 2024 state PDFs (2024), "
                "DTS 2025 Table 9 (2025)",
        "Per-state panel, 6 indicators. 2017-2023 taken at full precision from the XLSX; "
        "the 2018-2023 overlap agrees with the PDF parser in all 576 cells."),
    "reconciliation_2023_pdf_vs_xlsx.csv": (
        "REAL", "DTS 2024 state PDFs (our parser) vs DTS 2023 state XLSX (published)",
        "Cell-by-cell validation of the PDF parser against an independent machine-readable "
        "publication of the same 2023 figures: 592 cells, 0 disagreements."),
    "district_homestay_accommodation_2020_2022.csv": (
        "REAL", "GDP by Administrative District 2015-2020 (doc 11782), Table 72",
        "Registered homestay clusters and accommodation premises for 156 administrative "
        "districts, 2020-2022. The only district-level tourism statistic found in DOSM's "
        "catalogue. District sums reconcile exactly to the printed state totals."),
    "state_quarterly_visitors_2025_MODELLED.csv": (
        "DERIVED", "state annual visitors (DTS 2025 Table 9) x national quarterly share "
                   "(DTS bulletins)",
        "MODELLED quarterly visitors per state. DOSM publishes no state-level quarterly "
        "tourism figures; this assumes every state follows the national seasonal profile "
        "and must never be presented as observed data. See data/GAPS.md section 1."),
    "state_summary_2024.csv": (
        "REAL+DERIVED", "join of the above with population_state, hh_income*, hh_access_amenities",
        "One row per state. Ratio columns (visitors_per_capita, visitors_per_room, "
        "beach_room_share, income_gap_pct, population-weighted amenities) are DERIVED "
        "arithmetic on REAL inputs; all other columns are read directly from source."),
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    man = json.load(open(MANIFEST, encoding="utf-8")) if os.path.exists(MANIFEST) \
        else {"files": []}
    files = {f.get("savedAs"): f for f in man.get("files", [])}

    # --- raw OpenDOSM CSVs ---------------------------------------------------
    for name, (did, title, url) in OPENDOSM.items():
        p = os.path.join(ROOT, "data", "raw", "opendosm", name)
        if not os.path.exists(p):
            print(f"  MISSING raw file: {name}")
            continue
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        files[rel] = {
            "dataset_id": did, "dosm_release_name": title, "savedAs": rel,
            "sourceUrl": url, "resolvedFileUrl": url,
            "api_url": f"https://api.data.gov.my/data-catalogue?id={did}",
            "catalogue_page": f"https://open.dosm.gov.my/data-catalogue/{did}",
            "bytes": os.path.getsize(p), "sha256": sha(p), "retrieved": NOW,
            "publisher": "Department of Statistics Malaysia (DOSM)",
            "licence": DOSM_LICENCE, "status": "REAL",
        }

    # --- OpenDOSM tourism workbooks (storage.dosm.gov.my, machine-readable) --
    tdir = os.path.join(ROOT, "data", "raw", "opendosm-tourism")
    for name in sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []:
        if not name.endswith(".xlsx"):
            continue
        p = os.path.join(tdir, name)
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        url = f"https://storage.dosm.gov.my/tourism/{name}"
        stem = name[:-5]
        if stem == "tourism_domestic_2025":
            title = "Domestic Tourism Survey 2025 (Malaysia)"
            pubid = "tourism_domestic_annual_2025"
        else:
            st = stem.rsplit("_", 1)[-1]
            title = f"Domestic Tourism Survey 2023 -- {st}"
            pubid = "tourism_domestic_state_2023"
        files[rel] = {
            "savedAs": rel, "dosm_release_name": title,
            "opendosm_publication_id": pubid,
            "sourceUrl": f"https://open.dosm.gov.my/publications/{pubid}",
            "resolvedFileUrl": url, "bytes": os.path.getsize(p), "sha256": sha(p),
            "retrieved": NOW, "publisher": "Department of Statistics Malaysia (DOSM)",
            "licence": DOSM_LICENCE, "status": "REAL",
        }

    # --- geospatial boundaries from the official DOSM open-data repo ---------
    for name in ("administrative_1_state.geojson", "administrative_2_district.geojson",
                 "state_district.csv"):
        p = os.path.join(ROOT, "data", "raw", "geodata", name)
        if not os.path.exists(p):
            continue
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        url = ("https://raw.githubusercontent.com/dosm-malaysia/data-open/main/"
               f"datasets/geodata/{name}")
        files[rel] = {
            "savedAs": rel, "dosm_release_name": f"DOSM open geodata: {name}",
            "sourceUrl": "https://github.com/dosm-malaysia/data-open",
            "resolvedFileUrl": url, "bytes": os.path.getsize(p), "sha256": sha(p),
            "retrieved": NOW, "publisher": "Department of Statistics Malaysia (DOSM)",
            "licence": DOSM_LICENCE, "status": "REAL",
        }

    # --- DTS 2024 state PDFs already on disk from the earlier session --------
    prev = os.path.join(ROOT, "dosm-tourism-data", "2024-states", "manifest.json")
    if os.path.exists(prev):
        old = json.load(open(prev, encoding="utf-8"))
        for f in old.get("files", []):
            rel = f"dosm-tourism-data/2024-states/{f['savedAs']}"
            if not os.path.exists(os.path.join(ROOT, *rel.split("/"))):
                continue
            files[rel] = {
                "release_document_id": f.get("docId", ""),
                "dosm_release_name": f"Domestic Tourism Survey 2024 -- {f['savedAs']}",
                "release_date": "18 September 2025", "savedAs": rel,
                "sourceUrl": f.get("sourceUrl", ""),
                "resolvedFileUrl": f.get("resolvedFileUrl", ""),
                "serverFilename": f.get("serverFilename", ""),
                "bytes": f.get("bytes", 0), "retrieved": old.get("generated", ""),
                "publisher": "Department of Statistics Malaysia (DOSM)",
                "licence": DOSM_LICENCE, "status": "REAL",
            }

    # --- processed outputs ---------------------------------------------------
    for name, (status, src, desc) in PROCESSED.items():
        p = os.path.join(ROOT, "data", "processed", name)
        if not os.path.exists(p):
            print(f"  MISSING processed file: {name}")
            continue
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        with open(p, encoding="utf-8") as f:
            n = sum(1 for _ in f) - 1
        files[rel] = {
            "savedAs": rel, "derived_from": src, "description": desc,
            "rows": n, "bytes": os.path.getsize(p), "sha256": sha(p),
            "generated": NOW,
            "publisher": "Department of Statistics Malaysia (DOSM), extracted by this project",
            "licence": DOSM_LICENCE, "status": status,
        }

    out = {
        "project": "DOSM Datathon 2026 -- sustainable domestic tourism load-balancer",
        "generated": NOW,
        "status_legend": {
            "REAL": "value read directly from an official Malaysian publication or dataset",
            "DERIVED": "arithmetic computed from REAL values; formula recorded in derived_from",
            "MISSING": "no Malaysian official source found; see data/GAPS.md",
        },
        "files": sorted(files.values(), key=lambda f: f["savedAs"]),
    }
    json.dump(out, open(MANIFEST, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    n = len(out["files"])
    tot = sum(f.get("bytes", 0) for f in out["files"])
    print(f"manifest: {n} files, {tot/1e6:.1f} MB -> {os.path.relpath(MANIFEST, ROOT)}")


if __name__ == "__main__":
    main()
