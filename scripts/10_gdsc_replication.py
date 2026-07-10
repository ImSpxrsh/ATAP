"""
10_gdsc_replication.py — CROSS-COHORT REPLICATION (the antidote to single-source bias).

The M2/cycle-8 findings are from ONE cohort (BeatAML patients). The user's central worry:
is the BCL2->venetoclax-resistance signal biology, or an artifact of that one biased sample?
The clean test is replication in an INDEPENDENT cohort with DIFFERENT biases — GDSC2 cell
lines (Sanger platform) joined to DepMap heme expression. If the BCL2 effect replicates in
data whose artifacts don't overlap BeatAML's, that argues biology; if it vanishes, artifact.

Data (all real): GDSC2 venetoclax (+navitoclax) dose-response (cancerrxgene.org release 8.5)
joined to DepMap 24Q2 heme-lineage expression via SangerModelID. Response: LN_IC50 and AUC
(higher = more resistant, same direction as BeatAML). Predictors correlated with resistance,
each with permutation null + bootstrap CI. No fitting to drug data; no efficacy claim.

Run: .venv/bin/python scripts/10_gdsc_replication.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from atap import data, features, scoring  # noqa: E402

GDSC = ROOT / "data" / "raw" / "gdsc" / "GDSC2_fitted_dose_response.xlsx"
SEED = 7


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
    rs = [spearmanr(x[b], y[b]).statistic
          for b in (rng.choice(idx, len(idx), replace=True) for _ in range(n))]
    return float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))


def _drug_response(df, drug):
    d = df[df["DRUG_NAME"].astype(str).str.contains(drug, case=False, na=False)]
    return d.groupby("SANGER_MODEL_ID")[["LN_IC50", "AUC"]].median()


def main() -> None:
    gdsc = pd.read_excel(GDSC)
    co = data.load_depmap(heme_only=True)
    model = pd.read_csv(ROOT / "data" / "raw" / "depmap" / "Model.csv").set_index("ModelID")
    smid = model["SangerModelID"].reindex(co.expr.index)  # ModelID -> SangerModelID

    z = features.zscore_expression(co.expr)
    blocks = features.build_feature_blocks(co.expr, co.mutations)
    sc = scoring.SusceptibilityModel().score(blocks)
    el = features.executioner_loss_score(co.expr, co.mutations)

    preds = pd.DataFrame({
        "BCL2": z["BCL2"], "MCL1": z["MCL1"], "BCL2_minus_MCL1": z["BCL2"] - z["MCL1"],
        "composite_venetoclax_score": sc["venetoclax_score"].values,
        "executioner_loss_score": el["executioner_loss_score"].values,
    }, index=co.expr.index)
    preds["SangerModelID"] = smid.values
    preds = preds.dropna(subset=["SangerModelID"]).set_index("SangerModelID")

    for drug in ("Venetoclax", "Navitoclax"):
        resp = _drug_response(gdsc, drug)
        j = preds.join(resp, how="inner").dropna()
        print(f"\n=== {drug}: GDSC2 x DepMap-heme, n={len(j)} cell lines "
              f"(independent of BeatAML) ===")
        print(f"    (LN_IC50/AUC higher = resistant; predictors expect NEGATIVE rho for "
              f"sensitivity-markers like BCL2)")
        for metric in ("LN_IC50", "AUC"):
            print(f"  vs {metric}:")
            for p in ("BCL2", "BCL2_minus_MCL1", "composite_venetoclax_score",
                      "executioner_loss_score"):
                rho = spearmanr(j[p], j[metric]).statistic
                pp = _perm_p(j[p].values, j[metric].values, rho)
                lo, hi = _boot_ci(j[p].values, j[metric].values)
                print(f"     {p:28s} rho={rho:+.3f}  perm_p={pp:.3f}  95%CI[{lo:+.3f},{hi:+.3f}]")

    print("\nREPLICATION READ vs BeatAML (BCL2 rho=-0.567 there): if BCL2 stays clearly negative "
          "and significant here (independent cohort, different biases), the BCL2->venetoclax-"
          "sensitivity link is biology, not a BeatAML artifact. Cell-line culture-artifact bias "
          "still applies (LIMITATIONS #4). No efficacy claim.")


if __name__ == "__main__":
    main()
