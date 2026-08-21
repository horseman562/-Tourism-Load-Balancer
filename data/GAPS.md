# Gaps — what could not be sourced, and what was tried

Competition rules prohibit fabricated or simulated data. This file records every
field that has **no** Malaysian official source, so that no placeholder value
survives silently into the submission.

Status as of 16 August 2026.

---

## RESOLVED — placeholder columns now backed by a real source

| Placeholder column | Status | Real source |
|---|---|---|
| `visitors_2023_millions` | **REAL** | DTS 2024 state reports, Table 1 |
| `visitors_2024_millions` | **REAL** | DTS 2024 state reports, Table 1; independently confirmed by DTS 2025 Table 9 |
| `visitor_growth_pct` | **DERIVED** | computed from the two REAL columns above |
| `population_thousands` | **REAL** | `population_state`, 2024 |
| `income_gap_pct` | **DERIVED** | `hh_income_state` vs national median from `hh_income`, 2024 |
| `income_bracket` | **REAL** | DTS 2024 state reports, Table 13 — modal monthly household income class |
| `shopping_spend_rm_m` | **REAL** | DTS 2024 state reports, Table 7 |
| `fnb_spend_rm_m` | **REAL** | DTS 2024 state reports, Table 7 |
| `alos_nights` | **REAL** | DTS 2024 state reports, Table 1 |
| `amenities_access_pct` | **REAL** (was invented) | see below |

### `amenities_access_pct` — the invented column

Previously flagged as having no real source. It does have one:
**`hh_access_amenities`** ("Access to Basic Amenities by State & District",
OpenDOSM, 2024) gives the proportion of households with piped water,
sanitation and electricity, **at district level for all 160 districts**.

Two caveats that affect how it should be used:

* **At state level it is nearly saturated** and therefore barely
  discriminating — piped-water access is 98–100% in 12 of 16 states. Only
  Kelantan (72.3%), Sabah (88.4%), Sarawak (92.7%) and Pahang (98.6%) sit
  meaningfully below.
* **At district level it has real spread** — 25.0% (Bukit Mabong, Sarawak) to
  100%. If the project wants amenities to carry analytical weight, it has to be
  used at district granularity, not state.

State values in `state_summary_2024.csv` are **population-weighted district
means** (weights from `population_district`, 2024), not DOSM-published state
figures — DOSM's own 2024 state rows report only electricity. This makes the
column DERIVED, and it is labelled as such in `manifest.json`.

**A better capacity metric is now available:** hotels and rooms per state from
NAPIC (DTS Tables 14/15), giving `visitors_per_room_2024`, which ranges from 265
(W.P. Labuan) to 2,510 (Perlis) — a genuine, well-spread pressure measure.

---

## UNRESOLVED — no Malaysian official source found

### 1. Monthly or quarterly visitors **by state** — MISSING

This is the most consequential gap. The whole load-balancer concept rests on
peak-load redistribution, and DOSM does not publish sub-annual tourism figures
below the national level.

What exists: national quarterly domestic visitors and tourists
(`dts_national_quarterly.csv`, Q1–Q4 2025).

What was tried:
* All 16 DTS 2024 state reports — annual only; no monthly or quarterly table.
* DTS 2025 Malaysia report — annual by state (Table 9), quarterly only nationally.
* All four quarterly DTS bulletins held — Malaysia-level headline figures plus
  national indicator panels (airport arrivals, fuel retail sales, theme park,
  accommodation); no state table.
* OpenDOSM and data.gov.my catalogues — no tourism dataset at all (see §4).
* `api.data.gov.my` probed for `tourism_domestic`, `tourism_state`,
  `hotel_occupancy`, `tourism_domestic_state`, `domestic_tourism`,
  `tourism_satellite`, `tourism_expenditure`, `dts_state` — all return a JSON
  404 "does not exist".

**Resolution taken:** `data/processed/state_quarterly_visitors_2025_MODELLED.csv`
applies the real national quarterly shares to the real state annual totals. Every
row carries `basis = MODELLED` plus the method string. It is **quarterly, not
monthly** — interpolating quarters into months would stack a second invention on
top of the first. `dashboard/PLACEHOLDER_monthly_2024.csv` is superseded and
should be deleted; `app.py` still reads it and needs a small change to consume
quarters.

**A finding that undercuts the premise, and should not be buried:** the 2025
national quarterly shares are **Q1 24.0%, Q2 25.4%, Q3 25.0%, Q4 25.5%** —
essentially *no* seasonality. Malaysian domestic tourism has no national peak
season worth redistributing in time.

