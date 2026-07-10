#!/usr/bin/env python3
"""F11 — synthetic validation: ground truth vs recovered routing + ROC. SYNTHETIC (method
validation only, no biological reading). F12 — power curves + permutation-null histograms
(backbone association null + spatial join-count null)."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, roc_auc_score
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "figures"))
import style  # noqa: E402
style.apply()
TAB = ROOT / "outputs" / "tables"
LOGS = ROOT / "outputs" / "logs"

field = pd.read_csv(TAB / "M8_recovery_field.csv", index_col=0)
power = pd.read_csv(TAB / "M8_power_curve.csv")

# F11
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
axes[0].scatter(field["x"], field["y"], c=field["truth"].astype(int), cmap="Reds", s=8)
axes[0].set_title("(a) ground truth (bypass region)"); axes[0].set_aspect("equal"); axes[0].axis("off")
axes[1].scatter(field["x"], field["y"], c=field["pred_bypass"].astype(int), cmap="Reds", s=8)
axes[1].set_title("(b) recovered (routing pipeline)"); axes[1].set_aspect("equal"); axes[1].axis("off")
fpr, tpr, _ = roc_curve(field["truth"], field["score"])
auc = roc_auc_score(field["truth"], field["score"])
axes[2].plot(fpr, tpr, color=style.ACCENT, lw=2, label=f"AUC = {auc:.3f}")
axes[2].plot([0, 1], [0, 1], color=style.GRAY, ls="--", lw=1)
axes[2].set_xlabel("false positive rate"); axes[2].set_ylabel("true positive rate")
axes[2].set_title("(c) ROC vs ground truth"); axes[2].legend(loc="lower right")
fig.suptitle("F11 — method validation (SYNTHETIC). Pipeline recovers a known routing "
             "pattern. No biological reading.", fontsize=9.5, y=1.03)
style.save(fig, "F11_synthetic_validation")

# F12
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
# power curve
for eff, g in power.groupby("effect"):
    axes[0].plot(g["n_spots"], g["mean_auc"], "o-", label=f"effect {eff}")
axes[0].axhline(0.7, color=style.GRAY, ls="--", lw=1)
axes[0].set_xscale("log"); axes[0].set_xlabel("# spots"); axes[0].set_ylabel("mean ROC-AUC")
axes[0].set_title("(a) power: gradient detectability"); axes[0].legend(fontsize=8)

# backbone permutation null
bn = np.load(LOGS / "null_backbone_venetoclax_LN_IC50.npy")
obs = pd.read_csv(TAB / "M2_backbone_permutation.csv").iloc[0]["obs_beta"]
axes[1].hist(bn, bins=40, color=style.LIGHTGRAY)
axes[1].axvline(obs, color=style.RED, lw=2, label=f"observed β={obs:.3f}")
axes[1].set_xlabel("permuted β"); axes[1].set_ylabel("count")
axes[1].set_title("(b) backbone null (venetoclax)"); axes[1].legend(fontsize=8)

# spatial join-count null
sn = np.load(LOGS / "null_spatial_joincount.npy")
obs2 = pd.read_csv(TAB / "M8_spatial_null.csv").iloc[0]["obs_joincount"]
axes[2].hist(sn, bins=40, color=style.LIGHTGRAY)
axes[2].axvline(obs2, color=style.RED, lw=2, label=f"observed={obs2:.3f}")
axes[2].set_xlabel("permuted join-count"); axes[2].set_ylabel("count")
axes[2].set_title("(c) spatial structure null (synthetic)"); axes[2].legend(fontsize=8)
fig.suptitle("F12 — power curves + permutation nulls. Panels (a,c) synthetic; (b) real "
             "backbone association vs its label-permutation null.", fontsize=9.5, y=1.03)
style.save(fig, "F12_power_nulls")
