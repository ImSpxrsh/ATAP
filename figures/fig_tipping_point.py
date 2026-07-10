#!/usr/bin/env python3
"""F_tipping — the calibrated decision boundary in the two-axis plane.
Patients/lines plotted by (guardian dependence, executioner availability), colored by observed
venetoclax response; the fitted P=0.5 boundary + bootstrap band overlaid. The honest tipping
point: driven by the guardian axis, executioner axis ~flat (needs functional data)."""
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

bnd = pd.read_csv(TAB / "TIPPING_boundary.csv").set_index("cohort")
fig, axes = plt.subplots(1, 2, figsize=(12, 5.4))
for ax, coh, title in zip(axes, ["depmap", "beataml"],
                          ["DepMap cell lines (venetoclax LN_IC50)",
                           "Beat AML patients (ex-vivo venetoclax AUC)"]):
    pts = pd.read_csv(TAB / f"TIPPING_points_{coh}.csv", index_col=0)
    r = bnd.loc[coh]
    res_m = pts["resistant"] == 1
    ax.scatter(pts.loc[~res_m, "guardian_dependence"], pts.loc[~res_m, "executioner_availability"],
               s=14, c=style.ACCENT, alpha=0.7, label="venetoclax responder")
    ax.scatter(pts.loc[res_m, "guardian_dependence"], pts.loc[res_m, "executioner_availability"],
               s=14, c=style.RED, alpha=0.7, label="venetoclax non-responder")
    # decision boundary line: b0 + b1*g_z + b2*e_z = 0, converted back to [0,1] axes
    g = pts["guardian_dependence"]; e = pts["executioner_availability"]
    gz_m, gz_s = g.mean(), g.std(ddof=0); ez_m, ez_s = e.mean(), e.std(ddof=0)
    b1, b2, b0 = r["coef_guardian"], r["coef_exec"], r["intercept"]
    xs = np.linspace(0, 1, 100)
    if abs(b2) > 1e-6:
        # solve for e given g
        gz = (xs - gz_m) / gz_s
        ez = -(b0 + b1 * gz) / b2
        ys = ez * ez_s + ez_m
        ax.plot(xs, ys, color=style.GRAY, lw=2, label="decision boundary (P=0.5)")
    # guardian tipping point + CI (vertical band)
    ax.axvspan(r["tip_lo"], r["tip_hi"], color=style.AMBER, alpha=0.18)
    ax.axvline(r["guardian_tip"], color=style.AMBER, lw=2,
               label=f"guardian tipping point {r['guardian_tip']:.2f}")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("guardian dependence (rank)")
    ax.set_ylabel("executioner availability (rank)")
    ax.set_title(f"{title}\nAUC={r['auc']:.2f} · βguardian={r['coef_guardian']:+.2f}, "
                 f"βexec={r['coef_exec']:+.2f}", fontsize=9)
    ax.legend(fontsize=7, loc="lower left")
fig.suptitle("Calibrated 'tipping point' — the venetoclax response boundary is a guardian-"
             "dependence threshold; the executioner axis is ~flat (needs functional data)",
             fontsize=10, y=1.02)
style.save(fig, "F_tipping_point")
