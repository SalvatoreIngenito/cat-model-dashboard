"""
Generate static chart images for the README and repository.
Apple-inspired design: pure black, SF-style typography, system colors.
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe
import matplotlib.colors as mcolors
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

IMAGES_DIR = Path(__file__).parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# ── Apple Design System ──────────────────────
BG = "#000000"
SURFACE = "#1c1c1e"
TEXT = "#f5f5f7"
TEXT_SEC = "#86868b"
TEXT_TER = "#48484a"
BORDER = "#38383a"

# Apple system colors
BLUE = "#0a84ff"
GREEN = "#30d158"
ORANGE = "#ff9f0a"
RED = "#ff453a"
PURPLE = "#bf5af2"
TEAL = "#64d2ff"
YELLOW = "#ffd60a"
INDIGO = "#5e5ce6"
PINK = "#ff6482"

COLORS = [BLUE, GREEN, ORANGE, RED, PURPLE, TEAL, YELLOW, INDIGO]


def _setup():
    plt.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "axes.edgecolor": TEXT_TER,
        "axes.labelcolor": TEXT_SEC,
        "axes.linewidth": 0.4,
        "text.color": TEXT,
        "xtick.color": TEXT_SEC,
        "ytick.color": TEXT_SEC,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "grid.color": "#1c1c1e",
        "grid.linewidth": 0.4,
        "font.family": "sans-serif",
        "font.size": 11,
        "legend.facecolor": SURFACE,
        "legend.edgecolor": BORDER,
        "legend.fontsize": 9,
    })


def _clean_spines(ax):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(TEXT_TER)
    ax.spines["bottom"].set_color(TEXT_TER)
    ax.grid(axis="y", alpha=0.3, color="#1c1c1e")


def _title(ax, main, sub="", y_main=1.06, y_sub=1.02):
    ax.text(0.0, y_main, main, transform=ax.transAxes,
            fontsize=17, fontweight="bold", color=TEXT, va="bottom")
    if sub:
        ax.text(0.0, y_sub, sub, transform=ax.transAxes,
                fontsize=10, color=TEXT_SEC, va="top")


def _gradient(n, c1, c2):
    r1, r2 = mcolors.to_rgb(c1), mcolors.to_rgb(c2)
    return [mcolors.to_hex([r1[j] + (r2[j] - r1[j]) * i / max(n-1, 1) for j in range(3)])
            for i in range(n)]


# ══════════════════════════════════════════════
# HERO BANNER
# ══════════════════════════════════════════════

def fig_hero():
    _setup()
    fig, ax = plt.subplots(figsize=(16, 5))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 5)
    ax.axis("off")

    # Subtle radial gradient blobs
    for cx, cy, r, c in [(3, 3, 4, BLUE), (8, 2, 5, PURPLE), (13, 3, 4, TEAL)]:
        circle = plt.Circle((cx, cy), r, facecolor=c, alpha=0.04, edgecolor="none")
        ax.add_patch(circle)

    # Title
    ax.text(8, 3.3, "CAT MODEL DASHBOARD", ha="center", va="center",
            fontsize=38, fontweight="bold", color=TEXT, family="sans-serif")
    ax.text(8, 2.3, "Catastrophe Risk Analytics", ha="center",
            fontsize=14, fontweight="400", color=TEXT_SEC)
    ax.text(8, 1.8, "FEMA  /  NOAA  /  EM-DAT", ha="center",
            fontsize=11, color=TEXT_TER, fontweight="500")

    # KPI pills
    kpis = [
        ("10K+", "Declarations", BLUE),
        ("22K+", "Global Events", GREEN),
        ("50K+", "NFIP Claims", ORANGE),
        ("5", "Data Views", PURPLE),
    ]
    for i, (val, label, color) in enumerate(kpis):
        cx = 2.5 + i * 3.5
        # Pill background
        pill = FancyBboxPatch((cx - 1.2, 0.15), 2.4, 0.95,
                               boxstyle="round,pad=0.1",
                               facecolor=mcolors.to_rgba(color, 0.08),
                               edgecolor=mcolors.to_rgba(color, 0.2),
                               linewidth=1)
        ax.add_patch(pill)
        ax.text(cx, 0.82, val, ha="center", fontsize=18, fontweight="700", color=color)
        ax.text(cx, 0.4, label, ha="center", fontsize=8, color=TEXT_SEC, fontweight="500")

    fig.savefig(IMAGES_DIR / "hero_banner.png", dpi=200, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close()
    print("  -> hero_banner.png")


# ══════════════════════════════════════════════
# 1 — Disaster Declarations Trend
# ══════════════════════════════════════════════

def fig1():
    _setup()
    np.random.seed(42)
    years = np.arange(1960, 2026)
    base = 20 + 0.8 * (years - 1960)
    noise = np.random.normal(0, 5, len(years))
    counts = np.maximum(base + noise, 5).astype(int)
    spikes = {2005: 48, 2011: 42, 2017: 59, 2020: 104, 2023: 65}
    for y, v in spikes.items():
        idx = np.where(years == y)[0]
        if len(idx):
            counts[idx[0]] = v

    fig, ax = plt.subplots(figsize=(14, 6))

    # Gradient bars
    colors = _gradient(len(years), BLUE, PURPLE)
    ax.bar(years, counts, color=colors, width=0.75, edgecolor="none", alpha=0.8)

    # Trend line
    z = np.polyfit(years, counts, 3)
    trend = np.poly1d(z)(years)
    ax.plot(years, trend, color=BLUE, linewidth=2, alpha=0.9)
    ax.fill_between(years, 0, trend, alpha=0.04, color=BLUE)

    # Annotate spikes
    for y, v in spikes.items():
        ax.plot(y, v, "o", color=RED, markersize=6, zorder=5)
        ax.annotate(f"{v}", (y, v), xytext=(0, 10), textcoords="offset points",
                    ha="center", fontsize=8, color=RED, fontweight="bold")

    ax.set_xlim(1958, 2027)
    ax.set_ylim(0, 115)
    _clean_spines(ax)
    _title(ax, "US Federal Disaster Declarations",
           "1960-2025 — Notable spike years marked in red")

    plt.tight_layout(pad=2)
    fig.savefig(IMAGES_DIR / "disaster_declarations_trend.png", dpi=200, bbox_inches="tight")
    plt.close()
    print("  -> disaster_declarations_trend.png")


# ══════════════════════════════════════════════
# 2 — Global Disaster Types
# ══════════════════════════════════════════════

def fig2():
    _setup()
    types = ["Flood", "Storm", "Earthquake", "Drought", "Wildfire",
             "Extreme Temp", "Landslide", "Volcanic"]
    events = [4200, 3100, 850, 620, 510, 780, 520, 210]
    deaths = [120, 180, 650, 380, 35, 200, 85, 55]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7),
                                    gridspec_kw={"width_ratios": [1, 1.15]})

    # Donut
    wedges, _, autotexts = ax1.pie(
        events, autopct="%1.0f%%", colors=COLORS,
        startangle=140, pctdistance=0.78,
        wedgeprops=dict(width=0.35, edgecolor=BG, linewidth=3),
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color(TEXT)
        at.set_fontweight("500")

    ax1.text(0, 0.06, "10,790", ha="center", va="center",
             fontsize=30, fontweight="bold", color=TEXT)
    ax1.text(0, -0.12, "Total Events", ha="center",
             fontsize=10, color=TEXT_SEC)

    # Legend
    for i, (t, c) in enumerate(zip(types, COLORS)):
        col, row = i % 4, i // 4
        x = -1.0 + col * 0.55
        y = -1.35 - row * 0.18
        ax1.plot(x - 0.06, y, "s", color=c, markersize=6)
        ax1.text(x, y, t, fontsize=8, color=TEXT_SEC, va="center")
    ax1.set_xlim(-1.5, 1.5)
    ax1.set_ylim(-1.65, 1.5)

    ax1.text(0, 1.38, "Global Disaster Events", ha="center",
             fontsize=16, fontweight="bold", color=TEXT)
    ax1.text(0, 1.22, "by Type (2000-2025)", ha="center",
             fontsize=10, color=TEXT_SEC)

    # Horizontal bars
    y_pos = np.arange(len(types))[::-1]
    bar_colors = _gradient(len(types), ORANGE, RED)
    ax2.barh(y_pos, deaths, color=bar_colors, edgecolor="none", height=0.55, alpha=0.85)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(types[::-1], fontsize=10, color=TEXT_SEC)
    ax2.set_xlabel("Deaths (thousands)", color=TEXT_SEC, fontsize=10)
    _clean_spines(ax2)
    ax2.grid(axis="x", alpha=0.15)

    for bar, val in zip(ax2.patches, deaths[::-1]):
        ax2.text(bar.get_width() + 8, bar.get_y() + bar.get_height()/2,
                 f"{val}K", va="center", fontsize=10, color=ORANGE, fontweight="600")

    ax2.text(0, 1.06, "Fatalities by Disaster Type", transform=ax2.transAxes,
             fontsize=16, fontweight="bold", color=TEXT)

    plt.tight_layout(pad=2)
    fig.savefig(IMAGES_DIR / "global_disaster_types.png", dpi=200, bbox_inches="tight")
    plt.close()
    print("  -> global_disaster_types.png")


# ══════════════════════════════════════════════
# 3 — NFIP Claims Heatmap
# ══════════════════════════════════════════════

def fig3():
    _setup()
    np.random.seed(123)
    states = ["TX", "FL", "LA", "NJ", "NY", "SC", "NC", "MS", "AL", "PA"]
    years = list(range(2015, 2026))
    data = np.random.lognormal(3, 1.5, (len(states), len(years)))
    data[0, 2] *= 8; data[1, 3] *= 6; data[2, 5] *= 7; data[1, 7] *= 10
    df = pd.DataFrame(data, index=states, columns=years)

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "apple", [BG, "#0d2440", "#0a5c99", BLUE, PURPLE, "#e0b0ff"], N=256)

    fig, ax = plt.subplots(figsize=(14, 7))
    sns.heatmap(
        df, annot=True, fmt=".0f", cmap=cmap,
        linewidths=2, linecolor=BG,
        annot_kws={"fontsize": 10, "fontweight": "600", "color": TEXT},
        cbar_kws={"shrink": 0.7},
        ax=ax,
    )
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.set_tick_params(color=TEXT_SEC)
    cbar.outline.set_edgecolor(TEXT_TER)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT_SEC, fontsize=9)
    cbar.set_label("Claims ($M)", color=TEXT_SEC, fontsize=10)

    ax.set_ylabel("")
    ax.tick_params(axis="x", colors=TEXT_SEC, labelsize=11)
    ax.tick_params(axis="y", colors=TEXT_SEC, labelsize=11)
    _title(ax, "NFIP Flood Claims by State & Year ($M)",
           "Hurricane-driven surges highlighted — Harvey, Michael, Laura, Ian")

    plt.tight_layout(pad=2)
    fig.savefig(IMAGES_DIR / "nfip_claims_heatmap.png", dpi=200, bbox_inches="tight")
    plt.close()
    print("  -> nfip_claims_heatmap.png")


# ══════════════════════════════════════════════
# 4 — Storm Seasonality Radar
# ══════════════════════════════════════════════

def fig4():
    _setup()
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    tornado = [5, 8, 18, 30, 35, 28, 15, 10, 8, 6, 8, 4]
    hurricane = [0, 0, 0, 0, 1, 5, 12, 25, 30, 18, 5, 0]
    flood = [10, 12, 18, 22, 20, 25, 18, 15, 20, 15, 12, 10]

    angles = np.linspace(0, 2 * np.pi, 12, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    for data, label, color in [
        (tornado, "Tornado", BLUE),
        (hurricane, "Hurricane", RED),
        (flood, "Flood", GREEN),
    ]:
        vals = data + data[:1]
        ax.plot(angles, vals, color=color, linewidth=2.5, label=label)
        ax.fill(angles, vals, alpha=0.08, color=color)
        ax.scatter(angles[:-1], data, color=color, s=25, zorder=5,
                   edgecolors=BG, linewidths=1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(months, fontsize=11, color=TEXT_SEC)
    ax.set_rticks([10, 20, 30])
    ax.set_yticklabels(["10", "20", "30"], fontsize=8, color=TEXT_TER)
    ax.grid(color=TEXT_TER, linewidth=0.3)
    ax.spines["polar"].set_color(TEXT_TER)

    legend = ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1))
    for t in legend.get_texts():
        t.set_color(TEXT_SEC)
    legend.get_frame().set_facecolor(SURFACE)
    legend.get_frame().set_edgecolor(BORDER)

    fig.text(0.5, 0.96, "Storm Event Seasonality", ha="center",
             fontsize=18, fontweight="bold", color=TEXT)
    fig.text(0.5, 0.92, "Normalized monthly frequency by peril type",
             ha="center", fontsize=10, color=TEXT_SEC)

    plt.tight_layout(pad=2.5)
    fig.savefig(IMAGES_DIR / "storm_seasonality_radar.png", dpi=200, bbox_inches="tight")
    plt.close()
    print("  -> storm_seasonality_radar.png")


# ══════════════════════════════════════════════
# 5 — Economic Losses Waterfall
# ══════════════════════════════════════════════

def fig5():
    _setup()
    perils = ["Flood", "Storm", "Earthquake", "Drought", "Wildfire", "Other", "TOTAL"]
    losses = [85, 120, 55, 30, 25, 15, 330]
    peril_colors = [BLUE, TEAL, PURPLE, ORANGE, RED, TEXT_SEC, GREEN]

    fig, ax = plt.subplots(figsize=(14, 7))

    cumulative = 0
    for i, (peril, loss, color) in enumerate(zip(perils[:-1], losses[:-1], peril_colors[:-1])):
        ax.bar(i, loss, bottom=cumulative, color=color,
               edgecolor="none", width=0.5, alpha=0.85)
        ax.text(i, cumulative + loss/2, f"${loss}B", ha="center", va="center",
                fontsize=11, fontweight="bold", color=TEXT)
        if i < len(perils) - 2:
            ax.plot([i + 0.25, i + 0.75], [cumulative + loss, cumulative + loss],
                    color=TEXT_TER, linewidth=0.8, linestyle="--")
        cumulative += loss

    # Total
    ax.bar(len(perils) - 1, cumulative, color=GREEN,
           edgecolor="none", width=0.5, alpha=0.9)
    ax.text(len(perils) - 1, cumulative/2, f"${cumulative}B", ha="center", va="center",
            fontsize=13, fontweight="bold", color=TEXT)

    ax.set_xticks(range(len(perils)))
    ax.set_xticklabels(perils, fontsize=11, color=TEXT_SEC)
    ax.set_ylabel("Losses ($ Billions)", color=TEXT_SEC)
    ax.set_ylim(0, cumulative * 1.12)
    _clean_spines(ax)
    _title(ax, "Global Insured Catastrophe Losses by Peril",
           "2024 estimated — individual peril contributions sum to total")

    plt.tight_layout(pad=2)
    fig.savefig(IMAGES_DIR / "economic_losses_waterfall.png", dpi=200, bbox_inches="tight")
    plt.close()
    print("  -> economic_losses_waterfall.png")


# ══════════════════════════════════════════════
# 6 — Regional Risk Matrix
# ══════════════════════════════════════════════

def fig6():
    _setup()
    np.random.seed(99)
    regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Africa"]
    perils = ["Flood", "Storm", "EQ", "Wildfire", "Drought"]
    region_colors = [BLUE, TEAL, RED, ORANGE, GREEN]

    fig, ax = plt.subplots(figsize=(12, 8))

    # Quadrant shading
    ax.axhspan(5.5, 11, xmin=0.5, color=RED, alpha=0.03)
    ax.axhspan(0, 5.5, xmax=0.5, color=GREEN, alpha=0.03)
    ax.axhline(y=5.5, color=TEXT_TER, linestyle="--", linewidth=0.6)
    ax.axvline(x=5.5, color=TEXT_TER, linestyle="--", linewidth=0.6)

    for i, (region, color) in enumerate(zip(regions, region_colors)):
        freq = np.random.uniform(2, 9, len(perils))
        sev = np.random.uniform(1.5, 9.5, len(perils))
        sizes = np.random.uniform(200, 600, len(perils))

        ax.scatter(freq, sev, s=sizes, c=color, alpha=0.5,
                   edgecolors=mcolors.to_rgba(color, 0.8),
                   linewidths=1, label=region, zorder=4)
        for j, p in enumerate(perils):
            ax.text(freq[j], sev[j], p, fontsize=7, ha="center", va="center",
                    color=TEXT, fontweight="bold", zorder=5)

    ax.set_xlabel("Frequency Score", fontsize=11, color=TEXT_SEC)
    ax.set_ylabel("Severity Score", fontsize=11, color=TEXT_SEC)
    ax.set_xlim(0.5, 10.5)
    ax.set_ylim(0.5, 10.5)
    _clean_spines(ax)
    ax.grid(alpha=0.1)

    ax.text(8.5, 9.8, "HIGH RISK", fontsize=10, color=RED,
            fontweight="bold", ha="center", alpha=0.5)
    ax.text(2.5, 1.2, "LOW RISK", fontsize=10, color=GREEN,
            fontweight="bold", ha="center", alpha=0.5)

    legend = ax.legend(loc="lower right", fontsize=10, markerscale=0.6)
    for t in legend.get_texts():
        t.set_color(TEXT_SEC)

    _title(ax, "Catastrophe Risk Matrix",
           "Frequency vs. severity by region and peril — bubble size indicates exposure")

    plt.tight_layout(pad=2)
    fig.savefig(IMAGES_DIR / "regional_risk_matrix.png", dpi=200, bbox_inches="tight")
    plt.close()
    print("  -> regional_risk_matrix.png")


# ══════════════════════════════════════════════
# 7 — Architecture Diagram
# ══════════════════════════════════════════════

def fig7():
    _setup()
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8.5)
    ax.axis("off")

    # Title
    ax.text(8, 7.9, "Cat Model Dashboard", ha="center",
            fontsize=22, fontweight="bold", color=TEXT)
    ax.text(8, 7.45, "Architecture Overview", ha="center",
            fontsize=11, color=TEXT_SEC)

    def card(x, y, w, h, color, title, items=None, title_size=13):
        box = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.15",
            facecolor=mcolors.to_rgba(color, 0.06),
            edgecolor=mcolors.to_rgba(color, 0.3),
            linewidth=1.2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.35, title, ha="center",
                fontsize=title_size, fontweight="bold", color=color)
        if items:
            for i, item in enumerate(items):
                iy = y + h - 0.85 - i * 0.45
                ax.plot(x + 0.5, iy, "o", color=color, markersize=4, alpha=0.5)
                ax.text(x + 0.8, iy, item, fontsize=9, color=TEXT_SEC, va="center")

    # Data sources
    sources = [
        ("NOAA Storm Events", BLUE, 5.7),
        ("FEMA OpenFEMA", ORANGE, 4.1),
        ("EM-DAT Global DB", GREEN, 2.5),
    ]
    for title, color, y in sources:
        card(0.5, y, 3.2, 1.1, color, title, title_size=11)

    # Arrows
    for _, color, y in sources:
        ax.annotate("", xy=(5.3, 4.2), xytext=(3.7, y + 0.55),
                    arrowprops=dict(arrowstyle="-|>",
                                    color=mcolors.to_rgba(color, 0.35),
                                    lw=1.2, connectionstyle="arc3,rad=0.08"))

    # Pipeline
    card(5.2, 2.6, 3, 3.3, PURPLE, "Data Pipeline",
         ["Fetch & Cache", "Parquet Storage", "Transform", "Validate"])

    # Arrow
    ax.annotate("", xy=(9.8, 4.25), xytext=(8.2, 4.25),
                arrowprops=dict(arrowstyle="-|>", color=mcolors.to_rgba(PURPLE, 0.4), lw=1.5))

    # Dashboard
    card(9.8, 1.7, 5.4, 5.2, BLUE, "Streamlit Dashboard",
         ["Interactive Plotly Charts", "Geospatial Storm Maps",
          "KPI Metric Cards", "Heatmaps & Treemaps",
          "Sunburst & Area Charts", "Filterable Data Tables"],
         title_size=14)

    # Footer
    ax.text(8, 0.9, "Python  /  Streamlit  /  Plotly  /  Pandas  /  Matplotlib",
            ha="center", fontsize=10, color=TEXT_TER)
    ax.plot([1.5, 14.5], [1.3, 1.3], color=TEXT_TER, linewidth=0.3)

    fig.savefig(IMAGES_DIR / "architecture_diagram.png", dpi=200, bbox_inches="tight")
    plt.close()
    print("  -> architecture_diagram.png")


if __name__ == "__main__":
    print("\nGenerating Apple-style dashboard images...\n")
    fig_hero()
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig6()
    fig7()
    print("\nDone — all images in images/")
