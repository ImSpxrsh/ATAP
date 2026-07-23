"""
baselines.py — issue #10: baseline model battery with honest reporting.

Every claim of predictive value must be measured against a DUMB baseline, with the SAME metric
and the SAME cross-validation scheme. The single most credibility-enhancing thing here is to
show we tried to beat our own composite with something trivial — and report the result whatever
it is. Prior work already found BCL2 expression alone rivals/beats the hand-weighted composite;
this module makes that comparison formal, cross-validated, and front-and-centre.

Cohort: DepMap heme cell lines joined to GDSC2 venetoclax + navitoclax dose-response
(fully local, reproducible). Response: LN_IC50 / AUC (higher = more resistant).

Predictors compared (each a single per-line score):
  - composite            the pipeline's venetoclax_score (scoring.SusceptibilityModel)  [THE MODEL]
  - BCL2_alone           BCL2 expression z-score                                         [dumb baseline]
  - BCL2_minus_MCL1      BCL2 - MCL1 z (guardian dominance)                              [dumb baseline]
  - MCL1_over_BCL2L1     MCL1 - BCL2L1 z (log-ratio proxy; issue-requested)             [dumb baseline]
  - monocytic_signature  mean z of monocytic-differentiation markers                     [confound baseline]
  - random_feature       gaussian noise, many draws -> null envelope                     [floor]

Metric: cross-validated Spearman |rho| (repeated K-fold; predictors are precomputed, UNFITTED
scores, so CV quantifies out-of-fold stability and yields honest spread). Each also gets a
permutation p and a bootstrap CI on the full-sample rho. A predictor is only meaningful if it
clearly exceeds the random-feature envelope. No fitting to drug labels; no efficacy claim.

Run: PYTHONPATH=src python src/analysis/baselines.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import spearmanr
from sklearn.model_selection import RepeatedKFold

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from atap import data, features, scoring  # noqa: E402

CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
SEED = CFG.get("seed", 20260710)
GDSC = ROOT / "data" / "raw" / "gdsc" / "GDSC2_fitted_dose_response.xlsx"
DEPMAP_EXPR_FULL = ROOT / "data" / "raw" / "depmap" / "OmicsExpressionProteinCodingGenesTPMLogp1.csv"
OUT_T = ROOT / "outputs" / "tables"
MONO = CFG["monocytic_markers"]


def _load_monocytic(model_ids) -> pd.Series:
    """Mean z-score of monocytic-differentiation markers, read from the FULL DepMap
    expression matrix (panel-subset loader drops these genes). Returns per-ModelID score."""
    header = pd.read_csv(DEPMAP_EXPR_FULL, nrows=0).columns
    idcol = header[0]
    want = {idcol: idcol}
    for col in header[1:]:
        sym = col.split(" (")[0]
        if sym in MONO:
            want[col] = sym
    use = list(want.keys())
    df = pd.read_csv(DEPMAP_EXPR_FULL, usecols=use).rename(columns=want).set_index(idcol)
    df = df.reindex(model_ids).dropna(how="all")
    z = (df - df.mean()) / df.std(ddof=0)
    return z.mean(axis=1).rename("monocytic_signature")


def _cv_abs_rho(x, y, k=5, repeats=20):
    """Repeated K-fold out-of-fold Spearman |rho| (predictors unfitted). Returns
    (mean_abs_rho, lo, hi) over folds x repeats."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    rkf = RepeatedKFold(n_splits=k, n_repeats=repeats, random_state=SEED)
    vals = []
    for _, test in rkf.split(x):
        if len(test) >= 8 and np.ptp(x[test]) > 0:
            vals.append(abs(spearmanr(x[test], y[test]).statistic))
    vals = np.asarray(vals)
    return float(np.nanmean(vals)), float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))


def _full_rho(x, y):
    return float(spearmanr(x, y).statistic)


def _perm_p(x, y, obs, n=2000):
    rng = np.random.default_rng(SEED)
    yv = np.asarray(y, float).copy()
    ge = 0
    for _ in range(n):
        rng.shuffle(yv)
        if abs(spearmanr(x, yv).statistic) >= abs(obs):
            ge += 1
    return (ge + 1) / (n + 1)


