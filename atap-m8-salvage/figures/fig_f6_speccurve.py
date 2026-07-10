#!/usr/bin/env python3
"""F6 — specification curve (signature figure). Top: sorted effect estimates with 95% CIs
across all 360 specs. Bottom: specification descriptor matrix. Inset: stability summary.
This figure exists to bound overclaiming."""
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
res = pd.read_csv(TAB / "M4_specification_curve.csv").reset_index(drop=True)
stab = pd.read_csv(TAB / "M4_stability.csv").iloc[0]

fig = plt.figure(figsize=(12, 7))
gs = fig.add_gridspec(2, 1, height_ratios=[2.2, 1.6], hspace=0.08)
axc = fig.add_subplot(gs[0]); axm = fig.add_subplot(gs[1], sharex=axc)

x = np.arange(len(res))
sig = res["p"] < 0.05
axc.fill_between(x, res["ci_low"], res["ci_high"], color=style.LIGHTGRAY, alpha=0.5, lw=0)
axc.scatter(x, res["beta"], c=np.where(sig, style.ACCENT, style.GRAY), s=10)
axc.axhline(0, color=style.RED, ls="--", lw=1)
axc.axhline(stab["median_beta"], color=style.AMBER, lw=1.2, ls=":")
axc.set_ylabel("standardized β")
axc.set_title("F6 — specification curve: executioner loss → BH3-mimetic resistance "
              f"({len(res)} specs)")
axc.text(0.01, 0.97,
         f"median β = {stab['median_beta']:.3f} | positive-direction {stab['positive_share']:.0%}\n"
         f"significant (p<.05) {stab['sig_share_uncorrected']:.0%} | "
         f"FDR<.05 {stab['sig_share_fdr']:.0%} | S³ = {stab['S3_stability']:.2f}",
         transform=axc.transAxes, va="top", fontsize=9,
         bbox=dict(boxstyle="round", fc="white", ec=style.LIGHTGRAY))
axc.tick_params(labelbottom=False)

# descriptor matrix
factors = {"lof": res["lof"], "expr_q": res["expr_q"].astype(str),
           "drug": res["drug"], "metric": res["metric"],
           "lineage_subset": res["lineage_subset"], "covset": res["covset"]}
rowlabels, ys, xs = [], [], []
yi = 0
for fac, series in factors.items():
    for lvl in sorted(series.unique()):
        rowlabels.append(f"{fac}: {lvl}")
        mask = (series == lvl).values
        xs.extend(x[mask]); ys.extend([yi] * mask.sum())
        yi += 1
axm.scatter(xs, ys, marker="|", s=14, color=style.GRAY, lw=0.5)
axm.set_yticks(range(len(rowlabels))); axm.set_yticklabels(rowlabels, fontsize=6.5)
axm.set_xlabel("specification (sorted by effect size)")
axm.invert_yaxis()

style.save(fig, "F6_specification_curve")
