#!/usr/bin/env python3
"""F5 — confounder decomposition. Nested-model R²/ΔR² bars + partial effects (full model).
Must-not-claim: don't hide a small increment — report it. Here the increment is ~0."""
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
tbl = pd.read_csv(TAB / "M3_nested_models.csv")
partial = pd.read_csv(TAB / "M3_executioner_partial.csv").iloc[0]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

# nested R²
ax1.bar(tbl["model"], tbl["r2"], color=[style.LIGHTGRAY, style.GRAY, style.ACCENT])
ax1.set_ylabel("R²"); ax1.set_title("(a) nested models — venetoclax LN_IC50")
ax1.set_xticklabels(tbl["model"], rotation=20, ha="right")
for i, r in tbl.iterrows():
    if not np.isnan(r.get("dR2", np.nan)):
        ax1.text(i, r["r2"] + 0.01, f"ΔR²={r['dR2']:.4f}", ha="center", fontsize=8, color=style.GRAY)
style.annotate_n(ax1, int(tbl["n"].iloc[0]), "upper left")

# partial effect of executioner loss with CI, vs the confounders (from report text values)
labels = ["executioner\nloss"]
betas = [partial["beta"]]; los = [partial["ci_low"]]; his = [partial["ci_high"]]
ax2.errorbar(betas, [0], xerr=[[betas[0]-los[0]], [his[0]-betas[0]]], fmt="o",
             color=style.ACCENT, ecolor=style.GRAY, capsize=4, ms=8)
ax2.axvline(0, color=style.RED, ls="--", lw=1)
ax2.set_yticks([0]); ax2.set_yticklabels(labels)
ax2.set_xlabel("partial standardized β (full model, confounders present)")
ax2.set_title("(b) executioner loss adds ~0 beyond confounders")
ax2.text(0.5, 0.2, f"β = {partial['beta']:.3f}\n[{partial['ci_low']:.3f}, {partial['ci_high']:.3f}]"
         f"\np = {partial['p']:.2g}", transform=ax2.transAxes, fontsize=9, color=style.GRAY)
ax2.set_xlim(-0.4, 0.4)

fig.suptitle("F5 — confounder decomposition: MCL1 + BCL2/BCL-xL ratio dominate; "
             "executioner loss adds negligible incremental signal (reported, not hidden).",
             fontsize=9.5, y=1.03)
style.save(fig, "F5_confounder_decomposition")
