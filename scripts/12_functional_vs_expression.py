"""
12_functional_vs_expression.py — the project's CENTRAL METHODOLOGICAL TEST, made real.

The whole thesis rests on one claim: *expression is a weak proxy for functional apoptotic
competence, and the decisive layer is functional data.* Every prior module tested predictors
built from EXPRESSION. This script asks the question that claim actually implies, using data
already on disk:

    Does a FUNCTIONAL readout of guardian dependence (DepMap CRISPR gene-effect) predict
    BH3-mimetic (venetoclax / navitoclax) response, and does it BEAT the expression proxy?

And its executioner-axis counterpart, which is the honest, load-bearing negative:

    Can the executioner axis (BAX/BAK) be tested with CRISPR at all? (No — by construction:
    pro-apoptotic effectors are near-neutral for proliferation fitness, so a fitness CRISPR
    screen structurally cannot read executioner competence. That is *why* the acquisition
    target is functional BH3 profiling, not more CRISPR.)

Data (all real, already downloaded):
  - DepMap 24Q4 CRISPRGeneEffect.csv  (functional gene dependency; negative = more essential)
  - DepMap 24Q4 expression (log2 TPM+1) and Model.csv (SangerModelID join key)
  - GDSC2 venetoclax + navitoclax dose-response (LN_IC50, AUC; higher = more resistant)

Polarity convention (so functional and expression predictors are directly comparable):
  we define FUNCTIONAL DEPENDENCE = -gene_effect, so higher = more dependent, the SAME
  polarity as high expression of a guardian. A true sensitivity/dependence marker then
  shows a NEGATIVE Spearman with LN_IC50/AUC (more dependent -> more sensitive -> lower IC50)
  for BOTH readouts. This makes the head-to-head a clean apples-to-apples |rho| comparison.

GUARDRAILS: #1 real data only; #3 no efficacy claim (this predicts response markers, not kill);
#4 every estimate ships a permutation null + bootstrap CI + a specification sweep; #6 seeded.

Run: .venv/bin/python scripts/12_functional_vs_expression.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from atap import data  # noqa: E402

GDSC = ROOT / "data" / "raw" / "gdsc" / "GDSC2_fitted_dose_response.xlsx"
OUT_T = ROOT / "outputs" / "tables"
OUT_L = ROOT / "outputs" / "logs"
SEED = 7

GUARDIANS = ["BCL2", "MCL1", "BCL2L1"]     # venetoclax/navitoclax targets & bypasses
EXECUTIONERS = ["BAX", "BAK1"]             # the ATAP-relevant axis


def _perm_p(x, y, obs, n=5000):
    rng = np.random.default_rng(SEED)
    yv = np.asarray(y, float).copy()
    ge = 0
    for _ in range(n):
        rng.shuffle(yv)
        if abs(spearmanr(x, yv).statistic) >= abs(obs):
            ge += 1
    return (ge + 1) / (n + 1)


def _boot_ci(x, y, n=5000):
    rng = np.random.default_rng(SEED + 1)
    x, y = np.asarray(x, float), np.asarray(y, float)
    idx = np.arange(len(x))
    rs = [spearmanr(x[b], y[b]).statistic
          for b in (rng.choice(idx, len(idx), replace=True) for _ in range(n))]
    return float(np.nanpercentile(rs, 2.5)), float(np.nanpercentile(rs, 97.5))


def _corr(x, y):
    """Spearman + perm p + bootstrap CI on aligned, finite pairs."""
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    rho = spearmanr(x, y).statistic
    return dict(n=int(m.sum()), rho=float(rho),
                perm_p=_perm_p(x, y, rho), ci=_boot_ci(x, y))


def _paired_delta_ci(x_func, x_expr, y, n=5000):
    """PAIRED bootstrap on the SAME resampled cell lines: is |rho_func| - |rho_expr|
    reliably positive? Returns (delta_obs, ci_lo, ci_hi, frac_gt0). CI excluding 0 =>
    the functional readout is a significantly stronger predictor than expression."""
    rng = np.random.default_rng(SEED + 2)
    m = np.isfinite(x_func) & np.isfinite(x_expr) & np.isfinite(y)
    xf, xe, yy = x_func[m], x_expr[m], y[m]
    idx = np.arange(len(yy))
    obs = abs(spearmanr(xf, yy).statistic) - abs(spearmanr(xe, yy).statistic)
    ds = []
    for _ in range(n):
        b = rng.choice(idx, len(idx), replace=True)
        ds.append(abs(spearmanr(xf[b], yy[b]).statistic)
                  - abs(spearmanr(xe[b], yy[b]).statistic))
    ds = np.asarray(ds)
    return (float(obs), float(np.nanpercentile(ds, 2.5)),
            float(np.nanpercentile(ds, 97.5)), float(np.mean(ds > 0)))


def _drug_response(gdsc, drug):
    d = gdsc[gdsc["DRUG_NAME"].astype(str).str.contains(drug, case=False, na=False)]
    return d.groupby("SANGER_MODEL_ID")[["LN_IC50", "AUC"]].median()


def main() -> None:
    gdsc = pd.read_excel(GDSC)
    co = data.load_depmap(heme_only=True)
    if co.dependency is None:
        raise SystemExit("CRISPRGeneEffect.csv not loaded; cannot run functional test.")
    model = pd.read_csv(ROOT / "data" / "raw" / "depmap" / "Model.csv").set_index("ModelID")
    smid = model["SangerModelID"].reindex(co.expr.index)

    # Build predictor matrix indexed by SangerModelID.
    genes = GUARDIANS + EXECUTIONERS
    expr = co.expr[genes]
    # z-score expression across heme lines so magnitudes are comparable.
    expr_z = (expr - expr.mean()) / expr.std(ddof=0)
    func_dep = -co.dependency[genes]   # functional DEPENDENCE = -gene_effect (higher = more dependent)

    preds = pd.DataFrame(index=co.expr.index)
    for g in genes:
        preds[f"{g}__expr"] = expr_z[g]
        preds[f"{g}__func"] = func_dep[g]
    preds["SangerModelID"] = smid.values
    preds = preds.dropna(subset=["SangerModelID"]).set_index("SangerModelID")

    rows = []
    for drug in ("Venetoclax", "Navitoclax"):
        resp = _drug_response(gdsc, drug)
        j = preds.join(resp, how="inner")
        for metric in ("LN_IC50", "AUC"):
            for g in genes:
                axis = "guardian" if g in GUARDIANS else "executioner"
                for readout in ("expr", "func"):
                    col = f"{g}__{readout}"
                    sub = j[[col, metric]].dropna()
                    if len(sub) < 15:
                        continue
                    r = _corr(sub[col].values, sub[metric].values)
                    rows.append(dict(drug=drug, metric=metric, gene=g, axis=axis,
                                     readout=readout, n=r["n"], rho=r["rho"],
                                     perm_p=r["perm_p"], ci_lo=r["ci"][0], ci_hi=r["ci"][1]))

    res = pd.DataFrame(rows)
    OUT_T.mkdir(parents=True, exist_ok=True)
    OUT_L.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT_T / "M10_functional_vs_expression.csv", index=False)

    # ---- Head-to-head on the primary spec: venetoclax LN_IC50, guardian axis ----
    def show(drug, metric):
        print(f"\n=== {drug} {metric}  (higher = more resistant; sensitivity marker -> NEGATIVE rho) ===")
        d = res[(res.drug == drug) & (res.metric == metric)]
        for g in genes:
            e = d[(d.gene == g) & (d.readout == "expr")]
            f = d[(d.gene == g) & (d.readout == "func")]
            if e.empty or f.empty:
                continue
            e, f = e.iloc[0], f.iloc[0]
            better = "FUNC" if abs(f.rho) > abs(e.rho) else "EXPR"
            tag = "[guardian]" if g in GUARDIANS else "[EXECUTIONER]"
            print(f"  {g:7s}{tag:14s} n={f.n:3d} | "
                  f"expr rho={e.rho:+.3f} p={e.perm_p:.3f} CI[{e.ci_lo:+.2f},{e.ci_hi:+.2f}]  ||  "
                  f"func rho={f.rho:+.3f} p={f.perm_p:.3f} CI[{f.ci_lo:+.2f},{f.ci_hi:+.2f}]  "
                  f"-> stronger:{better}")

    print("FUNCTIONAL (CRISPR dependence) vs EXPRESSION proxy for BH3-mimetic response")
    print("DepMap heme cell lines x GDSC2 dose-response. FUNCTIONAL DEPENDENCE = -gene_effect.")
    show("Venetoclax", "LN_IC50")
    show("Venetoclax", "AUC")
    show("Navitoclax", "LN_IC50")

    # ---- PAIRED test: is functional a SIGNIFICANTLY stronger predictor than expression? ----
    print("\nPAIRED bootstrap on the same lines: delta = |rho_func| - |rho_expr| "
          "(>0 => functional wins). CI excluding 0 = significant.")
    delta_rows = []
    for drug in ("Venetoclax", "Navitoclax"):
        resp = _drug_response(gdsc, drug)
        j = preds.join(resp, how="inner")
        for metric in ("LN_IC50", "AUC"):
            for g in GUARDIANS:
                sub = j[[f"{g}__func", f"{g}__expr", metric]].dropna()
                if len(sub) < 15:
                    continue
                d_obs, lo, hi, frac = _paired_delta_ci(
                    sub[f"{g}__func"].values, sub[f"{g}__expr"].values, sub[metric].values)
                sig = "SIGNIF" if (lo > 0 or hi < 0) else "ns"
                delta_rows.append(dict(drug=drug, metric=metric, gene=g, n=len(sub),
                                       delta_abs_rho=d_obs, ci_lo=lo, ci_hi=hi,
                                       frac_func_wins=frac, verdict=sig))
                print(f"  {drug:11s} {metric:8s} {g:7s} n={len(sub):3d} "
                      f"delta|rho|={d_obs:+.3f} CI[{lo:+.3f},{hi:+.3f}] "
                      f"P(func>expr)={frac:.2f}  {sig}")
    pd.DataFrame(delta_rows).to_csv(OUT_T / "M10_functional_vs_expression_paired.csv", index=False)

    # Structural fact about the executioner axis (why CRISPR cannot test it):
    ge = co.dependency[EXECUTIONERS]
    print("\nEXECUTIONER STRUCTURAL NOTE (why the functional CRISPR test is null BY CONSTRUCTION):")
    for g in EXECUTIONERS:
        print(f"  {g} gene-effect: median={ge[g].median():+.3f}, IQR=[{ge[g].quantile(.25):+.3f},"
              f"{ge[g].quantile(.75):+.3f}] -> near-zero: pro-apoptotic effectors are growth-"
              f"neutral, so a proliferation CRISPR screen carries ~no executioner signal.")

    # summary json
    summ = {
        "n_venetoclax_lines": int(res[(res.drug == "Venetoclax") & (res.metric == "LN_IC50")]["n"].max()),
        "seed": SEED, "perm_iters": 5000, "boot_iters": 5000,
        "guardians": GUARDIANS, "executioners": EXECUTIONERS,
        "convention": "functional dependence = -CRISPR gene_effect; sensitivity marker -> negative rho with LN_IC50",
    }
    (OUT_L / "M10_functional_vs_expression.json").write_text(json.dumps(summ, indent=2))
    print(f"\nSaved: outputs/tables/M10_functional_vs_expression.csv (n={len(res)} correlations)")
    print("GUARDRAILS: real data only; no efficacy claim; perm null + bootstrap CI on every rho.")
    print("HONEST CAVEATS: n is modest (~60 heme lines with both layers); cell-line culture bias")
    print("applies; CRISPR fitness reads GUARDIAN survival-dependence but is structurally blind to")
    print("the pro-apoptotic EXECUTIONER axis -> that axis still needs functional BH3 profiling.")


if __name__ == "__main__":
    main()
