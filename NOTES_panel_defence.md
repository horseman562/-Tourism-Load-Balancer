# Panel defence notes — Tourism Load-Balancer

One entry per dashboard element: what it shows, exactly where the number comes from,
how it was verified, why it is useful to the community, and the challenges a judge is
likely to raise with the answers.

Built up panel by panel. Last updated: 2026-08-16.

---

## KPI 1 — "Total 2024 visitors · 260.1M · ▲21.7% vs 2023"

### What the card is for

The scale anchor. Everything else on the dashboard is a share, a rate or a
recommendation; this card is the one absolute number that tells the reader how big
domestic tourism actually is before they read anything else. It also establishes
the direction of travel — the sector is still growing hard post-recovery, which is
what makes a redistribution problem worth solving at all.

### Exact provenance

| | |
|---|---|
| File | `data/processed/state_summary_2024.csv` |
| Columns | `visitors_2024_millions`, `visitors_2023_millions` |
| Computation | plain sum across the 16 state rows; growth = (2024 − 2023) / 2023 |
| Extracted from | DTS 2024 state publications, Table 1 (Key Statistics), via `scripts/extract_dts_pdfs.py` |
| Original source | DOSM Domestic Tourism Survey 2024, published 18.09.2025 |
| Retrieved | see `data/manifest.json` — every PDF carries a SHA-256 and retrieval timestamp |

### Verification — this is the strongest number on the dashboard

| Measure | Our figure | DOSM published | Delta |
|---|---|---|---|
| 2024 visitors | **260.126M** | 260.1M | +0.026M |
| 2023 visitors | **213.744M** | 213.7M | +0.044M |
| Growth | **21.70%** | 21.7% | 0.00pp |

The deltas are rounding in the per-state source figures, nothing else. We did not
copy the national total — we summed 16 independently extracted state tables and it
reproduced the published headline. **That is a genuine end-to-end check on the whole
extraction pipeline**, not just on this card.

Second, independent check: the same pipeline gives 2025 state sum = **290.064M**,
while the separately extracted national quarterly bulletins sum to **290.1M**. Two
different documents, two different parsers, same answer.

### The definitional point you must get right

**"Visitors" is not "tourists".** DOSM uses both and they differ by a factor of ~2.7:

| 2025 | Value |
|---|---|
| Domestic **visitors** | 290.1M |
| Domestic **tourists** | 106.5M |

- **Visitor** = any domestic trip, including same-day excursionists.
- **Tourist** = overnight stays only.

The card says *visitors*, so 260.1M is the all-trips figure. If someone challenges
"Malaysia doesn't have 260 million tourists" — they are right, and they are quoting
the other measure. Say: *this is domestic visitor arrivals, DOSM's broader measure
including day trips; the overnight tourist figure for 2025 is 106.5 million.*

⚠️ **Related caveat for the allocator panel:** the O-D matrix is published in
**tourists**, while the redistribution volumes are computed from **visitors** per
resident. Only the origin *shares* (dimensionless) are taken from the O-D matrix, so
the mixing of measures does not corrupt the arithmetic — but state it before someone
else spots it.

### Why 2024 and 2023 — and the open question about 2025

2024 is the most recent year with a **complete per-state publication set**: the 16
DTS state reports carry receipts by component, ALOS, visitor income class and
accommodation type. 2023 is simply its comparison year, and both come from the same
Table 1, so the growth figure is internally consistent.

We *do* hold complete 2025 state visitor totals (290.064M, zero nulls) and 2025
national quarterly data. What 2025 does not have is the per-state detail — spend
components, ALOS, income class. The dashboard is 2024 because the supporting panels
are 2024, not because 2025 is missing.

**DECIDED (2026-08-16): keep the 2024 headline, carry 2025 as a secondary line.**
The card now renders:

```
260.1M  ▲21.7% vs 2023
Total 2024 visitors
2025: 290.1M (▲11.5%) — totals only, no state detail published
```

Rationale: the headline stays consistent with every panel beneath it, while the
secondary line removes the recency objection before it is raised. Moving the headline
to 2025 was rejected because it would create a visible year mismatch between the hero
number and the detail panels — one explanation instead of none, and a worse one.