def _boot_ci(x, y, n=2000):
    rng = np.random.default_rng(SEED + 1)
    x, y = np.asarray(x, float), np.asarray(y, float)
    idx = np.arange(len(x))
    rs = [spearmanr(x[b], y[b]).statistic for b in
          (rng.choice(idx, len(idx), replace=True) for _ in range(n))]
    return float(np.nanpercentile(rs, 2.5)), float(np.nanpercentile(rs, 97.5))


def _random_envelope(y, n=200):
    """95th-percentile |rho| achievable by pure gaussian noise on this response -> the floor
    a real predictor must clear."""
    rng = np.random.default_rng(SEED + 2)
    y = np.asarray(y, float)
    rs = [abs(spearmanr(rng.standard_normal(len(y)), y).statistic) for _ in range(n)]
    return float(np.mean(rs)), float(np.nanpercentile(rs, 95))


def _drug_response(gdsc, drug):
    d = gdsc[gdsc["DRUG_NAME"].astype(str).str.contains(drug, case=False, na=False)]
    return d.groupby("SANGER_MODEL_ID")[["LN_IC50", "AUC"]].median()


def main() -> None:
    co = data.load_depmap(heme_only=True)
    z = features.zscore_expression(co.expr)
    blocks = features.build_feature_blocks(co.expr, co.mutations)
    comp = scoring.SusceptibilityModel().score(blocks)["venetoclax_score"]
    mono = _load_monocytic(list(co.expr.index))

    preds = pd.DataFrame(index=co.expr.index)
    preds["composite"] = comp.values
    preds["BCL2_alone"] = z["BCL2"]
    preds["BCL2_minus_MCL1"] = z["BCL2"] - z["MCL1"]
    preds["MCL1_over_BCL2L1"] = z["MCL1"] - z["BCL2L1"]
    preds["monocytic_signature"] = mono.reindex(preds.index)

    model = pd.read_csv(ROOT / "data" / "raw" / "depmap" / "Model.csv").set_index("ModelID")
    preds["SangerModelID"] = model["SangerModelID"].reindex(preds.index).values
    preds = preds.dropna(subset=["SangerModelID"]).set_index("SangerModelID")

    gdsc = pd.read_excel(GDSC)
    predictor_cols = ["composite", "BCL2_alone", "BCL2_minus_MCL1",
                      "MCL1_over_BCL2L1", "monocytic_signature"]
    rows = []
    for drug in ("Venetoclax", "Navitoclax"):
        resp = _drug_response(gdsc, drug)
        for metric in ("LN_IC50", "AUC"):
            j = preds.join(resp[[metric]], how="inner").dropna(subset=[metric])
            y = j[metric]
            rmean, r95 = _random_envelope(y.values)
            for p in predictor_cols:
                sub = j[[p, metric]].dropna()
                if len(sub) < 20:
                    continue
                x, yy = sub[p].values, sub[metric].values
                rho = _full_rho(x, yy)
                cvm, cvlo, cvhi = _cv_abs_rho(x, yy)
                lo, hi = _boot_ci(x, yy)
                rows.append(dict(
                    drug=drug, metric=metric, predictor=p, n=len(sub),
                    full_rho=round(rho, 3), abs_rho=round(abs(rho), 3),
                    cv_abs_rho=round(cvm, 3), cv_lo=round(cvlo, 3), cv_hi=round(cvhi, 3),
                    boot_lo=round(lo, 3), boot_hi=round(hi, 3), perm_p=round(_perm_p(x, yy, rho), 4),
                    random_floor95=round(r95, 3),
                    beats_BCL2=None, above_random=abs(rho) > r95))
    res = pd.DataFrame(rows)

    # mark, per (drug,metric), whether each predictor beats the BCL2_alone baseline
    for (d, m), g in res.groupby(["drug", "metric"]):
        bcl2 = g.loc[g.predictor == "BCL2_alone", "abs_rho"]
        if bcl2.empty:
            continue
        b = bcl2.iloc[0]
        res.loc[g.index, "beats_BCL2"] = (g["abs_rho"] > b).values

    OUT_T.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT_T / "M12_baseline_battery.csv", index=False)

    # ---- honest narrative ----
    print("BASELINE BATTERY — composite vs dumb baselines (GDSC heme cell lines, CV Spearman |rho|)\n")
    for (d, m), g in res.groupby(["drug", "metric"]):
        g = g.set_index("predictor")
        rfloor = g["random_floor95"].iloc[0]
        n = int(g["n"].iloc[0])
        print(f"=== {d} {m}  (n={n}; random-noise 95% floor |rho|={rfloor}) ===")
        for p in predictor_cols:
            if p not in g.index:
                continue
            r = g.loc[p]
            flag = "  <-- THE MODEL" if p == "composite" else ""
            beat = "" if p == "BCL2_alone" else ("  beats-BCL2" if r["beats_BCL2"] else "  <BCL2")
            print(f"  {p:20s} full_rho={r['full_rho']:+.3f}  cv|rho|={r['cv_abs_rho']:.3f} "
                  f"[{r['cv_lo']:.3f},{r['cv_hi']:.3f}]  p={r['perm_p']:.4f}"
                  f"{'' if r['above_random'] else '  (~random!)'}{beat}{flag}")
        comp_beats = bool(g.loc['composite', 'beats_BCL2']) if 'composite' in g.index else None
        print(f"  -> composite beats BCL2_alone here: {comp_beats}\n")

    print("HONEST READ: report both directions. Where composite does NOT beat BCL2_alone, say so.")
    print("A predictor at/below the random 95% floor carries no real signal regardless of its p.")
    print(f"Saved: outputs/tables/M12_baseline_battery.csv (seed={SEED}). No efficacy claim.")

    _make_figure(res)


