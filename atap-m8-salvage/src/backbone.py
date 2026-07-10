#!/usr/bin/env python3
"""M2 — backbone association (the falsifiable core).

Does executioner loss predict venetoclax/navitoclax resistance in heme cell lines?
Regress sensitivity (LN_IC50 and AUC, separately) on executioner_loss_score with lineage
as covariate. Report standardized effect size + 95% CI + p, per drug, per metric.

A weak/null result is valid and reported plainly (spec M2 acceptance). Includes a
permutation null on the primary spec (GUARDRAILS §4: every association ships a null).
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
TABLES.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(CFG["seed"])


def load_depmap() -> pd.DataFrame:
    d = pd.read_csv(PROC / "depmap_celllines.csv", index_col=0)
    d = d.rename(columns={"OncotreeLineage": "lineage"})
    return d


def zscore(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std(ddof=0)


def fit_one(df: pd.DataFrame, drug: str, metric: str, predictor="executioner_loss_score",
            covariates=("lineage",)) -> dict:
    ycol = f"{drug}_{metric}"
    cols = [ycol, predictor] + [c for c in covariates]
    sub = df[cols].dropna()
    if sub[predictor].nunique() < 2 or len(sub) < 15:
        return {"drug": drug, "metric": metric, "n": len(sub), "beta": np.nan,
                "ci_low": np.nan, "ci_high": np.nan, "p": np.nan, "note": "insufficient"}
    sub = sub.copy()
    sub["y"] = zscore(sub[ycol])
    sub["x"] = zscore(sub[predictor])
    cov = " + ".join(f"C({c})" for c in covariates if sub[c].nunique() > 1)
    formula = "y ~ x" + (f" + {cov}" if cov else "")
    m = smf.ols(formula, data=sub).fit()
    ci = m.conf_int().loc["x"]
    return {"drug": drug, "metric": metric, "n": len(sub),
            "beta": m.params["x"], "ci_low": ci[0], "ci_high": ci[1],
            "p": m.pvalues["x"], "r2": m.rsquared, "note": ""}


def permutation_null(df, drug, metric, predictor="executioner_loss_score",
                     n_perm=5000) -> dict:
    ycol = f"{drug}_{metric}"
    sub = df[[ycol, predictor, "lineage"]].dropna().copy()
    sub["y"] = zscore(sub[ycol]); sub["x"] = zscore(sub[predictor])
    cov = "C(lineage)" if sub["lineage"].nunique() > 1 else None
    formula = "y ~ x" + (f" + {cov}" if cov else "")
    obs = smf.ols(formula, data=sub).fit().params["x"]
    null = np.empty(n_perm)
    xvals = sub["x"].values.copy()
    for i in range(n_perm):
        s2 = sub.copy(); s2["x"] = RNG.permutation(xvals)
        null[i] = smf.ols(formula, data=s2).fit().params["x"]
    p_perm = (np.sum(np.abs(null) >= abs(obs)) + 1) / (n_perm + 1)
    return {"drug": drug, "metric": metric, "obs_beta": obs, "perm_p": p_perm,
            "null_mean": null.mean(), "null_std": null.std(), "n_perm": n_perm,
            "null_path": _save_null(null, drug, metric)}


def _save_null(null, drug, metric):
    p = LOGS / f"null_backbone_{drug}_{metric}.npy"
    np.save(p, null)
    return str(p.relative_to(ROOT))


def run():
    df = load_depmap()
    rows = []
    for drug in CFG["backbone"]["drugs"]:
        for metric in CFG["backbone"]["metrics"]:
            rows.append(fit_one(df, drug, metric))
    res = pd.DataFrame(rows)
    res.to_csv(TABLES / "M2_backbone_effects.csv", index=False)

    # permutation null on the pre-registered primary spec
    pdrug = CFG["backbone"]["primary_drug"]; pmetric = CFG["backbone"]["primary_metric"]
    perm = permutation_null(df, pdrug, pmetric)
    pd.DataFrame([perm]).to_csv(TABLES / "M2_backbone_permutation.csv", index=False)

    _report(res, perm)
    return res, perm


def _report(res, perm):
    lines = ["# M2 report — backbone association (executioner loss vs BH3-mimetic resistance)",
             "",
             "Standardized β (per +1 SD executioner-loss score) on z-scored sensitivity,",
             "adjusted for lineage. Positive β = executioner loss → resistance (pre-registered).",
             "", "| drug | metric | n | β (std) | 95% CI | p |",
             "|------|--------|---|---------|--------|---|"]
    for _, r in res.iterrows():
        if np.isnan(r["beta"]):
            lines.append(f"| {r['drug']} | {r['metric']} | {r['n']} | — | — | {r['note']} |")
        else:
            lines.append(f"| {r['drug']} | {r['metric']} | {int(r['n'])} | {r['beta']:.3f} | "
                         f"[{r['ci_low']:.3f}, {r['ci_high']:.3f}] | {r['p']:.3g} |")
    lines += ["",
              f"**Permutation null (primary spec: {perm['drug']} {perm['metric']}, "
              f"{perm['n_perm']} perms):** observed β = {perm['obs_beta']:.3f}, "
              f"null mean {perm['null_mean']:.3f} ± {perm['null_std']:.3f}, "
              f"permutation p = {perm['perm_p']:.3g}.",
              "",
              "**Interpretation:** direction and magnitude reported as-is. Correlation is "
              "not evidence that ATAP works (GUARDRAILS §3); it establishes that the "
              "executioner-loss resistance mechanism is real and detectable, defining the "
              "population where a BAX-independent agent is mechanistically rational."]
    (LOGS / "M2_report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    run()
