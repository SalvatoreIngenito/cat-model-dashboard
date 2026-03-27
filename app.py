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
    ["Overview", "FEMA Disaster Declarations", "FEMA NFIP Claims",
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
