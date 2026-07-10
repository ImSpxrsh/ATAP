"""
08_discrimination.py — is the M2 signal BCL-2 BIOLOGY or a transcriptional SHORTCUT?

M2 found venetoclax_score predicts real venetoclax ex-vivo AUC (rho=-0.275). This script
stress-tests that against the specific ways it could be an artifact rather than mechanism,
on the same real BeatAML n=367. Four decisive tests:

  1. SINGLE-GENE BASELINES. Does the hand-weighted composite beat the best single gene
     (BCL2 / MCL1 alone)? If a single gene does as well, the "mechanistic model" adds nothing.
  2. SIGN-SCRAMBLE NULL (exhaustive). The venetoclax axis is a signed sum over 5 blocks
     (2^5=32 sign patterns). If the true biological signs are NOT among the best patterns,
     the specific mechanism (which gene pushes which way) isn't doing the work.
  3. RANDOM-WEIGHTS NULL. Random signs+magnitudes on the same blocks, 2000 draws. Where does
     the biological weighting fall in that null? Tests whether biology-informed weighting beats
     arbitrary weighting of the same genes.
  4. MONOCYTIC-DIFFERENTIATION CONFOUND. Monocytic AML is venetoclax-resistant via a broad
     program (Pei et al.), and MCL1 co-varies with it. Does the BCL-2 signal SURVIVE
     partialling out a monocytic signature, or is it a proxy for differentiation state?

No efficacy claim. All on ex-vivo resistance. Run: .venv/bin/python scripts/08_discrimination.py
"""
from __future__ import annotations

import itertools
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
from atap import biology, data, features, scoring  # noqa: E402

AUC_PATH = ROOT / "data" / "raw" / "beataml" / "beataml_probit_curve_fits_v4.txt"
SEED = 7
STUDY = "aml_ohsu_2022"
# Canonical monocytic / monocyte-differentiation markers (venetoclax-resistance program).
MONOCYTIC = ["LYZ", "CD14", "CSF1R", "FCN1", "MAFB", "VCAN", "CD68", "ITGAM"]
VEN_SIGNS = {b: s[0] for b, s in biology.DIRECTIONAL_PRIORS.items() if s[0] != 0}  # 5 blocks


def _ba(x):
    m = re.search(r"(BA\d+)", str(x))
    return m.group(1) if m else None


def _fetch_genes(genes):
    """Fetch cBioPortal expression for arbitrary genes (for the monocytic signature)."""
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


