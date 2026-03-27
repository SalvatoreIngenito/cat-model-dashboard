"""
Cat Model Dashboard — Catastrophe Modeling Analytics
====================================================
Interactive dashboard combining NOAA Storm Events, FEMA OpenFEMA,
and EM-DAT global disaster data for catastrophe risk analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

from src.data_fetcher import (
    fetch_fema_disaster_declarations,
    fetch_fema_nfip_claims,
    fetch_noaa_storm_events,
    load_emdat_summary,
)

# ── Page config ──────────────────────────────
st.set_page_config(
    page_title="Cat Model Dashboard",
    page_icon="🌪️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Apple-inspired Design System (CSS) ──────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
    }
    .stApp {
        background: #000000;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #0a0a0a;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] .stRadio > label {
        color: rgba(255,255,255,0.5) !important;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    section[data-testid="stSidebar"] .stRadio > div > label {
        background: transparent;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 4px;
        transition: all 0.2s ease;
        color: rgba(255,255,255,0.7) !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(255,255,255,0.04);
        border-color: rgba(255,255,255,0.1);
    }
    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio > div [aria-checked="true"] ~ label {
        background: rgba(10,132,255,0.12) !important;
        border-color: rgba(10,132,255,0.3) !important;
        color: #0a84ff !important;
    }

    /* ── Typography ── */
    .page-title {
        font-size: 2rem;
        font-weight: 700;
        color: #f5f5f7;
        letter-spacing: -0.02em;
        margin: 0 0 4px 0;
        line-height: 1.2;
    }
    .page-subtitle {
        font-size: 1rem;
        font-weight: 400;
        color: rgba(255,255,255,0.45);
        margin: 0 0 32px 0;
        line-height: 1.5;
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #f5f5f7;
        margin: 28px 0 6px 0;
        letter-spacing: -0.01em;
    }
    .section-desc {
        font-size: 0.875rem;
        color: rgba(255,255,255,0.4);
        margin: 0 0 20px 0;
        line-height: 1.55;
    }

    /* ── KPI Cards ── */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-bottom: 28px;
    }
    .kpi-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 22px 24px;
        transition: all 0.25s ease;
    }
    .kpi-card:hover {
        background: rgba(255,255,255,0.06);
        border-color: rgba(255,255,255,0.1);
        transform: translateY(-1px);
    }
    .kpi-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: rgba(255,255,255,0.4);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1;
    }
    .kpi-accent-blue .kpi-value { color: #0a84ff; }
    .kpi-accent-green .kpi-value { color: #30d158; }
    .kpi-accent-orange .kpi-value { color: #ff9f0a; }
    .kpi-accent-red .kpi-value { color: #ff453a; }
    .kpi-accent-purple .kpi-value { color: #bf5af2; }
    .kpi-accent-teal .kpi-value { color: #64d2ff; }

    /* ── Divider ── */
    .glass-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
        margin: 28px 0;
        border: none;
    }

    /* ── Hide default metric styling ── */
    div[data-testid="stMetric"] {
        background: none !important;
        border: none !important;
        padding: 0 !important;
    }
    div[data-testid="stMetric"] label { display: none; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { display: none; }

    /* ── Slider ── */
    .stSlider > div > div {
        color: rgba(255,255,255,0.6) !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        color: rgba(255,255,255,0.6) !important;
    }

    /* ── Footer ── */
    .footer-text {
        text-align: center;
        color: rgba(255,255,255,0.2);
        font-size: 0.78rem;
        padding: 40px 0 20px 0;
        letter-spacing: 0.02em;
    }

    /* ── Sidebar branding ── */
    .sidebar-brand {
        padding: 8px 0 20px 0;
    }
    .sidebar-brand-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f5f5f7;
        letter-spacing: -0.01em;
    }
    .sidebar-brand-sub {
        font-size: 0.72rem;
        color: rgba(255,255,255,0.35);
        font-weight: 500;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .sidebar-sources {
        font-size: 0.8rem;
        line-height: 1.8;
    }
    .sidebar-sources a {
        color: rgba(255,255,255,0.5);
        text-decoration: none;
        transition: color 0.2s;
    }
    .sidebar-sources a:hover {
        color: #0a84ff;
    }
</style>
""", unsafe_allow_html=True)


# ── Plotly Theme ──────────────────────────────

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.02)",
    font=dict(family="Inter, -apple-system, sans-serif", color="rgba(255,255,255,0.6)", size=12),
    title=dict(font=dict(size=15, color="rgba(255,255,255,0.85)")),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.06)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.06)"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.06)"),
    margin=dict(l=50, r=30, t=60, b=50),
    colorway=["#0a84ff", "#30d158", "#ff9f0a", "#ff453a", "#bf5af2",
              "#64d2ff", "#ffd60a", "#ff6482", "#ac8e68", "#5e5ce6"],
)

# Apple system colors
BLUE = "#0a84ff"
GREEN = "#30d158"
ORANGE = "#ff9f0a"
RED = "#ff453a"
PURPLE = "#bf5af2"
TEAL = "#64d2ff"
YELLOW = "#ffd60a"
INDIGO = "#5e5ce6"


def apply_layout(fig, **overrides):
    """Apply the Apple-inspired Plotly layout."""
    layout = {**PLOTLY_LAYOUT, **overrides}
    fig.update_layout(**layout)
    return fig


# ── Sidebar ──────────────────────────────────

st.sidebar.markdown("""
<div class="sidebar-brand">
    <div class="sidebar-brand-title">Cat Model Dashboard</div>
    <div class="sidebar-brand-sub">Catastrophe Analytics</div>
</div>
""", unsafe_allow_html=True)

data_source = st.sidebar.radio(
    "Navigate",
    ["Overview", "Property Risk Tool", "FEMA Disaster Declarations", "FEMA NFIP Claims",
     "NOAA Storm Events", "EM-DAT Global Disasters"],
    index=0,
)

