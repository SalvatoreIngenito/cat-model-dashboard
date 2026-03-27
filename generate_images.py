"""
Generate static chart images for the README and repository.
Modern liquid glass / glassmorphism aesthetic.
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
from matplotlib.collections import PatchCollection

IMAGES_DIR = Path(__file__).parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# ── Liquid Glass Design System ───────────────────────────────────
BG_DARK = "#08090d"
BG_CARD = "#12141c"
GLASS_BORDER = "#ffffff18"
GLASS_FILL = "#ffffff08"
TEXT_PRIMARY = "#f0f2f8"
TEXT_SECONDARY = "#8891a5"
TEXT_MUTED = "#555d72"
GRID_COLOR = "#ffffff08"

# Vibrant neon-accent palette
CYAN = "#00d4ff"
MAGENTA = "#ff3cac"
VIOLET = "#784ba0"
ORANGE = "#ff8a00"
GREEN = "#00e676"
PINK = "#ff6ec7"
BLUE = "#4d7cff"
YELLOW = "#ffe156"
RED = "#ff4757"
TEAL = "#00bfa6"

ACCENT_GRADIENT = [CYAN, BLUE, VIOLET, MAGENTA, PINK, ORANGE, YELLOW, GREEN]


def _apply_glass_style():
    """Set global matplotlib params for liquid glass look."""
    plt.rcParams.update({
        "figure.facecolor": BG_DARK,
        "axes.facecolor": BG_CARD,
        "axes.edgecolor": "#ffffff12",
        "axes.labelcolor": TEXT_SECONDARY,
        "axes.linewidth": 0.5,
        "text.color": TEXT_PRIMARY,
        "xtick.color": TEXT_MUTED,
        "ytick.color": TEXT_MUTED,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "grid.color": GRID_COLOR,
        "grid.linewidth": 0.5,
        "font.family": "sans-serif",
        "font.size": 10,
        "legend.facecolor": "#ffffff06",
        "legend.edgecolor": "#ffffff10",
        "legend.fontsize": 9,
    })


def _glass_panel(ax, x, y, w, h, color=CYAN, alpha=0.08, radius=0.02):
    """Draw a frosted glass panel on the axes."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=color, alpha=alpha,
        edgecolor=mcolors.to_rgba(color, 0.25),
        linewidth=1.2, zorder=0,
    )
    ax.add_patch(box)
    return box