The over-tourism signal in this data is **spatial and structural**, not temporal:

* **concentration** — Selangor and W.P. Kuala Lumpur together take 24% of all
  domestic visitors, and `visitors_per_room_2024` spans 265 (W.P. Labuan) to
  2,510 (Perlis);
* **accommodation type** — beach hotels ran at **89.0%** occupancy in Q4 2025
  against 61.1% hill and 64.3% town (DTS Q4 2025 bulletin, DOSM Quarterly Survey
  of Services). That is the real load imbalance, and it is a coastal one, which
  lines the project up with SDG 14 rather than a seasonal story.

The pitch should lead with spatial redistribution and coastal pressure rather
than peak-load timing.

Nearest genuine monthly proxies, all real and by state:
* `fish_landings` — monthly, by state and by coast, 2018–2023.
* `air_pollution` — monthly, by state.
* `electricity_consumption` — monthly.
* Quarterly hotel occupancy by *location type* (town / hill / beach) from the
  DTS bulletins — national, but it does establish that beach accommodation runs
  at ~89% occupancy against ~61–64% for town and hill, which is direct evidence
  of coastal over-load.

### 2. District-level tourism — PARTIAL (supply counted, demand ranked)

**Corrected 16 Aug 2026.** An earlier version said district-level demand "does
not exist". That is withdrawn — DTS 2025 sheet 8B publishes it as a **rank**.

**Demand exists as an ordering, not a magnitude.** *Table 8B — Top Five
Administrative Districts Most Visited by Domestic Visitors, 2025* names the five
most-visited districts for each of 12 states (Perlis, W.P. Kuala Lumpur, W.P.
Labuan and W.P. Putrajaya have no administrative districts). Extracted to
`data/processed/dts_top_districts_visited_2025.csv` — 58 rows. Sheet 8A does the
same for 80 named destinations across all 16 states.

No visitor *count* is published per district, so this can order and name
districts but cannot size them. Anything requiring a magnitude still stops at
state level.

**It is a snapshot, not a trend.** Sheet 8B is **new in the 2025 edition** — no
district ranking appears in any of the 16 DTS 2023 state workbooks, nor in the
2024 state PDFs. A two-year district comparison is therefore impossible until the
2026 edition.

What *does* run multi-year is the top-five **destination** ranking (named
attractions, not districts): 2022 and 2023 in the state workbooks (Jadual 9,
split by visitors and tourists), 2024 in the state PDFs as a narrative Exhibit 7
rather than a table, and 2025 in sheet 8A. That gives four consecutive years of
destination movement if we want to show change over time.

**Supply is available by district.** One table was found in the whole
3,065-publication catalogue: *GDP by Administrative District, 2015–2020*
(doc 11782), **Table 72 — registered homestay clusters and accommodation
premises by administrative district, 2020–2022**. Extracted to
`data/processed/district_homestay_accommodation_2020_2022.csv`: **156 districts**
across all 16 states. District sums reconcile exactly to DOSM's printed state
totals for all 12 states that have district rows; Perlis, W.P. Kuala Lumpur,
W.P. Labuan and W.P. Putrajaya are reported undivided.

Caveats: it ends in 2022, and the 2022 premises column is `n.a` throughout
(flagged as `not_available`, not zero, in the output).

Also available at district level (non-tourism): `population_district`,
`hh_income_district`, `hh_poverty_district`, `hh_inequality_district`,
`hh_access_amenities`, `crops_district_area`, `crops_district_production`, GDP by
district (same publication), and `administrative_2_district.geojson` boundaries.

**The two sides join.** `data/processed/district_demand_supply_2025.csv` puts the
demand rank next to the supply count, population and amenities for all 58
top-five districts — all 58 matched across all four sources with no unresolved
names (`scripts/district_names.py` normalises the four different spellings DOSM
uses, e.g. `Larut & Matang` / `Larut dan Matang` / `Larut Dan Matang`).

This supports claims of the shape *"district X is among the five most-visited in
its state yet holds only N accommodation premises"* — subject to the two limits
below, both of which are carried as columns in the output file itself.

#### Limit 1 — vintage mismatch: 2025 demand against 2021 supply

Demand rank is **2025**. Supply is **2021** (Table 72 runs 2020–2022 but its 2022
premises column is `n.a` throughout). That is a four-year gap on two halves of
one claim, and it is the most likely thing for a reviewer to attack under QLT2
("accurate, current").

