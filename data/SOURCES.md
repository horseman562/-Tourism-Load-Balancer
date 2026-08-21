# Data sources — DOSM Datathon 2026, sustainable domestic tourism

Every figure used by this project traces to one of the sources below. All are
open, publicly accessible, and published **within Malaysia**. No foreign source
(World Bank, UN, UNWTO) is used as an analytical base.

Machine-readable provenance for every individual file — source URL, retrieval
timestamp, SHA-256, licence and REAL/DERIVED status — is in
[`data/manifest.json`](manifest.json). Fields that could **not** be sourced are
listed in [`GAPS.md`](GAPS.md).

**Licence for all DOSM / data.gov.my material:** Open Data Terms of Use,
<https://www.data.gov.my/terms-of-use> — free to use and redistribute with
attribution to the Department of Statistics Malaysia.

Retrieved: 16 August 2026.

---

## 1. Primary tourism source — DOSM Domestic Tourism Survey (DTS)

The DTS is conducted following UNWTO guidelines and the *International
Recommendations for Tourism Statistics 2008* (IRTS 2008), as stated in each
report's preface.

| # | Release | Published | Coverage used | Doc ID |
|---|---|---|---|---|
| 1.1 | **Domestic Tourism Survey 2024, by State** — 16 separate state reports (81 pp. each) | 18 Sep 2025 | Tables 1, 7, 12, 13, 14, 15 | 15985–16005 |
| 1.2 | **Domestic Tourism Survey 2025 (Malaysia)** | 16 Jun 2026 | Tables 1, 9, 10 | 19783 |
| 1.3 | **Performance of Domestic Tourism, Q2 2025** | 18 Sep 2025 | national quarterly visitors/tourists | 16024 |
| 1.4 | **Performance of Domestic Tourism, Q3 2025** | 18 Dec 2025 | national quarterly visitors/tourists | 17756 |
| 1.5 | **Bulletin of Domestic Tourism Survey, Q4 2025** | 17 Mar 2026 | national quarterly + hotel occupancy by location | 17778 |
| 1.6 | **Bulletin of Domestic Tourism Survey 2026** | 24 Jun 2026 | national quarterly | 19838 |
| 1.7 | **Tourism Satellite Account 2024** | 12 Sep 2025 | context / tourism GDP | 15861 |
| 1.8 | **Tourism Satellite Account 2023** | 12 Sep 2024 | context / tourism GDP | 11181 |
| 1.9 | **Regional Tourism Satellite Account, Sabah 2024** | 16 Dec 2025 | only sub-national TSA DOSM publishes | 17173 |
| 1.10 | **Regional Tourism Satellite Account, Sabah 2023** | 18 Dec 2024 | comparison year | 12718 |
| 1.11 | **Publication on Domestic Tourism Malaysia 2022** | 26 Jun 2023 | historical | 4886 |

Citation form: Department of Statistics Malaysia (2025). *Domestic Tourism
Survey 2024: Selangor*. Putrajaya: DOSM.

Retrieval pattern: `https://www.dosm.gov.my/portal-main/release-document-log?release_document_id=<ID>`
issues a 302 to the actual file under `/uploads/release-content/`.

### Third-party data republished inside the DTS reports

* **National Property Information Centre (NAPIC)** — Tables 14 and 15 of every
  DTS state report (hotels and rooms by star rating and by location) are
  credited to NAPIC, not to DOSM. Cite NAPIC as the originator.
* **Ministry of Transport Malaysia (MOT)** — domestic airport arrivals, used as
  a supplementary indicator in the quarterly bulletins.
* **DOSM Quarterly Survey of Services (QSS)** — hotel occupancy rates by star
  rating and by location in the quarterly bulletins.

---

## 2. OpenDOSM / data.gov.my machine-readable catalogue

Downloaded directly as CSV; each also has a JSON API endpoint
`https://api.data.gov.my/data-catalogue?id=<id>` and a catalogue page
`https://open.dosm.gov.my/data-catalogue/<id>`.

| Dataset id | Title | Used for |
|---|---|---|
| `population_state` | Population Table: States | `population_thousands` |
| `population_district` | Population Table: Administrative Districts | district weights for amenities |
| `hh_income` | Household Income (Malaysia) | national median, denominator of `income_gap_pct` |
| `hh_income_state` | Household Income by State | `income_gap_pct` |
| `hh_income_district` | Household Income by Administrative District | district-level extension |
| `hh_inequality_state` | Income Inequality by State | equity dimension |
| `hh_poverty_state` | Poverty by State | equity dimension |
| `hh_access_amenities` | Access to Basic Amenities by State & District | `amenities_access_pct` (**replaces an invented column**) |
| `water_access` | Access to Treated Water by State & Strata | readiness |
| `water_pollution_basin` | River Basin Pollution Monitoring | SDG 14 (see caveat in GAPS.md) |
| `fish_landings` | Monthly Landings of Marine Fish by State | SDG 14, monthly, by state and coast |
| `gdp_state_real_supply` | Annual Real GDP by State & Economic Sector | economic weight of tourism-linked sectors |

## 3. Environment and district publications (SDG 14 and district granularity)

