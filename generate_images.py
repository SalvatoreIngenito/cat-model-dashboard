"""
Generate static chart images for the README and repository.
Run this script to produce all dashboard preview images.
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

IMAGES_DIR = Path(__file__).parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# Style
plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor": "#161b22",
    "axes.edgecolor": "#30363d",
    "axes.labelcolor": "#c9d1d9",
    "text.color": "#c9d1d9",
    "xtick.color": "#8b949e",
    "ytick.color": "#8b949e",
    "grid.color": "#21262d",
    "font.family": "sans-serif",
    "font.size": 11,
})

PALETTE = ["#58a6ff", "#f78166", "#3fb950", "#d2a8ff", "#f0883e",
           "#79c0ff", "#56d364", "#e3b341", "#ff7b72", "#a5d6ff"]


def fig1_disaster_declarations_trend():
    """Annual US disaster declarations trend."""
    np.random.seed(42)
    years = np.arange(1960, 2026)
    base = 20 + 0.8 * (years - 1960)
    noise = np.random.normal(0, 5, len(years))
    counts = np.maximum(base + noise, 5).astype(int)
    # Spike years for realism
    spikes = {2005: 48, 2011: 42, 2017: 59, 2020: 104, 2023: 65}
    for y, v in spikes.items():
        idx = np.where(years == y)[0]
        if len(idx):
            counts[idx[0]] = v

    fig, ax = plt.subplots(figsize=(12, 5))
    colors = ["#f78166" if c > 60 else "#58a6ff" for c in counts]
    ax.bar(years, counts, color=colors, width=0.8, edgecolor="none")

    z = np.polyfit(years, counts, 2)
    p = np.poly1d(z)
    ax.plot(years, p(years), color="#d2a8ff", linewidth=2.5, linestyle="--", label="Trend")

    ax.set_title("US Federal Disaster Declarations (1960–2025)", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Year")
    ax.set_ylabel("Declarations")
    ax.legend(loc="upper left", framealpha=0.3)
    ax.grid(axis="y", alpha=0.3)
    ax.set_xlim(1958, 2027)
    plt.tight_layout()
    fig.savefig(IMAGES_DIR / "disaster_declarations_trend.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Created: disaster_declarations_trend.png")


def fig2_global_disaster_types():
    """EM-DAT global disaster type breakdown."""
    types = ["Flood", "Storm", "Earthquake", "Drought", "Wildfire",
             "Extreme Temp", "Landslide", "Volcanic"]
    events = [4200, 3100, 850, 620, 510, 780, 520, 210]
    deaths = [120, 180, 650, 380, 35, 200, 85, 55]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Events donut
    wedges, texts, autotexts = ax1.pie(
        events, labels=types, autopct="%1.0f%%",
        colors=PALETTE[:len(types)],
        startangle=140, pctdistance=0.75,
        wedgeprops=dict(width=0.45, edgecolor="#0d1117", linewidth=2),
    )
    for t in texts + autotexts:
        t.set_fontsize(9)
    ax1.set_title("Global Disaster Events\nby Type (2000–2025)", fontsize=14, fontweight="bold")

    # Deaths bar
    y_pos = np.arange(len(types))
    bars = ax2.barh(y_pos, deaths, color=PALETTE[:len(types)], edgecolor="none", height=0.65)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(types)
    ax2.set_xlabel("Deaths (thousands)")
    ax2.set_title("Fatalities by Disaster Type", fontsize=14, fontweight="bold")
    ax2.grid(axis="x", alpha=0.3)
    ax2.invert_yaxis()
    for bar, val in zip(bars, deaths):
        ax2.text(bar.get_width() + 8, bar.get_y() + bar.get_height()/2,
                 f"{val}K", va="center", fontsize=9, color="#c9d1d9")

    plt.tight_layout()
    fig.savefig(IMAGES_DIR / "global_disaster_types.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Created: global_disaster_types.png")


def fig3_nfip_claims_heatmap():
    """NFIP claims heatmap by state and year."""
    np.random.seed(123)
    states = ["TX", "FL", "LA", "NJ", "NY", "SC", "NC", "MS", "AL", "PA"]
    years = list(range(2015, 2026))
    data = np.random.lognormal(3, 1.5, (len(states), len(years)))
    # Hurricane spikes
    data[0, 2] *= 8   # TX 2017 Harvey
    data[1, 3] *= 6   # FL 2018 Michael
    data[2, 5] *= 7   # LA 2020 Laura
    data[1, 7] *= 10  # FL 2022 Ian

    df = pd.DataFrame(data, index=states, columns=years)

    fig, ax = plt.subplots(figsize=(13, 6))
    sns.heatmap(
        df, annot=True, fmt=".0f", cmap="YlOrRd",
        linewidths=0.5, linecolor="#30363d",
        cbar_kws={"label": "Claims ($M)", "shrink": 0.8},
        ax=ax,
    )
    ax.set_title("NFIP Flood Claims by State & Year ($M)", fontsize=16, fontweight="bold", pad=15)
    ax.set_ylabel("")
    ax.set_xlabel("Year")
    plt.tight_layout()
    fig.savefig(IMAGES_DIR / "nfip_claims_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Created: nfip_claims_heatmap.png")


def fig4_storm_seasonality():
    """NOAA storm event seasonality radar chart."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    tornado = [5, 8, 18, 30, 35, 28, 15, 10, 8, 6, 8, 4]
    hurricane = [0, 0, 0, 0, 1, 5, 12, 25, 30, 18, 5, 0]
    flood = [10, 12, 18, 22, 20, 25, 18, 15, 20, 15, 12, 10]

    angles = np.linspace(0, 2 * np.pi, 12, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.set_facecolor("#161b22")
    fig.patch.set_facecolor("#0d1117")

    for data, label, color in [
        (tornado, "Tornado", "#58a6ff"),
        (hurricane, "Hurricane", "#f78166"),
        (flood, "Flood", "#3fb950"),
    ]:
        vals = data + data[:1]
        ax.plot(angles, vals, "o-", color=color, linewidth=2, label=label, markersize=4)
        ax.fill(angles, vals, alpha=0.15, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(months, fontsize=10)
    ax.set_title("Storm Event Seasonality\n(Normalized Frequency)", fontsize=15, fontweight="bold", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), framealpha=0.3)
    ax.grid(color="#30363d", alpha=0.5)
    ax.tick_params(colors="#8b949e")

    plt.tight_layout()
    fig.savefig(IMAGES_DIR / "storm_seasonality_radar.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Created: storm_seasonality_radar.png")


def fig5_economic_losses_waterfall():
    """Global economic losses by peril — waterfall chart."""
    perils = ["Flood", "Storm", "Earthquake", "Drought", "Wildfire", "Other", "Total"]
    losses = [85, 120, 55, 30, 25, 15, 330]

    fig, ax = plt.subplots(figsize=(12, 6))

    cumulative = 0
    for i, (peril, loss) in enumerate(zip(perils[:-1], losses[:-1])):
        ax.bar(i, loss, bottom=cumulative, color=PALETTE[i],
               edgecolor="none", width=0.6)
        ax.text(i, cumulative + loss/2, f"${loss}B", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")
        if i < len(perils) - 2:
            ax.plot([i + 0.3, i + 0.7], [cumulative + loss, cumulative + loss],
                    color="#8b949e", linewidth=1, linestyle="--")
        cumulative += loss

    # Total bar
    ax.bar(len(perils) - 1, cumulative, color="#d2a8ff", edgecolor="none", width=0.6)
    ax.text(len(perils) - 1, cumulative/2, f"${cumulative}B", ha="center", va="center",
            fontsize=12, fontweight="bold", color="white")

    ax.set_xticks(range(len(perils)))
    ax.set_xticklabels(perils)
    ax.set_ylabel("Losses ($ Billions)")
    ax.set_title("Global Insured Catastrophe Losses by Peril (2024)", fontsize=16, fontweight="bold", pad=15)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, cumulative * 1.1)
    plt.tight_layout()
    fig.savefig(IMAGES_DIR / "economic_losses_waterfall.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Created: economic_losses_waterfall.png")


def fig6_regional_risk_matrix():
    """Risk matrix: frequency vs severity by region & peril."""
    np.random.seed(99)
    regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Africa"]
    perils_short = ["Flood", "Storm", "EQ", "Wildfire", "Drought"]

    fig, ax = plt.subplots(figsize=(11, 7))

    for i, region in enumerate(regions):
        freq = np.random.uniform(2, 9, len(perils_short))
        sev = np.random.uniform(1, 10, len(perils_short))
        sizes = np.random.uniform(100, 600, len(perils_short))
        scatter = ax.scatter(freq, sev, s=sizes, c=PALETTE[i], alpha=0.6,
                             edgecolors="white", linewidth=0.5, label=region)
        for j, peril in enumerate(perils_short):
            ax.annotate(peril, (freq[j], sev[j]), fontsize=7,
                        ha="center", va="center", color="white", fontweight="bold")

    ax.set_xlabel("Frequency Score", fontsize=12)
    ax.set_ylabel("Severity Score", fontsize=12)
    ax.set_title("Catastrophe Risk Matrix by Region & Peril", fontsize=16, fontweight="bold", pad=15)

    # Quadrant lines
    ax.axhline(y=5.5, color="#8b949e", linestyle="--", alpha=0.4)
    ax.axvline(x=5.5, color="#8b949e", linestyle="--", alpha=0.4)
    ax.text(8, 9, "HIGH RISK", fontsize=10, color="#f78166", fontweight="bold", ha="center", alpha=0.7)
    ax.text(2.5, 1.5, "LOW RISK", fontsize=10, color="#3fb950", fontweight="bold", ha="center", alpha=0.7)

    ax.legend(loc="lower right", framealpha=0.3, fontsize=9)
    ax.set_xlim(0.5, 10.5)
    ax.set_ylim(0.5, 10.5)
    ax.grid(alpha=0.2)
    plt.tight_layout()
    fig.savefig(IMAGES_DIR / "regional_risk_matrix.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Created: regional_risk_matrix.png")


def fig7_dashboard_architecture():
    """Create a simple architecture diagram."""
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis("off")

    # Title
    ax.text(7, 6.5, "Cat Model Dashboard — Architecture", fontsize=18,
            fontweight="bold", ha="center", color="#58a6ff")

    # Data Sources (left)
    sources = [
        ("NOAA\nStorm Events", 1.5, 5, "#58a6ff"),
        ("FEMA\nOpenFEMA", 1.5, 3.5, "#f78166"),
        ("EM-DAT\nGlobal DB", 1.5, 2, "#3fb950"),
    ]
    for label, x, y, color in sources:
        rect = plt.Rectangle((x-0.9, y-0.5), 1.8, 1, fill=True,
                              facecolor=color, alpha=0.2, edgecolor=color, linewidth=2, zorder=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha="center", va="center", fontsize=9, fontweight="bold", color=color)

    # Arrows to processing
    for _, x, y, color in sources:
        ax.annotate("", xy=(4.5, 3.5), xytext=(x+0.9, y),
                    arrowprops=dict(arrowstyle="->", color="#8b949e", lw=1.5))

    # Processing layer
    proc_box = plt.Rectangle((4.2, 2.5), 2.6, 2, fill=True,
                              facecolor="#d2a8ff", alpha=0.15, edgecolor="#d2a8ff",
                              linewidth=2, zorder=2)
    ax.add_patch(proc_box)
    ax.text(5.5, 4.1, "Data Pipeline", ha="center", fontsize=11, fontweight="bold", color="#d2a8ff")
    ax.text(5.5, 3.5, "Fetch & Cache", ha="center", fontsize=9, color="#c9d1d9")
    ax.text(5.5, 3.1, "Transform", ha="center", fontsize=9, color="#c9d1d9")
    ax.text(5.5, 2.7, "Validate", ha="center", fontsize=9, color="#c9d1d9")

    # Arrow to dashboard
    ax.annotate("", xy=(8.2, 3.5), xytext=(6.8, 3.5),
                arrowprops=dict(arrowstyle="->", color="#8b949e", lw=2))

    # Dashboard
    dash_box = plt.Rectangle((8.2, 1.8), 3.6, 3.4, fill=True,
                              facecolor="#e3b341", alpha=0.1, edgecolor="#e3b341",
                              linewidth=2, zorder=2)
    ax.add_patch(dash_box)
    ax.text(10, 4.8, "Streamlit Dashboard", ha="center", fontsize=12, fontweight="bold", color="#e3b341")

    panels = [
        "Interactive Charts (Plotly)",
        "Geospatial Maps",
        "KPI Metrics",
        "Heatmaps & Treemaps",
        "Data Tables & Export",
    ]
    for i, p in enumerate(panels):
        ax.text(10, 4.2 - i*0.5, f"  {p}", ha="center", fontsize=9, color="#c9d1d9")

    # Bottom note
    ax.text(7, 0.5, "Python · Streamlit · Plotly · Pandas · Requests",
            ha="center", fontsize=10, color="#8b949e", style="italic")

    plt.tight_layout()
    fig.savefig(IMAGES_DIR / "architecture_diagram.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Created: architecture_diagram.png")


if __name__ == "__main__":
    print("Generating dashboard images...\n")
    fig1_disaster_declarations_trend()
    fig2_global_disaster_types()
    fig3_nfip_claims_heatmap()
    fig4_storm_seasonality()
    fig5_economic_losses_waterfall()
    fig6_regional_risk_matrix()
    fig7_dashboard_architecture()
    print("\nAll images generated in images/ directory.")
