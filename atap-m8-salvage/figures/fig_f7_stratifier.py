#!/usr/bin/env python3
"""F7 — susceptibility stratifier. Violin of susceptibility score by heme subtype/cohort +
calibration against observed venetoclax resistance. Must-not-claim: score = mechanistic
rationale, not predicted kill rate."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "figures"))
import style  # noqa: E402
style.apply()

TAB = ROOT / "outputs" / "tables"
PROC = ROOT / "data" / "processed"

# collect susceptibility distributions by cohort
dep = pd.read_csv(TAB / "M5_susceptibility_depmap.csv", index_col=0)
depL = pd.read_csv(PROC / "depmap_celllines.csv", index_col=0)["OncotreeLineage"]
dep = dep.join(depL)
bea = pd.read_csv(TAB / "M5_susceptibility_beataml.csv", index_col=0)
laml = pd.read_csv(TAB / "M5_susceptibility_tcga_LAML.csv", index_col=0)
dlbc = pd.read_csv(TAB / "M5_susceptibility_tcga_DLBC.csv", index_col=0)

dists = {
    "DepMap myeloid": dep[dep["OncotreeLineage"] == "Myeloid"]["susceptibility_score"].dropna(),
    "DepMap lymphoid": dep[dep["OncotreeLineage"] == "Lymphoid"]["susceptibility_score"].dropna(),
    "TCGA-LAML": laml["susceptibility_score"].dropna(),
    "TCGA-DLBC": dlbc["susceptibility_score"].dropna(),
    "BeatAML": bea["susceptibility_score"].dropna(),
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.3, 1]})

parts = ax1.violinplot(list(dists.values()), showmedians=True)
for pc in parts["bodies"]:
    pc.set_facecolor(style.ACCENT); pc.set_alpha(0.6)
for key in ("cbars", "cmins", "cmaxes", "cmedians"):
    parts[key].set_color(style.GRAY)
ax1.set_xticks(range(1, len(dists) + 1)); ax1.set_xticklabels(list(dists), rotation=20, ha="right")
ax1.set_ylabel("predicted susceptibility score"); ax1.set_title("(a) susceptibility by cohort/subtype")
for i, (k, v) in enumerate(dists.items(), 1):
    ax1.text(i, 1.02, f"n={len(v)}", ha="center", fontsize=7.5, color=style.GRAY)

# (b) calibration: susceptibility quintile vs observed venetoclax AUC (BeatAML)
beav = bea.join(pd.read_csv(PROC / "beataml_patients.csv", index_col=0)["venetoclax_AUC"])
beav = beav.dropna(subset=["venetoclax_AUC", "susceptibility_score"])
beav["q"] = pd.qcut(beav["susceptibility_score"], 5, labels=False, duplicates="drop")
grp = beav.groupby("q")["venetoclax_AUC"].agg(["mean", "sem", "count"])
ax2.errorbar(grp.index + 1, grp["mean"], yerr=grp["sem"], fmt="o-", color=style.ACCENT,
             ecolor=style.GRAY, capsize=3)
rho, p = stats.spearmanr(beav["susceptibility_score"], beav["venetoclax_AUC"])
ax2.set_xlabel("susceptibility quintile (1=low, 5=high)")
ax2.set_ylabel("mean ex vivo venetoclax AUC (↑ resistant)")
ax2.set_title(f"(b) calibration in Beat AML (ρ={rho:.2f}, p={p:.1e})")
style.annotate_n(ax2, int(grp["count"].sum()), "lower right")

fig.suptitle("F7 — susceptibility stratifier: mechanistic rationale (predicted), not a kill rate.",
             fontsize=9.5, y=1.02)
style.save(fig, "F7_susceptibility_stratifier")
