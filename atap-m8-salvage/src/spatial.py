#!/usr/bin/env python3
"""M7 — spatial priming + routing map (routing logic).

Per spot, quantify executioner availability (BAX/BAK1) and guardian dependence
(BCL2/MCL1), then assign a routing category:
  - "bypass-required": guardian-dependent BUT executioner-low -> venetoclax predicted to
    fail, a BAX-independent agent (ATAP) is mechanistically rational.
  - "venetoclax-sufficient": executioners intact.
  - "low-signal": neither guardian dependence nor executioner deficit is high.

A per-spot stability score (S³-style) is computed across a multiverse of spatial analytic
choices (normalization, neighbourhood smoothing, thresholds): the fraction of choices that
agree on the spot's routing category.

The routing functions are PURE (operate on a spots x genes DataFrame) so they work on a
real Visium/Xenium object or on synthetic ground-truth data (M8) identically. No efficacy
is implied — this is a PREDICTED routing map, not a treatment map (GUARDRAILS §3).
"""
from __future__ import annotations
import itertools
import numpy as np
import pandas as pd

EXEC = ["BAX", "BAK1"]
GUARD = ["BCL2", "MCL1"]


def _rank01(s):
    return s.rank(pct=True)


def _normalize(df, method):
    if method == "rank":
        return df.apply(_rank01)
    if method == "zscore":
        return (df - df.mean()) / df.std(ddof=0)
    if method == "minmax":
        return (df - df.min()) / (df.max() - df.min() + 1e-9)
    raise ValueError(method)


def _smooth(values: pd.Series, coords: pd.DataFrame | None, k: int) -> pd.Series:
    """Neighbourhood mean smoothing over the k nearest spots (if coords given)."""
    if coords is None or k <= 0:
        return values
    from scipy.spatial import cKDTree
    tree = cKDTree(coords[["x", "y"]].values)
    _, idx = tree.query(coords[["x", "y"]].values, k=min(k + 1, len(coords)))
    return pd.Series(values.values[idx].mean(axis=1), index=values.index)


def routing(expr: pd.DataFrame, coords: pd.DataFrame | None = None, *,
            norm="rank", guardian_hi=0.6, exec_lo=0.4, k=0) -> pd.DataFrame:
    """One routing assignment for a given set of analytic choices.

    expr: spots x genes (must contain BAX/BAK1/BCL2/MCL1). coords: spots x {x,y} (optional).
    """
    g = [c for c in GUARD if c in expr.columns]
    e = [c for c in EXEC if c in expr.columns]
    norml = _normalize(expr[g + e], norm)
    guardian_dep = norml[g].max(axis=1)
    exec_avail = norml[e].mean(axis=1)
    if coords is not None and k > 0:
        guardian_dep = _smooth(guardian_dep, coords, k)
        exec_avail = _smooth(exec_avail, coords, k)
    # re-rank to [0,1] after any smoothing/normalization so thresholds are comparable
    gd = _rank01(guardian_dep)
    ea = _rank01(exec_avail)
    cat = np.where((gd >= guardian_hi) & (ea <= exec_lo), "bypass-required",
                   np.where(ea > exec_lo, "venetoclax-sufficient", "low-signal"))
    return pd.DataFrame({"guardian_dependence": gd, "executioner_availability": ea,
                         "routing": cat}, index=expr.index)


MULTIVERSE = {
    "norm": ["rank", "zscore", "minmax"],
    "guardian_hi": [0.5, 0.6, 0.7],
    "exec_lo": [0.3, 0.4, 0.5],
    "k": [0, 6, 12],
}


def routing_with_stability(expr: pd.DataFrame, coords: pd.DataFrame | None = None):
    """Primary routing (default choices) + per-spot stability = fraction of the analytic
    multiverse that agrees with the primary category."""
    primary = routing(expr, coords)  # defaults
    votes = pd.DataFrame(index=expr.index)
    combos = list(itertools.product(*MULTIVERSE.values()))
    for i, (norm, ghi, elo, k) in enumerate(combos):
        r = routing(expr, coords, norm=norm, guardian_hi=ghi, exec_lo=elo, k=k)
        votes[i] = (r["routing"] == primary["routing"]).astype(int)
    primary["stability"] = votes.mean(axis=1)
    primary["n_specs"] = len(combos)
    return primary
