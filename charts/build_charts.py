"""
Generates the charts used in the report. Every number plotted is either directly
copied from a cited fact, or a simple, clearly-labeled arithmetic derivation from one
— never invented.

Uses fig.text() + explicit subplots_adjust() margins instead of tight_layout() +
ax.text(transform=ax.transAxes) — the latter combination has a bug where a long
caption confuses tight_layout's width calculation and compresses the axes, causing
category labels to overlap.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_DIR = Path(__file__).resolve().parent
INK = "#1a2332"
ACCENT = "#8c1d2b"
MUTED = "#5b6472"
BARCOLOR = "#3d5a73"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "Inter", "DejaVu Sans"],
    "axes.edgecolor": "#d8dce1",
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.titlecolor": INK,
})


def _finalize(fig, ax, title, source_note):
    import textwrap
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left", pad=10)
    ax.spines[["top", "right"]].set_visible(False)

    wrapped = textwrap.fill(source_note, width=95)
    n_lines = wrapped.count("\n") + 1
    bottom_margin = 0.14 + 0.045 * n_lines

    fig.subplots_adjust(left=0.13, right=0.95, top=0.86, bottom=bottom_margin)
    fig.text(0.02, 0.02, wrapped, fontsize=7, color=MUTED, ha="left", va="bottom")


def chart_policy_rates() -> str:
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    banks = ["ECB\n(deposit facility)", "Federal Reserve\n(range midpoint)", "Bank of England\n(Bank Rate)"]
    rates = [2.25, 3.625, 3.75]
    bars = ax.bar(banks, rates, color=[ACCENT, BARCOLOR, BARCOLOR], width=0.5)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, rate + 0.08, f"{rate}%",
                 ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 4.5)
    ax.set_ylabel("Policy rate (%)")
    _finalize(fig, ax, "Current Policy Rates — August 2026",
              "Source: ECB (2026-06-11), Federal Reserve (2026-07-29), Bank of England (2026-07-29). Fed shown at range midpoint (3.50-3.75%).")
    path = OUT_DIR / "policy_rates.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def chart_h1_investment_by_sector() -> str:
    fig, ax = plt.subplots(figsize=(6, 3.4))
    sectors = ["Living*", "Office", "Industrial &\nLogistics", "Retail", "Hotels"]
    values = [30.2, 22.6, 19.2, 18.1, 11.8]
    colors = [ACCENT if s == "Living*" else BARCOLOR for s in sectors]
    bars = ax.barh(sectors, values, color=colors)
    for bar, val in zip(bars, values):
        ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2, f"€{val}bn",
                 va="center", fontsize=9, fontweight="bold")
    ax.set_xlabel("EUR billion")
    ax.invert_yaxis()
    _finalize(fig, ax, "European Real Estate Investment by Sector, H1 2026",
              "Source: CBRE, European Real Estate Investment Figures H1 2026 (2026-07-30). "
              "*Living derived as 26% of the cited EUR 116bn H1 total.")
    path = OUT_DIR / "h1_investment_by_sector.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def chart_datacenter_vacancy() -> str:
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    periods = ["Late 2024", "End 2026 (forecast)"]
    values = [9.9, 6.5]
    bars = ax.bar(periods, values, color=[BARCOLOR, ACCENT], width=0.4)
    for bar, val, label in zip(bars, values, ["<10%", "6.5%"]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.2, label,
                 ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 12)
    ax.set_ylabel("Vacancy rate (%)")
    _finalize(fig, ax, "European Data Center Vacancy",
              "Source: CBRE, European Data Centres Outlook 2026 (2026-01-01). Late-2024 bar "
              "shows the cited upper bound ('below 10%'), not an exact reported figure.")
    path = OUT_DIR / "datacenter_vacancy.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def chart_lifesciences_vc() -> str:
    fig, ax = plt.subplots(figsize=(5, 3.2))
    years = ["2024*", "2025"]
    values = [12.84, 13.2]
    bars = ax.bar(years, values, color=[BARCOLOR, ACCENT], width=0.4)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.1, f"€{val}bn",
                 ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 15)
    ax.set_ylabel("VC funding (EUR billion)")
    _finalize(fig, ax, "European Life Sciences VC Funding",
              "Source: CBRE, European Life Sciences Ecosystems Sector Guide 2026 (2026-02-24). "
              "*2024 derived from the cited 2.8% YoY increase to 2025.")
    path = OUT_DIR / "lifesciences_vc.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def chart_defense_spending_target() -> str:
    fig, ax = plt.subplots(figsize=(5, 3.2))
    labels = ["Prior NATO target", "New target (by 2035)"]
    values = [2.0, 3.5]
    bars = ax.bar(labels, values, color=[BARCOLOR, ACCENT], width=0.4)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.08, f"{val}%",
                 ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 4.2)
    ax.set_ylabel("Core defense spending (% of GDP)")
    _finalize(fig, ax, "NATO Core Defense Spending Target",
              "Source: Janus Henderson Investors, citing NATO Summit commitments (2026-02-04). "
              "An additional 1.5% of GDP is earmarked for broader security investment, not shown.")
    path = OUT_DIR / "defense_spending_target.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def chart_affordable_housing_gap() -> str:
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    labels = ["Current annual\nbuild rate", "Additional units\nneeded per year"]
    values = [1.6, 0.65]
    bars = ax.bar(labels, values, color=[BARCOLOR, ACCENT], width=0.4)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.04, f"{val}M",
                 ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 2.1)
    ax.set_ylabel("Dwellings per year (millions)")
    _finalize(fig, ax, "EU Housing Supply Gap",
              "Source: European Commission, Affordable Housing Plan SWD 2025-1053-2 (2025-12-16).")
    path = OUT_DIR / "affordable_housing_gap.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def build_all_charts() -> dict[str, str]:
    return {
        "policy_rates": chart_policy_rates(),
        "h1_investment_by_sector": chart_h1_investment_by_sector(),
        "datacenter_vacancy": chart_datacenter_vacancy(),
        "lifesciences_vc": chart_lifesciences_vc(),
        "defense_spending_target": chart_defense_spending_target(),
        "affordable_housing_gap": chart_affordable_housing_gap(),
    }


if __name__ == "__main__":
    paths = build_all_charts()
    for name, path in paths.items():
        print(f"{name}: {path}")
