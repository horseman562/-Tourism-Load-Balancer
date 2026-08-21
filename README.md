# Tourism Load-Balancer

**DOSM Datathon 2026 — "Leveraging ML & AI for sustainable tourism in Malaysia"**
SDGs addressed: **8** (decent work & economic growth), **9** (industry, innovation &
infrastructure), **12** (responsible consumption & production), **14** (life below water).

A decision tool that identifies which Malaysian states are carrying more domestic
tourism than their residents can comfortably absorb, and calculates how much of that
demand could realistically move — and to exactly where.

---

## The problem, in one comparison

| | Visitors 2024 | Residents | Visitors per resident |
|---|---|---|---|
| **Johor** | 17.1M | 4,184k | **4.1** |
| **Melaka** | 19.1M | 1,047k | **18.3** |

Almost the same crowd. But Melaka is a quarter the size, so it carries **four times the
load** — on roads, water, waste collection and housing built for one million people.

Malaysia recorded **260.1 million domestic visitor arrivals in 2024, up 21.7%**. Counting
visitors hides this problem entirely. Dividing by the people who live there reveals it.

---

## What the dashboard does

1. **Measures pressure** — visitors per resident for all 16 states and federal
   territories. Range: 4.1 (Johor) to 21.3 (Putrajaya).
2. **Flags the top third** — six territories above 11.65 per resident: Putrajaya,
   Melaka, Negeri Sembilan, Kuala Lumpur, Pahang, Terengganu.
3. **Allocates the excess** — using DOSM's published origin–destination matrix, it
   matches each pressured state to destinations that *already draw the same travellers*,
   then caps the volume twice: by what the target can absorb, and by what is realistically
   achievable.
4. **Goes down to district level** — for each recommended state, which districts inside
   it are most visited, and whether they have the accommodation and water infrastructure
   to host more people.

**Result: 31.3 million visits reallocated across 10 routes — and 4.53 million that
cannot be placed anywhere.**

---

## Four findings worth the jury's attention

**1. There is no tourist season to spread out.**
Quarterly shares for 2025: 24.0 / 25.4 / 25.0 / 25.5%. Q1 2026 continues the pattern —
five straight quarters within 1.5 percentage points. Off-peak promotion is spending
against a problem that does not exist. **The imbalance is spatial, not temporal.**

**2. The pressure sits in a corridor, and Selangor is the hole in it.**
Four of the six most pressured territories form a strip down the west coast. Yet
Selangor, which physically surrounds Kuala Lumpur and Putrajaya, is one of the calmest
states at 4.7 per resident. The strain is concentrated in small territories embedded
beside it — so the unit of action is the territory, not the region.

**3. Domestic tourism is not an affluent activity.**
52% of visitors come from households earning RM1,001–5,000 a month; the largest single
band is RM5,001–10,000 at just 31%. Redirecting demand redistributes *ordinary household
spending*, which is an equity argument as much as a congestion one.

**4. Some destinations need capacity before they need visitors.**
Ranau is the **#2 most-visited district in Sabah** and has **46.5% piped-water coverage**
for 89,000 residents. The dashboard flags it as a *capacity-building target, not a
redirect target*. Sending more visitors there would shift the burden onto residents
rather than relieve it.

---

## Every figure is official Malaysian statistics

No fabricated, simulated or estimated data is used anywhere in the analysis.

| Source | Used for |
|---|---|
| **DOSM Domestic Tourism Survey 2024** (state reports, 18.09.2025) | visitors, receipts by component, length of stay, visitor income class, accommodation type |
| **DOSM Domestic Tourism Survey 2025** (national + workbook) | 2025 state totals, origin–destination matrix, top-5 districts visited |
| **DOSM quarterly DTS bulletins** (Q1 2025 – Q1 2026) | seasonality evidence |
| **NAPIC** (via DOSM publications) | hotels and rooms by state, beachfront share |
| **OpenDOSM / data.gov.my** | population, household income, amenity access, water quality, fish landings |
| **DOSM open geodata** | state boundaries (`administrative_1_state.geojson`) |
| **Dept. of Environment, Dept. of Irrigation & Drainage, Dept. of Fisheries, MOTAC** | SDG-14 indicators and accommodation supply, republished in DOSM compendiums |

**Full provenance:**

- [`data/SOURCES.md`](data/SOURCES.md) — every source with URLs, in five sections, plus
  an 11-item verification log. Credits originating agencies rather than attributing
  everything to DOSM.
