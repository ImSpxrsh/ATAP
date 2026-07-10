"""
04_validate_beataml.py — M2 backbone validation on the primary external cohort.

The falsifiable core of the project (per the build spec, module M2): does the
mechanistic BCL-2-family state predict REAL venetoclax resistance in patients?

This joins two independent real sources — no synthetic data, no fitting to drug
response:
  1. Expression + mutations for the ~39-gene panel, live from the cBioPortal API
     (BeatAML study aml_ohsu_2022).  -> mechanistic venetoclax_score / salvage_index.
  2. Venetoclax EX-VIVO dose-response AUC from the BeatAML2 data release
     (Bottomly et al. 2022; biodev/beataml2.0_data), joined on the BA#### barcode.

The mechanistic score is a fixed function of BCL-2-family biology (biology.py priors);
it is NOT trained on the drug response here, so any association is genuine out-of-the-box
prediction. Reported with a permutation null and a bootstrap CI, per the guardrails.

HONESTY (see GUARDRAILS.md): this validates that the model identifies the venetoclax-
RESISTANT population. It does NOT show ATAP-M8 kills anything — no ATAP-response data
exists. The salvage_target call's first half (venetoclax will fail) is what is tested
here; the second half (ATAP will work) remains a mechanistic hypothesis for the bench.

Run:  .venv/bin/python scripts/04_validate_beataml.py
Downloads the BeatAML AUC table into data/raw/beataml/ (gitignored) if absent.
"""
from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from atap import data, features, scoring  # noqa: E402

AUC_PATH = ROOT / "data" / "raw" / "beataml" / "beataml_probit_curve_fits_v4.txt"
AUC_URL = ("https://media.githubusercontent.com/media/biodev/beataml2.0_data/main/"
           "beataml_probit_curve_fits_v4_dbgap.txt")
SEED = 7


def _ba(x: str) -> str | None:
    m = re.search(r"(BA\d+)", str(x))
    return m.group(1) if m else None


def _load_venetoclax_auc() -> pd.Series:
    if not AUC_PATH.exists():
        AUC_PATH.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading BeatAML AUC table -> {AUC_PATH} ...")
        urllib.request.urlretrieve(AUC_URL, AUC_PATH)
    d = pd.read_csv(AUC_PATH, sep="\t", low_memory=False)
    ven = d[d["inhibitor"].str.fullmatch("Venetoclax", case=False, na=False)].copy()
    ven["ba"] = ven["dbgap_rnaseq_sample"].map(_ba)
    return ven.dropna(subset=["ba"]).groupby("ba")["auc"].median()  # higher AUC = resistant


def _perm_p(x: pd.Series, y: pd.Series, obs: float, n_perm: int = 2000) -> float:
    rng = np.random.default_rng(SEED)
    yv = y.values.copy()
    ge = 0
    for _ in range(n_perm):
        rng.shuffle(yv)
        if abs(spearmanr(x.values, yv).statistic) >= abs(obs):
            ge += 1
    return (ge + 1) / (n_perm + 1)


def _boot_ci(x: pd.Series, y: pd.Series, n_boot: int = 2000) -> tuple[float, float]:
    rng = np.random.default_rng(SEED + 1)
    idx = np.arange(len(x))
    rs = [spearmanr(x.values[b], y.values[b]).statistic
          for b in (rng.choice(idx, len(idx), replace=True) for _ in range(n_boot))]
    return float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))


def _figure(j: pd.DataFrame, rho: float, out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.2, 5))
    st = j["quadrant"] == "salvage_target"
    ax.scatter(j.loc[~st, "venetoclax_score"], j.loc[~st, "veneto_auc"], s=16,
               c="#9aa0a6", alpha=0.7, label="other")
    ax.scatter(j.loc[st, "venetoclax_score"], j.loc[st, "veneto_auc"], s=20,
               c="#d1495b", alpha=0.85, label="predicted salvage_target")
    ax.set_xlabel("Mechanistic venetoclax axis (higher = predicted sensitive)")
    ax.set_ylabel("Venetoclax ex-vivo AUC (higher = more resistant)")
    ax.set_title(f"BeatAML (n={len(j)}): mechanistic score vs real venetoclax response\n"
                 f"Spearman rho = {rho:+.3f} (model not fit to drug data)", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    plt.close(fig)


def main() -> None:
    auc = _load_venetoclax_auc()
    co = data.load_cbioportal("aml_ohsu_2022")
    blocks = features.build_feature_blocks(co.expr, co.mutations)
    sc = scoring.SusceptibilityModel().score(blocks)
    sc["ba"] = [_ba(i) for i in sc.index]
    sc = sc.dropna(subset=["ba"]).drop_duplicates("ba").set_index("ba")

    j = sc.join(auc.rename("veneto_auc"), how="inner")
    print(f"M2 backbone validation — BeatAML patients with expression + venetoclax AUC: n={len(j)}")

    print("\n=== does the mechanistic axis predict REAL venetoclax response? ===")
    print("(prediction: higher venetoclax_score -> more sensitive -> LOWER AUC -> negative rho)")
    results = {}
    for col, expect in [("venetoclax_score", "neg"), ("salvage_index", "pos")]:
        rho = float(spearmanr(j[col], j["veneto_auc"]).statistic)
        p = _perm_p(j[col], j["veneto_auc"], rho)
        lo, hi = _boot_ci(j[col], j["veneto_auc"])
        results[col] = (rho, p, lo, hi)
        print(f"  {col:16s} vs AUC: rho={rho:+.3f}  perm_p={p:.4f}  "
              f"95%CI[{lo:+.3f},{hi:+.3f}]  (expect {expect})")

    # responder vs resistant separation (outer tertiles)
    q = j["veneto_auc"].quantile([1 / 3, 2 / 3])
    sens = j[j["veneto_auc"] <= q.iloc[0]]
    res = j[j["veneto_auc"] >= q.iloc[1]]
    u = mannwhitneyu(sens["venetoclax_score"], res["venetoclax_score"], alternative="greater")
    print(f"\nvenetoclax_score  sensitive(low-AUC) median={sens['venetoclax_score'].median():+.3f}"
          f"  vs resistant(high-AUC) median={res['venetoclax_score'].median():+.3f}"
          f"  MWU p={u.pvalue:.2e}  (n_sens={len(sens)}, n_res={len(res)})")

    _figure(j, results["venetoclax_score"][0], ROOT / "results" / "figures" / "beataml_backbone.png")
    print("\nwrote results/figures/beataml_backbone.png")
    print("\nGUARDRAIL: validates the venetoclax-RESISTANT target population only; "
          "does NOT demonstrate ATAP-M8 efficacy (no ATAP-response data exists).")


if __name__ == "__main__":
    main()
