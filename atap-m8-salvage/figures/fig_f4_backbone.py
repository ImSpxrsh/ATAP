#!/usr/bin/env python3
"""F4 — backbone association. Forest plot of standardized effects (per drug x metric)
with 95% CIs, plus supporting scatter of executioner-loss score vs venetoclax LN_IC50.
Must-not-claim: correlation != ATAP efficacy; this shows the resistance mechanism is
real and detectable."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "figures"))
import style  # noqa: E402
style.apply()

TAB = ROOT / "outputs" / "tables"
PROC = ROOT / "data" / "processed"
res = pd.read_csv(TAB / "M2_backbone_effects.csv")
dep = pd.read_csv(PROC / "depmap_celllines.csv", index_col=0)

fig, (axf, axs) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})

# forest
res = res.dropna(subset=["beta"]).reset_index(drop=True)
labels = [f"{r.drug}\n{r.metric}" for r in res.itertuples()]
y = np.arange(len(res))[::-1]
axf.errorbar(res["beta"], y,
             xerr=[res["beta"] - res["ci_low"], res["ci_high"] - res["beta"]],
             fmt="o", color=style.ACCENT, ecolor=style.GRAY, capsize=3, lw=1.5, ms=7)
axf.axvline(0, color=style.RED, ls="--", lw=1)
axf.set_yticks(y); axf.set_yticklabels(labels)
axf.set_xlabel("standardized β  (executioner loss → resistance ▶)")
axf.set_title("(a) backbone effect sizes (lineage-adjusted)")
for r, yy in zip(res.itertuples(), y):
    axf.text(r.ci_high + 0.01, yy, f"p={r.p:.2f}, n={int(r.n)}", va="center",
             fontsize=8, color=style.GRAY)
axf.set_xlim(-0.35, 0.55)

# scatter: score vs venetoclax LN_IC50
s = dep[["executioner_loss_score", "venetoclax_LN_IC50", "executioner_loss_call"]].dropna()
colors = np.where(s["executioner_loss_call"], style.RED, style.LIGHTGRAY)
axs.scatter(s["executioner_loss_score"], s["venetoclax_LN_IC50"], c=colors, s=28,
            edgecolor="white", lw=0.4)
# trend
z = np.polyfit(s["executioner_loss_score"], s["venetoclax_LN_IC50"], 1)
xx = np.linspace(s["executioner_loss_score"].min(), s["executioner_loss_score"].max(), 50)
axs.plot(xx, np.polyval(z, xx), color=style.ACCENT, lw=1.8)
axs.set_xlabel("executioner-loss score"); axs.set_ylabel("venetoclax LN_IC50 (↑ = resistant)")
axs.set_title("(b) score vs venetoclax resistance")
style.annotate_n(axs, len(s), "lower right")
axs.scatter([], [], c=style.RED, label="executioner-loss call"); axs.legend(loc="upper left", fontsize=8)

fig.suptitle("F4 — executioner loss vs BH3-mimetic resistance (DepMap heme + GDSC2). "
             "Correlation, not ATAP efficacy.", fontsize=9.5, y=1.03)
style.save(fig, "F4_backbone_association")