| # | Release | Published | Coverage used | Doc ID |
|---|---|---|---|---|
| 3.1 | **Compendium of Environment Statistics, Malaysia 2025** | 30 Dec 2025 | Tables 1.11, 1.16d, 1.20, 1.36, 1.37, 1.38, 2.24, 4.15 | 18503 |
| 3.2 | **Environment Statistics by State 2025** — 12 state volumes + Wilayah Persekutuan | 31 Dec 2025 | state-level detail incl. gazetted marine parks island by island | 18154–18262 |
| 3.3 | **GDP by Administrative District, 2015–2020** | 2 Nov 2024 | Table 72 — homestay clusters and accommodation premises by district | 11782 |
| 3.4 | **My Local Stats (Malaysia, State & Administrative District) 2024** | 24 Nov 2025 | district compendium | 18191 |

Note: DOSM published **no 2025 state Environment Statistics volume for Johor or
Sabah**. The Malaysia compendium (3.1) covers all states and is therefore the
source used for every SDG 14 series.

Originating agencies for the SDG 14 measurements — cite these, not DOSM:
**Department of Environment** (Marine Water Quality Index), **Department of
Irrigation and Drainage** (coastal length, coastal erosion), **Department of
Fisheries** (marine fish landings), **Department of Marine Park** (gazetted
marine park areas and species counts).

## 4. Geospatial boundaries

From the official DOSM open-data repository
<https://github.com/dosm-malaysia/data-open> (`datasets/geodata/`):

* `administrative_1_state.geojson` — 16 state polygons. This is the file the
  dashboard already ships as `dashboard/geo_state.json`.
* `administrative_2_district.geojson` — district polygons.
* `state_district.csv` — the state↔district lookup.

**State naming is normalised to this geodata's spelling** throughout:
`Pulau Pinang` (not Penang), `W.P. Kuala Lumpur`, `W.P. Labuan`,
`W.P. Putrajaya`.

## 5. Indexes produced by this project

Not sources in themselves, but the searchable record of what DOSM publishes:

* `data/index/dosm_publications.csv` — all 3,065 entries of the DOSM
  publication portal (307 pages, crawled 16 Aug 2026, 0 failed pages).
* `data/index/datasets.csv` — 487 rows: 183 OpenDOSM dataset ids, 290
  data.gov.my ids, 14 `data-open` repo files.
* `data/index/resolved_docs.csv` — resolved file URL and live/dead HTTP status
  per document id.

---

## Verification performed

The extraction was checked against DOSM's own published aggregates rather than
assumed correct:

1. **National spend totals reproduce exactly.** Summing the extracted per-state
   shopping and F&B receipts gives RM 39.9 billion and RM 17.3 billion — the
   figures DOSM states in the 18 September 2025 press release.
2. **Per-state spot checks match the press release** for KL, Selangor, Sarawak
   (shopping) and Selangor, KL, Perak (F&B).
3. **Visitor-weighted ALOS = 2.48 nights** against DOSM's published national
   average of 2.49.
4. **Two independent DOSM publications agree.** The 2018–2024 visitor series
   read out of the 16 state reports (Table 1) matches the same series in the
   national 2025 report (Table 9) to within 1 thousand visitors in 2 of 112
   cells, and exactly elsewhere.
5. **State panel reconciles to the national total** for all 8 years 2018–2025.
6. **Table internals balance**: receipts components sum to their subtotals
   (max discrepancy RM 2 thousand, i.e. print rounding); hotel star-rating and
   location breakdowns each sum to the printed total exactly; income-class
   shares sum to 100.0 for every state.
7. **The origin–destination matrix reconciles row-wise** — every origin row sums
   to its own printed Malaysia total within 0.2 thousand, confirming no column
   misalignment during extraction.
8. **A third independent source agrees.** The Sabah hotel and room counts read
   from the DTS Sabah state report match the Regional Tourism Satellite Account
   Sabah 2024 (Tables 24/25) in **every cell**, star rating and location alike.
9. **SDG 14 tables match their printed totals exactly** — coastal length sums to
   8,840.0 km, eroding coastline to 1,347.6 km, and the 2024 marine water quality
   station counts to E103 / G22 / M63 / P0.
10. **District tourism sums to state totals.** In the district homestay table,
    all 12 states that have district rows reconcile exactly to DOSM's printed
    state figure; the other four are published undivided.

### 11. The PDF parser tested against an independent machine-readable source

The strongest check available, and the one that matters most: our 2023 per-state
figures were produced by our own regex parser reading the DTS **2024** state
PDFs. DOSM separately publishes those same 2023 figures as **XLSX** in the DTS
2023 state edition. The two share no code path, no file format and no extraction
method.

| Comparison | Cells | Disagreements |
|---|---|---|
| Table 1 key statistics, 2023 | 96 | **0** |
| Table 7 receipts by component (values + shares), 2023 | 320 | **0** |
| Table 13 monthly household income class, 2023 | 80 | **0** |
| Table 12 accommodation type, 2023 | 96 | **0** |
| Table 1 key statistics, full 2018–2023 overlap | 576 | **0** |
| **Total** | **1,168** | **0** |

The XLSX carries full float precision and the PDF prints rounded values, so each
comparison rounds the XLSX figure to the PDF's printed precision first; 465
distinct values are involved and no cell is null, so the result is not vacuous.
Output: `data/processed/reconciliation_2023_pdf_vs_xlsx.csv`.

**Scope of this check, stated precisely.** It validates the parser against the
**2023** column of the 2024 PDFs. The **2024** column has no independent
publication to check against and is therefore *not* externally verified. The
inference is that the same parser reading the same rows of the same tables is
unlikely to be correct for one column and wrong for the adjacent one — a
reasonable inference, but an inference, not a measurement. The 2024 figures
remain supported only by internal consistency (items 1–8 above).