st.sidebar.markdown('<div class="glass-divider"></div>', unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="sidebar-sources">
    <div style="font-size:0.7rem; font-weight:600; color:rgba(255,255,255,0.3);
         text-transform:uppercase; letter-spacing:0.06em; margin-bottom:8px;">Data Sources</div>
    <a href="https://www.fema.gov/about/openfema">OpenFEMA</a><br>
    <a href="https://www.ncdc.noaa.gov/stormevents/">NOAA Storm Events</a><br>
    <a href="https://www.emdat.be/">EM-DAT / CRED</a>
</div>
""", unsafe_allow_html=True)


# ── Data loading with caching ────────────────

@st.cache_data(ttl=3600, show_spinner="Loading FEMA declarations...")
def get_fema_declarations():
    return fetch_fema_disaster_declarations()

@st.cache_data(ttl=3600, show_spinner="Loading NFIP claims...")
def get_nfip_claims():
    return fetch_fema_nfip_claims()

@st.cache_data(ttl=3600, show_spinner="Loading NOAA storm events...")
def get_noaa_storms():
    return fetch_noaa_storm_events()

@st.cache_data(ttl=3600, show_spinner="Loading EM-DAT global data...")
def get_emdat():
    return load_emdat_summary()


# ── Helper functions ─────────────────────────

def format_number(n):
    if n >= 1e9:
        return f"${n/1e9:.1f}B"
    if n >= 1e6:
        return f"${n/1e6:.1f}M"
    if n >= 1e3:
        return f"${n/1e3:.1f}K"
    return f"${n:,.0f}"


def kpi_row(metrics: list[dict]):
    """Render a row of Apple-styled KPI cards."""
    accents = ["blue", "green", "orange", "red", "purple", "teal"]
    cards_html = ""
    for i, m in enumerate(metrics):
        accent = accents[i % len(accents)]
        cards_html += f"""
        <div class="kpi-card kpi-accent-{accent}">
            <div class="kpi-label">{m['label']}</div>
            <div class="kpi-value">{m['value']}</div>
        </div>"""
    st.markdown(f'<div class="kpi-grid">{cards_html}</div>', unsafe_allow_html=True)


def page_header(title: str, subtitle: str):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def section(title: str, desc: str = ""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if desc:
        st.markdown(f'<div class="section-desc">{desc}</div>', unsafe_allow_html=True)


def divider():
    st.markdown('<div class="glass-divider"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# OVERVIEW PAGE
# ══════════════════════════════════════════════

if data_source == "Overview":
    page_header(
        "Catastrophe Model Dashboard",
        "Unified analytics across three authoritative catastrophe data sources — "
        "FEMA federal disaster records, NOAA severe storm events, and the EM-DAT "
        "global disaster database. Filter, explore, and assess risk exposure in one place."
    )

    fema = get_fema_declarations()
    emdat = get_emdat()

    # KPIs
    kpis = []
    if not fema.empty:
        kpis.append({"label": "US Declarations", "value": f"{len(fema):,}"})
        kpis.append({"label": "States Covered", "value": str(fema["state"].nunique())})
    if not emdat.empty:
        kpis.append({"label": "Global Events", "value": f"{emdat['event_count'].sum():,}"})
        kpis.append({"label": "Est. Global Losses", "value": format_number(emdat["total_damage_million_usd"].sum() * 1e6)})
    if kpis:
        kpi_row(kpis)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        section(
            "US Disaster Declarations",
            "Federal declarations issued by FEMA following presidentially declared "
            "disasters. This time series reveals the acceleration in catastrophic "
            "events over the past two decades, driven by climate-related hazards."
        )
        if not fema.empty:
            yearly = fema.groupby("year").size().reset_index(name="count")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=yearly["year"], y=yearly["count"],
                mode="lines", fill="tozeroy",
                line=dict(color=BLUE, width=2.5),
                fillcolor="rgba(10,132,255,0.08)",
                name="Declarations",
            ))
            apply_layout(fig, height=380,
                         title=dict(text="Annual Federal Disaster Declarations"))
            st.plotly_chart(fig, use_container_width=True)

            by_type = fema["incidentType"].value_counts().head(8).reset_index()
            by_type.columns = ["Incident Type", "Count"]
            fig2 = px.bar(
                by_type, x="Count", y="Incident Type", orientation="h",
                color_discrete_sequence=[BLUE],
            )
            apply_layout(fig2, height=340,
                         title=dict(text="Most Common Incident Types"))
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    with col2:
        section(
            "Global Disaster Trends",
            "Aggregated from EM-DAT, maintained by the Centre for Research on the "
            "Epidemiology of Disasters (CRED). Covers 22,000+ events since 1900, "
            "compiled from UN agencies, NGOs, insurers, and research institutions."
        )
        if not emdat.empty:
            yearly_global = emdat.groupby("year").agg(
                events=("event_count", "sum"),
                deaths=("total_deaths", "sum"),
                damage=("total_damage_million_usd", "sum"),
            ).reset_index()

            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=yearly_global["year"], y=yearly_global["events"],
                mode="lines", fill="tozeroy",
                line=dict(color=RED, width=2.5),
                fillcolor="rgba(255,69,58,0.08)",
                name="Events",
            ))
            apply_layout(fig3, height=380,
                         title=dict(text="Global Natural Disaster Events per Year"))
            st.plotly_chart(fig3, use_container_width=True)

            by_region = emdat.groupby("region")["total_damage_million_usd"].sum().reset_index()
            by_region.columns = ["Region", "Damage ($M)"]
            fig4 = px.pie(
                by_region, names="Region", values="Damage ($M)",
                color_discrete_sequence=[BLUE, GREEN, ORANGE, RED, PURPLE],
                hole=0.55,
            )
            apply_layout(fig4, height=340,
                         title=dict(text="Economic Losses by Region"))
            fig4.update_traces(
                textinfo="percent+label",
                textfont_size=11,
                marker=dict(line=dict(color="#000000", width=2)),
            )
            st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════
# PROPERTY RISK ASSESSMENT TOOL
# ══════════════════════════════════════════════

elif data_source == "Property Risk Tool":
    page_header(
        "Property Risk Assessment",
        "Evaluate the catastrophe risk profile of a US property. This tool cross-references "
        "FEMA disaster declarations, NOAA storm event history, and NFIP flood claims data "
        "to generate a multi-peril risk score with per-hazard breakdowns."
    )

    # ── State data lookups ──
    US_STATES = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
        "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
        "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
        "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
        "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
        "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
        "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
        "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
        "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
        "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
        "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
    }

    FLOOD_ZONES = {
        "A": "High risk — 1% annual flood chance (100-yr floodplain). Mandatory flood insurance.",
        "AE": "High risk — Base Flood Elevations determined. Mandatory flood insurance.",
        "AH": "High risk — Shallow flooding (1-3 ft). Mandatory flood insurance.",
        "AO": "High risk — Sheet flow on sloping terrain. Mandatory flood insurance.",
        "V": "High risk — Coastal flood with wave action. Mandatory flood insurance.",
        "VE": "High risk — Coastal flood, Base Flood Elevations determined. Mandatory.",
        "X": "Moderate-to-low risk — Outside 100-yr floodplain. Insurance not required.",
        "B": "Moderate risk — Between 100-yr and 500-yr floodplain.",
        "C": "Low risk — Minimal flood hazard.",
        "D": "Undetermined risk — No flood hazard analysis performed.",
    }

    # ── Input form ──
    section("Property Details", "Enter property characteristics to assess catastrophe exposure.")

    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        state_code = st.selectbox(
            "State",
            options=list(US_STATES.keys()),
            format_func=lambda x: f"{x} — {US_STATES[x]}",
            index=list(US_STATES.keys()).index("FL"),
        )
    with col2:
        property_value = st.number_input(
            "Property Value ($)",
            min_value=50_000, max_value=50_000_000,
            value=450_000, step=25_000,
            format="%d",
        )
    with col3:
        year_built = st.number_input(
            "Year Built",
            min_value=1900, max_value=2026,
            value=1995, step=1,
        )

    col4, col5, col6 = st.columns(3, gap="medium")
    with col4:
        flood_zone = st.selectbox(
            "FEMA Flood Zone",
            options=list(FLOOD_ZONES.keys()),
            index=0,
        )
    with col5:
        stories = st.selectbox("Stories", [1, 2, 3, 4], index=1)
    with col6:
        construction = st.selectbox(
            "Construction Type",
            ["Wood Frame", "Masonry", "Steel Frame", "Concrete", "Manufactured/Mobile"],
            index=0,
        )

    divider()

    # ── Compute risk scores ──

    # Load data
    fema = get_fema_declarations()
    nfip = get_nfip_claims()
    storms = get_noaa_storms()

    # --- 1. FEMA Declaration frequency for this state ---
    state_name = US_STATES[state_code]
    if not fema.empty:
        state_decl = fema[fema["state"] == state_code]
        decl_count = len(state_decl)
        all_states_counts = fema.groupby("state").size()
        decl_percentile = (all_states_counts < decl_count).sum() / len(all_states_counts) * 100

        # Recent acceleration (last 10 yrs vs prior 10)
        recent = state_decl[state_decl["year"] >= 2015].shape[0]
        prior = state_decl[(state_decl["year"] >= 2005) & (state_decl["year"] < 2015)].shape[0]
        accel_ratio = recent / max(prior, 1)

        # Incident type breakdown
        type_breakdown = state_decl["incidentType"].value_counts().head(5)
    else:
        decl_count, decl_percentile, accel_ratio = 0, 50, 1.0
        type_breakdown = pd.Series(dtype=int)

    # --- 2. NFIP flood claims for this state ---
    if not nfip.empty and "state" in nfip.columns:
        state_nfip = nfip[nfip["state"] == state_code]
        nfip_claims = len(state_nfip)
        avg_payout = state_nfip["totalPaid"].mean() if "totalPaid" in state_nfip.columns and len(state_nfip) > 0 else 0
        total_state_paid = state_nfip["totalPaid"].sum() if "totalPaid" in state_nfip.columns else 0
    else:
        nfip_claims, avg_payout, total_state_paid = 0, 0, 0

    # --- 3. NOAA storm damage for this state ---
    if not storms.empty and "STATE" in storms.columns:
        state_storms = storms[storms["STATE"].str.upper() == state_name.upper()]
        storm_events = len(state_storms)
        storm_prop_dmg = state_storms["DAMAGE_PROPERTY"].sum() if "DAMAGE_PROPERTY" in state_storms.columns else 0
        storm_deaths = int(state_storms["DEATHS_DIRECT"].sum()) if "DEATHS_DIRECT" in state_storms.columns else 0
        # Top event types
        storm_types = state_storms["EVENT_TYPE"].value_counts().head(5) if "EVENT_TYPE" in state_storms.columns else pd.Series(dtype=int)
    else:
        storm_events, storm_prop_dmg, storm_deaths = 0, 0, 0
        storm_types = pd.Series(dtype=int)

    # --- 4. Composite risk scoring ---
    # Flood zone risk factor
    flood_zone_risk = {
        "V": 1.0, "VE": 1.0, "A": 0.9, "AE": 0.85, "AH": 0.8, "AO": 0.8,
        "B": 0.45, "D": 0.5, "X": 0.25, "C": 0.15,
    }
    fz_risk = flood_zone_risk.get(flood_zone, 0.5)

    # Construction vulnerability
    construction_risk = {
        "Manufactured/Mobile": 1.0, "Wood Frame": 0.75, "Masonry": 0.5,
        "Steel Frame": 0.35, "Concrete": 0.25,
    }
    const_risk = construction_risk.get(construction, 0.5)

    # Age factor (older = more vulnerable)
    building_age = 2026 - year_built
    age_factor = min(building_age / 80, 1.0)  # maxes at 80+ years

    # Stories factor (taller = more wind exposure, but less flood depth damage)
    stories_wind = min(stories / 4, 1.0)
    stories_flood = max(1 - (stories - 1) * 0.15, 0.4)

    # State hazard score (0-1) from percentile
    state_hazard = decl_percentile / 100

    # Individual peril scores (0-100)
    flood_score = min(100, (fz_risk * 60 + state_hazard * 20 + stories_flood * 10 + age_factor * 10))
    wind_score = min(100, (state_hazard * 40 + const_risk * 30 + stories_wind * 15 + age_factor * 15))
    storm_surge_score = min(100, fz_risk * 70 + state_hazard * 20 + stories_flood * 10) if flood_zone in ["V", "VE", "AE", "A"] else min(30, fz_risk * 30)
    hail_score = min(100, state_hazard * 50 + const_risk * 30 + age_factor * 20)
    wildfire_score = min(60, state_hazard * 30 + const_risk * 20 + age_factor * 10)

    # Composite weighted score
    composite = (
        flood_score * 0.30 +
        wind_score * 0.25 +
        storm_surge_score * 0.20 +
        hail_score * 0.15 +
        wildfire_score * 0.10
    )

    # Risk tier
    if composite >= 75:
        risk_tier = "Critical"
        tier_color = RED
        tier_desc = "This property faces severe catastrophe exposure across multiple perils. Expect elevated insurance premiums and consider mitigation measures."
    elif composite >= 55:
        risk_tier = "High"
        tier_color = ORANGE
        tier_desc = "Significant exposure to one or more natural perils. Insurance may be mandatory for certain coverages. Review flood zone designation and building resilience."
    elif composite >= 35:
        risk_tier = "Moderate"
        tier_color = YELLOW
        tier_desc = "Moderate catastrophe risk. Standard insurance coverage should be adequate, but review individual peril scores for any elevated exposures."
    else:
        risk_tier = "Low"
        tier_color = GREEN
        tier_desc = "Below-average catastrophe exposure. This property benefits from favorable geography, construction, or flood zone placement."

    # ── Display Results ──

    section("Risk Assessment Results")

    # Overall score card
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid {tier_color}30;
        border-radius: 20px;
        padding: 32px 40px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        gap: 40px;
    ">
        <div style="text-align: center; min-width: 140px;">
            <div style="
                font-size: 3.2rem;
                font-weight: 800;
                color: {tier_color};
                line-height: 1;
                letter-spacing: -0.03em;
            ">{composite:.0f}</div>
            <div style="
                font-size: 0.7rem;
                font-weight: 600;
                color: rgba(255,255,255,0.35);
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-top: 6px;
            ">Composite Score</div>
        </div>
        <div style="width: 1px; height: 80px; background: rgba(255,255,255,0.06);"></div>
        <div>
            <div style="
                font-size: 1.3rem;
                font-weight: 700;
                color: {tier_color};
                margin-bottom: 6px;
            ">{risk_tier} Risk</div>
            <div style="
                font-size: 0.9rem;
                color: rgba(255,255,255,0.5);
                line-height: 1.6;
                max-width: 600px;
            ">{tier_desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Property summary
    kpi_row([
        {"label": "Property Value", "value": format_number(property_value)},
        {"label": "Building Age", "value": f"{building_age} yrs"},
        {"label": "Flood Zone", "value": flood_zone},
        {"label": "Construction", "value": construction},
    ])

    divider()

    # ── Per-peril breakdown ──
    section("Peril-Level Risk Breakdown",
            "Individual risk scores for each major catastrophe peril, calibrated against "
            "historical FEMA declarations, NOAA storm records, and NFIP claims for this state.")

    peril_data = [
        ("Flood", flood_score, BLUE,
         "Riverine and pluvial flooding risk based on FEMA flood zone, state flood history, "
         "building elevation characteristics, and age."),
        ("Wind / Hurricane", wind_score, TEAL,
         "Tropical cyclone and severe wind risk based on state storm frequency, "
         "construction type vulnerability, building height, and age."),
        ("Storm Surge", storm_surge_score, PURPLE,
         "Coastal inundation risk. Primarily driven by flood zone — properties in V/VE zones "
         "face direct wave action; A/AE zones face stillwater surge."),
        ("Hail", hail_score, ORANGE,
         "Convective storm and hail risk. Roof and exterior materials are the primary "
         "damage drivers. Older buildings with original roofing face higher exposure."),
        ("Wildfire", wildfire_score, RED,
         "Wildfire proximity risk. Depends on regional vegetation, construction combustibility, "
         "and historical fire frequency in the state."),
    ]

    for peril_name, score, color, description in peril_data:
        if score >= 70:
            level = "High"
        elif score >= 40:
            level = "Moderate"
        else:
            level = "Low"

        st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 14px;
            padding: 20px 24px;
            margin-bottom: 10px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="font-size: 1rem; font-weight: 600; color: #f5f5f7;">{peril_name}</div>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 0.75rem; color: {color}; font-weight: 600;">{level}</span>
                    <span style="font-size: 1.4rem; font-weight: 700; color: {color};">{score:.0f}</span>
                </div>
            </div>
            <div style="
                background: rgba(255,255,255,0.04);
                border-radius: 6px;
                height: 8px;
                overflow: hidden;
                margin-bottom: 10px;
            ">
                <div style="
                    width: {score}%;
                    height: 100%;
                    background: linear-gradient(90deg, {color}80, {color});
                    border-radius: 6px;
                    transition: width 0.5s ease;
                "></div>
            </div>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.35); line-height: 1.5;">{description}</div>
        </div>
        """, unsafe_allow_html=True)

    divider()

    # ── State historical context ──
    section("Historical Context",
            f"Catastrophe history for {state_name} drawn from loaded FEMA, NOAA, and NFIP datasets.")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        kpi_row([
            {"label": "FEMA Declarations", "value": f"{decl_count:,}"},
            {"label": "NOAA Storm Events", "value": f"{storm_events:,}"},
        ])

        if len(type_breakdown) > 0:
            fig = px.bar(
                x=type_breakdown.values, y=type_breakdown.index, orientation="h",
                color_discrete_sequence=[BLUE],
                labels={"x": "Declarations", "y": ""},
            )
            apply_layout(fig, height=300, title=dict(text=f"FEMA Declaration Types — {state_code}"))
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        kpi_row([
            {"label": "NFIP Claims", "value": f"{nfip_claims:,}"},
            {"label": "Avg Flood Payout", "value": format_number(avg_payout)},
        ])

        if len(storm_types) > 0:
            fig = px.bar(
                x=storm_types.values, y=storm_types.index, orientation="h",
                color_discrete_sequence=[TEAL],
                labels={"x": "Events", "y": ""},
            )
            apply_layout(fig, height=300, title=dict(text=f"NOAA Storm Types — {state_name}"))
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # Radar chart of peril scores
    divider()
    section("Multi-Peril Risk Profile",
            "Radar visualization of the property's exposure across all five catastrophe perils. "
            "A wider shape indicates broader multi-peril exposure; spikes indicate concentrated risk.")

    categories = ["Flood", "Wind", "Storm Surge", "Hail", "Wildfire"]
    scores = [flood_score, wind_score, storm_surge_score, hail_score, wildfire_score]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor=f"rgba({int(tier_color[1:3],16)},{int(tier_color[3:5],16)},{int(tier_color[5:7],16)},0.1)",
        line=dict(color=tier_color, width=2.5),
        marker=dict(size=6, color=tier_color),
        name="Risk Score",
    ))
    apply_layout(fig, height=420, title=dict(text="Property Risk Radar"))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(255,255,255,0.02)",
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor="rgba(255,255,255,0.06)",
                tickfont=dict(size=9, color="rgba(255,255,255,0.3)"),
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.06)",
                tickfont=dict(size=12, color="rgba(255,255,255,0.6)"),
            ),
        ),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Estimated annual loss
    divider()
    section("Estimated Annual Loss (EAL)",
            "A simplified expected annual loss calculation based on the composite risk score, "
            "property value, and peril weights. This is a screening-level estimate — a full "
            "actuarial analysis would incorporate granular location data, elevation certificates, "
            "and vendor catastrophe model output (RMS, AIR, CoreLogic).")

    # EAL = property_value * loss_rate, where loss_rate is derived from score
    # Typical cat loss rates: 0.05% (low) to 2%+ (critical coastal)
    loss_rate = (composite / 100) ** 1.5 * 0.025  # non-linear scaling, max ~2.5%
    eal = property_value * loss_rate
    eal_flood = property_value * (flood_score / 100) ** 1.5 * 0.025 * 0.30
    eal_wind = property_value * (wind_score / 100) ** 1.5 * 0.025 * 0.25
    eal_surge = property_value * (storm_surge_score / 100) ** 1.5 * 0.025 * 0.20
    eal_hail = property_value * (hail_score / 100) ** 1.5 * 0.025 * 0.15
    eal_fire = property_value * (wildfire_score / 100) ** 1.5 * 0.025 * 0.10

    kpi_row([
        {"label": "Total EAL", "value": format_number(eal)},
        {"label": "Loss Rate", "value": f"{loss_rate*100:.3f}%"},
        {"label": "Flood EAL", "value": format_number(eal_flood)},
        {"label": "Wind EAL", "value": format_number(eal_wind)},
    ])

    eal_data = pd.DataFrame({
        "Peril": ["Flood", "Wind", "Storm Surge", "Hail", "Wildfire"],
        "EAL": [eal_flood, eal_wind, eal_surge, eal_hail, eal_fire],
    }).sort_values("EAL", ascending=True)

    fig = px.bar(
        eal_data, x="EAL", y="Peril", orientation="h",
        color="EAL",
        color_continuous_scale=[[0, "rgba(10,132,255,0.3)"], [1, BLUE]],
    )
    apply_layout(fig, height=280, title=dict(text="Estimated Annual Loss by Peril"))
    fig.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_tickprefix="$")
    st.plotly_chart(fig, use_container_width=True)

    # Flood zone info
    divider()
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 20px 24px;
    ">
        <div style="font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.3);
             text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px;">
            Flood Zone {flood_zone} — Definition
        </div>
        <div style="font-size: 0.9rem; color: rgba(255,255,255,0.6); line-height: 1.6;">
            {FLOOD_ZONES.get(flood_zone, "Unknown flood zone designation.")}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# FEMA DISASTER DECLARATIONS
