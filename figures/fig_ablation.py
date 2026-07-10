#!/usr/bin/env python3
"""Ablation figure — Spearman ρ of each susceptibility component vs observed venetoclax
resistance. Shows the guardian-dependence term carries all the signal; the
executioner-deficiency term (the ATAP-mechanism half) is orthogonal to measured venetoclax
resistance. Bounds the M5 claim honestly."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "figures"))
import style  # noqa: E402
style.apply()

res = pd.read_csv(ROOT / "outputs" / "tables" / "ABLATION_susceptibility.csv")
comps = ["guardian_only", "executioner_only", "combined"]
labels = ["guardian\ndependence", "executioner\ndeficiency", "combined\nscore"]
colors = [style.AMBER, style.RED, style.ACCENT]

fig, ax = plt.subplots(figsize=(8, 4.6))
w = 0.36
x = np.arange(len(comps))
for i, (_, r) in enumerate(res.iterrows()):
    vals = [r[f"{c}_rho"] for c in comps]
    ps = [r[f"{c}_p"] for c in comps]
    bars = ax.bar(x + (i - 0.5) * w, vals, w, color=colors,
                  alpha=1 - 0.35 * i, edgecolor="white",
                  label=r["cohort"].split(" (")[0] + f" (n={int(r['n'])})")
    for xi, v, p in zip(x + (i - 0.5) * w, vals, ps):
        ax.text(xi, v + 0.01, "***" if p < 1e-3 else ("*" if p < 0.05 else "ns"),
                ha="center", fontsize=8, color=style.GRAY)
ax.axhline(0, color=style.GRAY, lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel("Spearman ρ vs observed venetoclax resistance")
ax.set_title("Ablation — guardian dependence carries the signal; executioner deficiency\n"
             "(the ATAP-mechanism half) is orthogonal to measured venetoclax resistance",
             fontsize=10)
ax.legend(fontsize=8, loc="upper right")
style.save(fig, "F_ablation_susceptibility")