Confirmed by the data-acquisition session: no "Domestic Tourism Survey (States) 2025"
exists. The states edition publishes each September (15.09.2023 → 20.09.2024 →
18.09.2025), so a 2025 edition is estimated at **15–18 Sept 2026** — days before the
22 Sept submission deadline, and the maximum-gap scenario (24 Sept) lands after it.
**Treated as upside, never a dependency.** 2025 per-state receipts, ALOS and income
class do not exist in any DOSM product today — verified across the publication index,
the release archive from four entry points, the OpenDOSM publications index, and the
machine-readable 2025 workbook (which is Malaysia-level for all detail sheets).

### Why this is useful to the community

- **Scale sets policy priority.** 260M domestic visitor arrivals against a population
  of ~34M is the argument for treating distribution as a real planning problem rather
  than a marketing one.
- **Growth of 21.7% is the urgency.** Pressure that is growing this fast cannot be
  absorbed by the same places indefinitely — which is the case for acting now.
- It is the number a state tourism officer or MOTAC planner would quote first, so it
  makes the dashboard legible to the audience that could actually use it.

### Anticipated challenges

| Challenge | Answer |
|---|---|
| "260 million is impossible for Malaysia." | It is *visitor arrivals*, including day trips and repeat trips — not unique people. Overnight tourists were 106.5M in 2025. |
| "Did you just copy the press release?" | No. We summed 16 independently extracted state tables; it reproduced the published national figure to within rounding. The extraction is in `scripts/extract_dts_pdfs.py`. |
| "Why not 2025, it's 2026 now?" | 2025 totals are in our data and agree with the quarterly bulletins. The dashboard is 2024 because the per-state *detail* — spend, ALOS, income class — is only published at state level for 2024. |
| "Is the growth real or base effect?" | Both years come from the same DTS Table 1 on a consistent definition. 2023 was itself a recovery year, so some of the 21.7% is post-pandemic normalisation — worth saying before being asked. |
| "Where is the raw file?" | `data/manifest.json`, with source URL, SHA-256 and retrieval timestamp for all 75 files. |

### Status

**Legitimate — DOSM official, verified against the published headline, cleared for
submission.** No open items; the 2024-vs-2025 framing was decided on 2026-08-16 and
is implemented on the card.

---

## Panel — "Where inside each target state"

### What it is for

The pitch says we redirect demand toward under-visited **districts**. Until this panel
every dataset was state-level, so that claim was unsupported. This is the panel that
makes it real: for each state the allocator selected, it shows the most-visited
districts inside it and how much accommodation they actually have.

### Exact provenance

| Element | Source |
|---|---|
| District demand rank | DTS 2025 workbook, **sheet 8B** "Top Five Administrative Districts Most Visited by Domestic Visitors, 2025" — `storage.dosm.gov.my/tourism/tourism_domestic_2025.xlsx` |
| Accommodation premises | District homestay/accommodation counts, **2021** |
| Piped water, population | OpenDOSM `hh_access_amenities`, `population_district` |
| Joined file | `data/processed/district_demand_supply_2025.csv` (58 districts, 12 states) |

Melaka shows 3 districts, not 5, because it has exactly 3. Labuan, Putrajaya, KL and
Perlis have no districts and are absent by design.

### Two limitations, both stated on the panel itself

**1. Rank is ordinal.** Sheet 8B gives position within a state, not a count. We can
say "the #2 most-visited district in Sabah". We **cannot** say how many visitors it
received, cannot compute a demand-to-supply ratio, and cannot compare Sabah #2 against
Johor #2. No ratio is computed anywhere in the code, and the CSV carries the constraint
in a `demand_measure` column so nothing downstream can forget it.

**2. Four-year vintage gap.** Demand is 2025; supply is 2021, because DOSM has
published no district accommodation count since. We measured the risk rather than
ignoring it, using MOTAC's state-level series (My Local Stats Table 10.9) which does
run to 2024:

- national premises 5,253 (2021) → 5,277 (2024) = **+0.5%**
- median absolute state change **6.2%**; 2 of 16 states moved more than 15%
- **Spearman rank correlation 0.977** — the ordering of states by supply is essentially unchanged

So the 2021 district split is very likely still close. Every row carries
`state_supply_change_2021_2024_pct` so the risk is visible exactly where it bites.

⚠️ **Do not use Seberang Perai Selatan as the headline example.** It sits in Pulau
Pinang, the state with the largest drift (+25.3%), making it the least reliable case
in the set. Lead with **Kelantan — Pasir Mas and Pasir Puteh**, ranks 3 and 4, 5
premises each, state drift +6.2%.