def main() -> None:
    rng = np.random.default_rng(SEED)
    auc = (pd.read_csv(AUC_PATH, sep="\t", low_memory=False)
           .query("inhibitor.str.fullmatch('Venetoclax', case=False, na=False)", engine="python"))
    auc["ba"] = auc["dbgap_rnaseq_sample"].map(_ba)
    auc = auc.dropna(subset=["ba"]).groupby("ba")["auc"].median()

    co = data.load_cbioportal(STUDY)
    z = features.zscore_expression(co.expr)
    blocks = features.build_feature_blocks(co.expr, co.mutations)
    sc = scoring.SusceptibilityModel().score(blocks)

    def align(s):
        s = s.copy()
        s.index = [_ba(i) for i in s.index]
        return s[~s.index.duplicated()].dropna()

    y = align(pd.Series(sc["venetoclax_score"].values, index=sc.index)).rename("score")
    j = pd.DataFrame({"score": y}).join(auc.rename("auc"), how="inner")
    common_ba = j.index
    real_rho = spearmanr(j["score"], j["auc"]).statistic
    print(f"Discrimination battery on BeatAML n={len(j)}. Composite venetoclax_score vs "
          f"venetoclax AUC: rho={real_rho:+.3f}\n")

    # ---- 1. single-gene baselines ------------------------------------------------
    print("1. SINGLE-GENE BASELINES (|rho| of one gene's z-expr vs AUC):")
    zb = z.copy(); zb.index = [_ba(i) for i in z.index]; zb = zb[~zb.index.duplicated()]
    best_g, best_r = None, 0.0
    for g in ["BCL2", "MCL1", "BCL2L1", "PMAIP1", "BAX", "BAK1"]:
        if g in zb.columns:
            gr = spearmanr(zb.loc[common_ba, g], j["auc"]).statistic
            print(f"     {g:7s}: rho={gr:+.3f}")
            if abs(gr) > abs(best_r):
                best_g, best_r = g, gr
    print(f"   best single gene: {best_g} |rho|={abs(best_r):.3f}  vs composite |rho|="
          f"{abs(real_rho):.3f}  -> composite {'beats' if abs(real_rho)>abs(best_r) else 'does NOT beat'} best single gene")

    # ---- 2. exhaustive sign-scramble null ----------------------------------------
    bl = blocks.copy(); bl.index = [_ba(i) for i in bl.index]; bl = bl[~bl.index.duplicated()]
    bl = bl.loc[common_ba]
    w = scoring.BLOCK_WEIGHTS
    order = list(VEN_SIGNS)
    def axis(signs):
        tot = sum(signs[i] * w.get(order[i], 1.0) * bl[order[i]] for i in range(len(order)))
        return spearmanr(tot, j["auc"]).statistic
    true_signs = [VEN_SIGNS[b] for b in order]
    all_rhos = [axis(list(c)) for c in itertools.product([1, -1], repeat=len(order))]
    true_rho = axis(true_signs)
    # rank by predictive strength (most negative rho = best, since sensitivity->low AUC)
    better = sum(1 for r in all_rhos if r <= true_rho)
    print(f"\n2. SIGN-SCRAMBLE NULL (all 2^{len(order)}={len(all_rhos)} sign patterns):")
    print(f"   biological signs: rho={true_rho:+.3f}. Patterns at least as predictive: "
          f"{better}/{len(all_rhos)} (rank {better}). "
          f"{'Biology is near-best' if better<=3 else 'Biology is NOT specially predictive'}.")

    # ---- 3. random-weights null --------------------------------------------------
    ge = 0
    for _ in range(2000):
        rs = rng.choice([1, -1], len(order)) * rng.uniform(0.5, 2.0, len(order))
        tot = sum(rs[i] * bl[order[i]] for i in range(len(order)))
        if spearmanr(tot, j["auc"]).statistic <= true_rho:
            ge += 1
    print(f"\n3. RANDOM-WEIGHTS NULL (2000 random sign+magnitude vectors on same blocks): "
          f"p={ (ge+1)/2001:.4f}  (fraction as predictive as biology)")

    # ---- 4. monocytic-differentiation confound -----------------------------------
    try:
        mono = _fetch_genes(MONOCYTIC)
        mz = features.zscore_expression(mono).mean(axis=1)
        mz.index = [_ba(i) for i in mz.index]
        mz = mz[~mz.index.duplicated()]
        m = j.join(mz.rename("mono"), how="inner").dropna()
        r_mono = spearmanr(m["mono"], m["auc"]).statistic
        # partial Spearman of score vs AUC controlling for monocytic score (residualize on ranks)
        def rankresid(a, b):
            ar, br = pd.Series(a).rank(), pd.Series(b).rank()
            beta = np.polyfit(br, ar, 1)
            return ar - (beta[0] * br + beta[1])
        pr = spearmanr(rankresid(m["score"].values, m["mono"].values),
                       rankresid(m["auc"].values, m["mono"].values)).statistic
        print(f"\n4. MONOCYTIC CONFOUND (n={len(m)}): monocytic score vs AUC rho={r_mono:+.3f} "
              f"(monocytic->resistant if positive).")
        print(f"   venetoclax_score vs AUC controlling for monocytic state: partial rho={pr:+.3f} "
              f"(vs raw {real_rho:+.3f}). "
              f"{'Signal SURVIVES' if abs(pr) > 0.6*abs(real_rho) else 'Signal LARGELY EXPLAINED'} "
              f"by differentiation state.")
    except Exception as e:  # network / API hiccup — report honestly, don't fake it
        print(f"\n4. MONOCYTIC CONFOUND: fetch failed ({str(e)[:60]}); rerun next cycle.")

    print("\nGUARDRAIL: ex-vivo venetoclax resistance only; no ATAP efficacy claim.")


if __name__ == "__main__":
    main()