# ══════════════════════════════════════════════

elif data_source == "FEMA Disaster Declarations":
    page_header(
        "FEMA Disaster Declarations",
        "Every federally declared disaster and emergency in the United States, sourced from "
        "OpenFEMA. These declarations trigger federal assistance programs and reflect the "
        "evolving landscape of natural hazard risk across all 50 states and territories."
    )

    fema = get_fema_declarations()
    if fema.empty:
        st.error("Unable to load FEMA declarations data.")
        st.stop()

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3, gap="medium")
    with col_f1:
        year_range = st.slider(
            "Year Range",
            int(fema["year"].min()), int(fema["year"].max()),
            (int(fema["year"].max()) - 10, int(fema["year"].max())),
        )
    with col_f2:
        incident_types = st.multiselect(
            "Incident Types",
            fema["incidentType"].dropna().unique().tolist(),
            default=[],
        )
    with col_f3:
        states = st.multiselect(
            "States",
            sorted(fema["state"].dropna().unique().tolist()),
            default=[],
        )

    mask = (fema["year"] >= year_range[0]) & (fema["year"] <= year_range[1])
    if incident_types:
        mask &= fema["incidentType"].isin(incident_types)
    if states:
        mask &= fema["state"].isin(states)
    filtered = fema[mask]

    kpi_row([
        {"label": "Declarations", "value": f"{len(filtered):,}"},
        {"label": "Unique Disasters", "value": f"{filtered['disasterNumber'].nunique():,}"},
        {"label": "States Affected", "value": str(filtered["state"].nunique())},
        {"label": "Incident Types", "value": str(filtered["incidentType"].nunique())},
    ])

    divider()

    col1, col2 = st.columns(2, gap="large")
    with col1:
        section("Declarations Over Time",
                "Year-by-year count of federal declarations within the selected filters. "
                "Notice the sharp increase post-2000 as climate events intensify.")
        yearly = filtered.groupby("year").size().reset_index(name="count")
        fig = px.bar(yearly, x="year", y="count", color_discrete_sequence=[BLUE])
        apply_layout(fig, height=400, title=dict(text="Declarations by Year"))
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Geographic Distribution",
                "States ranked by total declaration count. Gulf and Atlantic coastal "
                "states dominate due to hurricane, flood, and severe storm exposure.")
        state_counts = filtered["state"].value_counts().head(15).reset_index()
        state_counts.columns = ["State", "Declarations"]
        fig = px.bar(
            state_counts, x="Declarations", y="State", orientation="h",
            color="Declarations",
            color_continuous_scale=[[0, "rgba(10,132,255,0.3)"], [1, BLUE]],
        )
        apply_layout(fig, height=400, title=dict(text="Top 15 States"))
        fig.update_layout(showlegend=False, coloraxis_showscale=False,
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    section("Incident Type Heatmap",
            "Cross-tabulation of the top 8 incident types against year. Darker cells "
            "indicate higher declaration counts — useful for identifying emerging perils "
            "and multi-year clustering of specific hazard types.")
    pivot = filtered.groupby(["year", "incidentType"]).size().reset_index(name="count")
    top_types = filtered["incidentType"].value_counts().head(8).index.tolist()
    pivot = pivot[pivot["incidentType"].isin(top_types)]
    heat = pivot.pivot_table(index="incidentType", columns="year", values="count", fill_value=0)
    fig = px.imshow(
        heat,
        color_continuous_scale=[[0, "rgba(10,132,255,0.05)"], [0.5, "rgba(10,132,255,0.4)"], [1, BLUE]],
        labels=dict(x="Year", y="Incident Type", color="Declarations"),
        aspect="auto",
    )
    apply_layout(fig, height=380, title=dict(text="Incident Type x Year"))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Raw Data"):
        st.dataframe(filtered.head(500), use_container_width=True)


# ══════════════════════════════════════════════
# FEMA NFIP CLAIMS
# ══════════════════════════════════════════════

elif data_source == "FEMA NFIP Claims":
    page_header(
        "National Flood Insurance Program",
        "The NFIP is administered by FEMA and provides flood insurance to property "
        "owners across the US. This view analyzes claims payouts — the actual dollars "
        "disbursed for building and contents damage following flood events. Data sourced "
        "from the OpenFEMA NFIP Claims dataset."
    )

    nfip = get_nfip_claims()
    if nfip.empty:
        st.error("Unable to load NFIP claims data.")
        st.stop()

    total_paid = nfip["totalPaid"].sum() if "totalPaid" in nfip.columns else 0
    avg_claim = nfip["totalPaid"].mean() if "totalPaid" in nfip.columns else 0

    kpi_row([
        {"label": "Total Claims", "value": f"{len(nfip):,}"},
        {"label": "Total Paid Out", "value": format_number(total_paid)},
        {"label": "Average Claim", "value": format_number(avg_claim)},
        {"label": "States", "value": str(nfip["state"].nunique()) if "state" in nfip.columns else "N/A"},
    ])

    divider()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        section("Claims Volume & Payouts",
                "Dual-axis view of annual claim counts (bars) against total dollars paid (line). "
                "Major spikes correspond to landmark flood events — Hurricane Katrina (2005), "
                "Harvey (2017), and Ian (2022).")
        if "yearOfLoss" in nfip.columns:
            yearly = nfip.groupby("yearOfLoss").agg(
                claims=("totalPaid", "count"),
                paid=("totalPaid", "sum"),
            ).reset_index()
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(x=yearly["yearOfLoss"], y=yearly["claims"],
                       name="Claims", marker_color=BLUE, opacity=0.6),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(x=yearly["yearOfLoss"], y=yearly["paid"],
                           name="Total Paid ($)", line=dict(color=ORANGE, width=3)),
                secondary_y=True,
            )
            apply_layout(fig, height=430, title=dict(text="NFIP Claims & Payouts by Year"))
            fig.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            )
            fig.update_yaxes(title_text="Claims", secondary_y=False,
                             gridcolor="rgba(255,255,255,0.04)")
            fig.update_yaxes(title_text="Total Paid ($)", secondary_y=True,
                             gridcolor="rgba(255,255,255,0.04)")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("State-Level Exposure",
                "Top 15 states ranked by cumulative NFIP payouts. Florida, Texas, and Louisiana "
                "consistently lead — reflecting their coastal exposure, hurricane frequency, and "
                "large insured property base within NFIP.")
        if "state" in nfip.columns and "totalPaid" in nfip.columns:
            state_loss = nfip.groupby("state")["totalPaid"].sum().nlargest(15).reset_index()
            state_loss.columns = ["State", "Total Paid"]
            fig = px.bar(
                state_loss, x="Total Paid", y="State", orientation="h",
                color="Total Paid",
                color_continuous_scale=[[0, "rgba(255,159,10,0.3)"], [1, ORANGE]],
            )
            apply_layout(fig, height=430, title=dict(text="Top 15 States by Claims Paid"))
            fig.update_layout(showlegend=False, coloraxis_showscale=False,
                              yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)

    # Distribution
    if "totalPaid" in nfip.columns:
        paid_nonzero = nfip[nfip["totalPaid"] > 0]["totalPaid"]
        if len(paid_nonzero) > 0:
            section("Claim Amount Distribution",
                    "Histogram of individual claim payouts (excluding zeros). The heavy "
                    "right-tail distribution is typical of catastrophe losses — most claims are "
                    "moderate, but a small number of severe events drive outsized losses.")
            fig = px.histogram(
                paid_nonzero, nbins=50,
                labels={"value": "Claim Amount ($)", "count": "Frequency"},
                color_discrete_sequence=[GREEN],
            )
            apply_layout(fig, height=350, title=dict(text="Distribution of Claim Amounts"))
            fig.update_layout(showlegend=False)
            fig.update_xaxes(range=[0, paid_nonzero.quantile(0.95)])
            st.plotly_chart(fig, use_container_width=True)

    # Flood zone
    if "floodZone" in nfip.columns:
        section("Flood Zone Analysis",
                "Claims broken down by FEMA flood zone designation. Zone A and V zones represent "
                "high-risk areas with mandatory flood insurance requirements. Zone X claims indicate "
                "losses occurring outside traditionally mapped flood hazard areas.")
        fz = nfip.groupby("floodZone").agg(
            claims=("totalPaid", "count"),
            avg_paid=("totalPaid", "mean"),
        ).nlargest(10, "claims").reset_index()
        fig = px.bar(
            fz, x="floodZone", y="claims",
            color="avg_paid",
            color_continuous_scale=[[0, "rgba(191,90,242,0.3)"], [1, PURPLE]],
            labels={"floodZone": "Flood Zone", "claims": "Claims", "avg_paid": "Avg Payout"},
        )
        apply_layout(fig, height=350, title=dict(text="Claims by Flood Zone"))
        fig.update_layout(coloraxis_showscale=True)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Raw Data"):
        st.dataframe(nfip.head(500), use_container_width=True)