- [`data/manifest.json`](data/manifest.json) — 99 files, each with source URL, resolved
  URL, retrieval timestamp, **SHA-256 checksum**, and a REAL / DERIVED status flag.
- [`data/GAPS.md`](data/GAPS.md) — every field that could not be sourced, what was tried,
  and what changed when a gap was later closed.
- [`data/index/`](data/index) — an index of **3,065 DOSM publications** and **487
  machine-readable datasets** built while sourcing this project.

**Raw source files** (321 MB of PDFs and workbooks) are attached to the
[latest Release](../../releases) rather than committed, to keep the repository small.
Everything needed to run the dashboard is in `data/processed/`.

---

## Verification

Tourism figures were extracted from PDF publications, so the extraction itself was
tested rather than trusted:

- **1,168 cells reconciled, zero disagreements.** The 2023 figures parsed from the 2024
  state PDFs were compared cell-by-cell against DOSM's independently published 2023
  machine-readable workbooks — key statistics, receipts by component, income class and
  accommodation type, across all 16 states and 2018–2023.
- **The national headline reproduces.** Summing our 16 independently extracted state
  tables gives 260.126M for 2024 and 213.744M for 2023, against DOSM's published 260.1M
  and 213.7M — agreement to rounding, on a figure we never copied.
- **Two sources agree on 2025.** Our state totals sum to 290.064M; the separately parsed
  quarterly bulletins sum to 290.1M.
- Component sums, origin–destination row totals, district-to-state sums and SDG-14
  indicators all reconcile internally. Details in `data/SOURCES.md`.

---

## How the model works

**Pressure** = visitors ÷ residents. Flagged if in the top third (above 11.65).

**Headroom** = how many more visitors a state could take before reaching the national
median (8.85 per resident).

**Matching** = cosine similarity of origin mixes from the 2025 origin–destination matrix.
Melaka's visitors come from Selangor (38%), Johor (19%) and KL (13%); Johor's come from
Johor (35%), Selangor (20%) and KL (15%) — the same people, so the swap is realistic.

**Two caps, both necessary:**

- *Capacity* — a target cannot exceed the national median intensity.
- *Feasibility* — a route cannot more than **double a journey people already make**.
  Without this, the model proposed quadrupling peninsula-to-Sabah travel: Sabah has
  headroom, but 75% of its tourists are Sabahans and only 20% come from the peninsula.
  Similar origin *shape* is not the same as existing origin *volume*.

Anything that cannot be placed within both caps is reported as unplaceable rather than
quietly recommended.

---

## Honest limitations

- **This is a capacity calculation, not a forecast.** It shows where room exists and
  which pairings are credible. It does not model pricing, marketing, transport,
  elasticity or visitor preference, and nobody is compelled to travel anywhere.
- **District demand is ordinal.** DOSM publishes the top five most-visited districts per
  state as a ranking without counts. We never compute a demand-to-supply ratio and never
  compare ranks across states.
- **District accommodation supply is 2021**, the most recent DOSM publishes, against 2025
  demand. The drift was measured rather than ignored: national supply moved +0.5% and
  state-level Spearman rank correlation is 0.977 over 2021–2024. Every row carries its
  state's drift figure.
- **2025 has state totals but no state detail.** Receipts, length of stay and income class
  are published at state level only up to 2024, so the analysis year is 2024 with 2025
  totals shown alongside.

---

## Running it

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r dashboard/requirements.txt
.venv/Scripts/python.exe -m streamlit run dashboard/app.py
```

Windows users can double-click `dashboard/run_dashboard.bat`.
`dashboard/requirements-lock.txt` holds exact pinned versions if the loose ones drift.

---

## Repository layout

```
dashboard/
  app.py                    the Streamlit dashboard
  geo_state.json            DOSM state boundaries, 16 features
  requirements.txt          runtime dependencies
data/
  processed/                16 analysis-ready CSVs — what the app reads
  index/                    3,065 publications + 487 datasets indexed
  SOURCES.md                citation-ready source list + verification log
  manifest.json             99 files with SHA-256 and provenance
  GAPS.md                   what could not be sourced, and what was tried
scripts/                    crawl, resolve, download, extract, reconcile
NOTES_panel_defence.md      per-panel provenance and challenge/answer notes
```

---

*Built for DOSM Datathon 2026. All statistics © Department of Statistics Malaysia and the
originating agencies credited in `data/SOURCES.md`.*
