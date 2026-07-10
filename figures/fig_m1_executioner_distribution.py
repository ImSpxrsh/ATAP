#!/usr/bin/env python3
"""M1 acceptance figure: distribution of the executioner-loss score and its components
across the DepMap heme cohort and BeatAML patients. Purely a function of BAX/BAK1 state
(no drug/ATAP data) — this figure exists to show the score is well-defined and its
prevalence, before any association is tested."""
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "figures"))
import style  # noqa: E402

PROC = ROOT / "data" / "processed"
style.apply()

dep = pd.read_csv(PROC / "depmap_celllines.csv", index_col=0)
bea = pd.read_csv(PROC / "beataml_patients.csv", index_col=0)

fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))

# (a) DepMap executioner-loss score distribution
ax = axes[0]
s = dep["executioner_loss_score"].dropna()
ax.hist(s, bins=[-0.01, 0.15, 0.35, 0.55, 0.75, 1.01], color=style.ACCENT, edgecolor="white")
ax.set_xlabel("executioner-loss score"); ax.set_ylabel("cell lines")
ax.set_title("(a) DepMap heme cell lines")
style.annotate_n(ax, len(s))

# (b) component prevalence (DepMap)
ax = axes[1]
comps = {"expr (both low)": dep["expr_low"].sum() if "expr_low" in dep else 0,
         "CN deep-del": dep["cn_del"].sum() if "cn_del" in dep else 0,
         "LOF mutation": dep["mut_lof"].sum() if "mut_lof" in dep else 0,
         "any (binary call)": dep["executioner_loss_call"].sum()}
ax.bar(range(len(comps)), list(comps.values()),
       color=[style.GRAY, style.GRAY, style.GRAY, style.RED])
ax.set_xticks(range(len(comps))); ax.set_xticklabels(list(comps), rotation=25, ha="right")
ax.set_ylabel("cell lines"); ax.set_title("(b) executioner-loss components")
style.annotate_n(ax, len(dep))

# (c) BeatAML score distribution
ax = axes[2]
sb = bea["executioner_loss_score"].dropna()
ax.hist(sb, bins=[-0.01, 0.15, 0.35, 0.55, 0.75, 1.01], color=style.AMBER, edgecolor="white")
ax.set_xlabel("executioner-loss score"); ax.set_ylabel("patients")
ax.set_title("(c) Beat AML patients")
style.annotate_n(ax, len(sb))

fig.suptitle("M1 — executioner-loss score: defined from BAX/BAK1 state only "
             "(expression bottom-decile-both, deep deletion, or LOF mutation)",
             fontsize=10, y=1.04)
style.save(fig, "F_M1_executioner_distribution")
