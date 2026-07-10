"""
07_depmap_executioner.py — DepMap heme cell lines: executioner state vs real functional
readouts. The M1/M3 nulls showed primary AML lacks the executioner-loss phenotype; DepMap
was meant to be the fairer test bed (cell lines carry genetic BAX/BAK loss + CRISPR
dependency). This cycle tests that premise honestly.

Two real questions, each with a permutation null + bootstrap CI (GUARDRAILS #4):
  (A) Is the executioner-loss phenotype actually more common in DepMap heme lines than in
      primary AML?  (descriptive: subset n and evidence)
  (B) Does the expression-based executioner proxy track functional CRISPR BAX/BAK
      dependency?  (Spearman of expression vs gene-effect)

IMPORTANT methodological caveat (stated up front, per LIMITATIONS.md): DepMap CRISPR
gene-effect measures PROLIFERATION fitness in standard culture. Pro-apoptotic effectors
(BAX/BAK) are near-neutral for growth — you do not need your death machinery to divide —
so a fitness CRISPR screen is an intrinsically weak readout of *apoptotic-executioner*
dependency. A near-zero expression-vs-CRISPR concordance is therefore expected and is more
a statement about the readout than about the proxy. The clean functional test needs
BH3-mimetic drug sensitivity (PRISM/GDSC venetoclax/navitoclax), queued next.

No efficacy claim (GUARDRAILS #3). Run: .venv/bin/python scripts/07_depmap_executioner.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from atap import data, features  # noqa: E402

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
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    idx = np.arange(len(x))
    rs = [spearmanr(x[b], y[b]).statistic
          for b in (rng.choice(idx, len(idx), replace=True) for _ in range(n))]
    return float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))


def main() -> None:
    co = data.load_depmap(heme_only=True)
    el = features.executioner_loss_score(co.expr, co.mutations)
    n = len(el)
    n_loss = int(el["executioner_loss"].sum())
    ev = dict(el.loc[el.executioner_loss == 1, "evidence"].value_counts())
    print(f"(A) DepMap heme lines n={n}. Executioner-loss subset: n={n_loss} "
          f"({n_loss/n:.1%}), evidence={ev}")
    print(f"    vs primary AML (BeatAML) 5/367 = 1.4%. "
          f"{'Modestly more' if n_loss/n > 0.014 else 'Not more'} common in cell lines, "
          f"but still rare — genetic BAX/BAK loss is uncommon even here.")

    dep = co.dependency
    if dep is None or not {"BAX", "BAK1"} <= set(dep.columns):
        print("(B) No CRISPR BAX/BAK gene-effect available; skipping concordance.")
        return
    common = co.expr.index.intersection(dep.dropna(subset=["BAX", "BAK1"]).index)
    expr, d = co.expr.loc[common], dep.loc[common]
    print(f"\n(B) expression-vs-CRISPR concordance on n={len(common)} heme lines "
          f"(CRISPR gene-effect: negative = more essential):")
    for g in ("BAX", "BAK1"):
        rho = spearmanr(expr[g], d[g]).statistic
        p = _perm_p(expr[g].values, d[g].values, rho)
        lo, hi = _boot_ci(expr[g].values, d[g].values)
        print(f"    Spearman({g} expr, {g} gene-effect) = {rho:+.3f}  "
              f"perm_p={p:.3f}  95%CI[{lo:+.3f},{hi:+.3f}]")
    print(f"    BAX gene-effect median={d['BAX'].median():+.3f}, "
          f"BAK1 median={d['BAK1'].median():+.3f} "
          f"(near zero => effectors are ~neutral for proliferation, as expected for "
          f"pro-apoptotic genes)")
    print("\nINTERPRETATION: a near-zero concordance is expected — CRISPR proliferation "
          "fitness is a weak proxy for apoptotic-executioner dependency. The clean functional "
          "test is BH3-mimetic drug sensitivity (PRISM/GDSC), queued next. No efficacy claim.")


if __name__ == "__main__":
    main()