**No district-level accommodation count exists for 2023, 2024 or 2025.** Checked:

| Candidate | Result |
|---|---|
| My Local Stats 2024, Table 10.9 (MOTAC) | **state only**, 2022–2024 — not district |
| GDP by Administrative District | no edition newer than the 2015–2020 volume |
| Economic Census 2023 Accommodation Services (doc 10623) | dead link, and 2022 reference year regardless |
| DTS 2023 state workbooks | no district tables at all |
| Publication index, district titles since 2024 | 12 hits, none tourism-supply |

**Mitigation, and it is a mitigation not a fix.** Table 10.9 is the *same MOTAC
series* at state level and runs to 2024, so the drift over the gap can be
measured directly (`motac_accommodation_by_state_2022_2024.csv`):

* national premises **5,253 (2021) → 5,277 (2024) = +0.5%**
* median absolute state change **6.2%**; only 2 of 16 states moved more than 15%
* **Spearman rank correlation of state supply, 2021 vs 2024 = 0.977** — the
  ordering of states by supply is essentially unchanged

So the 2021 district split is probably still close to right. Where it is most
likely to be wrong is named per row: `state_supply_change_2021_2024_pct`.

**This matters for our own headline example.** Seberang Perai Selatan (rank 5,
1 premise) sits in **Pulau Pinang, the state with the largest drift at +25.3%** —
it is the least reliable case in the set, not the best. The Kelantan examples
(Pasir Mas and Pasir Puteh, rank 3 and 4, 5 premises each, state drift +6.2%) are
the ones safe to lead with.

#### Limit 2 — rank is ordinal

Sheet 8B gives **position within a state, not a quantity**. Therefore:

* rank 3 in Kelantan is **not** comparable to rank 3 in Melaka;
* no demand-to-supply ratio can be computed — there is no demand magnitude;
* the gap between rank 1 and rank 2 has no size.

The output carries `demand_measure` on every row stating this, so it cannot be
mistaken downstream for a count.

**Consequence:** the pitch can honestly keep "districts" — naming and ordering
real districts on the demand side, and counting on the supply side. Only
per-district *magnitudes* remain unavailable, and the report should say so.

### 3. Marine park and island visitor numbers — MISSING from DOSM

Searched the full 3,065-entry publication index for `marine park`, `taman laut`,
`island`, `coastal`, `pesisir`, `maritim`: zero tourism-related hits (the only
`pulau` matches are constituency names such as Pulau Tikus).

Not yet checked, and outside DOSM: Department of Marine Park Malaysia, Tourism
Malaysia's MyTourismData portal, and state park authorities. All are Malaysian
and would satisfy the origin rule, but none carries the OpenDOSM/eStatistik/
StatsDW bonus.

**Partially mitigated.** Two DOSM sources give marine-park *supply* even though
no source gives marine-park *visitors*:

* **Gazetted marine park area**, island by island, with fish/coral/seagrass
  species counts — Compendium of Environment Statistics 2025, Table 1.16d, and
  Table 1.12 of each state Environment Statistics volume. For Terengganu alone
  this names 11 gazetted islands with hectares (Pulau Redang 12,750 ha, Pulau
  Perhentian Besar 9,121 ha, …).
* **Named visitor destinations for Sabah** — RTSA Sabah 2024, Table 15, lists the
  top five destinations for domestic visitors and tourists each year 2020–2024,
  including *Tunku Abdul Rahman Marine Park*, *Pulau Bohey Dulang* and *Pantai
  Tanjung Aru*. This is a **ranking with no counts**, and Sabah is the only state
  DOSM publishes it for, so it can support a narrative but cannot feed a model.

### 4. Tourism in the machine-readable catalogue — CONFIRMED ABSENT

Re-verified this session, not carried over: **all 183 OpenDOSM dataset ids and
all 290 data.gov.my ids were extracted and keyword-searched** for `touris`,
`travel`, `hotel`, `accommodat`, `visitor`, `lodging`, `excursion`, `holiday`,
`recreat`, `leisure`, `museum`, `park`, `herit`, `beach`, `island`, `marine`,
`coastal`. **Zero tourism datasets.** The single `marine` hit is `fish_landings`.

Tourism figures therefore exist only inside PDF publications, which is why PDF
table extraction is a core task of this project rather than a fallback.

### 5. Coastal / marine water quality — RESOLVED

Previously listed as missing. It exists, in the **Compendium of Environment
Statistics, Malaysia 2025** (doc 18503, published 30 December 2025).

