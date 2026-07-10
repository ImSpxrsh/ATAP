#!/usr/bin/env python3
"""F9 — spatial heterogeneity maps (BAX, BAK1, BCL2, MCL1 per spot).
F10 — routing map (bypass-required vs venetoclax-sufficient) + per-spot S³ stability.
Real 10x Human Lymph Node Visium. Must-not-claim: expression != function (expression-based
inference); predicted routing map, not a treatment map."""
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "figures"))
import style  # noqa: E402
style.apply()

df = pd.read_csv(ROOT / "data" / "processed" / "spatial_lymphnode_routing.csv", index_col=0)
x, y = df["x"], df["y"]

# F9 — four guardian/executioner maps
fig, axes = plt.subplots(1, 4, figsize=(15, 4))
for ax, g in zip(axes, ["BAX", "BAK1", "BCL2", "MCL1"]):
    sc = ax.scatter(x, y, c=df[f"expr_{g}"], s=6, cmap="viridis")
    ax.set_title(g); ax.set_aspect("equal"); ax.axis("off")
    fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.02)
fig.suptitle("F9 — spatial heterogeneity of executioners (BAX, BAK1) and guardians "
             "(BCL2, MCL1). 10x Human Lymph Node Visium. Expression-based inference.",
             fontsize=10, y=1.05)
style.save(fig, "F9_spatial_heterogeneity")

# F10 — routing map + stability
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))
cats = ["venetoclax-sufficient", "low-signal", "bypass-required"]
cmap = {"venetoclax-sufficient": style.ACCENT, "low-signal": style.LIGHTGRAY,
        "bypass-required": style.RED}
for cat in cats:
    m = df["routing"] == cat
    ax1.scatter(x[m], y[m], c=cmap[cat], s=7, label=f"{cat} ({m.sum()})")
ax1.set_title("(a) predicted routing map"); ax1.set_aspect("equal"); ax1.axis("off")
ax1.legend(loc="upper right", fontsize=8, markerscale=1.5)

sc = ax2.scatter(x, y, c=df["stability"], s=7, cmap="magma", vmin=0, vmax=1)
ax2.set_title(f"(b) per-spot S³ stability (mean {df['stability'].mean():.2f}, "
              f"{int(df['n_specs'].iloc[0])} choices)")
ax2.set_aspect("equal"); ax2.axis("off")
fig.colorbar(sc, ax=ax2, fraction=0.046, label="stability")
fig.suptitle("F10 — where venetoclax is predicted sufficient vs where a BAX-independent "
             "agent is rational, with per-spot confidence. Predicted routing, not treatment.",
             fontsize=9.5, y=1.02)
style.save(fig, "F10_spatial_routing_stability")
