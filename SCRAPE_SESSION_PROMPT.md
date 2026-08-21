# Data-acquisition session — DOSM Datathon 2026

Paste everything below the line into a fresh Claude Code session started in
`D:\2025_project_portfolio\dosm`.

---

## MISSION

Build a complete, citable index of DOSM's published data, then acquire the subset
needed to replace the placeholder values in `dashboard/PLACEHOLDER_mockup_data.csv`
and `dashboard/PLACEHOLDER_monthly_2024.csv` with real Malaysian official statistics.

Project: a DOSM Datathon 2026 entry on **sustainable domestic tourism** — a
"tourism load-balancer" that flags overcrowded states and recommends redirecting
demand toward under-visited, ready ones. Theme: ML/AI for sustainable tourism.
In-scope SDGs: **8, 9, 12, 14** (note: 11, 13 and 15 are *not* in scope).

Competition rules that constrain this work:
- Data must be **open and publicly accessible**. Fabricated or simulated data is
  **prohibited** and is grounds for disqualification.
- **Raw data must originate from within Malaysia.** Foreign sources (World Bank, UN)
  may only support a statement, never serve as the analytical base.
- Extra marks for **OpenDOSM / eStatistik / StatsDW** specifically.
- Every dataset, library and pre-trained model must be **cited** in the report.

Do not invent a single number. If a figure cannot be sourced, record it as missing.

---

## ALREADY ESTABLISHED — do not re-derive

Verified in a previous session. Trust these, but re-check anything that looks stale.

### Access facts

1. **`robots.txt` is `User-agent: * / Disallow:`** — an empty Disallow. Nothing is
   off-limits. That is permission, not licence to hammer the server: keep requests
   sequential with a ~1.5s delay. It is a government host.

2. **The DOSM portal is server-rendered.** Pagination is a plain `?page=N` and every
   document link is present in the raw HTML. **You do not need a browser for
   dosm.gov.my.** `curl` + an HTML parser is sufficient and much faster. Only reach
   for Playwright if you hit something genuinely JS-gated.

3. **TLS quirk, narrower than it looks.** `dosm.gov.my` serves an incomplete
   certificate chain. **`curl` works fine** (own CA bundle). **Node's `fetch` fails**
   with `UNABLE_TO_VERIFY_LEAF_SIGNATURE`, as does Python `requests` in some setups.
   Chromium works via AIA fetching. If a client fails on dosm.gov.my, it is this —
   switch client rather than debugging the network.

4. **There is no sitemap.** `/sitemap.xml` and `/sitemap_index.xml` both 404.
   Enumeration must go through the paginated indexes.

### Content gotchas

5. **`portal-main/release-document-log?release_document_id=NNNNN` is a 302 logger**,
   not a file. It redirects to `/uploads/release-content/file_<timestamp>.pdf` served
   as `application/pdf`. Follow the redirect, or catch the browser download event.
   Server filenames are opaque timestamps and carry no meaning.

6. **Many older release files are gone.** The 2023 Domestic Tourism Survey (States)
   release has **33 of 34 files returning 404** — only doc id 11206 (Johor) resolves.
   That release also vanished from DOSM's own release-archive index, and the Wayback
   Machine never captured the PDFs. **Always HEAD the resolved URL before downloading
   in bulk.** A listed link is not a live link.

7. **DOSM publication PDFs have no extractable text on page 1** (vector cover art).
   The title line sits on **page 2**:
   `SURVEI PELANCONGAN DOMESTIK DOMESTIC TOURISM SURVEY <STATE> <YEAR>`.
   **Page 3 is the publisher's address block and names Putrajaya in every report** —
   a naive state-name scan mislabels the entire corpus as Putrajaya.

8. **State naming differs between sources.** DOSM geodata uses `Pulau Pinang`; some
   datasets use `Penang`. Federal territories are `W.P. Kuala Lumpur`, `W.P. Labuan`,
   `W.P. Putrajaya`. Normalise everything to the geodata spelling.

### Confirmed source inventory

| Source | Scale | Access |
|---|---|---|
| `api.data.gov.my/data-catalogue?id=<id>` | — | Clean JSON. 404 with JSON error for unknown ids. Verified with `hh_income_state`. |
| `open.dosm.gov.my/data-catalogue` | **180 dataset ids** | Full list embedded in the page's `__NEXT_DATA__` script tag. Parse it — no clicking. |
| `data.gov.my/data-catalogue` | **287 dataset ids** (all agencies, superset) | Same `__NEXT_DATA__` pattern. |
| `github.com/dosm-malaysia/data-open` | **16 files, 6.4 MB** (7 csv, 5 geojson, 2 notebooks) | Just clone it. Dirs: `census`, `economy`, `geodata`, `prices`. |
| `dosm.gov.my/portal-main/publication?page=N` | **307 pages × 10 = ~3,070 publications** | Server-rendered, paginated. |
| `dosm.gov.my/portal-main/release-archive/<slug>` | ~29 releases per theme | Server-rendered. |

### The critical finding

**There is no tourism data in OpenDOSM's machine-readable catalogue.** All 180
dataset ids were extracted; none are tourism-related. Every plausible id
(`tourism_domestic`, `tourism_domestic_state`, `tourism_state`, `domestic_tourism`,
`dts_state`, `tourism`, `hotel_occupancy`, `tourism_expenditure`) returns 404.
Population, income, GDP, employment and water-quality datasets **are** available.

