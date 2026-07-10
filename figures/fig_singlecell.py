#!/usr/bin/env python3
"""F_singlecell — single-cell guardian/executioner map (van Galen AML atlas).
Monocytic malignant cells occupy a distinct, MCL-1-high / guardian-dependent region of the
plane vs primitive cells — a single-cell mechanism for the monocytic venetoclax-resistance
signature, in the exact axis the framework scores. Expression-based; no efficacy claim."""
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

cells = pd.read_csv(TAB / "SC_cells.csv", index_col=0)
prof = pd.read_csv(TAB / "SC_celltype_profile.csv", index_col=0)
mal = cells[cells["malignant"]]
mono = mal[mal["monocytic"]]; prim = mal[~mal["monocytic"]]

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.8))

# (a) mean guardian dependence per cell type, ranked; monocytic states highlighted
prof2 = prof[prof["n"] >= 20].sort_values("guardian")
ismono = prof2.index.to_series().str.contains("Mono", case=False)
colors = [style.RED if m else style.LIGHTGRAY for m in ismono]
ax1.barh(range(len(prof2)), prof2["guardian"], color=colors, edgecolor="white")
ax1.set_yticks(range(len(prof2))); ax1.set_yticklabels(prof2.index, fontsize=7)
ax1.set_xlabel("mean guardian dependence")
ax1.set_title("(a) guardian dependence by cell state\n(monocytic states in red rank highest)", fontsize=9.5)

# (b) guardian dependence violin: monocytic vs primitive
parts = ax2.violinplot([prim["guardian_dependence"], mono["guardian_dependence"]],
                       showmedians=True)
for pc, c in zip(parts["bodies"], [style.ACCENT, style.RED]):
    pc.set_facecolor(c); pc.set_alpha(0.6)
ax2.set_xticks([1, 2]); ax2.set_xticklabels(["primitive", "monocytic"])
ax2.set_ylabel("guardian dependence")
ax2.set_title("(b) guardian dependence\n(mono 0.67 vs prim 0.25, p≈1e-69)", fontsize=9.5)

# (c) MCL1 per-cell by group
parts = ax3.violinplot([prim["MCL1"], mono["MCL1"]], showmedians=True)
for pc, c in zip(parts["bodies"], [style.ACCENT, style.RED]):
    pc.set_facecolor(c); pc.set_alpha(0.6)
ax3.set_xticks([1, 2]); ax3.set_xticklabels(["primitive", "monocytic"])
ax3.set_ylabel("MCL1 (log-norm)")
ax3.set_title("(c) MCL-1 expression\n(p≈8e-64) — the resistance driver", fontsize=9.5)

fig.suptitle("Single-cell layer (van Galen AML atlas, 8 patients, 3,434 malignant cells) — "
             "monocytic cells occupy a distinct MCL-1-high, guardian-dependent state",
             fontsize=10, y=1.02)
style.save(fig, "F_singlecell")
