"""House figure style: single accent + gray, colorblind-safe, sample sizes on panels.
Every figure script imports this and calls apply() once."""
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIGDIR = ROOT / "outputs" / "figures"
FIGDIR.mkdir(parents=True, exist_ok=True)

# colorblind-safe: accent (teal for ATAP/bypass), amber (BH3-mimetic/conditional), grays
ACCENT = "#0B7A75"      # teal
AMBER = "#D9A404"       # amber
GRAY = "#5A5A5A"
LIGHTGRAY = "#BDBDBD"
RED = "#B23A48"         # "lost" executioner
PALETTE = [ACCENT, AMBER, GRAY, RED, "#7B6FB0"]


def apply():
    mpl.rcParams.update({
        "figure.dpi": 120,
        "savefig.dpi": 200,
        "font.size": 10,
        "font.family": "sans-serif",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#E6E6E6",
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "legend.frameon": False,
    })


def annotate_n(ax, n, loc="upper right"):
    xy = {"upper right": (0.98, 0.98), "upper left": (0.02, 0.98),
          "lower right": (0.98, 0.02), "lower left": (0.02, 0.02)}[loc]
    ha = "right" if "right" in loc else "left"
    va = "top" if "upper" in loc else "bottom"
    ax.text(*xy, f"n = {n}", transform=ax.transAxes, ha=ha, va=va,
            fontsize=9, color=GRAY)


def save(fig, name):
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGDIR / f"{name}.{ext}", bbox_inches="tight")
    print(f"  saved {name}.png / .pdf")
