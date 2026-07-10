#!/usr/bin/env python3
"""F_survival — Kaplan-Meier by susceptibility tertile + Cox HR forest (BeatAML).
Honest prognostic layer: crude executioner-survival signal is confounded by ELN2017/age and
does not survive adjustment (the score is a drug-response axis, not a prognostic marker)."""
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

data = pd.read_csv(TAB / "SURVIVAL_data.csv", index_col=0)
cox = pd.read_csv(TAB / "SURVIVAL_cox.csv", index_col=0)
from lifelines import KaplanMeierFitter

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.2))
colors = {"low": style.ACCENT, "mid": style.AMBER, "high": style.RED}
kmf = KaplanMeierFitter()
for t in ["low", "mid", "high"]:
    sub = data[data["tertile"] == t]
    kmf.fit(sub["OS"], sub["event"], label=f"{t} susceptibility (n={len(sub)})")
    kmf.plot_survival_function(ax=ax1, color=colors[t], ci_show=False, lw=2)
ax1.set_xlabel("overall survival (months)"); ax1.set_ylabel("survival probability")
ax1.set_title("(a) Kaplan-Meier by susceptibility tertile\n(log-rank across tertiles: n.s.)", fontsize=9.5)
ax1.legend(fontsize=8)

# Cox forest (adjusted HRs)
axes_lbl = {"susceptibility": "susceptibility", "guardian_dependence": "guardian dep.",
            "executioner_availability": "executioner avail."}
y = np.arange(len(cox))
for i, (ax_name, row) in enumerate(cox.iterrows()):
    for adj, off, col, mk in [("unadj", +0.15, style.GRAY, "o"), ("adj", -0.15, style.ACCENT, "s")]:
        hr = row[f"HR_{adj}"]; lo = row[f"ci_{adj}"][0] if isinstance(row[f"ci_{adj}"], list) else None
    # parse CI strings
for i, (ax_name, row) in enumerate(cox.iterrows()):
    import ast
    for adj, off, col in [("unadj", +0.16, style.LIGHTGRAY), ("adj", -0.16, style.ACCENT)]:
        hr = float(row[f"HR_{adj}"]); ci = ast.literal_eval(row[f"ci_{adj}"])
        ax2.plot(ci, [i+off, i+off], color=col, lw=2)
        ax2.plot(hr, i+off, "o", color=col, label=("adjusted (age+ELN2017)" if (adj=="adj" and i==0)
                 else ("unadjusted" if (adj=="unadj" and i==0) else None)))
ax2.axvline(1.0, color=style.GRAY, ls="--", lw=1)
ax2.set_yticks(y); ax2.set_yticklabels([axes_lbl[a] for a in cox.index])
ax2.set_xlabel("hazard ratio (per +1 SD; >1 = worse survival)")
ax2.set_title("(b) Cox HR — crude executioner signal is\nconfounded, null after ELN2017/age adjustment", fontsize=9.5)
ax2.legend(fontsize=8, loc="lower right")
fig.suptitle("Prognostic layer (BeatAML, n=649) — honest: the mechanistic score is a "
             "drug-response axis, not an independent prognostic marker", fontsize=10, y=1.02)
style.save(fig, "F_survival")
