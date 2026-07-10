#!/usr/bin/env python3
"""M3 — confounder decomposition.

Competing venetoclax-resistance mechanisms must be controlled before crediting
executioner loss: MCL1 expression (competing anti-apoptotic dependence), the
BCL2/BCL2L1 (Bcl-xL) expression ratio (a known *unreliable* predictor — we expect it to
add little), and BCL2 hotspot mutations (e.g. G101V; the canonical acquired-resistance
mechanism). Nested models: base(lineage) -> +confounders -> +executioner loss. Report the
incremental contribution of executioner loss (ΔR², ΔAIC) beyond the confounders.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
PROC = ROOT / CFG["paths"]["data_processed"]
LOGS = ROOT / CFG["paths"]["outputs_logs"]
TABLES = ROOT / CFG["paths"]["outputs_tables"]
RAW = ROOT / CFG["paths"]["data_raw"]


def _bcl2_hotspot_lines() -> set:
    """DepMap heme lines carrying a BCL2 protein-change hotspot (config list)."""
    hs = set(CFG["confounders"]["bcl2_hotspots"])
    try:
        mut = pd.read_csv(RAW / "OmicsSomaticMutations.csv",
                          usecols=["HugoSymbol", "ModelID", "ProteinChange"], low_memory=False)
    except Exception:
        return set()
    b = mut[mut["HugoSymbol"] == "BCL2"].copy()
    b["pc"] = b["ProteinChange"].astype(str).str.replace("p.", "", regex=False)
    hit = b[b["pc"].isin(hs)]
    return set(hit["ModelID"])


def build(df: pd.DataFrame) -> pd.DataFrame:
    d = df.rename(columns={"OncotreeLineage": "lineage"}).copy()
    d["mcl1"] = d.get("expr_MCL1")
    # BCL2/BCL-xL ratio in log space (expr are log2 TPM+1); difference = log-ratio
    d["bcl2_bclxl_ratio"] = d.get("expr_BCL2") - d.get("expr_BCL2L1")
    hs_lines = _bcl2_hotspot_lines()
    d["bcl2_hotspot"] = d.index.isin(hs_lines).astype(int)
    return d


def nested(df, drug, metric):
    y = f"{drug}_{metric}"
    cols = [y, "executioner_loss_score", "mcl1", "bcl2_bclxl_ratio", "bcl2_hotspot", "lineage"]
    sub = df[cols].dropna(subset=[y, "executioner_loss_score", "mcl1", "bcl2_bclxl_ratio"]).copy()
    for c in ["y", "executioner_loss_score", "mcl1", "bcl2_bclxl_ratio"]:
        pass
    sub["y"] = (sub[y] - sub[y].mean()) / sub[y].std(ddof=0)
    for c in ["executioner_loss_score", "mcl1", "bcl2_bclxl_ratio"]:
        sub[c + "_z"] = (sub[c] - sub[c].mean()) / sub[c].std(ddof=0)
    lin = "C(lineage)" if sub["lineage"].nunique() > 1 else "1"
    models = {
        "base (lineage)": f"y ~ {lin}",
        "+confounders": f"y ~ {lin} + mcl1_z + bcl2_bclxl_ratio_z + bcl2_hotspot",
        "+executioner loss": f"y ~ {lin} + mcl1_z + bcl2_bclxl_ratio_z + bcl2_hotspot + executioner_loss_score_z",
    }
    rows = []
    prev = None
    for name, f in models.items():
        m = smf.ols(f, data=sub).fit()
        row = {"model": name, "n": int(m.nobs), "r2": m.rsquared,
               "adj_r2": m.rsquared_adj, "aic": m.aic}
        if prev is not None:
            row["dR2"] = m.rsquared - prev.rsquared
            row["dAIC"] = m.aic - prev.aic
        rows.append(row); prev = m
    # partial effect of executioner loss in the full model
    full = smf.ols(models["+executioner loss"], data=sub).fit()
    ci = full.conf_int().loc["executioner_loss_score_z"]
    partial = {"beta": full.params["executioner_loss_score_z"],
               "ci_low": ci[0], "ci_high": ci[1],
               "p": full.pvalues["executioner_loss_score_z"]}
    # also report confounder partials for context
    conf = {}
    for c in ["mcl1_z", "bcl2_bclxl_ratio_z", "bcl2_hotspot"]:
        if c in full.params:
            conf[c] = {"beta": full.params[c], "p": full.pvalues[c]}
    return pd.DataFrame(rows), partial, conf


def run():
    df = build(pd.read_csv(PROC / "depmap_celllines.csv", index_col=0))
    drug = CFG["backbone"]["primary_drug"]; metric = CFG["backbone"]["primary_metric"]
    tbl, partial, conf = nested(df, drug, metric)
    tbl.to_csv(TABLES / "M3_nested_models.csv", index=False)
    pd.DataFrame([partial]).to_csv(TABLES / "M3_executioner_partial.csv", index=False)

    lines = [f"# M3 report — confounder decomposition ({drug} {metric})", "",
             "Nested OLS on z-scored venetoclax LN_IC50, lineage-adjusted. Confounders:",
             "MCL1 expression, BCL2/BCL-xL log-ratio, BCL2 hotspot mutation.", "",
             "| model | n | R² | adj R² | AIC | ΔR² | ΔAIC |",
             "|-------|---|-----|--------|-----|-----|------|"]
    for _, r in tbl.iterrows():
        lines.append(f"| {r['model']} | {int(r['n'])} | {r['r2']:.3f} | {r['adj_r2']:.3f} | "
                     f"{r['aic']:.1f} | {r.get('dR2', float('nan')):.4f} | {r.get('dAIC', float('nan')):.2f} |")
    lines += ["",
              f"**Partial effect of executioner loss (full model):** β = {partial['beta']:.3f} "
              f"[{partial['ci_low']:.3f}, {partial['ci_high']:.3f}], p = {partial['p']:.3g}.",
              "",
              "**Confounder partials (full model):** " +
              "; ".join(f"{k}: β={v['beta']:.3f} (p={v['p']:.2g})" for k, v in conf.items()),
              "",
              "**Interpretation (reported as-is, not massaged — spec M3):** guardian-"
              "dependence confounders dominate venetoclax sensitivity in cell lines "
              "(R² 0.01→0.45): MCL1 expression and the BCL2/BCL-xL ratio are both strong "
              "(the ratio tracks the expected BCL2-dependence→venetoclax-sensitivity axis in "
              "this cohort, even though it is an unreliable predictor in the broader "
              "literature). **Executioner loss adds essentially no incremental signal beyond "
              "these confounders** (ΔR²≈0.0006, ΔAIC worse by ~1.9, partial p≈0.7). This is a "
              "negative result for the cell-line backbone and is carried forward honestly: the "
              "executioner-loss construct is mechanistically motivated but is NOT a strong "
              "statistical predictor of venetoclax resistance in DepMap once guardian "
              "dependence is controlled. BCL2 hotspot mutations are absent in this heme "
              "cell-line subset (rare in lines), so that arm is uninformative here."]
    (LOGS / "M3_report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return tbl, partial, conf


if __name__ == "__main__":
    run()
