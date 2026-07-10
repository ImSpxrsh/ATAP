"""
06_m1_executioner_subgroup.py — M1 executioner-loss score + the subgroup test that
the M3 null motivated.

M3 showed executioner state is not a *general* predictor of venetoclax resistance
(the guardian/MCL1 axis dominates). The honest follow-up is narrower and correct: does
the specifically-isolated executioner-loss SUBSET sit in the venetoclax-resistant tail?
That is the population where ATAP salvage is mechanistically rational.

Uses the M1 `executioner_loss_score` (features.executioner_loss_score) — defined purely
from BAX/BAK genomic/expression state, NOT from drug response — on real BeatAML, then:
  - Mann-Whitney: is venetoclax ex-vivo AUC higher (more resistant) in the loss subset?
  - Fisher exact: is executioner-loss enriched in the top-tertile (resistant) vs bottom?
  - permutation null on the AUC difference; and an HONEST power/n statement.

No efficacy claim (GUARDRAILS #3): this is about the venetoclax-resistant target
population, not ATAP killing.
Run:  .venv/bin/python scripts/06_m1_executioner_subgroup.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from atap import data, features  # noqa: E402

AUC_PATH = ROOT / "data" / "raw" / "beataml" / "beataml_probit_curve_fits_v4.txt"
SEED = 7


def _ba(x):
    m = re.search(r"(BA\d+)", str(x))
    return m.group(1) if m else None


def main() -> None:
    auc = (pd.read_csv(AUC_PATH, sep="\t", low_memory=False)
           .query("inhibitor.str.fullmatch('Venetoclax', case=False, na=False)", engine="python"))
    auc["ba"] = auc["dbgap_rnaseq_sample"].map(_ba)
    auc = auc.dropna(subset=["ba"]).groupby("ba")["auc"].median()

    co = data.load_cbioportal("aml_ohsu_2022")
    el = features.executioner_loss_score(co.expr, co.mutations)
    el["ba"] = [_ba(i) for i in el.index]
    el = el.dropna(subset=["ba"]).drop_duplicates("ba").set_index("ba")

    j = el.join(auc.rename("auc"), how="inner")
    n = len(j)
    n_loss = int(j["executioner_loss"].sum())
    print(f"M1 executioner-loss subgroup — BeatAML n={n} (real expression + venetoclax AUC)")
    print(f"executioner-loss calls: n={n_loss} ({n_loss/n:.1%})  "
          f"[evidence: {dict(j.loc[j.executioner_loss==1,'evidence'].value_counts())}]")
    if n_loss < 5:
        print("  -> subset too small for a meaningful subgroup test; reporting descriptives only.")

    loss = j[j["executioner_loss"] == 1]["auc"]
    rest = j[j["executioner_loss"] == 0]["auc"]
    print(f"\nvenetoclax AUC (higher=resistant): loss median={loss.median():.1f} (n={len(loss)})  "
          f"vs rest median={rest.median():.1f} (n={len(rest)})")

    if n_loss >= 5:
        u = mannwhitneyu(loss, rest, alternative="greater")  # loss -> more resistant
        print(f"Mann-Whitney (loss more resistant): p={u.pvalue:.4f}")
        # permutation null on the median AUC difference
        obs = loss.median() - rest.median()
        rng = np.random.default_rng(SEED)
        allv = j["auc"].values
        ge = 0
        for _ in range(2000):
            idx = rng.permutation(n) < n_loss
            if (np.median(allv[idx]) - np.median(allv[~idx])) >= obs:
                ge += 1
        print(f"permutation p (median AUC gap by chance): {(ge+1)/2001:.4f}  (obs gap={obs:+.1f} AUC)")
        # Fisher: executioner-loss x resistant(top tertile) vs sensitive(bottom tertile)
        q = j["auc"].quantile([1/3, 2/3])
        top = j["auc"] >= q.iloc[1]
        bot = j["auc"] <= q.iloc[0]
        sub = j[top | bot]
        tab = pd.crosstab(sub["executioner_loss"], top.loc[sub.index])
        if tab.shape == (2, 2):
            odds, pf = fisher_exact(tab.values)
            print(f"Fisher exact (loss enriched in resistant tertile): OR={odds:.2f}  p={pf:.4f}")
            print(f"  2x2 [rows=loss 0/1, cols=sensitive/resistant]:\n{tab.to_string()}")

    print("\nHONEST NOTE: genetic BAX/BAK loss is rare in primary AML; the expression-"
          "bottom-decile definition drives most calls here. DepMap heme lines (genetic loss "
          "+ CRISPR dependency) are the fairer test bed and are the queued next step.")
    print("GUARDRAIL: venetoclax-resistant target population only; no ATAP efficacy claim.")


if __name__ == "__main__":
    main()
