#!/usr/bin/env python3
"""M1 — BCL-2-family gene panel + executioner-loss logic.

The executioner-loss score is a function of BAX/BAK1 genomic/expression state ONLY.
It never references drug response or any ATAP data (GUARDRAILS §M1 acceptance:
the score must be constructible before any outcome is seen — this prevents circularity
downstream when we test whether it predicts venetoclax resistance).

Executioner loss per sample = TRUE if ANY of:
  - damaging (LOF) mutation in BAX or BAK1, OR
  - deep copy-number deletion of BAX or BAK1, OR
  - bottom-quantile expression of BOTH BAX and BAK1
(thresholds all in config.yaml; rationale in DECISIONS.md).

Continuous executioner_loss_score in [0,1] = mean of the available component signals
(each mapped to [0,1]); binary call = score-based OR of the component booleans.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())


def panel(kind: str) -> list[str]:
    p = CFG["panels"]
    if kind in p:
        return list(p[kind])
    raise KeyError(kind)


def all_signature_genes() -> list[str]:
    p = CFG["panels"]
    genes = set(p["executioners"]) | set(p["guardians"]) | set(p["sensitizers"])
    for grp in p["signature_extra"].values():
        genes |= set(grp)
    return sorted(genes)


def _is_damaging(variant_info: str) -> bool:
    if not isinstance(variant_info, str):
        return False
    toks = variant_info.replace("&", " ").replace(",", " ").split()
    dmg = set(CFG["executioner_loss"]["damaging_classes"])
    return any(t in dmg for t in toks) or variant_info in dmg


def mutation_lof(mut_df: pd.DataFrame, gene_col: str, sample_col: str,
                 class_col: str, genes: list[str]) -> pd.Series:
    """Return boolean Series indexed by sample: has a damaging mutation in any `genes`."""
    sub = mut_df[mut_df[gene_col].isin(genes)].copy()
    if sub.empty:
        return pd.Series(dtype=bool)
    sub["dmg"] = sub[class_col].map(_is_damaging)
    dmg = sub[sub["dmg"]]
    if dmg.empty:
        return pd.Series(dtype=bool)
    hit = dmg.groupby(sample_col).size() > 0
    return hit


def cn_deep_deletion(cn: pd.DataFrame, genes: list[str]) -> pd.Series:
    """cn: samples x genes (DepMap LINEAR relative CN, neutral ~1.0).
    True if any gene <= the deep-deletion cutoff (config: cn_deep_del_relative)."""
    cutoff = CFG["executioner_loss"]["cn_deep_del_relative"]
    present = [g for g in genes if g in cn.columns]
    if not present:
        return pd.Series(dtype=bool)
    return (cn[present] <= cutoff).any(axis=1)


def expression_low_both(expr: pd.DataFrame, genes: list[str],
                        quantile: float | None = None) -> pd.Series:
    """expr: samples x genes. True where ALL executioners are below their own
    bottom-`quantile` across the cohort. 'Both low' (spec §M1) — losing one executioner
    still leaves a pore-forming path, so the executioner STEP is only compromised when
    every executioner is low."""
    q = CFG["executioner_loss"]["expr_low_quantile"] if quantile is None else quantile
    present = [g for g in genes if g in expr.columns]
    if not present:
        return pd.Series(False, index=expr.index)
    thresh = expr[present].quantile(q)
    low = expr[present].le(thresh, axis=1)
    return low.all(axis=1)


def executioner_loss_table(expr=None, cn=None, mut=None, *,
                           mut_cols=None, quantile=None,
                           samples: pd.Index | None = None) -> pd.DataFrame:
    """Assemble per-sample executioner-loss components, continuous score, and binary call.

    Any of expr/cn/mut may be None (dataset lacks that layer); the score averages only
    the components that are available, and the manifest of which components contributed
    is recorded per sample so downstream code and figures stay honest.
    """
    ex = CFG["panels"]["executioners"]
    idx = samples
    frames = []
    if idx is None:
        for src in (expr, cn):
            if src is not None:
                idx = src.index if idx is None else idx.union(src.index)
    if idx is None and mut is not None:
        idx = pd.Index(mut[mut_cols["sample"]].unique())
    idx = pd.Index([] if idx is None else idx, name="sample")

    comp = pd.DataFrame(index=idx)
    used = []
    if expr is not None:
        comp["expr_low"] = expression_low_both(expr, ex, quantile).reindex(idx)
        used.append("expression")
    if cn is not None:
        comp["cn_del"] = cn_deep_deletion(cn, ex).reindex(idx).fillna(False).astype(bool)
        used.append("cn")
    if mut is not None and mut_cols is not None:
        m = mutation_lof(mut, mut_cols["gene"], mut_cols["sample"],
                         mut_cols["cls"], ex).reindex(idx).fillna(False)
        comp["mut_lof"] = m.astype(bool)
        used.append("mutation")

    comp = comp.fillna(False)
    bool_cols = [c for c in ["mut_lof", "cn_del", "expr_low"] if c in comp.columns]
    # continuous score = fraction of available components that fire (0..1)
    comp["executioner_loss_score"] = comp[bool_cols].mean(axis=1) if bool_cols else np.nan
    comp["executioner_loss_call"] = comp[bool_cols].any(axis=1) if bool_cols else False
    comp["components_used"] = ",".join(used)
    return comp


if __name__ == "__main__":
    print("Executioner panel:", panel("executioners"))
    print("Guardians:", panel("guardians"))
    print("Signature genes:", all_signature_genes())
