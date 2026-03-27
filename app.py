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

# ── Custom CSS ───────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e3a5f 0%, #4a90d9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #6c757d;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 25px;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #4a90d9;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 15px 20px;
        border-left: 4px solid #4a90d9;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/FEMA_logo.svg/200px-FEMA_logo.svg.png", width=100)
st.sidebar.title("Cat Model Dashboard")
st.sidebar.markdown("---")

data_source = st.sidebar.radio(
    "Data Source",
    ["Overview", "FEMA Disaster Declarations", "FEMA NFIP Claims",
     "NOAA Storm Events", "EM-DAT Global Disasters"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Data Sources:**\n"
    "- [OpenFEMA](https://www.fema.gov/about/openfema)\n"
    "- [NOAA Storm Events](https://www.ncdc.noaa.gov/stormevents/)\n"
    "- [EM-DAT](https://www.emdat.be/)\n"
)


# ── Data loading with caching ───────────────
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


def create_kpi_row(metrics: list[dict]):
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        col.metric(label=m["label"], value=m["value"], delta=m.get("delta"))


# ══════════════════════════════════════════════
# OVERVIEW PAGE
# ══════════════════════════════════════════════

if data_source == "Overview":
    st.markdown('<p class="main-header">Catastrophe Model Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Multi-source catastrophe risk analytics — FEMA · NOAA · EM-DAT</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # FEMA overview
    with col1:
        st.subheader("US Disaster Declarations (FEMA)")
        fema = get_fema_declarations()
        if not fema.empty:
            yearly = fema.groupby("year").size().reset_index(name="count")
            fig = px.area(
                yearly, x="year", y="count",
                title="Annual Federal Disaster Declarations",
                color_discrete_sequence=["#4a90d9"],
                labels={"year": "Year", "count": "Declarations"},
            )
            fig.update_layout(
                template="plotly_white",
                height=350,
                margin=dict(l=40, r=20, t=50, b=40),
            )
            st.plotly_chart(fig, use_container_width=True)

            by_type = fema["incidentType"].value_counts().head(8).reset_index()
            by_type.columns = ["Incident Type", "Count"]
            fig2 = px.bar(
                by_type, x="Count", y="Incident Type", orientation="h",
                title="Top Incident Types",
                color="Count",
                color_continuous_scale="Blues",
            )
            fig2.update_layout(
                template="plotly_white", height=350,
                margin=dict(l=40, r=20, t=50, b=40),
                showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Could not load FEMA data.")

    # EM-DAT overview
    with col2:
        st.subheader("Global Disasters (EM-DAT)")
        emdat = get_emdat()
        if not emdat.empty:
            yearly_global = emdat.groupby("year").agg(
                events=("event_count", "sum"),
                deaths=("total_deaths", "sum"),
                damage=("total_damage_million_usd", "sum"),
            ).reset_index()

            fig3 = px.line(
                yearly_global, x="year", y="events",
                title="Global Natural Disaster Events per Year",
                color_discrete_sequence=["#e74c3c"],
                labels={"year": "Year", "events": "Events"},
            )
            fig3.update_layout(
                template="plotly_white", height=350,
                margin=dict(l=40, r=20, t=50, b=40),
            )
            st.plotly_chart(fig3, use_container_width=True)

            by_region = emdat.groupby("region")["total_damage_million_usd"].sum().reset_index()
            by_region.columns = ["Region", "Damage ($M)"]
            fig4 = px.pie(
                by_region, names="Region", values="Damage ($M)",
                title="Economic Losses by Region",
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.4,
            )
            fig4.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("Could not load EM-DAT data.")

    # Summary KPIs
    st.markdown("---")
    st.subheader("Key Risk Indicators")
    kpis = []
    if not fema.empty:
        kpis.append({"label": "Total US Declarations", "value": f"{len(fema):,}"})
        kpis.append({"label": "States Affected", "value": str(fema["state"].nunique())})
    if not emdat.empty:
        kpis.append({"label": "Global Events (2000-2025)", "value": f"{emdat['event_count'].sum():,}"})
        kpis.append({"label": "Est. Global Losses", "value": format_number(emdat["total_damage_million_usd"].sum() * 1e6)})
    if kpis:
        create_kpi_row(kpis)


# ══════════════════════════════════════════════
# FEMA DISASTER DECLARATIONS
# ══════════════════════════════════════════════

elif data_source == "FEMA Disaster Declarations":
    st.markdown('<p class="main-header">FEMA Disaster Declarations</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Federal disaster and emergency declarations across the United States</p>', unsafe_allow_html=True)

    fema = get_fema_declarations()
    if fema.empty:
        st.error("Unable to load FEMA declarations data.")
        st.stop()

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
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

    # KPIs
    create_kpi_row([
        {"label": "Declarations", "value": f"{len(filtered):,}"},
        {"label": "Unique Disaster #s", "value": f"{filtered['disasterNumber'].nunique():,}"},
        {"label": "States", "value": str(filtered["state"].nunique())},
        {"label": "Incident Types", "value": str(filtered["incidentType"].nunique())},
    ])

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        yearly = filtered.groupby("year").size().reset_index(name="count")
        fig = px.bar(
            yearly, x="year", y="count",
            title="Declarations by Year",
            color_discrete_sequence=["#4a90d9"],
        )
        fig.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        state_counts = filtered["state"].value_counts().head(15).reset_index()
        state_counts.columns = ["State", "Declarations"]
        fig = px.bar(
            state_counts, x="Declarations", y="State", orientation="h",
            title="Top 15 States by Declarations",
            color="Declarations", color_continuous_scale="Reds",
        )
        fig.update_layout(template="plotly_white", height=400, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap: incident type × year
    pivot = filtered.groupby(["year", "incidentType"]).size().reset_index(name="count")
    top_types = filtered["incidentType"].value_counts().head(8).index.tolist()
    pivot = pivot[pivot["incidentType"].isin(top_types)]
    heat = pivot.pivot_table(index="incidentType", columns="year", values="count", fill_value=0)
    fig = px.imshow(
        heat, title="Incident Type × Year Heatmap",
        color_continuous_scale="YlOrRd",
        labels=dict(x="Year", y="Incident Type", color="Declarations"),
        aspect="auto",
    )
    fig.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw Data"):
        st.dataframe(filtered.head(500), use_container_width=True)


# ══════════════════════════════════════════════
# FEMA NFIP CLAIMS
# ══════════════════════════════════════════════

elif data_source == "FEMA NFIP Claims":
    st.markdown('<p class="main-header">National Flood Insurance Program Claims</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">NFIP claims data from OpenFEMA — building & contents flood damage</p>', unsafe_allow_html=True)

    nfip = get_nfip_claims()
    if nfip.empty:
        st.error("Unable to load NFIP claims data.")
        st.stop()

    # KPIs
    total_paid = nfip["totalPaid"].sum() if "totalPaid" in nfip.columns else 0
    avg_claim = nfip["totalPaid"].mean() if "totalPaid" in nfip.columns else 0
    create_kpi_row([
        {"label": "Total Claims", "value": f"{len(nfip):,}"},
        {"label": "Total Paid", "value": format_number(total_paid)},
        {"label": "Avg Claim", "value": format_number(avg_claim)},
        {"label": "States", "value": str(nfip["state"].nunique()) if "state" in nfip.columns else "N/A"},
    ])

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if "yearOfLoss" in nfip.columns:
            yearly = nfip.groupby("yearOfLoss").agg(
                claims=("totalPaid", "count"),
                paid=("totalPaid", "sum"),
            ).reset_index()
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(x=yearly["yearOfLoss"], y=yearly["claims"],
                       name="Claims Count", marker_color="#4a90d9", opacity=0.7),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(x=yearly["yearOfLoss"], y=yearly["paid"],
                           name="Total Paid ($)", line=dict(color="#e74c3c", width=3)),
                secondary_y=True,
            )
            fig.update_layout(
                title="NFIP Claims & Payouts by Year",
                template="plotly_white", height=420,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            fig.update_yaxes(title_text="# Claims", secondary_y=False)
            fig.update_yaxes(title_text="Total Paid ($)", secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "state" in nfip.columns and "totalPaid" in nfip.columns:
            state_loss = nfip.groupby("state")["totalPaid"].sum().nlargest(15).reset_index()
            state_loss.columns = ["State", "Total Paid"]
            fig = px.bar(
                state_loss, x="Total Paid", y="State", orientation="h",
                title="Top 15 States by Claims Paid",
                color="Total Paid", color_continuous_scale="Reds",
            )
            fig.update_layout(template="plotly_white", height=420, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)

    # Distribution of claim amounts
    if "totalPaid" in nfip.columns:
        paid_nonzero = nfip[nfip["totalPaid"] > 0]["totalPaid"]
        if len(paid_nonzero) > 0:
            fig = px.histogram(
                paid_nonzero, nbins=50,
                title="Distribution of Claim Amounts (Non-Zero)",
                labels={"value": "Claim Amount ($)", "count": "Frequency"},
                color_discrete_sequence=["#2ecc71"],
            )
            fig.update_layout(template="plotly_white", height=350, showlegend=False)
            fig.update_xaxes(range=[0, paid_nonzero.quantile(0.95)])
            st.plotly_chart(fig, use_container_width=True)

    # Flood zone analysis
    if "floodZone" in nfip.columns:
        fz = nfip.groupby("floodZone").agg(
            claims=("totalPaid", "count"),
            avg_paid=("totalPaid", "mean"),
        ).nlargest(10, "claims").reset_index()
        fig = px.bar(
            fz, x="floodZone", y="claims",
            title="Claims by Flood Zone",
            color="avg_paid", color_continuous_scale="Viridis",
            labels={"floodZone": "Flood Zone", "claims": "# Claims", "avg_paid": "Avg Paid"},
        )
        fig.update_layout(template="plotly_white", height=350)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw Data"):
        st.dataframe(nfip.head(500), use_container_width=True)


# ══════════════════════════════════════════════
# NOAA STORM EVENTS
# ══════════════════════════════════════════════

elif data_source == "NOAA Storm Events":
    st.markdown('<p class="main-header">NOAA Severe Storm Events</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Storm location, impact, and damage from NOAA\'s Storm Events Database</p>', unsafe_allow_html=True)

    storms = get_noaa_storms()
    if storms.empty:
        st.warning("NOAA storm data is loading or unavailable. Showing EM-DAT storm data as fallback.")
        emdat = get_emdat()
        storms_emdat = emdat[emdat["disaster_type"] == "Storm"]
        yearly = storms_emdat.groupby("year").agg(
            events=("event_count", "sum"),
            deaths=("total_deaths", "sum"),
        ).reset_index()
        fig = px.bar(yearly, x="year", y="events", title="Global Storm Events (EM-DAT)")
        fig.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.stop()

    # KPIs
    total_prop_dmg = storms["DAMAGE_PROPERTY"].sum() if "DAMAGE_PROPERTY" in storms.columns else 0
    total_deaths = storms["DEATHS_DIRECT"].sum() if "DEATHS_DIRECT" in storms.columns else 0
    total_injuries = storms["INJURIES_DIRECT"].sum() if "INJURIES_DIRECT" in storms.columns else 0

    create_kpi_row([
        {"label": "Storm Events", "value": f"{len(storms):,}"},
        {"label": "Property Damage", "value": format_number(total_prop_dmg)},
        {"label": "Direct Deaths", "value": f"{int(total_deaths):,}"},
        {"label": "Direct Injuries", "value": f"{int(total_injuries):,}"},
    ])
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if "EVENT_TYPE" in storms.columns:
            top_events = storms["EVENT_TYPE"].value_counts().head(12).reset_index()
            top_events.columns = ["Event Type", "Count"]
            fig = px.bar(
                top_events, x="Count", y="Event Type", orientation="h",
                title="Top 12 Storm Event Types",
                color="Count", color_continuous_scale="Viridis",
            )
            fig.update_layout(template="plotly_white", height=450, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "STATE" in storms.columns and "DAMAGE_PROPERTY" in storms.columns:
            state_dmg = storms.groupby("STATE")["DAMAGE_PROPERTY"].sum().nlargest(15).reset_index()
            state_dmg.columns = ["State", "Property Damage"]
            fig = px.bar(
                state_dmg, x="Property Damage", y="State", orientation="h",
                title="Top 15 States by Property Damage",
                color="Property Damage", color_continuous_scale="OrRd",
            )
            fig.update_layout(template="plotly_white", height=450, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)

    # Storm event map
    if "BEGIN_LAT" in storms.columns and "BEGIN_LON" in storms.columns:
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
                title="High-Damage Storm Events Map (>$100K property damage)",
                mapbox_style="open-street-map",
                zoom=3, center={"lat": 39.8, "lon": -98.5},
                height=550,
            )
            fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)

    # Monthly seasonality
    if "BEGIN_DATE_TIME" in storms.columns:
        storms["month"] = storms["BEGIN_DATE_TIME"].dt.month
        monthly = storms.groupby("month").size().reset_index(name="count")
        monthly["month_name"] = monthly["month"].map({
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
        })
        fig = px.bar(
            monthly, x="month_name", y="count",
            title="Storm Event Seasonality",
            color="count", color_continuous_scale="Sunset",
        )
        fig.update_layout(template="plotly_white", height=350, xaxis_title="Month", yaxis_title="Events")
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw Data"):
        st.dataframe(storms.head(500), use_container_width=True)


# ══════════════════════════════════════════════
# EM-DAT GLOBAL DISASTERS
# ══════════════════════════════════════════════

elif data_source == "EM-DAT Global Disasters":
    st.markdown('<p class="main-header">EM-DAT Global Disaster Database</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Core data on 22,000+ mass disasters worldwide (2000–2025) — based on EM-DAT/CRED statistics</p>', unsafe_allow_html=True)

    emdat = get_emdat()
    if emdat.empty:
        st.error("Unable to load EM-DAT data.")
        st.stop()

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
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

    # KPIs
    create_kpi_row([
        {"label": "Total Events", "value": f"{filtered['event_count'].sum():,}"},
        {"label": "Total Deaths", "value": f"{filtered['total_deaths'].sum():,}"},
        {"label": "People Affected", "value": f"{filtered['total_affected'].sum():,}"},
        {"label": "Economic Losses", "value": format_number(filtered["total_damage_million_usd"].sum() * 1e6)},
    ])
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        yearly = filtered.groupby("year").agg(
            events=("event_count", "sum"),
            damage=("total_damage_million_usd", "sum"),
        ).reset_index()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=yearly["year"], y=yearly["events"],
                   name="Events", marker_color="#3498db", opacity=0.7),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=yearly["year"], y=yearly["damage"],
                       name="Damage ($M)", line=dict(color="#e74c3c", width=3)),
            secondary_y=True,
        )
        fig.update_layout(
            title="Events & Economic Damage by Year",
            template="plotly_white", height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        fig.update_yaxes(title_text="Events", secondary_y=False)
        fig.update_yaxes(title_text="Damage ($M)", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        by_type = filtered.groupby("disaster_type").agg(
            events=("event_count", "sum"),
            deaths=("total_deaths", "sum"),
            damage=("total_damage_million_usd", "sum"),
        ).reset_index()
        fig = px.treemap(
            by_type, path=["disaster_type"], values="events",
            color="damage", color_continuous_scale="YlOrRd",
            title="Disaster Types — Size: Events, Color: Damage",
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    # Regional breakdown
    regional = filtered.groupby(["region", "disaster_type"]).agg(
        events=("event_count", "sum"),
        damage=("total_damage_million_usd", "sum"),
    ).reset_index()
    fig = px.sunburst(
        regional, path=["region", "disaster_type"], values="events",
        color="damage", color_continuous_scale="Viridis",
        title="Regional Disaster Breakdown (Events)",
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Deaths by type over time
    deaths_by_type = filtered.groupby(["year", "disaster_type"])["total_deaths"].sum().reset_index()
    fig = px.area(
        deaths_by_type, x="year", y="total_deaths", color="disaster_type",
        title="Deaths by Disaster Type Over Time",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Damage heatmap region × type
    heat = filtered.pivot_table(
        index="disaster_type", columns="region",
        values="total_damage_million_usd", aggfunc="sum", fill_value=0,
    )
    fig = px.imshow(
        heat, title="Economic Damage Heatmap: Disaster Type × Region ($M)",
        color_continuous_scale="YlOrRd",
        labels=dict(color="Damage ($M)"),
        aspect="auto",
    )
    fig.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw Data"):
        st.dataframe(filtered.head(500), use_container_width=True)


# ── Footer ───────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #aaa; font-size: 0.85rem;'>"
    "Cat Model Dashboard · Data: FEMA OpenFEMA, NOAA NCEI, EM-DAT/CRED · "
    "Built with Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True,
)
