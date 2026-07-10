#!/usr/bin/env python3
"""
02_spatial_map.py — localize where within a tumor a BAX-independent agent is needed.

Scores every spot on the venetoclax/ATAP axes, runs spatial statistics (Moran's I +
Getis-Ord Gi*), and renders a slide map with the predicted ATAP-need hotspots. By
default it simulates a slide with a known BAX/BAK-deficient clone and checks that the
hotspot caller recovers the clone footprint. Point it at real spatial data by editing
`load_slide` (spot x gene matrix + x,y coordinates).

Usage:
    python scripts/02_spatial_map.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from atap.spatial import score_spatial, simulate_spatial_slide

RESULTS = ROOT / "results"
FIGS = RESULTS / "figures"
TABLES = RESULTS / "tables"


def load_slide():
    """Return (expr, coords, meta). Replace with a real Visium/Xenium loader as needed."""
    return simulate_spatial_slide()


def plot_slide(out: pd.DataFrame, meta: pd.DataFrame | None, path: Path):
    has_truth = meta is not None and "gt_resistant_clone" in meta.columns
    ncol = 3 if has_truth else 2
    fig, axes = plt.subplots(1, ncol, figsize=(5 * ncol, 4.6))

    ax = axes[0]
    sc = ax.scatter(out["x"], out["y"], c=out["salvage_index_smoothed"],
                    cmap="coolwarm", s=14)
    fig.colorbar(sc, ax=ax, fraction=0.046)
    ax.set_title("Salvage index (smoothed)\nred = ATAP favored over venetoclax")

    ax = axes[1]
    ax.scatter(out["x"], out["y"], c="#dddddd", s=14)
    hot = out[out["atap_hotspot"]]
    ax.scatter(hot["x"], hot["y"], c="#d62728", s=16, label="ATAP-need hotspot")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_title(f"Gi* hotspots (n={int(out['atap_hotspot'].sum())})\n"
                 f"Moran's I={out.attrs['morans_I']:.2f}, p={out.attrs['morans_p']:.3f}")

    if has_truth:
        ax = axes[2]
        gt = meta["gt_resistant_clone"].reindex(out.index).values.astype(bool)
        ax.scatter(out["x"], out["y"], c="#dddddd", s=14)
        ax.scatter(out["x"][gt], out["y"][gt], c="#1f77b4", s=16,
                   label="true BAX/BAK-deficient clone")
        ax.legend(fontsize=8, loc="upper right")
        ax.set_title("Ground truth (simulated)")

    for ax in axes:
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def main():
    FIGS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)

    expr, coords, meta = load_slide()
    out = score_spatial(expr, coords)

    print("=== Spatial summary ===")
    print(f"spots: {len(out)}")
    print(f"Moran's I (salvage index): {out.attrs['morans_I']:.3f}  "
          f"p={out.attrs['morans_p']:.3f}")
    print(f"ATAP-need hotspot spots: {out.attrs['n_hotspot_spots']}")

    if meta is not None and "gt_resistant_clone" in meta.columns:
        gt = meta["gt_resistant_clone"].reindex(out.index).values.astype(bool)
        pred = out["atap_hotspot"].values
        tp = int((gt & pred).sum()); fp = int((~gt & pred).sum()); fn = int((gt & ~pred).sum())
        prec = tp / (tp + fp) if (tp + fp) else float("nan")
        rec = tp / (tp + fn) if (tp + fn) else float("nan")
        # Jaccard between predicted hotspot and true clone footprint.
        jac = tp / (tp + fp + fn) if (tp + fp + fn) else float("nan")
        print(f"\nHotspot vs true clone — precision={prec:.2f} recall={rec:.2f} "
              f"Jaccard={jac:.2f}")

    out.to_csv(TABLES / "spatial_spot_scores.csv")
    plot_slide(out, meta, FIGS / "spatial_atap_need_map.png")


if __name__ == "__main__":
    main()
