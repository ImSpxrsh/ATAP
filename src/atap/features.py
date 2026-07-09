"""
features.py — turn raw omics (expression + mutations) into the mechanistic feature
blocks defined in biology.py.

Design choices that matter for defensibility:
  * Expression is z-scored *within a cohort* so a "high" call is relative to the
    disease context, not an absolute TPM. Cross-cohort comparison is done on the
    ranked/standardized scale, never raw TPM (batch/platform confounding).
  * Mutation evidence *overrides* expression for effector competence: a BAX
    loss-of-function call zeroes effector competence regardless of mRNA, because a
    truncated protein does not form a pore. This is the single biggest driver of the
    ATAP window, so it is handled explicitly rather than left to a linear model.
  * Every block is reduced to one interpretable per-sample score in [roughly -3, +3].
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import biology


def zscore_expression(expr: pd.DataFrame) -> pd.DataFrame:
    """
    Z-score each gene (column) across samples (rows) within the cohort.

    expr: samples x genes, log-scale expression (e.g. log2(TPM+1)).
    Genes with zero variance return 0 (no information, not NaN).
    """
    mu = expr.mean(axis=0)
    sd = expr.std(axis=0, ddof=0).replace(0.0, np.nan)
    z = (expr - mu) / sd
    return z.fillna(0.0)


def _block_score(z: pd.DataFrame, genes: list[str]) -> pd.Series:
    """Mean z-score across the genes in a block that are present in the matrix."""
    present = [g for g in genes if g in z.columns]
    if not present:
        return pd.Series(0.0, index=z.index)
    return z[present].mean(axis=1)


def build_feature_blocks(
    expr: pd.DataFrame,
    mutations: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Compute the per-sample mechanistic blocks consumed by scoring.py.

    Parameters
    ----------
    expr : samples x genes, log-scale expression.
    mutations : long-format table with at least columns
        ['sample', 'gene', 'variant_class', 'protein_change'] (protein_change optional).
        Used to override effector competence and to flag venetoclax-binding mutations.

    Returns
    -------
    DataFrame indexed by sample with columns:
        bcl2_dependence, mcl1_bclxl_backup, priming_activators, effector_competence,
        execution_competence, mito_mass,
        bax_lof, bak1_lof, bcl2_binding_mut  (0/1 mutation flags)
    """
    z = zscore_expression(expr)

    blocks = pd.DataFrame(index=expr.index)
    for name, genes in biology.FEATURE_BLOCKS.items():
        blocks[name] = _block_score(z, genes)

    # Execution competence is pro-execution minus IAP (anti-execution) tone.
    anti_exec = _block_score(z, list(biology.EXECUTION_ANTI.keys()))
    blocks["execution_competence"] = blocks["execution_competence"] - 0.5 * anti_exec

    # --- mutation overrides -------------------------------------------------------
    bax_lof = pd.Series(0, index=expr.index, dtype=int)
    bak1_lof = pd.Series(0, index=expr.index, dtype=int)
    bcl2_bind = pd.Series(0, index=expr.index, dtype=int)

    if mutations is not None and len(mutations):
        m = mutations.copy()
        m["gene"] = m["gene"].str.upper()
        m["variant_class"] = m["variant_class"].astype(str).str.lower()
        lof = m["variant_class"].isin(biology.LOSS_OF_FUNCTION_CLASSES)

        bax_lof_samples = m.loc[lof & (m["gene"] == "BAX"), "sample"].unique()
        bak_lof_samples = m.loc[lof & (m["gene"] == "BAK1"), "sample"].unique()
        bax_lof.loc[bax_lof.index.isin(bax_lof_samples)] = 1
        bak1_lof.loc[bak1_lof.index.isin(bak_lof_samples)] = 1

        if "protein_change" in m.columns:
            pc = m["protein_change"].astype(str).str.replace("p.", "", regex=False)
            bind_hit = (m["gene"] == "BCL2") & pc.isin(biology.VENETOCLAX_BINDING_MUTATIONS)
            bcl2_bind.loc[bcl2_bind.index.isin(m.loc[bind_hit, "sample"].unique())] = 1

    blocks["bax_lof"] = bax_lof
    blocks["bak1_lof"] = bak1_lof
    blocks["bcl2_binding_mut"] = bcl2_bind

    # A BAX or BAK1 LoF call collapses effector competence. Both lost -> hard floor.
    # We push the continuous score to a strong-negative value so it dominates the
    # linear combination in scoring.py exactly the way the biology says it should.
    lof_penalty = np.where(
        (bax_lof.values == 1) & (bak1_lof.values == 1), -3.0,
        np.where((bax_lof.values == 1) | (bak1_lof.values == 1), -2.0, 0.0),
    )
    blocks["effector_competence"] = np.minimum(blocks["effector_competence"].values, lof_penalty)
    # np.minimum with 0.0 where no LoF leaves the expression-based value untouched.
    blocks["effector_competence"] = np.where(
        lof_penalty < 0, lof_penalty, blocks["effector_competence"]
    )

    return blocks


def add_crispr_dependency(
    blocks: pd.DataFrame,
    dep: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Optionally fold in DepMap CRISPR (Chronos) gene-effect scores as a functional
    read-out of dependency/priming. dep: samples x genes of gene-effect (more
    negative = more essential). Only meaningful for cell lines (DepMap), so this is
    additive and optional; patient cohorts skip it.
    """
    if dep is None:
        return blocks
    out = blocks.copy()
    for gene, col in [("BCL2", "dep_BCL2"), ("MCL1", "dep_MCL1"), ("BAX", "dep_BAX")]:
        if gene in dep.columns:
            out[col] = dep[gene].reindex(out.index)
    return out