def _make_figure(res: pd.DataFrame) -> None:
    """Colorblind-safe comparison figure for the pre-registered primary spec
    (venetoclax LN_IC50): cv |rho| with fold-spread bars, random floor marked."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:  # noqa: BLE001
        print(f"(figure skipped: matplotlib unavailable: {e})")
        return
    g = res[(res.drug == "Venetoclax") & (res.metric == "LN_IC50")].set_index("predictor")
    order = ["composite", "BCL2_alone", "BCL2_minus_MCL1", "MCL1_over_BCL2L1", "monocytic_signature"]
    order = [p for p in order if p in g.index]
    # Okabe-Ito colorblind-safe: composite=blue, baselines=orange, confound=grey
    color = {"composite": "#0072B2", "BCL2_alone": "#E69F00", "BCL2_minus_MCL1": "#E69F00",
             "MCL1_over_BCL2L1": "#E69F00", "monocytic_signature": "#999999"}
    y = np.arange(len(order))
    vals = [g.loc[p, "cv_abs_rho"] for p in order]
    lo = [g.loc[p, "cv_abs_rho"] - g.loc[p, "cv_lo"] for p in order]
    hi = [g.loc[p, "cv_hi"] - g.loc[p, "cv_abs_rho"] for p in order]
    floor = g["random_floor95"].iloc[0]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.barh(y, vals, xerr=[lo, hi], color=[color[p] for p in order],
            edgecolor="black", linewidth=0.6, capsize=3, height=0.62)
    ax.axvline(floor, color="#D55E00", ls="--", lw=1.3, label=f"random-noise 95% floor ({floor:.2f})")
    ax.set_yticks(y); ax.set_yticklabels(order); ax.invert_yaxis()
    ax.set_xlabel("cross-validated Spearman |rho|  (higher = better predictor of venetoclax LN_IC50)")
    ax.set_title(f"Baseline battery — venetoclax, DepMap heme x GDSC2 (n={int(g['n'].iloc[0])})")
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    fig.tight_layout()
    figdir = ROOT / "figures"
    figdir.mkdir(exist_ok=True)
    fig.savefig(figdir / "baseline_comparison.svg")
    fig.savefig(ROOT / "outputs" / "figures" / "baseline_comparison.png", dpi=150)
    print("Saved: figures/baseline_comparison.svg + outputs/figures/baseline_comparison.png")


if __name__ == "__main__":
    main()
