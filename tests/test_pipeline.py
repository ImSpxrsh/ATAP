"""
Smoke + sanity tests for the ATAP computational spine.

Run with:  python -m pytest tests/ -q     (or)     python tests/test_pipeline.py
The tests assert the *mechanistic* behaviour the whole project rests on:
BAX/BAK loss must move a sample toward 'salvage_target', and the spatial hotspot
caller must recover a planted resistant clone.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd

from atap import data as datamod
from atap.features import build_feature_blocks
from atap.scoring import SusceptibilityModel
from atap.spatial import score_spatial, simulate_spatial_slide


def test_bax_loss_flips_axes():
    """A BAX/BAK LoF must lower the venetoclax axis and raise the ATAP axis."""
    genes = datamod.biology.all_genes()
    expr = pd.DataFrame(4.0, index=["wt", "bax_lof"], columns=genes)
    muts = pd.DataFrame([{"sample": "bax_lof", "gene": "BAX",
                          "variant_class": "frameshift", "protein_change": ""}])
    blocks = build_feature_blocks(expr, muts)
    s = SusceptibilityModel().raw_scores(blocks)
    assert s.loc["bax_lof", "venetoclax_score"] < s.loc["wt", "venetoclax_score"]
    assert s.loc["bax_lof", "atap_score"] > s.loc["wt", "atap_score"]


def test_simulated_recovery():
    """salvage_target precision/recall against ground truth stay in a sane band."""
    cohort = datamod.load_simulated(n=400, seed=7)
    blocks = build_feature_blocks(cohort.expr, cohort.mutations)
    scores = SusceptibilityModel().score(blocks)
    df = scores.join(cohort.meta)
    true = (df["gt_effector_loss"] == 1) & (df["gt_exec_loss"] == 0)
    pred = df["quadrant"] == "salvage_target"
    tp = int((true & pred).sum()); fp = int((~true & pred).sum()); fn = int((true & ~pred).sum())
    prec = tp / (tp + fp); rec = tp / (tp + fn)
    assert prec > 0.6, f"precision too low: {prec}"
    assert rec > 0.5, f"recall too low: {rec}"


def test_hard_escape_not_called_salvage():
    """Execution-loss samples (hard escape) must not be predicted salvage_target."""
    cohort = datamod.load_simulated(n=400, seed=7)
    blocks = build_feature_blocks(cohort.expr, cohort.mutations)
    scores = SusceptibilityModel().score(blocks).join(cohort.meta)
    exec_loss = scores[scores["gt_exec_loss"] == 1]
    frac_mislabeled = (exec_loss["quadrant"] == "salvage_target").mean()
    assert frac_mislabeled < 0.2, f"too many hard-escape called salvage: {frac_mislabeled}"


def test_spatial_hotspot_recovers_clone():
    """Gi* hotspot footprint must overlap the planted resistant clone (Jaccard > 0.5)."""
    expr, coords, meta = simulate_spatial_slide(n_side=40, seed=3)
    out = score_spatial(expr, coords)
    gt = meta["gt_resistant_clone"].reindex(out.index).values.astype(bool)
    pred = out["atap_hotspot"].values
    tp = int((gt & pred).sum()); fp = int((~gt & pred).sum()); fn = int((gt & ~pred).sum())
    jac = tp / (tp + fp + fn)
    assert jac > 0.5, f"spatial Jaccard too low: {jac}"
    assert out.attrs["morans_p"] < 0.05, "salvage index not spatially structured"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("all tests passed")
