#!/usr/bin/env python3
"""F3 — prevalence landscape. How common is executioner loss, and what does guardian
dependence look like, across heme lineages/cohorts. Must-not-claim: prevalence is the
addressable-population upper bound, NOT ATAP benefit."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "figures"))
import style  # noqa: E402
style.apply()

PROC = ROOT / "data" / "processed"
dep = pd.read_csv(PROC / "depmap_celllines.csv", index_col=0)
bea = pd.read_csv(PROC / "beataml_patients.csv", index_col=0)
laml = pd.read_csv(PROC / "tcga_LAML.csv", index_col=0)
dlbc = pd.read_csv(PROC / "tcga_DLBC.csv", index_col=0)

# executioner-loss prevalence per cohort
groups = {
    "DepMap\nmyeloid": dep[dep["OncotreeLineage"] == "Myeloid"],
    "DepMap\nlymphoid": dep[dep["OncotreeLineage"] == "Lymphoid"],
    "TCGA-LAML": laml,
    "TCGA-DLBC": dlbc,
    "BeatAML": bea,
}
prev = {k: (v["executioner_loss_call"].mean() * 100, len(v)) for k, v in groups.items()}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw={"width_ratios": [1, 1.1]})

ax1.bar(range(len(prev)), [p[0] for p in prev.values()], color=style.RED)
ax1.set_xticks(range(len(prev))); ax1.set_xticklabels(list(prev), fontsize=8.5)
ax1.set_ylabel("executioner-loss prevalence (%)")
ax1.set_title("(a) executioner loss across heme cohorts")
for i, (k, (pct, n)) in enumerate(prev.items()):
    ax1.text(i, pct + 0.1, f"{pct:.1f}%\nn={n}", ha="center", fontsize=8, color=style.GRAY)

# guardian dependence heatmap: median z-scored guardian expression per cohort
guardians = ["BCL2", "MCL1", "BCL2L1", "BCL2A1"]
rows = []
for k, v in groups.items():
    r = []
    for g in guardians:
        col = f"expr_{g}"
        if col in v.columns:
            allv = pd.concat([groups[c][col] for c in groups if col in groups[c].columns])
            z = (v[col].median() - allv.mean()) / allv.std()
            r.append(z)
        else:
            r.append(np.nan)
    rows.append(r)
H = np.array(rows)
im = ax2.imshow(H, cmap="PuOr_r", vmin=-1.5, vmax=1.5, aspect="auto")
ax2.set_xticks(range(len(guardians))); ax2.set_xticklabels(guardians)
ax2.set_yticks(range(len(groups))); ax2.set_yticklabels([k.replace("\n", " ") for k in groups])
ax2.set_title("(b) guardian dependence (median expr, z across cohorts)")
for i in range(H.shape[0]):
    for j in range(H.shape[1]):
        if not np.isnan(H[i, j]):
            ax2.text(j, i, f"{H[i,j]:.1f}", ha="center", va="center", fontsize=8,
                     color="black")
fig.colorbar(im, ax=ax2, fraction=0.046, label="z (rel. to cohort mean)")

fig.suptitle("F3 — prevalence landscape. Addressable-population upper bound, not ATAP benefit.",
             fontsize=9.5, y=1.02)
style.save(fig, "F3_prevalence_landscape")
print("prevalence:", {k: f"{p:.1f}% (n={n})" for k, (p, n) in prev.items()})
