"""
spatial.py — intratumoral mapping of where a BAX-independent agent is needed.

This is the second half of the computational spine: take spatial transcriptomics
(Visium / Xenium / MERFISH-style spot x gene matrix + x,y coordinates), score every
spot on the same two axes as the bulk model (venetoclax vs ATAP-M8), then use spatial
statistics to delineate *contiguous regions* where the BH3-mimetic class is predicted
to fail and a pore-forming salvage is predicted to work.

The clinical question this answers that bulk cannot: a tumor is not uniform. A biopsy
that reads "venetoclax-sensitive" in bulk can still harbor BAX/BAK-deficient pockets
that seed relapse. Mapping those pockets is what makes "predict-and-localize" a new
result rather than a re-statement of the 1-cell bypass.

Implemented on numpy/scipy only (no scanpy dependency): a KNN spatial graph, spatial
smoothing, Moran's I for spatial autocorrelation, and Getis-Ord Gi* hotspot detection.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import norm

from .features import build_feature_blocks
from .scoring import SusceptibilityModel


@dataclass
class SpatialGraph:
    """KNN graph over spot coordinates with row-normalized weights."""
    idx: np.ndarray      # (n, k) neighbor indices
    dist: np.ndarray     # (n, k) neighbor distances
    W: np.ndarray        # (n, n) row-normalized weight matrix (dense; fine for <~20k spots)

    @property
    def n(self) -> int:
        return self.W.shape[0]


def build_graph(coords: np.ndarray, k: int = 8, exclude_self: bool = True) -> SpatialGraph:
    """
    Build a symmetric-ish KNN graph. coords: (n, 2). Weights are inverse-distance,
    row-normalized so each spot's neighborhood sums to 1.
    """
    n = coords.shape[0]
    tree = cKDTree(coords)
    kk = k + 1 if exclude_self else k
    dist, idx = tree.query(coords, k=kk)
    if exclude_self:
        dist, idx = dist[:, 1:], idx[:, 1:]

    W = np.zeros((n, n), dtype=float)
    inv = 1.0 / np.maximum(dist, 1e-9)
    for i in range(n):
        W[i, idx[i]] = inv[i]
    row = W.sum(axis=1, keepdims=True)
    row[row == 0] = 1.0
    W = W / row
    return SpatialGraph(idx=idx, dist=dist, W=W)


def smooth(values: np.ndarray, graph: SpatialGraph, rounds: int = 1, alpha: float = 0.5) -> np.ndarray:
    """
    Neighborhood smoothing: x <- (1-alpha)*x + alpha*(W @ x). Denoises spot-level
    scores before hotspot calling. `rounds` applies it iteratively.
    """
    x = np.asarray(values, dtype=float)
    for _ in range(rounds):
        x = (1 - alpha) * x + alpha * (graph.W @ x)
    return x


def morans_i(values: np.ndarray, graph: SpatialGraph, n_perm: int = 199, seed: int = 0):
    """
    Global Moran's I of a spot-level score — is the ATAP-need signal spatially
    structured, or salt-and-pepper? Returns (I, permutation p-value). A significant
    positive I is the statistical justification for calling contiguous regions.
    """
    x = np.asarray(values, dtype=float)
    z = x - x.mean()
    W = graph.W
    s0 = W.sum()
    denom = (z ** 2).sum()
    num = z @ (W @ z)
    I = (len(x) / s0) * (num / denom) if denom > 0 else np.nan

    rng = np.random.default_rng(seed)
    perm = np.empty(n_perm)
    for p in range(n_perm):
        zp = rng.permutation(z)
        perm[p] = (len(x) / s0) * ((zp @ (W @ zp)) / denom)
    # two-sided permutation p
    pval = (1 + np.sum(np.abs(perm) >= np.abs(I))) / (n_perm + 1)
    return float(I), float(pval)


def getis_ord_gi(values: np.ndarray, graph: SpatialGraph) -> np.ndarray:
    """
    Getis-Ord Gi* z-scores (with self included). High positive z = a spot embedded in a
    neighborhood of *high* values -> an ATAP-need hotspot. Returns per-spot z-scores.
    """
    x = np.asarray(values, dtype=float)
    n = len(x)
    xbar = x.mean()
    s = x.std(ddof=0)

    # Binary weights incl. self from the KNN structure (Gi* convention).
    Wb = (graph.W > 0).astype(float)
    np.fill_diagonal(Wb, 1.0)

    z = np.empty(n)
    for i in range(n):
        wi = Wb[i]
        wsum = wi.sum()
        lag = (wi * x).sum()
        num = lag - xbar * wsum
        den = s * np.sqrt((n * (wi ** 2).sum() - wsum ** 2) / (n - 1))
        z[i] = num / den if den > 0 else 0.0
    return z


def score_spatial(
    expr: pd.DataFrame,
    coords: pd.DataFrame,
    mutations: pd.DataFrame | None = None,
    model: SusceptibilityModel | None = None,
    k: int = 8,
    smooth_rounds: int = 1,
    hotspot_z: float = 1.96,
) -> pd.DataFrame:
    """
    Full spatial pipeline.

    Parameters
    ----------
    expr   : spots x genes, log-scale expression.
    coords : spots x ['x','y'] pixel/array coordinates (index aligned to expr).
    mutations : optional; spatial platforms rarely give per-spot mutations, but a
        clone-level LoF flag can be passed through the same schema if available.
    hotspot_z : Gi* z threshold for calling an ATAP-need hotspot (1.96 ~ p<0.05).

    Returns
    -------
    Per-spot DataFrame: the two axis scores, salvage_index, smoothed salvage_index,
    Gi* hotspot z-score, and a boolean `atap_hotspot` flag marking regions where a
    BAX-independent agent is predicted to be needed.
    """
    model = model or SusceptibilityModel()
    coords = coords.reindex(expr.index)

    blocks = build_feature_blocks(expr, mutations)
    scores = model.score(blocks)

    graph = build_graph(coords[["x", "y"]].values, k=k)

    raw = scores["salvage_index"].values
    sm = smooth(raw, graph, rounds=smooth_rounds)
    gi = getis_ord_gi(sm, graph)

    I, p = morans_i(sm, graph)

    out = scores.copy()
    out["x"] = coords["x"].values
    out["y"] = coords["y"].values
    out["salvage_index_smoothed"] = sm
    out["gi_zscore"] = gi
    out["atap_hotspot"] = gi >= hotspot_z
    # stash cohort-level spatial stats as attrs for reporting
    out.attrs["morans_I"] = I
    out.attrs["morans_p"] = p
    out.attrs["n_hotspot_spots"] = int(out["atap_hotspot"].sum())
    return out


def simulate_spatial_slide(
    n_side: int = 40,
    seed: int = 3,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Simulate a tumor slide with a spatially contiguous BAX/BAK-deficient clone, so the
    spatial pipeline can be validated: the hotspot caller should recover the clone's
    footprint. Returns (expr, coords, meta) with meta carrying the ground-truth region.
    """
    from . import biology

    rng = np.random.default_rng(seed)
    xs, ys = np.meshgrid(np.arange(n_side), np.arange(n_side))
    coords = pd.DataFrame({"x": xs.ravel(), "y": ys.ravel()})
    n = len(coords)
    spots = [f"spot_{i:05d}" for i in range(n)]
    coords.index = spots

    # Ground-truth resistant clone: a disc in one quadrant + a smaller satellite.
    cx, cy, r = n_side * 0.3, n_side * 0.65, n_side * 0.16
    sx, sy, sr = n_side * 0.72, n_side * 0.30, n_side * 0.09
    d1 = np.sqrt((coords["x"] - cx) ** 2 + (coords["y"] - cy) ** 2)
    d2 = np.sqrt((coords["x"] - sx) ** 2 + (coords["y"] - sy) ** 2)
    resistant = ((d1 < r) | (d2 < sr)).values

    genes = biology.all_genes()
    base = rng.normal(4.0, 0.8, size=(n, len(genes)))
    expr = pd.DataFrame(base, index=spots, columns=genes).clip(lower=0)

    # In the resistant clone: BAX/BAK down (effector loss), priming intact, execution
    # intact -> should score as ATAP-need hotspot. Add smooth spatial noise elsewhere.
    for g in ("BAX", "BAK1"):
        expr.loc[resistant, g] -= 2.6
    for g in biology.BH3_ACTIVATORS:
        expr[g] += 0.8  # generally primed slide
    # BCL2 higher outside the clone (venetoclax-responsive bulk)
    expr.loc[~resistant, "BCL2"] += 1.8

    meta = pd.DataFrame({"gt_resistant_clone": resistant.astype(int)}, index=spots)
    return expr, coords, meta