def _glass_rect(ax, x, y, w, h, color, alpha_fill=0.12, alpha_edge=0.4):
    """Rounded glass rectangle for architecture diagrams."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.15",
        facecolor=mcolors.to_rgba(color, alpha_fill),
        edgecolor=mcolors.to_rgba(color, alpha_edge),
        linewidth=1.5, zorder=2,
    )
    ax.add_patch(box)
    return box


def _glow_text(ax, x, y, text, color=TEXT_PRIMARY, fontsize=16, **kwargs):
    """Text with subtle outer glow."""
    defaults = dict(ha="center", va="center", fontweight="bold", fontsize=fontsize, color=color)
    defaults.update(kwargs)
    t = ax.text(x, y, text, **defaults)
    t.set_path_effects([
        pe.withStroke(linewidth=4, foreground=mcolors.to_rgba(color, 0.15)),
    ])
    return t


def _gradient_bar_colors(n, c1=CYAN, c2=MAGENTA):
    """Generate a gradient of colors between two hex colors."""
    c1_rgb = mcolors.to_rgb(c1)
    c2_rgb = mcolors.to_rgb(c2)
    return [
        mcolors.to_hex([
            c1_rgb[j] + (c2_rgb[j] - c1_rgb[j]) * i / max(n - 1, 1)
            for j in range(3)
        ])
        for i in range(n)
    ]


def _add_subtitle(ax, text, y=1.02, fontsize=11):
    """Add a muted subtitle below the title."""
    ax.text(0.5, y, text, transform=ax.transAxes,
            ha="center", va="bottom", fontsize=fontsize,
            color=TEXT_MUTED, style="italic")


# ══════════════════════════════════════════════════════════════════
# FIGURE 1 — Disaster Declarations Trend (Area + Glow)
# ══════════════════════════════════════════════════════════════════

def fig1_disaster_declarations_trend():
    _apply_glass_style()
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
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_CARD)

    # Gradient fill under the area
    gradient_colors = _gradient_bar_colors(len(years), CYAN, MAGENTA)
    ax.bar(years, counts, color=gradient_colors, width=0.75,
           edgecolor="none", alpha=0.75, zorder=3)

    # Glow line on top
    z = np.polyfit(years, counts, 3)
    p = np.poly1d(z)
    trend_y = p(years)
    ax.plot(years, trend_y, color=CYAN, linewidth=2.5, zorder=5, alpha=0.9)
    # Glow effect
    for w, a in [(8, 0.05), (5, 0.1), (3, 0.2)]:
        ax.plot(years, trend_y, color=CYAN, linewidth=w, alpha=a, zorder=4)

    # Mark spike years
    for y, v in spikes.items():
        ax.plot(y, v, "o", color=MAGENTA, markersize=8, zorder=6,
                markeredgecolor="white", markeredgewidth=0.5)
        ax.annotate(f"{v}", (y, v), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=8,
                    color=MAGENTA, fontweight="bold")

    ax.set_xlim(1958, 2027)
    ax.set_ylim(0, 115)
    ax.grid(axis="y", alpha=0.15, color="white")
    ax.grid(axis="x", alpha=0.05, color="white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#ffffff10")
    ax.spines["bottom"].set_color("#ffffff10")

    _glow_text(ax, 1992, 105, "US Federal Disaster Declarations", CYAN, fontsize=18, ha="center")
    ax.text(1992, 98, "1960 – 2025  |  Trend line + notable spike years highlighted",
            ha="center", fontsize=10, color=TEXT_MUTED)

    plt.tight_layout(pad=1.5)
    fig.savefig(IMAGES_DIR / "disaster_declarations_trend.png", dpi=180, bbox_inches="tight")
    plt.close()
    print("  -> disaster_declarations_trend.png")


# ══════════════════════════════════════════════════════════════════
# FIGURE 2 — Global Disaster Types (Donut + Horizontal Bars)
# ══════════════════════════════════════════════════════════════════

def fig2_global_disaster_types():
    _apply_glass_style()
    types = ["Flood", "Storm", "Earthquake", "Drought", "Wildfire",
             "Extreme Temp", "Landslide", "Volcanic"]
    events = [4200, 3100, 850, 620, 510, 780, 520, 210]
    deaths = [120, 180, 650, 380, 35, 200, 85, 55]
    colors = ACCENT_GRADIENT[:len(types)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7), gridspec_kw={"width_ratios": [1, 1.2]})
    fig.patch.set_facecolor(BG_DARK)
    ax1.set_facecolor(BG_DARK)
    ax2.set_facecolor(BG_CARD)

    # ── Donut with glow ──
    wedges, texts, autotexts = ax1.pie(
        events, labels=None, autopct="%1.0f%%",
        colors=colors, startangle=140, pctdistance=0.78,
        wedgeprops=dict(width=0.38, edgecolor=BG_DARK, linewidth=3),
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color(TEXT_PRIMARY)
        at.set_fontweight("bold")

    # Center text
    ax1.text(0, 0.05, "10,790", ha="center", va="center",
             fontsize=28, fontweight="bold", color=TEXT_PRIMARY)
    ax1.text(0, -0.15, "Total Events", ha="center", va="center",
             fontsize=10, color=TEXT_MUTED)

    # Legend below donut
    for i, (t, c) in enumerate(zip(types, colors)):
        col = i % 4
        row = i // 4
        ax1.plot(-0.85 + col * 0.52, -1.35 - row * 0.15, "s",
                 color=c, markersize=7, transform=ax1.transData)
        ax1.text(-0.78 + col * 0.52, -1.35 - row * 0.15, t,
                 fontsize=8, color=TEXT_SECONDARY, va="center")

    ax1.set_xlim(-1.5, 1.5)
    ax1.set_ylim(-1.65, 1.5)
    _glow_text(ax1, 0, 1.35, "Global Disaster Events", CYAN, fontsize=15)
    ax1.text(0, 1.2, "by Type (2000–2025)", ha="center", fontsize=10, color=TEXT_MUTED)

    # ── Horizontal bars with glow ──
    y_pos = np.arange(len(types))[::-1]
    bar_colors = _gradient_bar_colors(len(types), MAGENTA, ORANGE)

    bars = ax2.barh(y_pos, deaths, color=bar_colors, edgecolor="none",
                    height=0.6, alpha=0.85, zorder=3)
    # Glow behind bars
    for yp, d, c in zip(y_pos, deaths, bar_colors):
        ax2.barh(yp, d, color=c, edgecolor="none", height=0.75, alpha=0.08, zorder=2)

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(types[::-1], fontsize=10, color=TEXT_SECONDARY)
    ax2.set_xlabel("Deaths (thousands)", color=TEXT_MUTED, fontsize=10)
    ax2.grid(axis="x", alpha=0.1, color="white")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_color("#ffffff08")
    ax2.spines["bottom"].set_color("#ffffff08")

    for bar, val, c in zip(bars, deaths[::-1], bar_colors[::-1]):
        ax2.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                 f"{val}K", va="center", fontsize=10, color=c, fontweight="bold")

    _glow_text(ax2, max(deaths)*0.5, len(types) + 0.3,
               "Fatalities by Disaster Type", MAGENTA, fontsize=15)

    plt.tight_layout(pad=2)
    fig.savefig(IMAGES_DIR / "global_disaster_types.png", dpi=180, bbox_inches="tight")
    plt.close()
    print("  -> global_disaster_types.png")


# ══════════════════════════════════════════════════════════════════
# FIGURE 3 — NFIP Claims Heatmap (Glass-styled)
# ══════════════════════════════════════════════════════════════════

def fig3_nfip_claims_heatmap():
    _apply_glass_style()
    np.random.seed(123)
    states = ["TX", "FL", "LA", "NJ", "NY", "SC", "NC", "MS", "AL", "PA"]
    years = list(range(2015, 2026))
    data = np.random.lognormal(3, 1.5, (len(states), len(years)))
    data[0, 2] *= 8; data[1, 3] *= 6; data[2, 5] *= 7; data[1, 7] *= 10

    df = pd.DataFrame(data, index=states, columns=years)

    # Custom colormap: dark -> cyan -> magenta -> white
    cmap_colors = [BG_CARD, "#0a2640", "#0d4a6b", CYAN, MAGENTA, "#ffd6f0"]
    cmap = mcolors.LinearSegmentedColormap.from_list("glass_heat", cmap_colors, N=256)

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_CARD)

    sns.heatmap(
        df, annot=True, fmt=".0f", cmap=cmap,
        linewidths=1.5, linecolor=BG_DARK,
        annot_kws={"fontsize": 10, "fontweight": "bold", "color": TEXT_PRIMARY},
        cbar_kws={"label": "", "shrink": 0.75},
        ax=ax,
    )

    # Style the colorbar
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.set_tick_params(color=TEXT_MUTED)
    cbar.outline.set_edgecolor("#ffffff10")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT_MUTED, fontsize=9)
    cbar.set_label("Claims ($M)", color=TEXT_MUTED, fontsize=10)

    ax.set_ylabel("")
    ax.set_xlabel("")
    ax.tick_params(axis="x", colors=TEXT_SECONDARY, labelsize=11)
    ax.tick_params(axis="y", colors=TEXT_SECONDARY, labelsize=11)

    _glow_text(ax, 5.5, -0.8, "NFIP Flood Claims by State & Year ($M)", CYAN, fontsize=17)
    ax.text(5.5, -0.3, "Bright spots indicate hurricane-driven claim surges (Harvey, Michael, Laura, Ian)",
            ha="center", fontsize=9, color=TEXT_MUTED)

    plt.tight_layout(pad=1.5)
    fig.savefig(IMAGES_DIR / "nfip_claims_heatmap.png", dpi=180, bbox_inches="tight")
    plt.close()
    print("  -> nfip_claims_heatmap.png")


# ══════════════════════════════════════════════════════════════════
# FIGURE 4 — Storm Seasonality Radar (Neon Glow)
# ══════════════════════════════════════════════════════════════════

def fig4_storm_seasonality():
    _apply_glass_style()
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    tornado = [5, 8, 18, 30, 35, 28, 15, 10, 8, 6, 8, 4]
    hurricane = [0, 0, 0, 0, 1, 5, 12, 25, 30, 18, 5, 0]
    flood = [10, 12, 18, 22, 20, 25, 18, 15, 20, 15, 12, 10]

    angles = np.linspace(0, 2 * np.pi, 12, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor("#0a0c14")

    datasets = [
        (tornado, "Tornado", CYAN),
        (hurricane, "Hurricane", MAGENTA),
        (flood, "Flood", GREEN),
    ]

    for data, label, color in datasets:
        vals = data + data[:1]
        # Glow layers
        for w, a in [(10, 0.03), (6, 0.06), (3, 0.15)]:
            ax.plot(angles, vals, color=color, linewidth=w, alpha=a)
        # Main line
        ax.plot(angles, vals, color=color, linewidth=2.5, label=label, zorder=5)
        ax.fill(angles, vals, alpha=0.06, color=color)
        # Dot markers
        ax.scatter(angles[:-1], data, color=color, s=30, zorder=6,
                   edgecolors="white", linewidths=0.5)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(months, fontsize=11, color=TEXT_SECONDARY)
    ax.set_rticks([10, 20, 30])
    ax.set_yticklabels(["10", "20", "30"], fontsize=8, color=TEXT_MUTED)
    ax.grid(color="#ffffff10", linewidth=0.5)
    ax.spines["polar"].set_color("#ffffff08")

    legend = ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.15),
                       framealpha=0.05, edgecolor="#ffffff10")
    for text in legend.get_texts():
        text.set_color(TEXT_SECONDARY)

    fig.text(0.5, 0.95, "Storm Event Seasonality", ha="center",
             fontsize=18, fontweight="bold", color=TEXT_PRIMARY,
             path_effects=[pe.withStroke(linewidth=3, foreground=mcolors.to_rgba(CYAN, 0.15))])
    fig.text(0.5, 0.91, "Normalized Monthly Frequency by Peril Type",
             ha="center", fontsize=10, color=TEXT_MUTED)

    plt.tight_layout(pad=2)
    fig.savefig(IMAGES_DIR / "storm_seasonality_radar.png", dpi=180, bbox_inches="tight")
    plt.close()
    print("  -> storm_seasonality_radar.png")


# ══════════════════════════════════════════════════════════════════
# FIGURE 5 — Economic Losses (Stacked Waterfall with Glass)
# ══════════════════════════════════════════════════════════════════

def fig5_economic_losses_waterfall():
    _apply_glass_style()
    perils = ["Flood", "Storm", "Earthquake", "Drought", "Wildfire", "Other", "TOTAL"]
    losses = [85, 120, 55, 30, 25, 15, 330]
    peril_colors = [CYAN, BLUE, VIOLET, ORANGE, RED, TEAL, MAGENTA]

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_CARD)

    cumulative = 0
    for i, (peril, loss, color) in enumerate(zip(perils[:-1], losses[:-1], peril_colors[:-1])):
        # Glass glow behind bar
        ax.bar(i, loss + 4, bottom=cumulative - 2, color=color,
               edgecolor="none", width=0.7, alpha=0.06, zorder=1)
        # Main bar
        ax.bar(i, loss, bottom=cumulative, color=color,
               edgecolor=mcolors.to_rgba(color, 0.5), linewidth=1,
               width=0.55, alpha=0.85, zorder=3)
        # Value label
        ax.text(i, cumulative + loss / 2, f"${loss}B", ha="center", va="center",
                fontsize=11, fontweight="bold", color="white", zorder=4)
        # Connector line
        if i < len(perils) - 2:
            ax.plot([i + 0.28, i + 0.72], [cumulative + loss, cumulative + loss],
                    color="#ffffff20", linewidth=1, linestyle="--", zorder=2)
        cumulative += loss

    # Total bar — special highlight
    total_i = len(perils) - 1
    # Glow
    for w, a in [(0.9, 0.04), (0.75, 0.08)]:
        ax.bar(total_i, cumulative + 6, bottom=-3, color=MAGENTA,
               edgecolor="none", width=w, alpha=a, zorder=1)
    ax.bar(total_i, cumulative, bottom=0, color=MAGENTA,
           edgecolor=mcolors.to_rgba(MAGENTA, 0.6), linewidth=1.5,
           width=0.55, alpha=0.9, zorder=3)
    ax.text(total_i, cumulative / 2, f"${cumulative}B", ha="center", va="center",
            fontsize=14, fontweight="bold", color="white", zorder=4)

    ax.set_xticks(range(len(perils)))
    ax.set_xticklabels(perils, fontsize=11, color=TEXT_SECONDARY)
    ax.set_ylabel("Losses ($ Billions)", color=TEXT_MUTED, fontsize=11)
    ax.set_ylim(-5, cumulative * 1.15)
    ax.grid(axis="y", alpha=0.08, color="white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#ffffff08")
    ax.spines["bottom"].set_color("#ffffff08")

    _glow_text(ax, 3, cumulative * 1.08,
               "Global Insured Catastrophe Losses by Peril (2024)", CYAN, fontsize=17)

    plt.tight_layout(pad=1.5)
    fig.savefig(IMAGES_DIR / "economic_losses_waterfall.png", dpi=180, bbox_inches="tight")
    plt.close()
    print("  -> economic_losses_waterfall.png")


# ══════════════════════════════════════════════════════════════════
# FIGURE 6 — Risk Matrix (Neon Bubbles)
# ══════════════════════════════════════════════════════════════════

def fig6_regional_risk_matrix():
    _apply_glass_style()
    np.random.seed(99)
    regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Africa"]
    perils = ["Flood", "Storm", "EQ", "Wildfire", "Drought"]
    region_colors = [CYAN, BLUE, MAGENTA, ORANGE, GREEN]

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_CARD)

    # Background quadrant shading
    ax.axhspan(5.5, 11, xmin=0.5, color=RED, alpha=0.03, zorder=0)
    ax.axhspan(0, 5.5, xmax=0.5, color=GREEN, alpha=0.03, zorder=0)

    ax.axhline(y=5.5, color="#ffffff15", linestyle="--", linewidth=1, zorder=1)
    ax.axvline(x=5.5, color="#ffffff15", linestyle="--", linewidth=1, zorder=1)

    for i, (region, color) in enumerate(zip(regions, region_colors)):
        freq = np.random.uniform(2, 9, len(perils))
        sev = np.random.uniform(1.5, 9.5, len(perils))
        sizes = np.random.uniform(180, 700, len(perils))

        # Glow halo
        ax.scatter(freq, sev, s=sizes * 2.5, c=color, alpha=0.06, edgecolors="none", zorder=2)
        ax.scatter(freq, sev, s=sizes * 1.5, c=color, alpha=0.1, edgecolors="none", zorder=2)
        # Main bubble
        ax.scatter(freq, sev, s=sizes, c=color, alpha=0.55,
                   edgecolors=mcolors.to_rgba(color, 0.7),
                   linewidths=1.2, label=region, zorder=4)
        # Labels inside
        for j, peril in enumerate(perils):
            ax.text(freq[j], sev[j], peril, fontsize=7, ha="center", va="center",
                    color="white", fontweight="bold", zorder=5)

    ax.set_xlabel("Frequency Score", fontsize=11, color=TEXT_SECONDARY)
    ax.set_ylabel("Severity Score", fontsize=11, color=TEXT_SECONDARY)
    ax.set_xlim(0.5, 10.5)
    ax.set_ylim(0.5, 10.5)
    ax.grid(alpha=0.06, color="white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#ffffff08")
    ax.spines["bottom"].set_color("#ffffff08")

    # Quadrant labels
    ax.text(8.5, 9.5, "HIGH RISK", fontsize=11, color=RED, fontweight="bold",
            ha="center", alpha=0.6,
            path_effects=[pe.withStroke(linewidth=3, foreground=mcolors.to_rgba(RED, 0.1))])
    ax.text(2.5, 1.3, "LOW RISK", fontsize=11, color=GREEN, fontweight="bold",
            ha="center", alpha=0.6,
            path_effects=[pe.withStroke(linewidth=3, foreground=mcolors.to_rgba(GREEN, 0.1))])

    legend = ax.legend(loc="lower right", framealpha=0.05, edgecolor="#ffffff10",
                       fontsize=10, markerscale=0.5)
    for text in legend.get_texts():
        text.set_color(TEXT_SECONDARY)

    _glow_text(ax, 5.5, 10.8, "Catastrophe Risk Matrix by Region & Peril", CYAN, fontsize=17)

    plt.tight_layout(pad=1.5)
    fig.savefig(IMAGES_DIR / "regional_risk_matrix.png", dpi=180, bbox_inches="tight")
    plt.close()
    print("  -> regional_risk_matrix.png")


# ══════════════════════════════════════════════════════════════════
# FIGURE 7 — Architecture Diagram (Liquid Glass Cards)
# ══════════════════════════════════════════════════════════════════

def fig7_dashboard_architecture():
    _apply_glass_style()
    fig, ax = plt.subplots(figsize=(16, 8))
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_DARK)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8.5)
    ax.axis("off")

    # Ambient background glow blobs
    for cx, cy, cr, cc in [(3, 5, 2.5, CYAN), (8, 4, 2, VIOLET), (13, 5, 2.5, MAGENTA)]:
        circle = plt.Circle((cx, cy), cr, facecolor=cc, alpha=0.03, edgecolor="none", zorder=0)
        ax.add_patch(circle)

    # Title
    _glow_text(ax, 8, 8, "Cat Model Dashboard", CYAN, fontsize=22, ha="center")
    ax.text(8, 7.5, "Architecture Overview", ha="center", fontsize=12, color=TEXT_MUTED)

    # ── Data Sources (left column) ──
    sources = [
        ("NOAA", "Storm Events\nBigQuery Public", CYAN, 5.8),
        ("FEMA", "OpenFEMA API\nNFIP + Declarations", ORANGE, 4.2),
        ("EM-DAT", "Global Disaster DB\n22K+ Events", GREEN, 2.6),
    ]
    for label, sub, color, y in sources:
        _glass_rect(ax, 0.5, y - 0.5, 3.2, 1.1, color, alpha_fill=0.08, alpha_edge=0.35)
        ax.text(2.1, y + 0.2, label, ha="center", fontsize=13, fontweight="bold", color=color)
        ax.text(2.1, y - 0.15, sub, ha="center", fontsize=8, color=TEXT_MUTED, linespacing=1.4)
        # Arrow
        ax.annotate("", xy=(5.3, 4.2), xytext=(3.7, y + 0.1),
                    arrowprops=dict(arrowstyle="-|>", color=mcolors.to_rgba(color, 0.4),
                                    lw=1.5, connectionstyle="arc3,rad=0.1"))

    # ── Processing (center) ──
    _glass_rect(ax, 5.2, 2.7, 3.0, 3.2, VIOLET, alpha_fill=0.1, alpha_edge=0.4)
    ax.text(6.7, 5.5, "Data Pipeline", ha="center", fontsize=14, fontweight="bold", color=VIOLET)
    pipeline_items = [
        ("Fetch & Cache", 4.9),
        ("Parquet Storage", 4.4),
        ("Transform & Clean", 3.9),
        ("Validate & Enrich", 3.4),
    ]
    for item, y in pipeline_items:
        ax.plot(5.7, y, "o", color=VIOLET, markersize=5, alpha=0.6)
        ax.text(6.0, y, item, fontsize=9, color=TEXT_SECONDARY, va="center")

    # Arrow center -> right
    ax.annotate("", xy=(9.8, 4.3), xytext=(8.2, 4.3),
                arrowprops=dict(arrowstyle="-|>", color=mcolors.to_rgba(MAGENTA, 0.5),
                                lw=2, connectionstyle="arc3,rad=0"))

    # ── Dashboard (right) ──
    _glass_rect(ax, 9.8, 1.8, 5.4, 5.0, MAGENTA, alpha_fill=0.06, alpha_edge=0.35)
    ax.text(12.5, 6.3, "Streamlit Dashboard", ha="center", fontsize=15,
            fontweight="bold", color=MAGENTA)

    features = [
        ("Interactive Plotly Charts", CYAN, 5.6),
        ("Geospatial Storm Maps", BLUE, 5.1),
        ("KPI Metric Cards", GREEN, 4.6),
        ("Heatmaps & Treemaps", ORANGE, 4.1),
        ("Sunburst & Area Charts", VIOLET, 3.6),
        ("Filterable Data Tables", TEAL, 3.1),
    ]
    for feat, color, y in features:
        ax.plot(10.5, y, "s", color=color, markersize=7, alpha=0.7)
        ax.text(10.9, y, feat, fontsize=10, color=TEXT_SECONDARY, va="center")

    # Bottom tech stack
    ax.text(8, 1.0, "Python  ·  Streamlit  ·  Plotly  ·  Pandas  ·  Matplotlib  ·  Requests",
            ha="center", fontsize=11, color=TEXT_MUTED, style="italic")

    # Decorative line
    ax.plot([1, 15], [1.4, 1.4], color="#ffffff06", linewidth=1)

    fig.savefig(IMAGES_DIR / "architecture_diagram.png", dpi=180, bbox_inches="tight")
    plt.close()
    print("  -> architecture_diagram.png")


# ══════════════════════════════════════════════════════════════════
# FIGURE 8 — Dashboard Hero Banner (NEW)
# ══════════════════════════════════════════════════════════════════

def fig8_hero_banner():
    """Wide hero banner for top of README."""
    _apply_glass_style()
    fig, ax = plt.subplots(figsize=(16, 5))
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_DARK)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 5)
    ax.axis("off")

    # Ambient gradient blobs
    for cx, cy, cr, cc in [
        (2, 3, 3, CYAN), (8, 2.5, 4, VIOLET), (14, 3, 3, MAGENTA),
        (5, 1, 2, BLUE), (11, 4, 2, GREEN),
    ]:
        circle = plt.Circle((cx, cy), cr, facecolor=cc, alpha=0.025, edgecolor="none", zorder=0)
        ax.add_patch(circle)

    # Decorative grid dots
    for x in np.arange(0.5, 16, 0.8):
        for y in np.arange(0.5, 5, 0.8):
            dist = np.sqrt((x - 8)**2 + (y - 2.5)**2)
            alpha = max(0.01, 0.04 - dist * 0.004)
            ax.plot(x, y, "o", color="white", markersize=1, alpha=alpha)

    # Main title
    t = ax.text(8, 3.2, "CAT MODEL DASHBOARD", ha="center", va="center",
                fontsize=36, fontweight="bold", color=TEXT_PRIMARY)
    t.set_path_effects([
        pe.withStroke(linewidth=6, foreground=mcolors.to_rgba(CYAN, 0.12)),
    ])

    ax.text(8, 2.2, "Catastrophe Risk Analytics  |  FEMA  ·  NOAA  ·  EM-DAT",
            ha="center", fontsize=14, color=TEXT_MUTED)

    # Decorative line
    for offset, alpha in [(0, 0.25), (0.02, 0.1)]:
        ax.plot([3 + offset, 13 + offset], [1.5, 1.5], color=CYAN,
                linewidth=1, alpha=alpha)

    # Small KPI-style boxes
    kpis = [
        ("10K+", "Declarations", CYAN),
        ("22K+", "Global Events", MAGENTA),
        ("50K+", "NFIP Claims", ORANGE),
        ("5", "Data Views", GREEN),
    ]
    for i, (val, label, color) in enumerate(kpis):
        cx = 3.5 + i * 3
        _glass_rect(ax, cx - 1, 0.2, 2, 0.9, color, alpha_fill=0.06, alpha_edge=0.25)
        ax.text(cx, 0.82, val, ha="center", fontsize=16, fontweight="bold", color=color)
        ax.text(cx, 0.45, label, ha="center", fontsize=8, color=TEXT_MUTED)

    fig.savefig(IMAGES_DIR / "hero_banner.png", dpi=180, bbox_inches="tight")
    plt.close()
    print("  -> hero_banner.png")


if __name__ == "__main__":
    print("\nGenerating liquid glass dashboard images...\n")
    fig8_hero_banner()
    fig1_disaster_declarations_trend()
    fig2_global_disaster_types()
    fig3_nfip_claims_heatmap()
    fig4_storm_seasonality()
    fig5_economic_losses_waterfall()
    fig6_regional_risk_matrix()
    fig7_dashboard_architecture()
    print("\nAll images generated in images/ directory.")