**Confirm or overturn this before anything else.** If it holds, the tourism figures
exist only inside PDF publications, and **PDF table extraction becomes a core task**
rather than a fallback. That is a feature, not a problem: most competing teams will
use whatever CSV they can find, and extracting structured data from official
publications lands directly on the QLT3 criterion (combining structured, unstructured
and geospatial data) inside the heaviest-weighted scoring component.

---

## ALREADY ON DISK

```
dosm-tourism-data/2024-states/    19 PDFs — 16 states + infographic, press statement,
                                  stats alert. manifest.json maps each file to its
                                  source URL, doc id and server filename.
dosm-tourism-data/2023-states/    1 PDF (Johor only) + manifest.json recording all
                                  33 dead links with their 404 status.
dashboard/geo_state.json          DOSM state boundaries, 16 features.
```

The 2024 state reports are **81 pages each and carry 2018–2024 time series per
state** — visitor arrivals, trips, receipts, ALOS, and social/demographic profiles.
Very likely the richest available source for the project's core numbers.

---

## PHASE 1 — INDEX EVERYTHING (do this first)

Crawl all **307 pages** of `portal-main/publication?page=N`. For every publication
capture: title, release date, theme/category, `release_document_id`, the resolved
`/uploads/...` URL, and an HTTP status from a HEAD request.

Cost: ~30 MB and roughly 8 minutes at a 1.5s delay. Cheap, and it is the highest-value
artefact of this whole session.

Also harvest, into the same index:
- all 180 OpenDOSM ids + their metadata
- all 287 data.gov.my ids (mark which are DOSM-published)
- the `data-open` repo file list

Write it to `data/index/dosm_publications.csv` and `data/index/datasets.csv`.

**Why this first:** it turns "does DOSM publish X?" from guesswork into a query, and
the HEAD status column would have told us the 2023 tourism release was dead before we
spent time downloading it. Do **not** download PDFs during this phase.

## PHASE 2 — SELECTIVE DOWNLOAD

Query your own index for: tourism, travel, accommodation, hotel, environment, marine,
coastal, water quality, population, household income, employment. Expect on the order
of 50–150 publications, a few GB.

**Do not bulk-download all ~3,070 publications.** At 14–24 MB each that is plausibly
20–30 GB, and the vast majority (CPI, trade, construction) is irrelevant here. QLT2
scores data that is *relevant to the problem statement*; volume earns nothing.

---

## WHAT THE PROJECT NEEDS

Per state, all 16 states/FTs. Current placeholder columns:

| Column | Needed | Notes |
|---|---|---|
| `visitors_2023/2024_millions` | domestic visitor arrivals by state | in the PDFs |
| monthly / quarterly visitors | seasonality | **highest value if it exists.** Over-tourism is seasonal and the whole concept rests on peak-load redistribution. Quarterly DTS releases exist — chase these hard |
| `population_thousands` | `population_state` | confirmed on OpenDOSM |
| `shopping_spend_rm_m`, `fnb_spend_rm_m` | expenditure by component by state | already have real figures for 8 states |
| `alos_nights` | average length of stay | in the PDFs; national avg 2.49 nights |
| `income_bracket` | visitor household income profile | PDF demographic sections |
| `amenities_access_pct` | **currently invented — no real source exists** | find a genuine infrastructure/amenities proxy, or redefine the metric. Flag loudly if nothing fits |
| `income_gap_pct` | `hh_income_state` | confirmed on OpenDOSM |

Also wanted, for **SDG 14 (Life Below Water)** — the differentiating angle, since
SDG 11/13/15 are out of scope:
- marine park / island visitor numbers
- coastal water quality (`water_pollution_basin` exists; Department of Environment
  publishes more)
- **anything district-level.** The project pitch says "districts" but every dataset so
  far is state-level. `population_district` and `hh_income_district` exist — establish
  whether tourism data goes below state level anywhere.

---

## DELIVERABLES

```
data/index/        dosm_publications.csv, datasets.csv   (Phase 1 output)
data/raw/          untouched downloads, original filenames preserved
data/processed/    tidy CSVs, one row per state per period
data/manifest.json every file: source URL, retrieval date, licence, DOSM release
                   name, and REAL vs DERIVED vs MISSING
data/SOURCES.md    citation-ready list for the competition report
data/GAPS.md       every field that could not be sourced, and what was tried
```

`manifest.json` and `SOURCES.md` are not optional — rule 10 requires every dataset to
be cited and documented. `GAPS.md` is what stops placeholder values silently
surviving into the final submission.

---

## HOW TO WORK

1. **Cheapest client first.** API → GitHub raw → `curl` + HTML parse → browser.
   Do not open a browser for something `curl` can fetch.
2. **Verify before scale.** HEAD every file URL. Prove a parser on two files before
   running it over fifty.
3. **Never fabricate a gap.** Missing is missing; write it in `GAPS.md`.
4. **Report before Phase 2.** Show the index summary and the tourism-availability
   finding, then get direction before downloading at scale.

Start with the "no tourism data in OpenDOSM" question, then Phase 1.
