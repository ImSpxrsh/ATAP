"""
09_model_comparison.py — the honest "what actually predicts venetoclax resistance?"
figure (build-spec F4/F5, done transparently after the cycle-8 discrimination result).

Cycle 8 showed the mechanistic composite is beaten by BCL2 alone and that a monocytic
signature is the dominant predictor. This makes that explicit: a forest plot of every
candidate predictor's Spearman correlation with real BeatAML venetoclax ex-vivo AUC, each
with a 95% bootstrap CI, sorted by strength. The composite must be shown next to the
baselines it should beat — and currently doesn't.

Predictors (all vs venetoclax AUC; negative rho = predicts sensitivity):
  BCL2 (single gene)              MCL1 (single gene)
  BCL2 - MCL1 (2-gene guardian)   monocytic signature (differentiation)
  composite venetoclax_score      executioner_loss_score (the ATAP-relevant axis)
  BCL2 + monocytic (honest baseline the composite should beat)

No efficacy claim; ex-vivo resistance only. Writes figures/model_comparison.png.
Run: .venv/bin/python scripts/09_model_comparison.py
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from atap import data, features, scoring  # noqa: E402

AUC_PATH = ROOT / "data" / "raw" / "beataml" / "beataml_probit_curve_fits_v4.txt"
STUDY = "aml_ohsu_2022"
MONOCYTIC = ["LYZ", "CD14", "CSF1R", "FCN1", "MAFB", "VCAN", "CD68", "ITGAM"]
SEED = 7


def _ba(x):
    m = re.search(r"(BA\d+)", str(x))
    return m.group(1) if m else None


def _fetch_genes(genes):
    api = "https://www.cbioportal.org/api"
    def post(p, b):
        r = urllib.request.Request(api + p, data=json.dumps(b).encode(),
                                   headers={"Content-Type": "application/json"}, method="POST")
        return json.load(urllib.request.urlopen(r, timeout=90))
    def get(p):
        return json.load(urllib.request.urlopen(api + p, timeout=60))
    gmap = {g["hugoGeneSymbol"]: g["entrezGeneId"]
            for g in post("/genes/fetch?geneIdType=HUGO_GENE_SYMBOL", genes)}
    ent2sym = {v: k for k, v in gmap.items()}
    sl = next(s["sampleListId"] for s in get(f"/studies/{STUDY}/sample-lists")
              if s["sampleListId"].endswith("_all"))
    md = post(f"/molecular-profiles/{STUDY}_rna_seq_v2_mrna/molecular-data/fetch",
              {"sampleListId": sl, "entrezGeneIds": list(gmap.values())})
    rows = {}
    for d in md:
        rows.setdefault(d["sampleId"], {})[ent2sym[d["entrezGeneId"]]] = d["value"]
    return pd.DataFrame(rows).T


def _boot_ci(x, y, n=2000):
    rng = np.random.default_rng(SEED)
    x, y = np.asarray(x, float), np.asarray(y, float)
    idx = np.arange(len(x))
    rs = [spearmanr(x[b], y[b]).statistic
          for b in (rng.choice(idx, len(idx), replace=True) for _ in range(n))]
    return float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))


def main() -> None:
    auc = (pd.read_csv(AUC_PATH, sep="\t", low_memory=False)
           .query("inhibitor.str.fullmatch('Venetoclax', case=False, na=False)", engine="python"))
    auc["ba"] = auc["dbgap_rnaseq_sample"].map(_ba)
    auc = auc.dropna(subset=["ba"]).groupby("ba")["auc"].median()

    co = data.load_cbioportal(STUDY)
    z = features.zscore_expression(co.expr)
    blocks = features.build_feature_blocks(co.expr, co.mutations)
    sc = scoring.SusceptibilityModel().score(blocks)
    el = features.executioner_loss_score(co.expr, co.mutations)
    mono = features.zscore_expression(_fetch_genes(MONOCYTIC)).mean(axis=1)

    def to_ba(s):
        s = pd.Series(np.asarray(s), index=[_ba(i) for i in (s.index if hasattr(s, "index") else co.expr.index)])
        return s[~s.index.duplicated()]

    zb = z.copy(); zb.index = [_ba(i) for i in z.index]; zb = zb[~zb.index.duplicated()]
    preds = {
        "BCL2 (single gene)": zb["BCL2"],
        "MCL1 (single gene)": zb["MCL1"],
        "BCL2 - MCL1 (guardian)": zb["BCL2"] - zb["MCL1"],
        "monocytic signature": to_ba(mono),
        "composite venetoclax_score": to_ba(pd.Series(sc["venetoclax_score"].values, index=sc.index)),
        "executioner_loss_score": to_ba(pd.Series(el["executioner_loss_score"].values, index=el.index)),
    }
    # honest combined baseline: resistance rises with monocytic, falls with BCL2
    preds["BCL2 + monocytic (baseline)"] = to_ba(mono).reindex(zb.index) - zb["BCL2"]

    rows = []
    for name, s in preds.items():
        d = pd.DataFrame({"x": s}).join(auc.rename("y"), how="inner").dropna()
        rho = spearmanr(d["x"], d["y"]).statistic
        lo, hi = _boot_ci(d["x"].values, d["y"].values)
        rows.append({"predictor": name, "rho": rho, "lo": lo, "hi": hi, "n": len(d)})
    df = pd.DataFrame(rows).sort_values("rho")
    print("What predicts BeatAML venetoclax ex-vivo AUC (Spearman, negative = sensitivity):")
    print(df.to_string(index=False))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    yy = np.arange(len(df))
    colors = ["#d1495b" if "composite" in p or "executioner" in p else "#30638e"
              for p in df["predictor"]]
    ax.errorbar(df["rho"], yy, xerr=[df["rho"] - df["lo"], df["hi"] - df["rho"]],
                fmt="o", color="none", ecolor="#999", capsize=3, zorder=1)
    ax.scatter(df["rho"], yy, c=colors, s=55, zorder=2)
    ax.axvline(0, color="#bbb", lw=1)
    ax.set_yticks(yy); ax.set_yticklabels(df["predictor"], fontsize=9)
    ax.set_xlabel("Spearman rho vs venetoclax ex-vivo AUC  (negative = predicts sensitivity)")
    ax.set_title(f"What actually predicts venetoclax resistance? BeatAML n={df['n'].iloc[0]}\n"
                 "single genes / differentiation vs the mechanistic composite (red)", fontsize=10)
    fig.tight_layout()
    out = ROOT / "figures" / "model_comparison.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    print(f"\nwrote {out.relative_to(ROOT)}")
    print("HONEST READ: BCL2 alone and the monocytic signature beat the composite; the composite "
          "and executioner_loss_score are the weakest. No efficacy claim.")


if __name__ == "__main__":
    main()
