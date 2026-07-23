"""
class_wide.py — issue #40: class-wide extension with EXPLICIT power accounting.

Tests the axes against multiple BH3-mimetics, not just venetoclax — but honestly, with the
sample size and achievable power reported for EVERY drug, family-wise correction across the
whole drug x axis grid, and an explicit refusal to celebrate a lone hit in the smallest cohort.

### Pre-registered test family (declared BEFORE running — do not add drugs post hoc)
Drugs:
  - venetoclax   (GDSC2; BCL2 inhibitor)                     — primary
  - navitoclax   (GDSC2; BCL2/BCL-xL inhibitor)              — class member
  - S63845       (PRISM Repurposing 24Q2; MCL1 inhibitor)    — class member, distinct target
Axes:
  - guardian_BCL2_minus_MCL1   (best guardian predictor from the #10 baseline battery)
  - executioner_loss_score     (the ATAP-relevant axis)
Grid = 3 drugs x 2 axes = 6 pre-registered tests.

### Power accounting
For each drug we report n and the achievable power to detect a Spearman |rho| = 0.30 (a modest
effect) at alpha = 0.05 two-sided, via the Fisher z-transform:
    z_r = atanh(r_target) * sqrt(n - 3);  power = P(Z > z_{1-a/2} - z_r) + P(Z < -z_{1-a/2} - z_r)
A drug with power < 0.8 is UNDERPOWERED and its null is uninformative (absence of evidence).

### Multiple comparisons
Holm-Bonferroni across all 6 tests (family-wise). Report raw p, Holm-adjusted p, and the decision.

PROVENANCE NOTE: S63845 uses PRISM Repurposing Public 24Q2 (figshare 25917643), read directly
from data/raw/prism/. That fetch is not yet wired into this repo's src/data/fetch_data.py (it is
tracked separately); GDSC drugs are fully in-repo. If PRISM is absent, S63845 rows are skipped
with a printed note — the venetoclax/navitoclax analysis is self-contained.

GUARDRAILS: real data; no efficacy claim; every estimate has n + power + FWER. Seeded.
Run: PYTHONPATH=src python src/analysis/class_wide.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import spearmanr, norm

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from atap import data, features, scoring  # noqa: E402

CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
SEED = CFG.get("seed", 20260710)
GDSC = ROOT / "data" / "raw" / "gdsc" / "GDSC2_fitted_dose_response.xlsx"
PRISM = ROOT / "data" / "raw" / "prism" / "Repurposing_Public_24Q2_Extended_Primary_Data_Matrix.csv"
OUT_T = ROOT / "outputs" / "tables"

# Pre-registered family (declared before running)
DRUGS = ["venetoclax", "navitoclax", "S63845"]
AXES = ["guardian_BCL2_minus_MCL1", "executioner_loss_score"]
R_TARGET = 0.30
ALPHA = 0.05
S63845_BRD = "K91876515"


def _power_spearman(n, r=R_TARGET, alpha=ALPHA):
    if n is None or n < 5:
        return float("nan")
    zc = norm.ppf(1 - alpha / 2)
    zr = np.arctanh(r) * np.sqrt(n - 3)
    return float(norm.cdf(zr - zc) + norm.cdf(-zr - zc))


def _holm(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        val = (m - rank) * pvals[idx]
        running = max(running, val)
        adj[idx] = min(running, 1.0)
    return adj


def _gdsc_response(gdsc, drug, metric="LN_IC50"):
    d = gdsc[gdsc["DRUG_NAME"].astype(str).str.contains(drug, case=False, na=False)]
    return d.groupby("SANGER_MODEL_ID")[metric].median()


def _prism_s63845(model_index):
    if not PRISM.exists():
        print("(PRISM absent — S63845 rows skipped; venetoclax/navitoclax are self-contained)")
        return None
    idx = pd.read_csv(PRISM, usecols=[0]); idx.columns = ["cid"]
    row = idx.index[idx.cid.str.contains(S63845_BRD)]
    if len(row) == 0:
        return None
    r = int(row[0])
    mat = pd.read_csv(PRISM, skiprows=lambda i: i != 0 and (i - 1) != r).set_index("Unnamed: 0")
    s = mat.T.iloc[:, 0]  # ACH-indexed viability LFC (lower = more killed = sensitive)
    s.name = "S63845"
    return s.reindex(model_index)


def main() -> None:
    co = data.load_depmap(heme_only=True)
    z = features.zscore_expression(co.expr)
    el = features.executioner_loss_score(co.expr, co.mutations)["executioner_loss_score"]
    axes = pd.DataFrame(index=co.expr.index)
    axes["guardian_BCL2_minus_MCL1"] = (z["BCL2"] - z["MCL1"]).values
    axes["executioner_loss_score"] = el.values

    model = pd.read_csv(ROOT / "data" / "raw" / "depmap" / "Model.csv").set_index("ModelID")
    smid = model["SangerModelID"].reindex(co.expr.index)

    # responses per drug (higher = more resistant, consistent sign across platforms)
    gdsc = pd.read_excel(GDSC)
    responses = {}
    for drug in ("venetoclax", "navitoclax"):
        r = _gdsc_response(gdsc, drug)                      # SangerModelID-indexed LN_IC50
        r = r.reindex(smid.values); r.index = co.expr.index  # -> ModelID
        responses[drug] = r
    s63 = _prism_s63845(co.expr.index)
    if s63 is not None:
        responses["S63845"] = s63

    rows = []
    for drug in DRUGS:
        if drug not in responses:
            rows.append(dict(drug=drug, axis="(all)", n=None, power=float("nan"),
                             rho=None, p_raw=None, note="registered; data not wired in this repo"))
            continue
        y = responses[drug]
        for axis in AXES:
            sub = pd.concat([axes[axis], y.rename("resp")], axis=1).dropna()
            n = len(sub)
            rho = spearmanr(sub[axis], sub["resp"]).statistic if n >= 5 else np.nan
            # p from the same Spearman
            p = spearmanr(sub[axis], sub["resp"]).pvalue if n >= 5 else np.nan
            rows.append(dict(drug=drug, axis=axis, n=n, power=round(_power_spearman(n), 3),
                             rho=round(float(rho), 3) if n >= 5 else None,
                             p_raw=float(p) if n >= 5 else None, note=""))

    res = pd.DataFrame(rows)
    testable = res["p_raw"].notna()
    res.loc[testable, "p_holm"] = _holm(res.loc[testable, "p_raw"].to_numpy())
    res["sig_holm"] = res["p_holm"] < ALPHA
    res["underpowered"] = res["power"] < 0.8

    OUT_T.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT_T / "M14_class_wide_power.csv", index=False)

    print("CLASS-WIDE EXTENSION with power accounting (pre-registered 3 drugs x 2 axes)\n")
    print(f"Target effect for power: Spearman |rho|={R_TARGET}, alpha={ALPHA}. Power<0.8 = underpowered.\n")
    for drug in DRUGS:
        d = res[res.drug == drug]
        n = d["n"].dropna().max()
        pw = d["power"].dropna().max()
        head = f"=== {drug}  n={int(n) if pd.notna(n) else 'NA'}  power@|r|=0.3: {pw if pd.notna(pw) else 'NA'} ==="
        print(head + ("  [UNDERPOWERED]" if pd.notna(pw) and pw < 0.8 else ""))
        for _, r in d.iterrows():
            if r["p_raw"] is None:
                print(f"  {r['axis']:28s} — {r['note']}")
            else:
                sig = "SIG(Holm)" if r["sig_holm"] else "ns"
                print(f"  {r['axis']:28s} rho={r['rho']:+.3f}  p_raw={r['p_raw']:.4f}  "
                      f"p_holm={r['p_holm']:.4f}  {sig}"
                      f"{'  (underpowered null)' if r['underpowered'] and not r['sig_holm'] else ''}")
        print()

    print("HONEST READ (per the issue): a lone Holm-significant hit in the SMALLEST cohort is not")
    print("a class-wide finding. Underpowered nulls are 'absence of evidence', not evidence of")
    print("absence. The guardian axis is expected to replicate across BCL2/BCL-xL agents; the")
    print("executioner axis is a registered null we do NOT expect to survive here. No efficacy claim.")
    print(f"Saved: outputs/tables/M14_class_wide_power.csv (seed={SEED})")
    _make_figure(res)


def _make_figure(res):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:  # noqa: BLE001
        print(f"(figure skipped: {e})"); return
    d = res[res["rho"].notna()].copy()
    if d.empty:
        return
    labels = [f"{r.drug}\n{r.axis.replace('guardian_','').replace('_',' ')}" for r in d.itertuples()]
    x = np.arange(len(d))
    colors = ["#0072B2" if "guardian" in a else "#D55E00" for a in d["axis"]]
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    ax.bar(x, d["rho"], color=colors, edgecolor="black", linewidth=0.6)
    for i, r in enumerate(d.itertuples()):
        mark = "*" if r.sig_holm else ("×" if r.underpowered else "")
        ax.text(i, r.rho + (0.03 if r.rho >= 0 else -0.06), f"n={r.n}{mark}",
                ha="center", fontsize=7)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("Spearman rho vs resistance")
    ax.set_title("Cross-agent generalization (blue=guardian, orange=executioner; * Holm-sig, × underpowered)")
    fig.tight_layout()
    (ROOT / "figures").mkdir(exist_ok=True)
    (ROOT / "outputs" / "figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(ROOT / "figures" / "cross_agent_generalization.svg")
    fig.savefig(ROOT / "outputs" / "figures" / "cross_agent_generalization.png", dpi=150)
    print("Saved: figures/cross_agent_generalization.svg + PNG")


if __name__ == "__main__":
    main()
