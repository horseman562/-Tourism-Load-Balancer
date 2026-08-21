"""
Tourism Load-Balancer — Streamlit + Plotly
DOSM Datathon 2026

All figures are real official statistics (DOSM DTS 2024/2025, NAPIC, OpenDOSM).
Saturation, readiness and redirect recommendations are derived — the formulas are
stated in the panels. Provenance: data/manifest.json and data/SOURCES.md.
"""

import json
import os

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Paths resolve relative to this file, not the working directory, so the app
# runs identically from the repo root (Streamlit Cloud) or from dashboard/.
_HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(_HERE, "..", "data", "processed")
DATA_FILE = f"{DATA}/state_summary_2024.csv"
OD_FILE = f"{DATA}/dts_origin_destination_2025.csv"
DISTRICT_FILE = f"{DATA}/district_demand_supply_2025.csv"

# Districts below this piped-water coverage are flagged: sending more visitors to a
# place that cannot supply its existing residents is not sustainable tourism.
WATER_FLOOR = 90.0

st.set_page_config(page_title="Tourism Load-Balancer (Mockup)", layout="wide")

# ============================ DESIGN TOKENS ============================
BG = "#f5f7f8"
CARD = "#ffffff"
BORDER = "#e3e9ed"

GREEN = "#4d9a68"        # primary
GREEN_SOFT = "#8cc4a1"
GREEN_PALE = "#dff0e5"
GOLD = "#e0a938"         # accent
GREY = "#c2cbd3"         # context / secondary data

TEXT = "#1f2933"
TEXT_MUTED = "#7b8794"
GRID = "#eef2f5"

# Severity ramp lives in BAND_COLORS below. Lightness decreases monotonically
# from low to high, so the ordering survives greyscale printing and colour-vision
# deficiency even when the hues themselves are confused.

INCOME_FILE = f"{DATA}/dts_visitor_income_class.csv"

# Income is ordinal, so the ramp runs light-to-dark with the band rather than using
# unrelated categorical hues.
INCOME_ORDER = ["≤RM1,000", "RM1,001-3,000", "RM3,001-5,000", "RM5,001-10,000", "≥RM10,001"]
INCOME_COLORS = {
    "≤RM1,000": "#dff0e5",
    "RM1,001-3,000": "#a8d5b8",
    "RM3,001-5,000": "#6fb98a",
    "RM5,001-10,000": "#4d9a68",
    "≥RM10,001": "#2f6b45",
}

NATIONAL_ALOS = 2.49
# DEMAND_SHIFT removed: impact is now allocated volume x observed spend per visitor

GEO_FILE = os.path.join(_HERE, "geo_state.json")

# Discrete quantile bands for the choropleth.
BAND_LABELS = ["Lowest", "Low", "Moderate", "High", "Highest"]
BAND_COLORS = {
    "Lowest": "#dff0e5",
    "Low": "#9ccbae",
    "Moderate": "#e8c26a",
    "High": "#d9803f",
    "Highest": "#a8331f",
}

# Our CSV says "Penang"; DOSM's geodata says "Pulau Pinang". Every other name matches.
GEO_NAME_FIX = {"Penang": "Pulau Pinang"}

# Label anchors for territories too small to see when filled by area. lat, lon.
# The map is drawn as two panels, so each set is anchored inside its own panel.
PENINSULA_LABELS = {
    "Perlis": (7.1, 101.9),
    "W.P. Kuala Lumpur": (4.5, 104.3),
    "W.P. Putrajaya": (2.8, 104.3),
    "Melaka": (1.4, 104.3),
}
BORNEO_LABELS = {
    "W.P. Labuan": (7.0, 112.2),
}

