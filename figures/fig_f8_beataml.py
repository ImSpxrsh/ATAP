#!/usr/bin/env python3
"""F8 — BeatAML patient-level. Susceptibility score vs ex vivo venetoclax AUC, colored by
executioner-loss call, with marginal densities. Must-not-claim: ex vivo venetoclax
resistance != ATAP sensitivity; this is the target population, validated on real patients."""
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
sus = pd.read_csv(TAB / "M5_susceptibility_beataml.csv", index_col=0)
bea = pd.read_csv(PROC / "beataml_patients.csv", index_col=0)
j = sus.join(bea["venetoclax_AUC"]).dropna(subset=["venetoclax_AUC", "susceptibility_score"])

fig = plt.figure(figsize=(8.2, 6.4))
gs = fig.add_gridspec(2, 2, width_ratios=[4, 1], height_ratios=[1, 4],
                      wspace=0.04, hspace=0.04)
ax = fig.add_subplot(gs[1, 0])
axt = fig.add_subplot(gs[0, 0], sharex=ax)
axr = fig.add_subplot(gs[1, 1], sharey=ax)

called = j["executioner_loss_call"].astype(bool)
ax.scatter(j.loc[~called, "susceptibility_score"], j.loc[~called, "venetoclax_AUC"],
           c=style.LIGHTGRAY, s=22, edgecolor="white", lw=0.3, label="executioner intact")
ax.scatter(j.loc[called, "susceptibility_score"], j.loc[called, "venetoclax_AUC"],
           c=style.RED, s=48, edgecolor="black", lw=0.5, label="executioner-loss call", zorder=5)
z = np.polyfit(j["susceptibility_score"], j["venetoclax_AUC"], 1)
xx = np.linspace(j["susceptibility_score"].min(), j["susceptibility_score"].max(), 50)
ax.plot(xx, np.polyval(z, xx), color=style.ACCENT, lw=2)
rho, p = stats.spearmanr(j["susceptibility_score"], j["venetoclax_AUC"])
ax.set_xlabel("predicted susceptibility score (mechanistic)")
ax.set_ylabel("ex vivo venetoclax AUC  (↑ = resistant)")
ax.text(0.03, 0.97, f"Spearman ρ = {rho:.2f}\np = {p:.1e}\nn = {len(j)}",
        transform=ax.transAxes, va="top", fontsize=9,
        bbox=dict(boxstyle="round", fc="white", ec=style.LIGHTGRAY))
ax.legend(loc="lower right", fontsize=8)

axt.hist(j["susceptibility_score"], bins=30, color=style.GRAY)
axt.axis("off")
axr.hist(j["venetoclax_AUC"], bins=30, orientation="horizontal", color=style.GRAY)
axr.axis("off")
axt.set_title("F8 — Beat AML patients: predicted susceptibility vs observed ex vivo "
              "venetoclax resistance\n(target population, NOT ATAP sensitivity)",
              fontsize=9.5, loc="left")
style.save(fig, "F8_beataml_patient_level")