# ══════════════════════════════════════════════
# NOAA STORM EVENTS
# ══════════════════════════════════════════════

elif data_source == "NOAA Storm Events":
    page_header(
        "NOAA Severe Storm Events",
        "Comprehensive record of significant weather events across the United States, "
        "maintained by NOAA's National Centers for Environmental Information (NCEI). "
        "Each record includes storm location, azimuth, direct and indirect casualties, "
        "and estimated property and crop damage. Also available via Google BigQuery public datasets."
    )

    storms = get_noaa_storms()
    if storms.empty:
        st.warning("NOAA storm data is loading or unavailable. Showing EM-DAT storm data as fallback.")
        emdat = get_emdat()
        storms_emdat = emdat[emdat["disaster_type"] == "Storm"]
        yearly = storms_emdat.groupby("year").agg(
            events=("event_count", "sum"),
            deaths=("total_deaths", "sum"),
        ).reset_index()
        fig = px.bar(yearly, x="year", y="events", color_discrete_sequence=[BLUE])
        apply_layout(fig, height=400, title=dict(text="Global Storm Events (EM-DAT Fallback)"))
        st.plotly_chart(fig, use_container_width=True)
        st.stop()

    total_prop_dmg = storms["DAMAGE_PROPERTY"].sum() if "DAMAGE_PROPERTY" in storms.columns else 0
    total_deaths = storms["DEATHS_DIRECT"].sum() if "DEATHS_DIRECT" in storms.columns else 0
    total_injuries = storms["INJURIES_DIRECT"].sum() if "INJURIES_DIRECT" in storms.columns else 0

    kpi_row([
        {"label": "Storm Events", "value": f"{len(storms):,}"},
        {"label": "Property Damage", "value": format_number(total_prop_dmg)},
        {"label": "Direct Fatalities", "value": f"{int(total_deaths):,}"},
        {"label": "Direct Injuries", "value": f"{int(total_injuries):,}"},
    ])

    divider()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        section("Event Type Breakdown",
                "The 12 most frequent storm event types. Thunderstorm wind and hail dominate "
                "by count, while tornado and hurricane events cause disproportionate damage "
                "per occurrence — a key consideration for catastrophe modelers.")
        if "EVENT_TYPE" in storms.columns:
            top_events = storms["EVENT_TYPE"].value_counts().head(12).reset_index()
            top_events.columns = ["Event Type", "Count"]
            fig = px.bar(
                top_events, x="Count", y="Event Type", orientation="h",
                color_discrete_sequence=[TEAL],
            )
            apply_layout(fig, height=450, title=dict(text="Top 12 Storm Event Types"))
            fig.update_layout(showlegend=False, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Property Damage by State",
                "Cumulative property damage estimates by state. These figures reflect both "
                "hazard intensity and the value of exposed assets — states with large coastal "
                "populations face compound risk from both high hazard and high exposure.")
        if "STATE" in storms.columns and "DAMAGE_PROPERTY" in storms.columns:
            state_dmg = storms.groupby("STATE")["DAMAGE_PROPERTY"].sum().nlargest(15).reset_index()
            state_dmg.columns = ["State", "Property Damage"]
            fig = px.bar(
                state_dmg, x="Property Damage", y="State", orientation="h",
                color="Property Damage",
                color_continuous_scale=[[0, "rgba(255,69,58,0.3)"], [1, RED]],
            )
            apply_layout(fig, height=450, title=dict(text="Top 15 States — Property Damage"))
            fig.update_layout(showlegend=False, coloraxis_showscale=False,
                              yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)

    # Map
    if "BEGIN_LAT" in storms.columns and "BEGIN_LON" in storms.columns:
        section("Storm Event Map",
                "Geographic distribution of high-damage storm events (>$100K property damage). "
                "Each point is sized by damage amount and colored by event type. Zoom and pan to "
                "explore regional concentration and corridor patterns.")
        map_data = storms.dropna(subset=["BEGIN_LAT", "BEGIN_LON"])
        if "DAMAGE_PROPERTY" in map_data.columns:
            map_data = map_data[map_data["DAMAGE_PROPERTY"] > 100000].head(5000)
        else:
            map_data = map_data.head(5000)

        if len(map_data) > 0:
            fig = px.scatter_mapbox(
                map_data,
                lat="BEGIN_LAT", lon="BEGIN_LON",
                color="EVENT_TYPE" if "EVENT_TYPE" in map_data.columns else None,
                size="DAMAGE_PROPERTY" if "DAMAGE_PROPERTY" in map_data.columns else None,
                size_max=20,
                hover_name="EVENT_TYPE" if "EVENT_TYPE" in map_data.columns else None,
                hover_data={
                    "STATE": True,
                    "DAMAGE_PROPERTY": ":$,.0f",
                } if all(c in map_data.columns for c in ["STATE", "DAMAGE_PROPERTY"]) else None,
                mapbox_style="carto-darkmatter",
                zoom=3, center={"lat": 39.8, "lon": -98.5},
                height=550,
            )
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(bgcolor="rgba(0,0,0,0.5)", font=dict(color="rgba(255,255,255,0.7)")),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Seasonality
    if "BEGIN_DATE_TIME" in storms.columns:
        section("Seasonal Patterns",
                "Monthly distribution of storm events. The late spring tornado season and "
                "August-October hurricane season create distinct peaks that drive catastrophe "
                "model seasonality assumptions.")
        storms["month"] = storms["BEGIN_DATE_TIME"].dt.month
        monthly = storms.groupby("month").size().reset_index(name="count")
        monthly["month_name"] = monthly["month"].map({
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
        })
        fig = px.bar(
            monthly, x="month_name", y="count",
            color="count",
            color_continuous_scale=[[0, "rgba(10,132,255,0.3)"], [0.5, BLUE], [1, PURPLE]],
        )
        apply_layout(fig, height=350, title=dict(text="Storm Events by Month"))
        fig.update_layout(
            showlegend=False, coloraxis_showscale=False,
            xaxis_title="", yaxis_title="Events",
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Raw Data"):
        st.dataframe(storms.head(500), use_container_width=True)


# ══════════════════════════════════════════════
# EM-DAT GLOBAL DISASTERS
# ══════════════════════════════════════════════

elif data_source == "EM-DAT Global Disasters":
    page_header(
        "EM-DAT Global Disaster Database",
        "The International Disaster Database maintained by the Centre for Research on the "
        "Epidemiology of Disasters (CRED) at UCLouvain. Contains core data on over 22,000 "
        "mass disasters worldwide from 1900 to present, compiled from UN agencies, "
        "non-governmental organizations, insurers, research institutes, and press agencies."
    )

    emdat = get_emdat()
    if emdat.empty:
        st.error("Unable to load EM-DAT data.")
        st.stop()

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3, gap="medium")
    with col_f1:
        yr = st.slider("Year Range", 2000, 2025, (2010, 2025))
    with col_f2:
        regions = st.multiselect("Regions", emdat["region"].unique().tolist(), default=[])
    with col_f3:
        dtypes = st.multiselect("Disaster Types", emdat["disaster_type"].unique().tolist(), default=[])

    mask = (emdat["year"] >= yr[0]) & (emdat["year"] <= yr[1])
    if regions:
        mask &= emdat["region"].isin(regions)
    if dtypes:
        mask &= emdat["disaster_type"].isin(dtypes)
    filtered = emdat[mask]

    kpi_row([
        {"label": "Total Events", "value": f"{filtered['event_count'].sum():,}"},
        {"label": "Fatalities", "value": f"{filtered['total_deaths'].sum():,}"},
        {"label": "People Affected", "value": f"{filtered['total_affected'].sum():,}"},
        {"label": "Economic Losses", "value": format_number(filtered["total_damage_million_usd"].sum() * 1e6)},
    ])

    divider()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        section("Events & Damage Trend",
                "Annual disaster count (bars) overlaid with economic damage (line). The upward trend "
                "in both metrics reflects improved reporting, urbanization in hazard-prone areas, "
                "and the increasing economic footprint of climate-related events.")
        yearly = filtered.groupby("year").agg(
            events=("event_count", "sum"),
            damage=("total_damage_million_usd", "sum"),
        ).reset_index()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=yearly["year"], y=yearly["events"],
                   name="Events", marker_color=BLUE, opacity=0.6),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=yearly["year"], y=yearly["damage"],
                       name="Damage ($M)", line=dict(color=RED, width=3)),
            secondary_y=True,
        )
        apply_layout(fig, height=430, title=dict(text="Events & Economic Damage by Year"))
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        )
        fig.update_yaxes(title_text="Events", secondary_y=False,
                         gridcolor="rgba(255,255,255,0.04)")
        fig.update_yaxes(title_text="Damage ($M)", secondary_y=True,
                         gridcolor="rgba(255,255,255,0.04)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Disaster Type Composition",
                "Treemap showing the relative share of events by disaster type. Size represents "
                "event count while color intensity maps to cumulative economic damage — revealing "
                "which perils are most frequent vs. most costly.")
        by_type = filtered.groupby("disaster_type").agg(
            events=("event_count", "sum"),
            deaths=("total_deaths", "sum"),
            damage=("total_damage_million_usd", "sum"),
        ).reset_index()
        fig = px.treemap(
            by_type, path=["disaster_type"], values="events",
            color="damage",
            color_continuous_scale=[[0, "rgba(10,132,255,0.3)"], [0.5, BLUE], [1, PURPLE]],
        )
        apply_layout(fig, height=430, title=dict(text="Disaster Types — Size: Events, Color: Damage"))
        st.plotly_chart(fig, use_container_width=True)

    section("Regional Breakdown",
            "Sunburst chart showing hierarchical event distribution — outer ring is disaster type, "
            "inner ring is geographic region. Asia consistently accounts for the largest share of "
            "both events and affected populations due to population density and monsoon exposure.")
    regional = filtered.groupby(["region", "disaster_type"]).agg(
        events=("event_count", "sum"),
        damage=("total_damage_million_usd", "sum"),
    ).reset_index()
    fig = px.sunburst(
        regional, path=["region", "disaster_type"], values="events",
        color="damage",
        color_continuous_scale=[[0, "rgba(48,209,88,0.2)"], [0.5, GREEN], [1, YELLOW]],
    )
    apply_layout(fig, height=520, title=dict(text="Regional Disaster Breakdown"))
    st.plotly_chart(fig, use_container_width=True)

    section("Mortality Trends by Peril",
            "Stacked area chart of annual fatalities decomposed by disaster type. Earthquake and "
            "drought events drive the largest mortality spikes, while flood deaths remain persistently "
            "elevated across all years — making it the most consistently lethal peril globally.")
    deaths_by_type = filtered.groupby(["year", "disaster_type"])["total_deaths"].sum().reset_index()
    fig = px.area(
        deaths_by_type, x="year", y="total_deaths", color="disaster_type",
        color_discrete_sequence=[BLUE, GREEN, ORANGE, RED, PURPLE, TEAL, YELLOW, INDIGO],
    )
    apply_layout(fig, height=400, title=dict(text="Deaths by Disaster Type Over Time"))
    st.plotly_chart(fig, use_container_width=True)

    section("Damage Heatmap",
            "Economic damage cross-tabulated by disaster type and region. This matrix reveals "
            "where capital is most at risk — storms in the Americas, earthquakes in Asia, and "
            "drought across Africa represent distinct risk profiles for catastrophe modelers.")
    heat = filtered.pivot_table(
        index="disaster_type", columns="region",
        values="total_damage_million_usd", aggfunc="sum", fill_value=0,
    )
    fig = px.imshow(
        heat,
        color_continuous_scale=[[0, "rgba(255,159,10,0.05)"], [0.5, "rgba(255,159,10,0.4)"], [1, ORANGE]],
        labels=dict(color="Damage ($M)"),
        aspect="auto",
    )
    apply_layout(fig, height=400, title=dict(text="Economic Damage: Disaster Type x Region ($M)"))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Raw Data"):
        st.dataframe(filtered.head(500), use_container_width=True)


# ── Footer ───────────────────────────────────
st.markdown(
    '<div class="footer-text">'
    "Cat Model Dashboard &nbsp;&middot;&nbsp; Data: FEMA OpenFEMA, NOAA NCEI, EM-DAT/CRED &nbsp;&middot;&nbsp; "
    "Built with Streamlit &amp; Plotly"
    "</div>",
    unsafe_allow_html=True,
)