### The finding this panel produced

**Ranau is the #2 most-visited district in Sabah and has 46.5% piped-water coverage
for 89,000 residents.** Keningau (#5) is at 86.3%.

That reframes the recommendation. Sending more visitors to Ranau without water
investment moves the burden onto residents instead of relieving it. The panel labels
these **capacity-building targets, not redirect targets** — which is the difference
between a tourism optimiser and a sustainable one, and is the single clearest
community-benefit argument on the dashboard.

### Anticipated challenges

| Challenge | Answer |
|---|---|
| "Your supply data is four years older than your demand data." | Correct, and DOSM publishes nothing newer at district level. We measured the drift: national +0.5%, Spearman 0.977. Every row carries its state's drift figure. |
| "Rank 3 in Kelantan vs rank 3 in Melaka — which is bigger?" | Unanswerable, and we never claim otherwise. Rank is ordinal within a state. Sheet 8B publishes no counts. |
| "Why only 15 districts?" | These are the districts inside the states the allocator selected. The full joined set is 58 across 12 states. |
| "Why is Melaka short?" | Melaka has three districts in total. |
| "Isn't sending tourists to a 46% water district irresponsible?" | Yes — which is why the panel flags it as a capacity-building target rather than a redirect target. The flag is the point. |

### Status

**Legitimate with two stated caveats.** Both caveats are rendered on the panel, carried
in the CSV, and recorded in `data/GAPS.md` §2. Cleared for submission provided the
Kelantan example is used rather than Pulau Pinang.

---

## KPI 2 — "Peak visitors per resident · 21.3 · vs 4.1 lowest"

### What the card is for

The over-tourism measure. Card 1 says how big domestic tourism is; this card says how
unevenly it lands. It shows the two ends of the range so the gap is visible at a
glance: the most pressured state carries **five times** the load of the least.

### What the number means

Plain division — total visitors divided by total residents:

```
Putrajaya:  2,557,000 visitors ÷ 120,300 residents = 21.3
Johor:     17,138,000 visitors ÷ 4,184,400 residents =  4.1
```

**It does not mean any resident causes, hosts or attracts anyone.** It is a load
measure, like "customers per staff member" in a restaurant. Putrajaya's roads, water,
waste collection and parking are built for 120,000 people; 2.5 million arrivals use
them each year.

"Peak" = the highest of the 16 states, not an average. National middle is ~9.

### Exact provenance

| | |
|---|---|
| File | `data/processed/state_summary_2024.csv`, column `visitors_per_capita_2024` |
| Inputs | `visitors_2024_millions` (DTS 2024 state reports, Table 1) ÷ `population_thousands` (OpenDOSM `population_state`) |
| Both sources | DOSM official; see `data/manifest.json` |

### Why this metric, and what was rejected

**Rejected: visitors per hotel room.** It was the first choice and it was wrong. It
measures accommodation *undersupply*, not over-tourism:

- Perlis ranked #1 on a 1,285-room denominator
- **Kuala Lumpur ranked last** despite 27.0M visitors, because it holds 47,525 rooms
- Consequence: the model recommended redirecting visitors **into KL**

Visitors per resident measures what over-tourism actually means — how heavily a place
is used relative to the people who live there and absorb the cost. The rejection and
its reason are recorded as a comment in `app.py` so the reasoning survives into the
methodology section.

### What the data enables (this is the whole product)

1. **Identify the overloaded** — top third: Putrajaya 21.3, Melaka 18.3, Negeri
   Sembilan 14.4, KL 13.1, Pahang 12.1, Terengganu 11.7.
2. **Identify who has room** — below median: Johor 4.1, Labuan 4.5, Sabah 5.5,
   Sarawak 7.8.
3. **Size the transfer.** Because it is a ratio, headroom is computable:
   Johor at 4.1 against a ~9 median across 4.18M residents could absorb roughly 20M
   more visitors before reaching average. This is exactly what the Redirect allocation
   panel does — 35.5M placed across 9 routes, 0.34M flagged as unplaceable.

### Why this is useful to the community

- **Raw counts hide the problem.** Johor 17.1M and Melaka 19.1M look alike; per
  resident they are 4 vs 18. Melaka carries four times the load. Only the ratio shows it.
- **It measures who pays.** Revenue accrues to businesses; congestion, water use and
  waste land on residents. This is the residents' side of the ledger.
- **It is fundable.** "18 visitors per resident against a national middle of 9" is an
  infrastructure argument a state officer can take to a budget meeting. "19 million
  visitors" sounds like success and funds nothing.

### Anticipated challenges

| Challenge | Answer |
|---|---|
| "Putrajaya and Labuan are tiny — the ratio is an artefact." | The ratio is the point. Small places have the least capacity to absorb visitors, which is precisely why they surface as most pressured. Absolute counts would hide them entirely. |
| "Does 21.3 mean 21 different people?" | No. A visitor is a *trip*, not a person — the same family visiting four times counts as four. It is 21 arrivals per resident per year, roughly two a month. |
| "Why not visitors per hotel room?" | Tried it; it measures undersupply, not over-tourism. It ranked KL — 27M visitors — as the emptiest state and had the model redirecting people into the capital. |
| "Is population the right denominator?" | It is the standard tourism-intensity denominator, and it is the population that bears the infrastructure cost. Room stock is used separately, as a capacity constraint in the allocator. |
| "Why 2024 population against 2024 visitors?" | Both are 2024, from the same reference year. No vintage gap on this card. |

### Status

**Legitimate — both inputs DOSM official, single reference year, no vintage gap.
Cleared for submission.** Metric choice was corrected once during development; the
rejected alternative and its failure mode are documented in code and above.

---

## KPI 3 — "6 · Most pressured states · top third · above 11.7 per resident"

### What the card is for

It turns Card 2's continuous measure into a decision. Card 2 says the range runs
4.1 to 21.3 — interesting but not actionable. This card says **which six need
attention**, and those six are the sources the redirect allocator moves demand away
from. Everything downstream keys off this list.

### The rule, stated plainly

Rank all 16 states by visitors per resident, flag the **top third**. The 66th
percentile falls at **11.65 visitors per resident**.

| State | Per resident | |
|---|---|---|
| W.P. Putrajaya | 21.26 | flagged |
| Melaka | 18.27 | flagged |
| Negeri Sembilan | 14.35 | flagged |
| W.P. Kuala Lumpur | 13.05 | flagged |
| Pahang | 12.10 | flagged |
| Terengganu | 11.74 | flagged |
| — cutoff 11.65 — | | |
| Perlis | 10.87 | not flagged |
| Pulau Pinang | 9.22 | not flagged |

National median is 8.85; the full range is 4.10 to 21.26.

### Naming — deliberate and important

The card originally read **"States over capacity"**. That was changed to
**"Most pressured states"**, because the first phrasing claims something the data
does not support.

**11.65 is not a capacity limit.** Nobody has studied Malaysian states and concluded
that 11.65 visitors per resident is the safe maximum. It is simply where the top third
of the current 16 states begins, and it **moves** when the data changes — feed in 2025
and the cutoff shifts.

Correct phrasing: *"six states sit in the top third by visitor intensity, above 11.65
visitors per resident."*
Incorrect: *"six states exceed capacity."*

The six states are now named on the card itself. Previously they were only inferable
from the Redirect allocation panel, where they appear as the sources.

### The weakness — raise it before a judge does

**1. The threshold is relative, not absolute.** Six states will always be flagged no
matter how much conditions improve. If every state halved its intensity tomorrow, the
card would still read 6. It identifies *who is worst*, not *who is in trouble*.

**2. Terengganu clears the line by 0.09.** 11.74 against a cutoff of 11.65, while
Perlis at 10.87 does not. That is a thin margin and anyone checking will find it.

Answer: *the threshold is a relative ranking, deliberately. There is no published
carrying-capacity standard for Malaysian states to anchor an absolute figure to. We
used the top tercile, state the cutoff on the card, and show every underlying value on
the map and in the full table so anyone can draw their own line.*

Alternative if a harder rule is wanted: an absolute cutoff such as 2× the national
median (17.7) would flag only Putrajaya and Melaka. Harder to argue with, much smaller
product. Not adopted.

### Why this is useful to the community

- It converts a spectrum into a shortlist a ministry can act on.
- Naming the six makes the dashboard accountable — a reader can immediately check
  whether the list matches their own experience of those places.
- It is the entry point for resource allocation: these six are where infrastructure
  and demand-management effort would go first.

### Anticipated challenges

| Challenge | Answer |
|---|---|
| "Where does 11.65 come from?" | The 66th percentile of the 16 states' visitors per resident. It is a relative cutoff, stated on the card, not a published standard. |
| "So it isn't really 'over capacity'?" | Correct, which is why the card says *most pressured*. No carrying-capacity standard exists for Malaysian states. |
| "Terengganu only just qualifies." | True — 11.74 against 11.65. The values are shown throughout so the margin is visible rather than hidden. |
| "Why a third and not a quarter or half?" | A tercile keeps the flagged group small enough to act on while large enough to allocate across. An absolute alternative was considered and rejected as too narrow. |
| "Will this change next year?" | Yes. It is recomputed from whatever data is loaded, by design. |

### Status

**Legitimate — derived transparently from Card 2, cutoff disclosed on the card.**
Renamed from "States over capacity" on 2026-08-16 because that phrasing overclaimed.

---

## KPI 4 — "35.5M · Demand reallocated · 9 routes · 0.3M unplaced"

### Say it this way out loud

> Melaka gets 19 million visitors and has 1 million residents. Johor gets 17 million
> and has 4 million residents. Almost the same crowd — but Melaka is a quarter the
> size, so it feels four times as busy.
>
> The card says: if about 10 million of those Melaka visits happened in Johor instead,
> both places would sit at a normal level. That's it — a plan for spreading people out,
> measured in visitors.
>
> The model checks two things before suggesting it. Does Johor have room? Yes, about
> 20 million more before it feels crowded. Do the same people already go there? Yes —
> Melaka's visitors come mostly from KL, Selangor and Negeri Sembilan, and those same
> people already visit Johor. So it's a realistic swap, not a fantasy.

### What it is for

The product in one number. It answers: if visitors moved from crowded places to quiet
ones, how many could actually move?

### How the allocator works

1. **Target level** — the national median, **8.85 visitors per resident**.
2. **Excess** — for each of the 6 pressured states, visitors held above that level.
3. **Headroom** — for each eligible target, visitors it could take before reaching it.
4. **Match** — pair by shared origin markets from the DTS 2025 origin-destination
   matrix, weighted by readiness; fill until the excess is placed or headroom is gone.

| Pressured | Excess | | Target | Headroom |
|---|---|---|---|---|
| Melaka | 9.86M | | Johor | 19.88M |
| W.P. Kuala Lumpur | 8.68M | | Sabah | 12.54M |
| Negeri Sembilan | 6.82M | | Sarawak | 2.64M |
| Pahang | 5.42M | | W.P. Labuan | 0.44M |
| Terengganu | 3.56M | | | |
| W.P. Putrajaya | 1.49M | | | |
| **Total** | **35.83M** | | **Total** | **35.50M** |

35.83 needed − 35.50 absorbable = **0.34M unplaced**. The figures reconcile exactly.

### The unplaced line is the most valuable thing on the card

The model reports that the quiet states physically cannot absorb everything. It is not
hiding its limit, it is publishing it. Labuan is the clearest demonstration: headroom
of exactly 0.44M, and the allocator sent it exactly 0.44M from Kuala Lumpur, then
stopped. The capacity cap is doing real work.

### Why this is useful to the community

- **Melaka residents** — less traffic, waste, water strain and housing pressure. Their
  infrastructure was built for 1 million people, not 19 million visits.
- **Johor residents** — 9.86M more visitors is roughly **RM 2.1 billion** more spent
  in local shops and restaurants, i.e. jobs in places currently missing out.
- **Visitors** — shorter queues, cheaper rooms, better trips.
- **MOTAC / state tourism offices** — nobody currently publishes where the spare
  capacity is or how much of it there is. This does.

### The honest limitation — state it first

**This is a capacity calculation, not a forecast.** It shows how much room exists and
which pairings are realistic. It does not model pricing, marketing, transport, visitor
preference or elasticity, and nobody is compelled to go anywhere. Actually shifting
demand is a policy job.

Framed as a capacity calculation it is a strength. Claimed as a prediction it collapses.

### Anticipated challenges

| Challenge | Answer |
|---|---|
| "Visitors won't move because a dashboard says so." | Agreed — it is a capacity calculation, not a forecast. It says where room exists and how much, not what people will do. |
| "Why is the median the right target?" | It is a neutral reference point, not a safety limit. Any level can be substituted; the median keeps the target inside observed Malaysian conditions rather than importing a foreign standard. |
| "Why can Johor take 20M more?" | 4.18M residents at 4.10 visitors each against a median of 8.85. The arithmetic is population × the intensity gap. |
| "Isn't 0.3M unplaced a failure?" | It is the opposite — the model reporting that eligible states cannot absorb everything. Hiding it would be the failure. |
| "The O-D matrix is in tourists, your volumes are in visitors." | Correct. Only the dimensionless origin *shares* are taken from the O-D matrix; volumes come from visitors per resident. The measures never multiply. |

### Status

**Legitimate — inputs DOSM official, arithmetic reconciles exactly, limits disclosed
on the card.** Cleared for submission provided it is presented as a capacity
calculation rather than a prediction.

---

## What to check next

Working down the dashboard. Tick as each is written up.

- [x] KPI 1 — Total 2024 visitors
- [x] KPI 2 — Peak visitors per resident
- [x] KPI 3 — Most pressured states
- [x] KPI 4 — Demand reallocated
- [x] Panel — Where inside each target state
- [x] Panel — "The imbalance is spatial, not seasonal" (scatter) — x-axis was wrong, corrected 2026-08-16
- [x] Panel — "The pressure sits in a corridor" (choropleth) — renamed, split into two panels
- [ ] Panel — "Redirect allocation" (the 9 routes list)
- [x] Panel — "Who's visiting" (income donut) — **was wrong, corrected 2026-08-16**
- [ ] Panel — "Fastest growing" — **known issue: Perlis 65.3% is a small-base effect
      and Perlis is no longer flagged as pressured; decide whether to add a base note
      or a volume filter**
- [ ] Panel — "Length of stay vs national average"
- [ ] Panel — "Where the money goes" (spend donut)
- [ ] Panel — "Why each target was picked" (3-factor breakdown)
- [ ] Panel — "Community impact" (RM per route)
- [ ] Table — "Show all 16 states and their scores"
- [ ] Footer — source line and provenance claim

Open items carried from earlier:
- `PLACEHOLDER_monthly_2024.csv` still sits in `dashboard/` although nothing reads it.
  It is fabricated seasonality contradicted by the real quarterly data. **Delete it.**
- Decide whether the header "Malaysia · 2024" should mention 2025 totals, now that
  KPI 1 does.

---

## Panel — "Who's visiting" (household income donut)

### Say it this way out loud

> Domestic tourism is not a rich people's activity. Just over half of all visitors come
> from households earning between RM1,001 and RM5,000 a month. No income group is
> anywhere near a majority — the biggest single band is RM5,001-10,000 at about a third.
>
> That matters for who benefits. When demand shifts to Johor or Sabah, the money
> arriving is ordinary household money spread across the income range, not luxury
> spending concentrated at the top.

### What it is for

It answers "who are these 260 million visits actually made by". Without it the reader
assumes tourism means affluent travellers, which changes who they think the policy
serves.

### CORRECTION — this panel was wrong until 2026-08-16

The card previously read **"76% of visitors come from RM5,001-10,000 households."**
That was false.

The error: `state_summary_2024.csv` carries a column `income_bracket` holding **one
value per state** — the *dominant* band among that state's visitors. Summing visitor
counts by it computed "share of visitors going to states whose dominant band is X",
then labelled the result as if it were the income distribution of visitors. It also
silently dropped two of the five income classes.

Fixed by using `data/processed/dts_visitor_income_class.csv` (DTS Table 13, 16 states
x 5 classes), weighting each state's distribution by its visitor volume.

**Do not reuse `income_bracket` as a distribution anywhere.** It is a modal value.

### The numbers

| Household income | Share of visitors 2024 | 2023 |
|---|---|---|
| ≤RM1,000 | **4.1%** | 3.8% |
| RM1,001-3,000 | **26.0%** | 26.4% |
| RM3,001-5,000 | **25.9%** | 25.9% |
| RM5,001-10,000 | **30.8%** | 31.6% |
| ≥RM10,001 | **13.2%** | 12.3% |

RM1,001-5,000 combined: **52%** of all visitors.

### Provenance

| | |
|---|---|
| File | `data/processed/dts_visitor_income_class.csv` — 80 rows |
| Source | DOSM DTS state publications, Table 13 (social and demographic characteristics) |
| Method | each state's five class shares weighted by that state's 2024 visitor volume, then renormalised to 100% |
| Shares within each state sum to 100 | verified |

### Design note

The ramp runs light-to-dark with rising income rather than using five unrelated hues.
Income is **ordinal**, so an ordered ramp is the correct encoding; categorical colours
would throw away the ordering the reader needs.

### Why this is useful to the community

- It corrects the assumption that domestic tourism serves the affluent. Over half of
  visitors are middle and lower-middle income households.
- It supports the redistribution argument on **equity** grounds, not just congestion:
  the spending redirected to Johor, Sabah and Sarawak is ordinary household money.
- It maps directly onto SDG 8's inclusive-growth framing, which is one of the four
  SDGs in scope for this competition.

### Anticipated challenges

| Challenge | Answer |
|---|---|
| "Is this the income of visitors or of residents?" | Visitors — the monthly household income of the people making the trips, from DTS Table 13. |
| "How do you get a national figure from state tables?" | Each state's distribution weighted by its visitor volume, then renormalised. States with more visitors count proportionally more. |
| "Why does the full data table still show one income bracket per state?" | That column is the state's *dominant* band. It is legitimate as a per-state label but must never be summed into a distribution — that was the bug fixed here. |
| "Did the mix change from 2023?" | Only slightly; the shape is stable year to year, which is why a single-year donut is representative rather than a snapshot artefact. |

### Status

**Legitimate — DOSM official, correctly weighted.** Was materially wrong until
2026-08-16; the error and its cause are recorded above so it cannot recur.


---

## Panel — "The imbalance is spatial, not seasonal" (scatter)

### Say it this way out loud

> Each dot is a state. Further right means more visitors. Higher up means more
> crowded. The bubble is how many people live there.
>
> Look at Selangor — furthest right, so it takes the biggest crowd in Malaysia, but it
> sits near the bottom because 7.4 million people live there. Now look at Melaka. Fewer
> visitors than Selangor, but near the top, because only 1 million people live there.
>
> That is the whole argument: counting visitors misleads you. You have to divide by the
> people who live there.

### What it shows

Three numbers in one picture — visitors on the x-axis, residents as the bubble size,
and the two divided as the height. The dashed line is the national median (8.85).

### The two claims, and how well each holds

**"Not seasonal" — strongly supported.** National quarterly shares for 2025 are
24.0 / 25.4 / 25.0 / 25.5%. Q1 2026 (74.7M) continues the pattern, giving five straight
quarters with no spike. There is no season to spread demand across.

**"Spatial" — strongly supported.** Intensity ranges 4.1 to 21.3, a five-fold spread.

### CORRECTION — the x-axis was wrong until 2026-08-16

The chart originally plotted **share of rooms that are beachfront** on the x-axis, with
a subtitle implying coastal states carry the load. Tested and false:

| | Pressure | Beach rooms |
|---|---|---|
| W.P. Putrajaya | 21.3 (highest) | **0%** |
| W.P. Kuala Lumpur | 13.0 | **0%** |
| Kedah | 6.6 (low) | **38%** |

**Pearson correlation: −0.065.** No relationship.

Cause of the error: the data-acquisition session reported "beach hotels run 89%
occupancy vs 61–64% elsewhere" — a **national hotel-occupancy** finding. That was
conflated with *which states are crowded*, a different question. Beach share does not
predict state-level intensity.

Replaced with total visitors on the x-axis (correlation with intensity −0.17, so a
genuine spread rather than a trivial relationship). Bubble size moved from visitors to
population, so the chart carries both halves of the ratio instead of double-encoding.

**What actually drives intensity is population size** — correlation −0.554, the
strongest relationship in the dataset.

### Why this is useful to the community

Two different actions fall out of the two findings.

**From "no season":** stop budgeting for off-peak campaigns — there is no off-peak.
Size roads, water and waste for year-round load, and accept there is no quiet window
for major maintenance.

**From "spatial":** direct infrastructure money by *intensity* rather than visitor
counts. Melaka and Johor receive similar visitor numbers, so count-based funding treats
them alike; intensity-based funding sends it to Melaka, where residents actually feel
it. It also makes targets measurable — "reduce Melaka from 18 to 14 per resident by
2030" is trackable in a way "improve sustainable tourism" is not.

### Anticipated challenges

| Challenge | Answer |
|---|---|
| "Isn't tourism obviously seasonal?" | Not domestically in Malaysia. Five consecutive quarters sit within 1.5 percentage points. We expected seasonality too; the data refused it. |
| "Isn't this just population in disguise?" | Partly — population correlates −0.554 with intensity, and we say so. But it is not tautological: a state can be small with few visitors (Labuan) or large with many (Selangor). The chart shows both dimensions so the reader can judge. |
| "Why not show beaches / coastal?" | We did, and removed it. Beach room share correlates −0.065 with intensity. Keeping it would have implied a relationship that does not exist. |

### Status

**Legitimate.** X-axis was materially misleading until 2026-08-16; corrected, with the
rejected version and its correlation recorded above.

---

## Panel — "The pressure sits in a corridor" (choropleth)

### Say it this way out loud

> Look at the peninsula. Melaka is dark red, Negeri Sembilan and Pahang are orange,
> Kuala Lumpur is orange, Putrajaya is the darkest of all.
>
> Now look at what sits in the middle of them — Selangor, pale green, one of the
> calmest states in the country at 4.7 visitors per resident. It physically surrounds
> Kuala Lumpur and Putrajaya.
>
> So the pressure is not "the west coast is busy". It is that the small territories
> embedded beside Selangor carry the strain while Selangor itself absorbs its share
> comfortably. You can only see that on a map.

### What it shows

The same measure as the scatter — visitors per resident — placed geographically, so
adjacency becomes visible. States are shaded by quantile band.

### Why both this and the scatter exist

They encode the same variable. That is deliberate duplication, justified only by what
each adds:

- **Scatter** — the *mechanism*: visitors and population separately, so the reader sees
  why a state is crowded.
- **Map** — the *geography*: which states are neighbours, revealing the corridor and
  the Selangor hole. A scatter cannot show adjacency.

If the map's subtitle ever reverts to explaining colour-ramp theory rather than stating
the corridor finding, it stops earning its place and should be cut.

### Design decisions

**Two panels, not one national map.** Malaysia's bounding box is roughly 3:1 wide with
a large sea gap, so a single map spends most of its area on the South China Sea and
shrinks the peninsula — where four of the six pressured territories sit — to
illegibility. Peninsula and Borneo are drawn separately, each zoomed to fit.

**Quantile bands, not equal-interval.** The values cluster; equal steps would flatten
most states into one class. Exact figures remain in the tooltip.

**Leader lines** for Perlis, KL, Putrajaya, Melaka and Labuan. A choropleth sizes by
land area, so the most pressured territory in the country (Putrajaya, 49 km2) is
invisible without one. Labels carry the real value (Putrajaya 21.3), not the normalised
score.

**Geometry** is DOSM's own open geodata — `administrative_1_state.geojson`, 16 features,
joined on state name with a guard that raises a visible error if any state fails to
match.

### Why this is useful to the community

- It shows the problem is **not regional**. A policy aimed at "the west coast" would
  wrongly include Selangor, which is coping. The unit of action is the territory, not
  the region.
- Adjacency suggests a mechanism worth investigating: KL and Putrajaya may be absorbing
  day-trip demand generated by Selangor's population without having the residents to
  spread it across.
- A map is the format planners and ministries already use, so it lands without
  translation.

### Anticipated challenges

| Challenge | Answer |
|---|---|
| "Why is Malaysia split into two maps?" | A single national map is ~3:1 wide and mostly sea; the peninsula becomes too small to read. Splitting is standard practice in Malaysian statistical publications. |
| "Choropleths exaggerate large states." | Correct, which is why the five smallest territories carry leader lines, and why the scatter and the ranked allocation list sit alongside carrying the true order. |
| "Isn't this the same as the scatter?" | Same variable, different question. The scatter shows *why*; the map shows *where* and *next to what*. The corridor finding is only visible on the map. |
| "Why quantile bands?" | The values cluster. Equal-interval bands would put most states in one class and hide the spread. Exact values are in the tooltip. |

### Status

**Legitimate — DOSM geometry, DOSM values, join guarded.** Subtitle rewritten
2026-08-16 from a design note to the corridor finding, which is what justifies keeping
both this and the scatter.