st.markdown(
    f"""
    <style>
      .block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1500px; }}

      /* Every panel is a card — the repeating container rhythm both references rely on */
      div[data-testid="stVerticalBlockBorderWrapper"] {{
          background: {CARD};
          border: 1px solid {BORDER};
          border-radius: 14px;
          padding: 6px 4px;
          box-shadow: 0 1px 2px rgba(31,41,51,.05);
      }}

      .card-head {{
          display: flex; align-items: baseline; justify-content: space-between;
          margin: 2px 6px 10px 6px;
      }}
      .card-title {{ font-size: 1rem; font-weight: 700; color: {TEXT}; letter-spacing: .01em; }}
      .card-meta  {{ font-size: .76rem; color: {TEXT_MUTED}; font-weight: 500; }}
      .card-sub   {{ font-size: .8rem; color: {TEXT_MUTED}; margin: -4px 6px 8px 6px; line-height: 1.4; }}

      /* KPI tiles — icon left, number right (ref-1 header pattern) */
      /* min-height keeps all four tiles level once card 1 carries a second line */
      .kpi {{ display: flex; align-items: center; gap: .8rem; padding: 6px 4px 4px 8px;
              min-height: 74px; }}
      .kpi-ico {{
          width: 42px; height: 42px; flex: 0 0 42px; border-radius: 11px;
          background: {GREEN_PALE}; display: inline-flex;
          align-items: center; justify-content: center; font-size: 1.15rem;
      }}
      .kpi-val {{ font-size: 1.7rem; font-weight: 700; color: {TEXT}; line-height: 1.15; }}
      .kpi-lab {{ font-size: .78rem; color: {TEXT_MUTED}; font-weight: 500; }}
      .kpi-sub {{
          font-size: .68rem; color: {TEXT_MUTED}; font-weight: 400;
          margin-top: 3px; padding-top: 3px; border-top: 1px solid {GRID};
          line-height: 1.35;
      }}
      .kpi-delta {{ font-size: .74rem; font-weight: 600; margin-left: .4rem; }}
      .up {{ color: {GREEN}; }} .flat {{ color: {TEXT_MUTED}; }}

      /* Ranked list rows (ref-1 "Users by Voivodeship") */
      .rank-row {{
          display: flex; align-items: center; justify-content: space-between;
          padding: 7px 8px; border-bottom: 1px solid {GRID}; font-size: .86rem;
      }}
      .rank-row:last-child {{ border-bottom: none; }}
      .rank-name {{ color: {TEXT}; font-weight: 600; }}
      .rank-to {{ color: {TEXT_MUTED}; font-weight: 400; }}
      .rank-val {{ color: {TEXT}; font-weight: 700; font-variant-numeric: tabular-nums; }}

      /* Impact rows */
      .imp {{ padding: 9px 8px; border-bottom: 1px solid {GRID}; }}
      .imp:last-child {{ border-bottom: none; }}
      .imp-route {{ font-size: .72rem; color: {TEXT_MUTED}; font-weight: 600;
                    letter-spacing: .04em; text-transform: uppercase; }}
      .imp-line {{ display: flex; justify-content: space-between; align-items: baseline; margin-top: 2px; }}
      .imp-txt {{ font-size: .85rem; color: {TEXT}; }}
      .imp-val {{ font-size: 1rem; font-weight: 700; color: {GREEN}; font-variant-numeric: tabular-nums; }}

      .page-title {{ font-size: 1.9rem; font-weight: 800; color: {TEXT}; margin: 0; }}
      .page-meta {{ font-size: .84rem; color: {TEXT_MUTED}; text-align: right; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def card_head(title, meta=""):
    st.markdown(
        f'<div class="card-head"><span class="card-title">{title}</span>'
        f'<span class="card-meta">{meta}</span></div>',
        unsafe_allow_html=True,
    )


def card_sub(text):
    st.markdown(f'<div class="card-sub">{text}</div>', unsafe_allow_html=True)


def style_fig(fig, height=None):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, size=12),
        margin=dict(l=0, r=0, t=6, b=0),
        hoverlabel=dict(bgcolor=CARD, bordercolor=BORDER, font=dict(color=TEXT)),
        showlegend=False,
    )
    if height:
        fig.update_layout(height=height)
    return fig


# ============================ DATA ============================
@st.cache_data
def load_data(_mtime):
    # _mtime is part of the cache key so edits to the CSV take effect on refresh
    df = pd.read_csv(DATA_FILE)
    df["state_key"] = df["state"].replace({"Pulau Pinang": "Penang"})
    return df


@st.cache_data
def load_od(_mtime):
    """2025 origin-destination flows, DTS 2025. Drops the 'Malaysia' aggregate
    rows so what remains is a clean 16x16 state-to-state matrix."""
    od = pd.read_csv(OD_FILE)
    od = od[(od["state_of_origin"] != "Malaysia") & (od["state_visited"] != "Malaysia")]
    return od.pivot(index="state_of_origin", columns="state_visited",
                    values="tourists_thousand_2025").fillna(0.0)


@st.cache_data
def load_income(_mtime):
    """Visitor household income distribution by state, DTS Table 13.
    Five classes per state, shares summing to 100 within each state."""
    return pd.read_csv(INCOME_FILE)


@st.cache_data
def load_districts(_mtime):
    """Top-5 most-visited districts per state, DTS 2025 sheet 8B, joined to
    accommodation supply. Demand is an ORDINAL rank within state — not a count and
    not comparable across states. Supply is 2021; no district-level accommodation
    count has been published since. See data/GAPS.md section 2."""
    return pd.read_csv(DISTRICT_FILE)


@st.cache_data
def load_geo(_mtime):
    """Malaysia state boundaries — DOSM open data.
    dosm-malaysia/data-open · datasets/geodata/administrative_1_state.geojson"""
    with open(GEO_FILE, encoding="utf-8") as fh:
        return json.load(fh)


STATE_COORDS = {
    "Selangor": (3.0738, 101.5183), "W.P. Kuala Lumpur": (3.1390, 101.6869),
    "Perak": (4.5921, 101.0901), "Johor": (1.4854, 103.7618),
    "Sarawak": (2.5000, 113.0000), "Sabah": (5.9788, 116.0753),
    "Pahang": (3.8126, 103.3256), "Penang": (5.4141, 100.3288),
    "Negeri Sembilan": (2.7258, 101.9424), "Melaka": (2.1896, 102.2501),
    "Kedah": (6.1184, 100.3685), "Kelantan": (6.1254, 102.2381),
    "Terengganu": (5.3117, 103.1324), "Perlis": (6.4449, 100.2048),
    "W.P. Labuan": (5.2831, 115.2308), "W.P. Putrajaya": (2.9264, 101.6964),
}

df = load_data(os.path.getmtime(DATA_FILE))
OD = load_od(os.path.getmtime(OD_FILE))
DIST = load_districts(os.path.getmtime(DISTRICT_FILE))
INCOME = load_income(os.path.getmtime(INCOME_FILE))
GEO = load_geo(os.path.getmtime(GEO_FILE))

# key used to join our rows onto the DOSM geometry
df["geo_name"] = df["state"].replace(GEO_NAME_FIX)
_geo_states = {f["properties"]["state"] for f in GEO["features"]}
_unmatched = set(df["geo_name"]) - _geo_states
if _unmatched:
    st.error(f"These states do not match the DOSM geodata and will not render: {sorted(_unmatched)}")

df["lat"] = df["state_key"].map(lambda s: STATE_COORDS.get(s, (np.nan, np.nan))[0])
df["lon"] = df["state_key"].map(lambda s: STATE_COORDS.get(s, (np.nan, np.nan))[1])


def minmax(s):
    return (s - s.min()) / (s.max() - s.min())


# ---- Saturation: tourist intensity per resident ----
# Visitors per head of population — the standard over-tourism measure: how heavily
# a place is used relative to the people who live there.
#
# Rejected: visitors per hotel room. It measures accommodation *undersupply*, not
# over-tourism. Perlis topped it on a 1,285-room denominator while Kuala Lumpur —
# 27.0M visitors, the most intensely visited place in the country — ranked lowest
# because it holds 47,525 rooms. That inverted the whole product.
df["saturation_calc"] = minmax(df["visitors_per_capita_2024"])
SATURATION_THRESHOLD = df["saturation_calc"].quantile(0.66)

# ---- Readiness: spare capacity + household amenity coverage ----
# Sanitation is excluded deliberately: it sits at 99.02-100% across every state
# (cv 0.00) and so cannot discriminate between candidates.
df["amenities_norm"] = (minmax(df["amenities_piped_water_pct"])
                        + minmax(df["amenities_electricity_pct"])) / 2
df["headroom_norm"] = 1 - df["saturation_calc"]
df["readiness_calc"] = (df["headroom_norm"] + df["amenities_norm"]) / 2


# ---- Redirect: shared origin markets, from the 2025 O-D matrix ----
# A destination is only a realistic substitute if it already draws the same
# travellers. For each state we take its origin mix (what share of its visitors
# comes from each origin state), then score candidates by cosine similarity of
# that mix, weighted by the candidate's readiness.
_mix = OD.div(OD.sum(axis=0).replace(0, np.nan), axis=1).fillna(0.0)  # cols = destination


def origin_similarity(a, b):
    va, vb = _mix[a].values, _mix[b].values
    na, nb = np.linalg.norm(va), np.linalg.norm(vb)
    return float(va @ vb / (na * nb)) if na and nb else 0.0


_ready = df.set_index("state")["readiness_calc"]
_saturated = set(df.loc[df["saturation_calc"] >= SATURATION_THRESHOLD, "state"])

# A relief valve must actually be under-visited. Without this, the model rewards
# raw spare room stock and recommends redirecting *into* Kuala Lumpur, which has
# more rooms than anywhere else. Require below-median on both intensity measures.
_med_sat = df["saturation_calc"].median()
_med_room = df["visitors_per_room_2024"].median()
_eligible = df[(df["saturation_calc"] < _med_sat)
               & (df["visitors_per_room_2024"] < _med_room)]["state"]
_candidates = [s for s in _eligible if s not in _saturated and s in _mix.columns]

# ---- Capacity-capped allocation ----
# A recommendation is only meaningful if the target can actually absorb the volume.
# Every state has a headroom ceiling: the extra visitors it could take before its own
# intensity reaches the national median. Sources are served worst-first, each drawing
# from its best-matching targets until its excess is placed or the headroom runs out.
# Without this the model sent five of six routes to Johor and pointed Kuala Lumpur at
# Labuan, a 1,697-room island that cannot absorb a 27M-visitor city.
_med_vpc = df["visitors_per_capita_2024"].median()
_pop = df.set_index("state")["population_thousands"]


def _visitors_m(vpc_delta, state):
    """Convert an intensity gap into millions of visitors for that state."""
    return vpc_delta * _pop[state] / 1000.0


headroom = {s: max(0.0, _visitors_m(_med_vpc - by_vpc, s))
            for s, by_vpc in df.set_index("state")["visitors_per_capita_2024"].items()
            if s in _candidates}

excess = {s: max(0.0, _visitors_m(by_vpc - _med_vpc, s))
          for s, by_vpc in df.set_index("state")["visitors_per_capita_2024"].items()
          if s in _saturated}

# ---- Feasibility cap ----
# Origin similarity compares the SHAPE of a destination's origin mix, not its SIZE.
# Sabah's non-local visitors come from Selangor and KL like everyone else's, so it
# scores a high match — but only 20% of Sabah's tourists come from the peninsula at
# all (75% are Sabahans). Uncapped, the model proposed quadrupling peninsula-to-Sabah
# travel, which needs flights and is not credible as sustainable redistribution.
#
# Rule: a route may not more than DOUBLE the journey that already exists between the
# source's origin markets and that target. Anything above the cap is reported as
# unplaceable rather than silently recommended.
FEASIBILITY_MULTIPLE = 1.0   # allow at most +100% on the existing flow
_v_per_t = 2.72              # national visitors:tourists ratio, to compare like with like


CORE_ORIGIN_N = 5


def _core_origins(src, tgt):
    """The `CORE_ORIGIN_N` states that supply most of this source's visitors.

    The target is excluded from its own origin list. Sabah and Sarawak draw 75% and
    65% of their tourists from themselves, so leaving them in would count a state's
    internal tourism as evidence that outsiders travel there."""
    return [o for o in _mix[src].nlargest(CORE_ORIGIN_N + 1).index if o != tgt][:CORE_ORIGIN_N]


def route_cap(src, tgt):
    """Max ADDITIONAL visitors this route can carry, in millions.

    Existing flow = tourists the target already receives from the very states that
    supply the source. Summed, not averaged — a total volume, so a target those
    origins simply do not travel to gets a small cap however similar its origin
    *mix* looks."""
    if src not in _mix.columns or tgt not in OD.columns:
        return float("inf")
    existing_k = float(OD.loc[_core_origins(src, tgt), tgt].sum())   # thousand tourists
    return existing_k / 1000.0 * _v_per_t * FEASIBILITY_MULTIPLE


_alloc = []
_capped = []
for src in sorted(excess, key=excess.get, reverse=True):
    if src not in _mix.columns:
        continue
    remaining = excess[src]
    ranked = sorted(
        ((c, origin_similarity(src, c)) for c in _candidates if headroom.get(c, 0) > 0),
        key=lambda t: t[1] * _ready.get(t[0], 0), reverse=True,
    )
    for tgt, sim in ranked:
        if remaining <= 0.01:
            break
        cap = route_cap(src, tgt)
        take = min(remaining, headroom[tgt], cap)
        if cap < min(remaining, headroom[tgt]):
            _capped.append({"source": src, "target": tgt,
                            "blocked_m": min(remaining, headroom[tgt]) - cap})
        if take <= 0.01:
            continue
        _alloc.append({"source": src, "target": tgt, "visitors_m": take,
                       "overlap": sim, "readiness": _ready[tgt]})
        headroom[tgt] -= take
        remaining -= take
    if remaining > 0.01:
        _alloc.append({"source": src, "target": None, "visitors_m": remaining,
                       "overlap": np.nan, "readiness": np.nan})

alloc = pd.DataFrame(_alloc)
placed = alloc[alloc["target"].notna()] if len(alloc) else alloc
unplaced = alloc[alloc["target"].isna()] if len(alloc) else alloc

# top target per source, kept so single-value consumers still work
_top = (placed.sort_values("visitors_m", ascending=False)
        .drop_duplicates("source").set_index("source")) if len(placed) else pd.DataFrame()
df["recommended_redirect"] = df["state"].map(_top["target"]) if len(_top) else None
df["origin_overlap"] = df["state"].map(_top["overlap"]) if len(_top) else np.nan

rec_rows = df[df["recommended_redirect"].notna()].sort_values("saturation_calc", ascending=False)
by_state = df.set_index("state")

# ============================ HEADER ============================
h1, h2 = st.columns([3, 1])
with h1:
    # inline styles: Streamlit's own <p> rules outrank a plain class selector here
    st.markdown(
        f'<div style="font-size:2rem;font-weight:800;color:{TEXT};line-height:1.1;'
        f'margin:0 0 2px 0;">Tourism Load-Balancer</div>'
        f'<div style="font-size:.86rem;color:{TEXT_MUTED};">'
        f'Redistributing domestic tourism demand across Malaysian states</div>',
        unsafe_allow_html=True,
    )
with h2:
    st.markdown(
        f'<div style="text-align:right;font-size:.8rem;color:{TEXT_MUTED};line-height:1.5;'
        f'margin-top:.5rem;">'
        f'Showing data for<br><b style="color:{TEXT};font-size:.95rem;">Malaysia · 2024</b></div>',
        unsafe_allow_html=True,
    )

st.info(
    "**All figures are real official statistics.** Visitors, receipts, ALOS and expenditure from "
    "the DOSM Domestic Tourism Survey 2024/2025; hotel and room counts from NAPIC; population, "
    "household income and amenity access from OpenDOSM; state boundaries from DOSM open geodata. "
    "Saturation, readiness and the redirect recommendations are **derived** — see the panels below "
    "for how each is calculated. Full provenance in `data/manifest.json` and `data/SOURCES.md`."
)

# ============================ KPI STRIP ============================
tot_2024 = df["visitors_2024_millions"].sum()
tot_2023 = df["visitors_2023_millions"].sum()
yoy = (tot_2024 - tot_2023) / tot_2023 * 100

# 2025 state totals exist and are verified against the national quarterly bulletins,
# but 2025 per-state DETAIL (receipts, ALOS, income class) has not been published.
# The headline therefore stays on 2024 to match every panel below it, with 2025
# carried as a secondary line so the dashboard cannot be caught out on recency.
_has25 = "visitors_2025_millions" in df.columns
tot_2025 = df["visitors_2025_millions"].sum() if _has25 else None
yoy25 = (tot_2025 - tot_2024) / tot_2024 * 100 if _has25 else None

# The threshold on the raw scale, for display. SATURATION_THRESHOLD is on the
# min-max normalised scale and means nothing to a reader.
# Note this is a RELATIVE cutoff — the 66th percentile of the current 16 states —
# not a published carrying-capacity limit. No such standard exists for Malaysia.
_raw_cut = df["visitors_per_capita_2024"].quantile(0.66)
_flagged_names = (
    df[df["saturation_calc"] >= SATURATION_THRESHOLD]
    .sort_values("visitors_per_capita_2024", ascending=False)["state"]
    .str.replace("W.P. ", "", regex=False)
    .str.replace("Negeri Sembilan", "N. Sembilan", regex=False)
    .tolist()
)

kpis = [
    ("🧳", f"{tot_2024:,.1f}M", "Total 2024 visitors", f"▲ {yoy:.1f}% vs 2023", "up",
     f"2025: {tot_2025:,.1f}M (▲{yoy25:.1f}%) — totals only, no state detail published"
     if _has25 else None),
    ("🛏️", f"{df['visitors_per_capita_2024'].max():.1f}", "Peak visitors per resident",
     f"vs {df['visitors_per_capita_2024'].min():.1f} lowest", "flat", None),
    ("🔥", f"{int((df['saturation_calc'] >= SATURATION_THRESHOLD).sum())}", "Most pressured states",
     f"top third · above {_raw_cut:.1f} per resident", "flat",
     ", ".join(_flagged_names)),
    ("🎯", f"{placed['visitors_m'].sum():.1f}M", "Demand reallocated",
     f"{len(placed)} routes" + (f" · {unplaced['visitors_m'].sum():.1f}M unplaced" if len(unplaced) else ""),
     "flat", None),
]
kcols = st.columns(4)
for col, (ico, val, lab, delta, cls, sub) in zip(kcols, kpis):
    with col:
        with st.container(border=True):
            st.markdown(
                f'<div class="kpi"><span class="kpi-ico">{ico}</span><span>'
                f'<span class="kpi-val">{val}</span>'
                f'<span class="kpi-delta {cls}">{delta}</span>'
                f'<div class="kpi-lab">{lab}</div>'
                + (f'<div class="kpi-sub">{sub}</div>' if sub else "")
                + "</span></div>",
                unsafe_allow_html=True,
            )

# ============================ ROW 1: MAP (full width hero) ============================
with st.container(border=True):
    _sel = by_state.loc["Selangor", "visitors_per_capita_2024"] if "Selangor" in by_state.index else None
    card_head("The pressure sits in a corridor — and Selangor is the hole in it",
              "colour = visitors per resident")
    card_sub(
        "Four of the six most pressured territories — Putrajaya, Kuala Lumpur, Negeri "
        "Sembilan and Melaka — form a continuous strip down the west coast. "
        f"<b>Selangor, which physically surrounds Kuala Lumpur and Putrajaya, is one of the "
        f"calmest states at {_sel:.1f} visitors per resident.</b> The strain is concentrated in "
        "the small territories embedded beside it, not in the region as a whole. "
        "Pahang and Terengganu on the east coast are a separate pattern."
    )

    # Quantile bands, not equal-interval: the score clusters, and equal steps would
    # flatten most states into one class. Exact figures stay in the tooltip.
    n_bands = min(5, df["saturation_calc"].nunique())
    df["sat_band"] = pd.qcut(df["saturation_calc"], q=n_bands, labels=BAND_LABELS[:n_bands],
                             duplicates="drop")

    def build_map(lat_range, lon_range, labels, height, show_legend):
        """One choropleth panel. Malaysia is drawn as two panels because a single
        national map spends most of its area on the South China Sea, shrinking the
        peninsula — where four of the six pressured territories sit — to illegibility."""
        fig = px.choropleth(
            df, geojson=GEO, locations="geo_name", featureidkey="properties.state",
            color="sat_band",
            category_orders={"sat_band": BAND_LABELS[:n_bands]},
            color_discrete_map=BAND_COLORS,
            hover_name="state",
            hover_data={"geo_name": False, "sat_band": False,
                        "visitors_2024_millions": ":.1f", "saturation_calc": ":.2f"},
        )
        fig.update_traces(marker_line=dict(color="#ffffff", width=0.8))
        fig.update_geos(visible=False, bgcolor="rgba(0,0,0,0)",
                        lataxis_range=lat_range, lonaxis_range=lon_range)

        # Area-bias fix: a choropleth sizes by land area, but Kuala Lumpur and
        # Putrajaya are the 4th and 1st most pressured territories and render as
        # specks inside Selangor. Leader lines pull them out over the water.
        for name, (lab_lat, lab_lon) in labels.items():
            row = df[df["state"] == name]
            if row.empty:
                continue
            r = row.iloc[0]
            fig.add_trace(go.Scattergeo(
                lat=[r["lat"], lab_lat], lon=[r["lon"], lab_lon],
                mode="lines", line=dict(width=1, color="#9aa5b1"),
                hoverinfo="skip", showlegend=False,
            ))
            fig.add_trace(go.Scattergeo(
                lat=[lab_lat], lon=[lab_lon], mode="text",
                text=[f"{r['state'].replace('W.P. ', '')} {r['visitors_per_capita_2024']:.1f}"],
                textfont=dict(size=10, color=TEXT),
                textposition="middle right",
                hoverinfo="skip", showlegend=False,
            ))

        style_fig(fig, height=height)
        fig.update_layout(
            showlegend=show_legend,
            legend=dict(orientation="h", yanchor="bottom", y=-0.04, x=0,
                        font=dict(color=TEXT_MUTED, size=10), title=None,
                        itemsizing="constant"),
        )
        return fig

    m1, m2 = st.columns([1, 1.35])
    with m1:
        st.plotly_chart(
            build_map([0.9, 7.4], [99.2, 105.6], PENINSULA_LABELS, 430, True),
            width="stretch", theme=None,
        )
    with m2:
        st.plotly_chart(
            build_map([0.5, 7.6], [108.8, 119.6], BORNEO_LABELS, 430, False),
            width="stretch", theme=None,
        )


# ============================ ROW: TREND + INCOME DONUT ============================
r1a, r1b = st.columns([2, 1])

with r1a:
    with st.container(border=True):
        top_press = df.nlargest(1, "visitors_per_capita_2024").iloc[0]
        _big_calm = df[(df["visitors_2024_millions"] > df["visitors_2024_millions"].median())
                       & (df["saturation_calc"] < SATURATION_THRESHOLD)]

        card_head("The imbalance is spatial, not seasonal",
                  f"peak {top_press['state']} · {top_press['visitors_per_capita_2024']:.1f} per resident")
        card_sub(
            "Quarterly demand is flat nationally (24.0 / 25.4 / 25.0 / 25.5%), so there is no "
            "seasonal peak to move. <b>Counting visitors misleads you</b> — states to the right "
            "receive the most, but only those high up are actually crowded. "
            f"<b>{', '.join(_big_calm.nlargest(3, 'visitors_2024_millions')['state'].str.replace('W.P. ', '', regex=False))}</b> "
            "take large numbers comfortably; the gold states carry far fewer people much harder."
        )

        fig_cap = go.Figure()
        fig_cap.add_trace(go.Scatter(
            x=df["visitors_2024_millions"], y=df["visitors_per_capita_2024"],
            mode="markers+text",
            marker=dict(
                # size = population, so the chart carries both halves of the ratio:
                # x is visitors, bubble is residents, y is the two divided
                size=np.sqrt(df["population_thousands"]) * 0.45,
                color=np.where(df["saturation_calc"] >= SATURATION_THRESHOLD, GOLD, GREEN),
                line=dict(width=1, color="#ffffff"), opacity=0.9,
            ),
            text=df["state"].str.replace("W.P. ", "", regex=False),
            textposition="top center", textfont=dict(size=9, color=TEXT_MUTED),
            customdata=np.stack([df["population_thousands"], df["rooms_total"]], axis=-1),
            hovertemplate=("<b>%{text}</b><br>%{y:.1f} visitors per resident<br>"
                           "%{x:.1f}M visitors · %{customdata[0]:,.0f}k residents<br>"
                           "%{customdata[1]:,.0f} rooms<extra></extra>"),
        ))
        fig_cap.add_hline(y=df["visitors_per_capita_2024"].median(), line_dash="dash",
                          line_color=GREY, line_width=1,
                          annotation_text="median intensity", annotation_position="top left",
                          annotation_font=dict(color=TEXT_MUTED, size=10))
        fig_cap.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, ticksuffix="M",
                             title=dict(text="Total visitors, 2024",
                                        font=dict(color=TEXT_MUTED, size=11)),
                             tickfont=dict(color=TEXT_MUTED, size=10))
        fig_cap.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False,
                             title=dict(text="Visitors per resident", font=dict(color=TEXT_MUTED, size=11)),
                             tickfont=dict(color=TEXT_MUTED, size=10))
        style_fig(fig_cap, height=270)
        fig_cap.update_layout(margin=dict(l=55, r=10, t=16, b=45))
        st.plotly_chart(fig_cap, width="stretch", theme=None)

with r1b:
    with st.container(border=True):
        # Weight each state's income distribution by its visitor volume to get the
        # national picture. NOTE: state_summary carries a single `income_bracket`
        # per state — that is the *dominant* band, not a distribution, and must not
        # be summed as if it were one.
        _inc = INCOME.merge(df[["state", "visitors_2024_millions"]], on="state")
        _inc["visitors_m"] = _inc["share_pct_2024"] / 100 * _inc["visitors_2024_millions"]
        inc = (_inc.groupby("income_class")["visitors_m"].sum()
               .reindex(INCOME_ORDER).fillna(0).reset_index())
        inc["share"] = inc["visitors_m"] / inc["visitors_m"].sum() * 100
        top = inc.loc[inc["share"].idxmax()]
        _mid = inc[inc["income_class"].isin(["RM1,001-3,000", "RM3,001-5,000"])]["share"].sum()

        card_head("Who's visiting", "household income, 2024")
        card_sub(f"No band dominates — the largest is {top['income_class']} at "
                 f"<b>{top['share']:.0f}%</b>, and <b>{_mid:.0f}%</b> of visitors come from "
                 "households earning RM1,001–5,000.")

        fig_inc = go.Figure(go.Pie(
            labels=inc["income_class"], values=inc["visitors_m"],
            hole=0.62, sort=False,
            marker=dict(colors=[INCOME_COLORS[b] for b in inc["income_class"]],
                        line=dict(color=CARD, width=2)),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value:.1f}M visitors · %{percent}<extra></extra>",
        ))
        style_fig(fig_inc, height=170)
        st.plotly_chart(fig_inc, width="stretch", theme=None)

        for _, r in inc.iterrows():
            st.markdown(
                f'<div class="rank-row"><span class="rank-name">'
                f'<span style="color:{INCOME_COLORS[r["income_class"]]}">●</span> '
                f'{r["income_class"]}</span>'
                f'<span class="rank-val">{r["share"]:.0f}%</span></div>',
                unsafe_allow_html=True,
            )


# ============================ ROW 3: ALLOCATION + DISTRICTS ============================
r3a, r3b = st.columns([1, 2])

with r3a:
    with st.container(border=True):
        card_head("Redirect allocation", f"{len(placed)} routes · {placed['visitors_m'].sum():.1f}M placed")
        card_sub("Matched on shared origin markets, capped twice: by how much the target can "
                 "absorb before reaching the national median, and by <b>no more than doubling a "
                 "journey people already make</b>.")
        for _, r in placed.iterrows():
            st.markdown(
                f'<div class="rank-row"><span class="rank-name">{r["source"]}<br>'
                f'<span class="rank-to">→ {r["target"]}</span></span>'
                f'<span class="rank-val">{r["visitors_m"]:.2f}M</span></div>',
                unsafe_allow_html=True,
            )
        if len(unplaced):
            tot = unplaced["visitors_m"].sum()
            st.markdown(
                f'<div class="rank-row"><span class="rank-name" style="color:{GOLD}">'
                f'Cannot be placed<br><span class="rank-to">no realistic target has headroom</span></span>'
                f'<span class="rank-val" style="color:{GOLD}">{tot:.2f}M</span></div>',
                unsafe_allow_html=True,
            )
        if _capped:
            _cap_df = pd.DataFrame(_capped)
            _worst = _cap_df.nlargest(1, "blocked_m").iloc[0]
            st.caption(
                f"Feasibility cap blocked **{_cap_df['blocked_m'].sum():.1f}M** of otherwise "
                f"available headroom — mostly **{_worst['target']}**, which has room but "
                "receives few visitors from these origins today. Filling it would mean "
                "several times the current cross-country travel, which is not credible "
                "redistribution."
            )


with r3b:
    _targets = [t for t in placed["target"].dropna().unique() if t in set(DIST["state"])]
    if _targets:
        with st.container(border=True):
            _d = DIST[DIST["state"].isin(_targets)].sort_values(["state", "rank"])
            _risk = _d[_d["piped_water"] < WATER_FLOOR]

            card_head("Where inside each target state",
                      f"{len(_d)} districts across {len(_targets)} states")
            card_sub(
                "The allocator routes demand between states; these are the most-visited "
                "districts inside the states it selected, with their accommodation stock. "
                f"<b>Rank is ordinal</b> — position within its own state, not a count and not "
                f"comparable across states. Bars show premises (2021, the most recent district "
                f"count DOSM publishes). Gold marks districts below {WATER_FLOOR:.0f}% piped-water "
                "coverage."
            )

            _d = _d.assign(
                label=_d["district"] + "  (" + _d["state"].str.replace("W.P. ", "", regex=False)
                + " #" + _d["rank"].astype(int).astype(str) + ")",
                flag=np.where(_d["piped_water"] < WATER_FLOOR, "Below water floor", "Adequate"),
            ).sort_values("accommodation_premises")

            fig_d = go.Figure(go.Bar(
                x=_d["accommodation_premises"], y=_d["label"], orientation="h",
                marker=dict(color=np.where(_d["piped_water"] < WATER_FLOOR, GOLD, GREEN),
                            line=dict(width=0)),
                width=0.62,
                customdata=np.stack([_d["piped_water"], _d["population_thousands"],
                                     _d["homestay_clusters"].fillna(0)], axis=-1),
                hovertemplate=("<b>%{y}</b><br>%{x:,.0f} accommodation premises (2021)<br>"
                               "%{customdata[0]:.1f}% piped water<br>"
                               "%{customdata[1]:,.0f}k residents · %{customdata[2]:.0f} homestay clusters"
                               "<extra></extra>"),
            ))
            fig_d.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False,
                               title=dict(text="Accommodation premises (2021)",
                                          font=dict(color=TEXT_MUTED, size=11)),
                               tickfont=dict(color=TEXT_MUTED, size=10))
            fig_d.update_yaxes(showgrid=False, tickfont=dict(color=TEXT, size=10), automargin=True)
            style_fig(fig_d, height=max(240, 26 * len(_d)))
            fig_d.update_layout(margin=dict(l=10, r=20, t=6, b=45))
            st.plotly_chart(fig_d, width="stretch", theme=None)

            if len(_risk):
                worst = _risk.nsmallest(1, "piped_water").iloc[0]
                st.warning(
                    f"**{len(_risk)} of these districts sit below {WATER_FLOOR:.0f}% piped-water "
                    f"coverage.** {worst['district']} is the #{int(worst['rank'])} most-visited "
                    f"district in {worst['state']} on **{worst['piped_water']:.1f}%** coverage for "
                    f"{worst['population_thousands']:,.0f}k residents. Directing additional demand "
                    "here without water investment would shift the burden onto residents rather "
                    "than relieve it — these are capacity-building targets, not redirect targets."
                )


# ============================ ROW: THREE SMALL PANELS ============================
r4a, r4b, r4c = st.columns(3)

with r4a:
    with st.container(border=True):
        g = df.nlargest(8, "visitor_growth_pct").sort_values("visitor_growth_pct")
        card_head("Fastest growing", "top 8 · 2023 → 2024")
        card_sub(f"<b>{g.iloc[-1]['state']}</b> leads at {g.iloc[-1]['visitor_growth_pct']:.1f}%.")
        fig_g = go.Figure(go.Bar(
            x=g["visitor_growth_pct"], y=g["state"], orientation="h",
            marker=dict(color=GREEN, line=dict(width=0)), width=0.55,
            text=[f"{v:.0f}%" for v in g["visitor_growth_pct"]],
            textposition="outside", textfont=dict(color=TEXT_MUTED, size=11),
            hovertemplate="<b>%{y}</b><br>%{x:.1f}% growth<extra></extra>",
        ))
        fig_g.update_xaxes(visible=False, range=[0, g["visitor_growth_pct"].max() * 1.22])
        fig_g.update_yaxes(showgrid=False, tickfont=dict(color=TEXT, size=11), automargin=True)
        style_fig(fig_g, height=280)
        st.plotly_chart(fig_g, width="stretch", theme=None)

with r4b:
    with st.container(border=True):
        a = df.copy()
        a["dev"] = a["alos_nights"] - NATIONAL_ALOS
        a = a.sort_values("dev")
        n_above = int((a["dev"] >= 0).sum())
        card_head("Length of stay", f"vs national {NATIONAL_ALOS} nights")
        card_sub(f"<b>{n_above} of 16</b> states hold visitors at or above the national average.")
        fig_a = go.Figure(go.Bar(
            x=a["dev"], y=a["state"], orientation="h",
            marker=dict(color=np.where(a["dev"] >= 0, GREEN, GOLD), line=dict(width=0)),
            width=0.6,
            hovertemplate="<b>%{y}</b><br>%{customdata:.2f} nights<extra></extra>",
            customdata=a["alos_nights"],
        ))
        fig_a.add_vline(x=0, line_color=GREY, line_width=1)
        fig_a.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False,
                           tickfont=dict(color=TEXT_MUTED, size=10), title=None)
        fig_a.update_yaxes(showgrid=False, tickfont=dict(color=TEXT, size=10), automargin=True)
        style_fig(fig_a, height=280)
        st.plotly_chart(fig_a, width="stretch", theme=None)

with r4c:
    with st.container(border=True):
        shop = df["shopping_spend_rm_m"].sum()
        fnb = df["fnb_spend_rm_m"].sum()
        card_head("Where the money goes", "national mix")
        card_sub(f"Shopping is <b>{shop / (shop + fnb) * 100:.0f}%</b> of tracked visitor spend.")
        fig_m = go.Figure(go.Pie(
            labels=["Shopping", "Food & beverage"], values=[shop, fnb],
            hole=0.62, sort=False,
            marker=dict(colors=[GREEN, GOLD], line=dict(color=CARD, width=2)),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>RM %{value:,.0f}M · %{percent}<extra></extra>",
        ))
        style_fig(fig_m, height=170)
        st.plotly_chart(fig_m, width="stretch", theme=None)
        for lab, val, col in [("Shopping", shop, GREEN), ("Food & beverage", fnb, GOLD)]:
            st.markdown(
                f'<div class="rank-row"><span class="rank-name">'
                f'<span style="color:{col}">●</span> {lab}</span>'
                f'<span class="rank-val">RM {val:,.0f}M</span></div>',
                unsafe_allow_html=True,
            )

# ============================ ROW: READINESS + IMPACT ============================
r4a, r4b = st.columns(2)

with r4a:
    with st.container(border=True):
        card_head("Why each target was picked", "the three factors behind each match")
        card_sub("A target must already draw the same travellers (<b>origin overlap</b>, from the "
                 "2025 O-D matrix), have room to absorb them (<b>spare capacity</b>) and the "
                 "amenities to host them. Each bar shows all three, normalised 0–1.")
        rows = []
        for _, r in placed.iterrows():
            t = by_state.loc[r["target"]]
            lab = f'{r["source"]} → {r["target"]} ({r["visitors_m"]:.1f}M)'
            rows.append({"route": lab, "Factor": "Origin overlap", "v": r["overlap"]})
            rows.append({"route": lab, "Factor": "Spare capacity", "v": t["headroom_norm"]})
            rows.append({"route": lab, "Factor": "Amenities", "v": t["amenities_norm"]})
        bd = pd.DataFrame(rows)
        fig_b = px.bar(bd, x="v", y="route", color="Factor", orientation="h", barmode="stack",
                       color_discrete_map={"Origin overlap": GREEN, "Spare capacity": GOLD,
                                           "Amenities": GREY})
        fig_b.update_traces(marker_line_width=0, width=0.6)
        fig_b.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, title=None,
                           tickfont=dict(color=TEXT_MUTED, size=10))
        fig_b.update_yaxes(showgrid=False, title=None, autorange="reversed",
                           tickfont=dict(color=TEXT, size=10), automargin=True)
        style_fig(fig_b, height=250)
        fig_b.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0,
                        font=dict(color=TEXT_MUTED, size=10), title=None),
        )
        st.plotly_chart(fig_b, width="stretch", theme=None)

with r4b:
    with st.container(border=True):
        _total_impact = 0.0
        _cards = []
        for _, r in placed.iterrows():
            t = by_state.loc[r["target"]]
            # observed shopping + F&B spend per visitor in the target state, applied
            # to the volume actually allocated to it
            per_visitor_rm = ((t["shopping_spend_rm_m"] + t["fnb_spend_rm_m"])
                              / t["visitors_2024_millions"])
            impact = r["visitors_m"] * per_visitor_rm
            _total_impact += impact
            _cards.append((r["source"], r["target"], r["visitors_m"], per_visitor_rm, impact))

        card_head("Community impact", f"RM {_total_impact:,.0f}M across {len(_cards)} routes")
        card_sub("Allocated visitors × the target's <b>observed</b> shopping + F&B spend per "
                 "visitor. <b>Not a forecast</b> — it assumes redirected visitors spend like "
                 "existing ones and models no elasticity, displacement or price response.")
        for src, tgt, vol, ppv, impact in _cards:
            st.markdown(
                f'<div class="imp"><div class="imp-route">{src} → {tgt}</div>'
                f'<div class="imp-line"><span class="imp-txt">{vol:.2f}M visitors × '
                f'RM {ppv:,.0f}/visitor</span>'
                f'<span class="imp-val">RM {impact:,.0f}M</span></div></div>',
                unsafe_allow_html=True,
            )

# ============================ DETAIL ============================
with st.expander("Show all 16 states and their scores"):
    st.dataframe(
        df[["state", "region_cluster", "visitors_2024_millions", "visitor_growth_pct",
            "income_bracket", "shopping_spend_rm_m", "fnb_spend_rm_m", "alos_nights",
            "saturation_calc", "readiness_calc", "recommended_redirect"]].round(2),
        width="stretch", hide_index=True,
    )

st.caption(
    "Sources: DOSM Domestic Tourism Survey 2024 & 2025 · NAPIC hotel supply 2024 · "
    "OpenDOSM population, household income and amenity access · DOSM open geodata. "
    "Full provenance and SHA-256 checksums in data/manifest.json · DOSM Datathon 2026"
)
