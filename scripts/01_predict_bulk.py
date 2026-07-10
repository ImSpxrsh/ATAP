#!/usr/bin/env python3
"""
01_predict_bulk.py — bulk prediction of ATAP-M8 susceptibility across a cohort.

Runs the mechanistic two-axis model over a cohort (simulated by default; pass a real
cohort with --cohort depmap|beataml|tcga once data/raw is populated), writes the
per-sample scores and a cohort summary, validates recovery of the salvage-target
population against ground truth (simulator only), and renders the two-axis map.

Usage:
    python scripts/01_predict_bulk.py                 # simulated cohort
    python scripts/01_predict_bulk.py --cohort depmap # real DepMap (needs data/raw)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from atap import data as datamod
from atap.features import build_feature_blocks
from atap.scoring import SusceptibilityModel, summarize

RESULTS = ROOT / "results"
TABLES = RESULTS / "tables"
FIGS = RESULTS / "figures"


def load_cohort(name: str):
    if name == "simulated":
        return datamod.load_simulated()
    if name == "depmap":
        return datamod.load_depmap()
    if name == "beataml":
        return datamod.load_beataml()
    if name.startswith("tcga"):
        proj = "TCGA-LAML" if ":" not in name else name.split(":", 1)[1]
        return datamod.load_tcga(proj)
    raise ValueError(f"unknown cohort {name!r}")


def validate_against_truth(scores: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame | None:
    """Simulator only: does 'salvage_target' recover the BAX/BAK-loss, execution-intact set?"""
    if "gt_class" not in meta.columns:
        return None
    df = scores.join(meta[["gt_class", "gt_effector_loss", "gt_exec_loss"]])
    ct = pd.crosstab(df["gt_class"], df["quadrant"])

    # Precision/recall for the salvage_target call vs ground truth.
    true_salvage = (df["gt_effector_loss"] == 1) & (df["gt_exec_loss"] == 0)
    pred_salvage = df["quadrant"] == "salvage_target"
    tp = int((true_salvage & pred_salvage).sum())
    fp = int((~true_salvage & pred_salvage).sum())
    fn = int((true_salvage & ~pred_salvage).sum())
    prec = tp / (tp + fp) if (tp + fp) else float("nan")
    rec = tp / (tp + fn) if (tp + fn) else float("nan")
    print("\n=== Validation vs ground truth (simulated) ===")
    print(ct)
    print(f"\nsalvage_target call — precision={prec:.2f}  recall={rec:.2f}  "
          f"(TP={tp} FP={fp} FN={fn})")
    return ct


def plot_two_axis(scores: pd.DataFrame, out: Path, color_by: str = "quadrant"):
    fig, ax = plt.subplots(figsize=(7, 6))
    palette = {
        "salvage_target": "#d62728", "standard_of_care": "#2ca02c",
        "hard_escape": "#7f7f7f", "ambiguous": "#c7c7c7",
    }
    if color_by in scores.columns and scores[color_by].dtype == object:
        for lab, sub in scores.groupby(color_by):
            ax.scatter(sub["venetoclax_pct"], sub["atap_pct"], s=18, alpha=0.75,
                       label=lab, color=palette.get(lab, None), edgecolor="none")
        ax.legend(title="predicted class", fontsize=8, loc="lower left")
    else:
        sc = ax.scatter(scores["venetoclax_pct"], scores["atap_pct"], s=18,
                        c=scores["salvage_index"], cmap="coolwarm", alpha=0.8)
        fig.colorbar(sc, label="salvage index")

    from atap.scoring import VENETO_LOW, ATAP_HIGH
    ax.axvline(VENETO_LOW, ls="--", c="k", lw=0.8, alpha=0.5)
    ax.axhline(ATAP_HIGH, ls="--", c="k", lw=0.8, alpha=0.5)
    ax.set_xlabel("venetoclax (BH3-mimetic) predicted efficacy  [cohort percentile]")
    ax.set_ylabel("ATAP-M8 predicted efficacy  [cohort percentile]")
    ax.set_title("Two-axis susceptibility map\nred = BH3-resistant, ATAP-salvageable")
    ax.text(0.03, 0.97, "SALVAGE\nTARGET", transform=ax.transAxes, va="top",
            fontsize=9, color="#d62728", weight="bold", alpha=0.6)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", default="simulated")
    args = ap.parse_args()

    TABLES.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)

    cohort = load_cohort(args.cohort)
    print(cohort)

    blocks = build_feature_blocks(cohort.expr, cohort.mutations)
    model = SusceptibilityModel()

    # If a real response readout exists, calibrate the venetoclax axis to it.
    if cohort.response is not None and "venetoclax_sensitive" in cohort.response.columns:
        model.calibrate_to_response(
            blocks, venetoclax_response=cohort.response["venetoclax_sensitive"])

    scores = model.score(blocks)
    scores = scores.join(cohort.meta[[c for c in ("lineage", "disease") if c in cohort.meta]])

    out_scores = TABLES / f"{cohort.name.replace(':','_')}_scores.csv"
    scores.to_csv(out_scores)
    print(f"\nwrote {out_scores.relative_to(ROOT)}  ({len(scores)} samples)")

    print("\n=== Cohort quadrant summary ===")
    summ = summarize(scores)
    print(summ)
    summ.to_csv(TABLES / f"{cohort.name.replace(':','_')}_summary.csv")

    validate_against_truth(scores, cohort.meta)

    # Example audit trail for the top salvage candidate.
    if (scores["quadrant"] == "salvage_target").any():
        top = scores[scores["quadrant"] == "salvage_target"] \
            .sort_values("salvage_index", ascending=False).index[0]
        print(f"\n=== Audit: top salvage candidate {top} ===")
        print(model.explain_sample(blocks, top))

    plot_two_axis(scores, FIGS / f"{cohort.name.replace(':','_')}_two_axis.png")


if __name__ == "__main__":
    main()
