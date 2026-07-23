"""
calibration.py — issue #12: calibration and uncertainty quantification for the composite score.

A susceptibility score that outputs a ranking should (a) be calibrated — when it says a line is
in the top efficacy bin, that bin should actually contain more sensitive lines — and (b) carry
uncertainty. This is also a genuinely computational-only contribution (uncertainty-aware
prediction) a wet lab cannot produce.

What this does, on DepMap heme × GDSC2 venetoclax (local, reproducible):
  1. CALIBRATION CURVE. Predicted = composite `venetoclax_pct` in [0,1] (higher = predicted more
     venetoclax-sensitive). Observed = binary sensitivity (GDSC AUC below cohort median). Bin by
     predicted quintile; plot observed sensitive-fraction vs mean predicted, with per-bin
     bootstrap CIs and the y=x reference.
  2. CALIBRATION METRICS with bootstrap CIs: Brier score, Expected Calibration Error (ECE),
     and a Platt calibration slope/intercept (logistic fit of outcome on predicted logit;
     slope≈1 & intercept≈0 = well calibrated).
  3. UNCERTAINTY on performance: bootstrap CIs on the score→response Spearman rho and on the
     discrimination AUC.

Uncertainty-propagation note: the composite is deterministic given expression, so its
per-line point value has no sampling noise of its own; the reported uncertainty is COHORT
(finite-sample) uncertainty, propagated by resampling cell lines (nonparametric bootstrap,
seeded). That is the honest uncertainty a ranking of this many lines actually carries.

GUARDRAILS: real data; no efficacy claim; seeded. Run: PYTHONPATH=src python src/analysis/calibration.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from atap import data, features, scoring  # noqa: E402

CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
SEED = CFG.get("seed", 20260710)
GDSC = ROOT / "data" / "raw" / "gdsc" / "GDSC2_fitted_dose_response.xlsx"
OUT_T = ROOT / "outputs" / "tables"
OUT_L = ROOT / "outputs" / "logs"
N_BOOT = 2000
N_BINS = 5


def _ece(pred, obs, bins=N_BINS):
    edges = np.linspace(0, 1, bins + 1)
    e, n = 0.0, len(obs)
    for i in range(bins):
        m = (pred >= edges[i]) & (pred < edges[i + 1] if i < bins - 1 else pred <= edges[i + 1])
        if m.sum():
            e += m.sum() / n * abs(obs[m].mean() - pred[m].mean())
    return e


def _platt(pred, obs):
    """slope/intercept of logistic(obs) ~ logit(pred). slope 1 / intercept 0 = calibrated."""
    eps = 1e-6
    logit = np.log(np.clip(pred, eps, 1 - eps) / (1 - np.clip(pred, eps, 1 - eps)))
    lr = LogisticRegression(C=1e6, solver="lbfgs").fit(logit.reshape(-1, 1), obs)
    return float(lr.coef_[0, 0]), float(lr.intercept_[0])


def _boot(fn, *arrs, n=N_BOOT):
    rng = np.random.default_rng(SEED + 1)
    idx = np.arange(len(arrs[0]))
    out = []
    for _ in range(n):
        b = rng.choice(idx, len(idx), replace=True)
        try:
            v = fn(*[a[b] for a in arrs])
            if v is not None and np.isfinite(v):
                out.append(v)
        except Exception:  # noqa: BLE001
            continue
    return float(np.nanpercentile(out, 2.5)), float(np.nanpercentile(out, 97.5))


def _drug_response(gdsc, drug):
    d = gdsc[gdsc["DRUG_NAME"].astype(str).str.contains(drug, case=False, na=False)]
    return d.groupby("SANGER_MODEL_ID")[["LN_IC50", "AUC"]].median()


def main() -> None:
    co = data.load_depmap(heme_only=True)
    blocks = features.build_feature_blocks(co.expr, co.mutations)
    sc = scoring.SusceptibilityModel().score(blocks)
    model = pd.read_csv(ROOT / "data" / "raw" / "depmap" / "Model.csv").set_index("ModelID")
    pred = pd.DataFrame({"venetoclax_pct": sc["venetoclax_pct"].values}, index=co.expr.index)
    pred["SangerModelID"] = model["SangerModelID"].reindex(pred.index).values
    pred = pred.dropna(subset=["SangerModelID"]).set_index("SangerModelID")

    gdsc = pd.read_excel(GDSC)
    resp = _drug_response(gdsc, "Venetoclax")
    j = pred.join(resp, how="inner").dropna(subset=["AUC", "venetoclax_pct"])
    p = j["venetoclax_pct"].to_numpy(float)
    # observed sensitivity: GDSC AUC below cohort median (lower AUC = more killing)
    obs = (j["AUC"].to_numpy(float) < np.median(j["AUC"])).astype(float)
    n = len(j)

    # ---- calibration curve (quintiles) with per-bin bootstrap CI ----
    q = pd.qcut(p, N_BINS, labels=False, duplicates="drop")
    rows = []
    for b in sorted(pd.unique(q)):
        m = q == b
        pm, om = p[m], obs[m]
        lo, hi = _boot(lambda o: o.mean(), om, n=1000)
        rows.append(dict(bin=int(b), n=int(m.sum()), mean_pred=round(pm.mean(), 3),
                         obs_sensitive=round(om.mean(), 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3)))
    curve = pd.DataFrame(rows)
    OUT_T.mkdir(parents=True, exist_ok=True); OUT_L.mkdir(parents=True, exist_ok=True)
    curve.to_csv(OUT_T / "M13_calibration_curve.csv", index=False)

    # ---- metrics + bootstrap CIs ----
    brier = brier_score_loss(obs, p)
    ece = _ece(p, obs)
    slope, intercept = _platt(p, obs)
    rho = spearmanr(p, obs).statistic
    auc = roc_auc_score(obs, p)
    brier_ci = _boot(lambda pp, oo: brier_score_loss(oo, pp), p, obs)
    ece_ci = _boot(lambda pp, oo: _ece(pp, oo), p, obs)
    rho_ci = _boot(lambda pp, oo: spearmanr(pp, oo).statistic, p, obs)
    auc_ci = _boot(lambda pp, oo: roc_auc_score(oo, pp) if len(np.unique(oo)) > 1 else np.nan, p, obs)
    slope_ci = _boot(lambda pp, oo: _platt(pp, oo)[0], p, obs)

    summary = dict(n=n, brier=round(brier, 3), brier_ci=[round(x, 3) for x in brier_ci],
                   ece=round(ece, 3), ece_ci=[round(x, 3) for x in ece_ci],
                   calib_slope=round(slope, 3), calib_slope_ci=[round(x, 3) for x in slope_ci],
                   calib_intercept=round(intercept, 3),
                   spearman=round(rho, 3), spearman_ci=[round(x, 3) for x in rho_ci],
                   auc=round(auc, 3), auc_ci=[round(x, 3) for x in auc_ci], seed=SEED)
    pd.Series(summary).to_json(OUT_L / "M13_calibration_summary.json", indent=2)

    print(f"CALIBRATION & UNCERTAINTY — composite venetoclax_pct vs observed sensitivity (n={n})\n")
    print("Reliability (predicted vs observed sensitive-fraction, quintiles):")
    print(curve.to_string(index=False))
    print(f"\nBrier={brier:.3f} CI{[round(x,3) for x in brier_ci]}  "
          f"ECE={ece:.3f} CI{[round(x,3) for x in ece_ci]}")
    print(f"Calibration slope={slope:.2f} CI{[round(x,2) for x in slope_ci]} (1=ideal), "
          f"intercept={intercept:.2f} (0=ideal)")
    print(f"Discrimination: Spearman={rho:+.3f} CI{[round(x,3) for x in rho_ci]}  "
          f"AUC={auc:.3f} CI{[round(x,3) for x in auc_ci]}")
    print("\nHONEST READ: discrimination (ranking) and calibration are separate. A good AUC with a")
    print("slope far from 1 means the ranking is useful but the score values are not literal")
    print("probabilities. Bins are small (~n/5) so per-bin CIs are wide — stated, not hidden.")
    _make_figure(curve, summary)


def _make_figure(curve, summary):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:  # noqa: BLE001
        print(f"(figure skipped: {e})"); return
    fig, ax = plt.subplots(figsize=(5.2, 5.0))
    ax.plot([0, 1], [0, 1], ls="--", color="#999999", lw=1.2, label="perfect calibration")
    yerr = [curve["obs_sensitive"] - curve["ci_lo"], curve["ci_hi"] - curve["obs_sensitive"]]
    ax.errorbar(curve["mean_pred"], curve["obs_sensitive"], yerr=yerr, fmt="o-",
                color="#0072B2", ecolor="#0072B2", capsize=3, lw=1.6, label="composite (95% CI)")
    ax.set_xlabel("mean predicted venetoclax_pct (per quintile)")
    ax.set_ylabel("observed fraction venetoclax-sensitive")
    ax.set_title(f"Calibration — composite score (n={summary['n']})\n"
                 f"slope={summary['calib_slope']} (1=ideal), AUC={summary['auc']}, ECE={summary['ece']}")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.legend(loc="upper left", fontsize=8, frameon=False)
    fig.tight_layout()
    (ROOT / "figures").mkdir(exist_ok=True)
    (ROOT / "outputs" / "figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(ROOT / "figures" / "calibration_curve.svg")
    fig.savefig(ROOT / "outputs" / "figures" / "calibration_curve.png", dpi=150)
    print("Saved: figures/calibration_curve.svg + outputs/figures/calibration_curve.png")


if __name__ == "__main__":
    main()
