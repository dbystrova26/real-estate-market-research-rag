"""
Builds a chart from an arbitrary set of {label, value, unit, derived, note} data
points — used by the autonomous pipeline, where topics aren't known in advance.
Uses fig.text() + explicit margins instead of tight_layout() — see
charts/build_charts.py for why.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
})


def build_dynamic_chart(chart_data: dict, out_path: str) -> str:
    import textwrap

    points = chart_data["data_points"]
    labels = [p["label"] + ("*" if p.get("derived") else "") for p in points]
    values = [p["value"] for p in points]
    colors = [ACCENT if p.get("derived") else BARCOLOR for p in points]
    unit = points[0].get("unit", "")

    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    bars = ax.bar(labels, values, color=colors, width=0.5)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + max(values) * 0.02,
                 f"{val:g}{unit}", ha="center", fontsize=9, fontweight="bold")
    ax.set_ylim(0, max(values) * 1.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(chart_data["chart_title"], fontsize=11, fontweight="bold", loc="left", pad=10)

    notes = "; ".join(p["note"] for p in points if p.get("note"))
    caption = notes[:220] + ("…" if len(notes) > 220 else "")
    if any(p.get("derived") for p in points):
        caption += "  (* derived from a cited figure)"
    wrapped = textwrap.fill(caption, width=95)
    n_lines = wrapped.count("\n") + 1
    bottom_margin = 0.14 + 0.045 * n_lines

    fig.subplots_adjust(left=0.13, right=0.95, top=0.86, bottom=bottom_margin)
    fig.text(0.02, 0.02, wrapped, fontsize=6.5, color=MUTED, ha="left", va="bottom")

    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out_path
