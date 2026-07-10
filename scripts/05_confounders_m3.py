"""
05_confounders_m3.py — M3 confounder decomposition on real BeatAML patients.

The M2 backbone showed the mechanistic venetoclax axis tracks real venetoclax ex-vivo
resistance. M3 asks the harder, honest question required by GUARDRAILS.md #4: does the
EXECUTIONER state (BAX/BAK) add signal BEYOND the known competing resistance mechanisms?

Nested linear models predicting venetoclax ex-vivo AUC (higher = resistant), all on the
same real BeatAML cohort (cBioPortal expression + BeatAML2 AUC, joined on BA barcode):

    base   : intercept only
    +conf  : + MCL1 expression, + BCL2:BCL2L1 (Bcl-xL) ratio, + BCL2 gatekeeper-mut flag
    +exec  : + executioner state (mean BAX/BAK1 expression, z-scored)

Reports R^2 and AIC at each step, the incremental dR^2 / dAIC from adding executioner
state, its standardized partial coefficient, and a permutation null (shuffle the
executioner variable, refit, 2000 draws). A near-zero increment is a valid, reportable
result and is not to be massaged (GUARDRAILS.md).

No efficacy claim: this concerns prediction of venetoclax RESISTANCE only.
Run:  .venv/bin/python scripts/05_confounders_m3.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from atap import biology, data, features, scoring  # noqa: E402

AUC_PATH = ROOT / "data" / "raw" / "beataml" / "beataml_probit_curve_fits_v4.txt"
SEED = 7
GATEKEEPER = biology.VENETOCLAX_BINDING_MUTATIONS  # G101V family


def _ba(x):
    m = re.search(r"(BA\d+)", str(x))
    return m.group(1) if m else None


def _z(v):
    v = np.asarray(v, float)
    s = v.std()
    return (v - v.mean()) / s if s > 0 else v * 0.0


def _ols_r2_aic(X, y):
    """Fit OLS with intercept via lstsq; return (r2, aic, beta)."""
    Xd = np.column_stack([np.ones(len(y)), X]) if X.size else np.ones((len(y), 1))
    beta, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    resid = y - Xd @ beta
    rss = float(resid @ resid)
    tss = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - rss / tss if tss > 0 else 0.0
    n, k = len(y), Xd.shape[1]
    aic = n * np.log(rss / n) + 2 * k
    return r2, aic, beta


def main() -> None:
    auc = (pd.read_csv(AUC_PATH, sep="\t", low_memory=False)
           .query("inhibitor.str.fullmatch('Venetoclax', case=False, na=False)", engine="python"))
    auc["ba"] = auc["dbgap_rnaseq_sample"].map(_ba)
    auc = auc.dropna(subset=["ba"]).groupby("ba")["auc"].median()

    co = data.load_cbioportal("aml_ohsu_2022")
    blocks = features.build_feature_blocks(co.expr, co.mutations)
    sc = scoring.SusceptibilityModel().score(blocks)

    # Confounder + executioner variables, all real, aligned to cBioPortal sample index.
    df = pd.DataFrame(index=co.expr.index)
    df["mcl1"] = co.expr["MCL1"] if "MCL1" in co.expr else np.nan
    ratio_ok = {"BCL2", "BCL2L1"} <= set(co.expr.columns)
    df["bcl2_bclxl_ratio"] = (co.expr["BCL2"] - co.expr["BCL2L1"]) if ratio_ok else np.nan  # log-space diff = log ratio
    gk = co.mutations[(co.mutations.gene == "BCL2") &
                      (co.mutations.protein_change.astype(str).isin(GATEKEEPER))]["sample"].unique()
    df["bcl2_gatekeeper"] = df.index.isin(gk).astype(float)
    df["exec_state"] = blocks["effector_competence"]  # BAX/BAK (z-scored mean, low = executioner loss)

    df["ba"] = [_ba(i) for i in df.index]
    df = df.dropna(subset=["ba"]).drop_duplicates("ba").set_index("ba")
    j = df.join(auc.rename("auc"), how="inner").dropna(subset=["mcl1", "bcl2_bclxl_ratio", "exec_state"])
    y = j["auc"].values.astype(float)
    n = len(j)
    print(f"M3 confounder decomposition — BeatAML n={n} (real expression + venetoclax AUC)")
    ng = int(j["bcl2_gatekeeper"].sum())
    print(f"BCL2 gatekeeper mutations in cohort: {ng}"
          + ("  (all-zero -> dropped from model)" if ng == 0 else ""))

    conf_cols = ["mcl1", "bcl2_bclxl_ratio"] + (["bcl2_gatekeeper"] if ng > 0 else [])
    Xconf = np.column_stack([_z(j[c]) for c in conf_cols])
    Xfull = np.column_stack([Xconf, _z(j["exec_state"])])

    r2_base, aic_base, _ = _ols_r2_aic(np.empty((n, 0)), y)
    r2_conf, aic_conf, _ = _ols_r2_aic(Xconf, y)
    r2_full, aic_full, beta_full = _ols_r2_aic(Xfull, y)
    d_r2 = r2_full - r2_conf
    d_aic = aic_full - aic_conf  # negative = executioner term improves the model

    print("\nNested models predicting venetoclax AUC (higher = resistant):")
    print(f"  base (intercept)        R2={r2_base:.3f}  AIC={aic_base:.1f}")
    print(f"  +confounders {conf_cols}  R2={r2_conf:.3f}  AIC={aic_conf:.1f}")
    print(f"  +executioner state      R2={r2_full:.3f}  AIC={aic_full:.1f}")
    print(f"\n  incremental from executioner state: dR2={d_r2:+.3f}  dAIC={d_aic:+.1f} "
          f"(negative dAIC = real improvement)")
    print(f"  executioner standardized partial coef = {beta_full[-1]:+.3f} "
          f"(positive => lower BAX/BAK -> higher AUC -> more resistant, as predicted)")

    # Permutation null: shuffle executioner state, refit full model, null dR2.
    rng = np.random.default_rng(SEED)
    ev = _z(j["exec_state"]).copy()
    ge = 0
    for _ in range(2000):
        rng.shuffle(ev)
        r2p, _, _ = _ols_r2_aic(np.column_stack([Xconf, ev]), y)
        if (r2p - r2_conf) >= d_r2:
            ge += 1
    p = (ge + 1) / 2001
    print(f"  permutation p (executioner adds this much beyond confounders by chance) = {p:.4f}")

    # Also: partial Spearman of exec_state vs AUC controlling for confounders (residualized).
    def resid(v):
        Xd = np.column_stack([np.ones(n), Xconf])
        b, *_ = np.linalg.lstsq(Xd, v, rcond=None)
        return v - Xd @ b
    r_partial = spearmanr(resid(_z(j["exec_state"])), resid(y)).statistic
    print(f"  partial Spearman(exec_state, AUC | confounders) = {r_partial:+.3f}")
    print("\nGUARDRAIL: venetoclax-resistance prediction only; no ATAP efficacy claim.")


if __name__ == "__main__":
    main()
