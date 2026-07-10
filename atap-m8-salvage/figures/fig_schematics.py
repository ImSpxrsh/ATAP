#!/usr/bin/env python3
"""F1 mechanism schematic, F2 study design, F13 wet-lab validation gate.
Flat house style, 2 colors + gray, sentence case, no chartjunk. Established biology (F1);
no efficacy claims anywhere."""
import sys
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "figures"))
import style  # noqa: E402
style.apply()


def box(ax, xy, w, h, text, fc, ec=None, fontsize=9, dashed=False, alpha=1.0):
    p = FancyBboxPatch((xy[0] - w/2, xy[1] - h/2), w, h,
                       boxstyle="round,pad=0.02,rounding_size=0.08",
                       fc=fc, ec=ec or style.GRAY, lw=1.3, alpha=alpha,
                       ls="--" if dashed else "-")
    ax.add_patch(p)
    ax.text(xy[0], xy[1], text, ha="center", va="center", fontsize=fontsize, wrap=True)


def arrow(ax, a, b, dashed=False, color=None):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=14,
                 lw=1.6, color=color or style.GRAY, ls="--" if dashed else "-",
                 shrinkA=2, shrinkB=2))


# ---------------- F1 mechanism ----------------
fig, ax = plt.subplots(figsize=(9, 6))
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
AMB = "#F2E2B6"; TEAL = "#BFE3E0"; GRY = "#E4E4E4"; REDF = "#F1C9CE"
ax.text(2.6, 9.6, "BH3-mimetic (venetoclax / MCL-1i)", ha="center", fontsize=10, color=style.AMBER, weight="bold")
box(ax, (2.6, 8.4), 3.4, 0.9, "inhibit BCL-2 / MCL-1 guardians", AMB)
box(ax, (2.6, 6.7), 3.4, 0.9, "free BAX / BAK executioners\n(LOST in resistance)", REDF, ec=style.RED)
box(ax, (2.6, 5.0), 3.4, 0.8, "MOMP / cytochrome c", GRY)
arrow(ax, (2.6, 7.95), (2.6, 7.15))
arrow(ax, (2.6, 6.25), (2.6, 5.4), dashed=True, color=style.RED)  # broken step
ax.text(4.7, 5.85, "breaks when\nexecutioners lost", fontsize=8, color=style.RED)

ax.text(7.4, 9.6, "ATAP-M8 (Bfl-1 tail anchor)", ha="center", fontsize=10, color=style.ACCENT, weight="bold")
box(ax, (7.4, 8.4), 3.4, 0.9, "insert into outer membrane", TEAL)
box(ax, (7.4, 6.7), 3.4, 0.9, "form pore directly\n(no BAX / BAK)", TEAL, ec=style.ACCENT)
arrow(ax, (7.4, 7.95), (7.4, 7.15))
arrow(ax, (7.4, 6.25), (5.1, 5.2), color=style.ACCENT)
arrow(ax, (2.6, 4.6), (4.7, 3.4))
box(ax, (5.0, 3.0), 3.6, 0.9, "MOMP → apoptosis", GRY, fontsize=10)
arrow(ax, (7.4, 6.25), (5.6, 3.5), color=style.ACCENT)
ax.text(5.0, 1.6, "When executioners are lost the whole BH3-mimetic class fails at the\n"
        "executioner step; ATAP-M8 bypasses them (established biology; no efficacy claimed).",
        ha="center", fontsize=8.5, color=style.GRAY)
ax.set_title("F1 — class-wide vulnerability and the BAX/BAK-independent bypass", weight="bold")
style.save(fig, "F1_mechanism_schematic")

# ---------------- F2 study design ----------------
fig, ax = plt.subplots(figsize=(11, 4.4))
ax.set_xlim(0, 12); ax.set_ylim(0, 6); ax.axis("off")
box(ax, (2, 4), 3.2, 1.6,
    "1 · PREDICT\ncell lines + patients →\nexecutioner-loss &\nsusceptibility score", TEAL)
box(ax, (6, 4), 3.2, 1.6,
    "2 · MAP\nspatial transcriptomics →\nper-spot routing map", TEAL)
box(ax, (10, 4), 3.2, 1.6,
    "3 · VALIDATE (if lab access)\none prediction → one\nresistant blood-cancer line", GRY, dashed=True, alpha=0.7)
arrow(ax, (3.6, 4), (4.4, 4)); arrow(ax, (7.6, 4), (8.4, 4))
ax.text(2, 2.4, "DepMap · GDSC · BeatAML · TCGA", ha="center", fontsize=8, color=style.GRAY)
ax.text(6, 2.4, "10x Human Lymph Node Visium", ha="center", fontsize=8, color=style.GRAY)
ax.text(10, 2.4, "grayed until access lands", ha="center", fontsize=8, color=style.GRAY)
ax.set_title("F2 — predict-and-map study design (two computational layers + optional wet-lab gate)",
             weight="bold")
style.save(fig, "F2_study_design")

# ---------------- F13 wet-lab gate ----------------
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.set_xlim(0, 11); ax.set_ylim(0, 5); ax.axis("off")
box(ax, (2, 3.2), 3.2, 1.5, "map-derived prediction:\nhigh susceptibility +\nexecutioner loss line", TEAL, dashed=True)
box(ax, (5.5, 3.2), 3.0, 1.5, "BAX/BAK-deficient,\nvenetoclax-resistant\nblood-cancer line", GRY, dashed=True)
box(ax, (9, 3.2), 3.0, 1.5, "test ONE prediction:\nATAP vs venetoclax\nviability readout", GRY, dashed=True)
arrow(ax, (3.6, 3.2), (4.0, 3.2)); arrow(ax, (7.0, 3.2), (7.5, 3.2))
ax.text(5.5, 1.2, "Pre-registered single-prediction validation (grayed until access). Validates one "
        "map-derived\nprediction, not a fishing trip. No efficacy is claimed by this project.",
        ha="center", fontsize=8.5, color=style.GRAY)
ax.set_title("F13 — pre-registered wet-lab validation design (optional gate)", weight="bold")
style.save(fig, "F13_validation_gate")