`water_pollution_basin` from OpenDOSM remains unsuitable — it is **river basin**
monitoring, reported as national proportions by class, and it **ends in 2021**.
It should not be used for a coastal claim.

What replaced it, all state-level and extracted to `data/processed/`:

| File | Content | Originating agency |
|---|---|---|
| `sdg14_marine_water_quality_2020_2024.csv` | Marine Water Quality Index station counts by state × area (coastal / estuary / island) × year × category (excellent/good/moderate/poor) | Department of Environment |
| `sdg14_coastal_length.csv` | Coastal length by state, sums to the published 8,840.0 km | Dept. of Irrigation and Drainage |
| `sdg14_coastal_erosion_2024.csv` | Eroding coastline by state and severity, sums to the published 1,347.6 km | Dept. of Irrigation and Drainage |
| `sdg14_mangrove_area.csv` | Mangrove forest hectares by state, 2019–2022 | DOSM |
| `sdg14_marine_fish_landings.csv` | Marine fish landings by state, 2020–2024 | DOSM / Dept. of Fisheries |

Each was validated against the total row DOSM prints in the same table, and all
matched exactly.

Two caveats:

* **Estuaries are the polluted ones.** In 2024, coastal stations were 103
  excellent / 22 good / 63 moderate / 0 poor and island stations 61/3/31/0, but
  estuary stations were 7/14/59/**5 poor** — the only "poor" readings in the
  country. A coastal-pressure story should be careful to say *estuary*, not
  *beach*, where that is what the data shows.
* **DOSM published no 2025 state Environment Statistics volume for Johor or
  Sabah** — 12 states plus a Wilayah Persekutuan volume only. The compendium
  covers all states, which is why it, and not the state volumes, is the source
  used here.

### 6. Dead links — a delivery-path problem, not a purge

**Corrected 16 Aug 2026.** An earlier version of this file said the pre-2025
tourism releases "have been purged". That is wrong and the claim is withdrawn.

What is true: of 52 unique tourism document ids resolved through
`dosm.gov.my/portal-main/release-document-log`, **27 return 404** — including all
16 DTS 2023 state reports, all 16 DTS 2022 state reports, the Q3 2023 / Q4 2023 /
Q1 2024 bulletins, TSA 2022 and RTSA Sabah 2022.

What is also true: **the same publications are alive on a different host.**
OpenDOSM serves them from `storage.dosm.gov.my`, and all 16 DTS 2023 state
editions return HTTP 200 there — as **XLSX (~381 KB each)** and PDF (8–15 MB):

```
https://storage.dosm.gov.my/tourism/tourism_domestic_2023_<state>.xlsx
https://storage.dosm.gov.my/tourism/tourism_domestic_2023_<state>.pdf
```

(`<state>` = johor, kedah, kelantan, melaka, negerisembilan, pahang, perak,
perlis, pulaupinang, sabah, sarawak, selangor, terengganu, wpkualalumpur,
wplabuan, wpputrajaya. All 16 HEAD-checked 200 on 16 Aug 2026.)

The 2022 state editions are likewise listed under OpenDOSM publication id
`tourism_domestic_state_2022`.

**Two lessons, both worth keeping:**

1. A 404 on the `dosm.gov.my` release-document-log path says nothing about
   whether the publication is available. **Check `storage.dosm.gov.my` via the
   OpenDOSM publications index before declaring anything lost.**
2. The XLSX route is strictly better than the PDF route — machine-readable,
   ~40× smaller, and no table extraction required.

Discovery path for this index (no public REST API exists; these are Next.js data
routes, and the build id changes on redeploy):

```
https://open.dosm.gov.my/publications?pub_type=tourism
https://open.dosm.gov.my/_next/data/<buildId>/en-GB/publications.json?pub_type=tourism
https://open.dosm.gov.my/_next/data/<buildId>/en-GB/publications/<publication_id>.json
```

**Consequence:** 2023 per-state detail (receipts by component, ALOS, income
class, hotels/rooms) is **recoverable in machine-readable form** and no longer
depends on the figures embedded in the 2024 reports. Not yet downloaded.

---

## Constructed scores, not data

`saturation_score` and `readiness_score` in the placeholder file are model
outputs, not observations. They have no source and should not have one — but
their formulas must be stated in the report and computed only from REAL columns
(e.g. visitors per capita, visitors per room, ALOS, amenities, income gap).
Until that formula is fixed they remain **MISSING** in `manifest.json`.
