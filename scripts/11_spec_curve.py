"""
11_spec_curve.py — M4 specification-curve (F6): which conclusions survive the multiverse
of reasonable analytic choices?

Enumerates specifications for the venetoclax/navitoclax association and computes the effect
(Spearman rho + bootstrap CI) for EVERY one, then plots the sorted specification curve with a
descriptor matrix, and scores three CONCLUSIONS by how robust they are to analytic choice:

  C1 guardian axis (BCL2 / BCL2-MCL1) is negative & significant   -> expect ~100% stable
  C2 executioner_loss_score is null (CI includes 0)               -> expect ~100% stable
  C3 the composite beats BCL2 alone (same cohort, |rho| larger)   -> expect ~0%  (fragile)

Specification axes:
  predictor  : BCL2, BCL2-MCL1, composite_venetoclax_score, executioner_loss_score, monocytic
  cohort/drug: BeatAML-venetoclax, GDSC-venetoclax, GDSC-navitoclax
  metric     : AUC (all); LN_IC50 (GDSC)
  covariate  : raw; monocytic-controlled (BeatAML only, where the signature is available)

All real data; no fitting to drug response; no efficacy claim. Writes figures/spec_curve.png
and outputs/tables/spec_curve.csv.  Run: .venv/bin/python scripts/11_spec_curve.py
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
GDSC = ROOT / "data" / "raw" / "gdsc" / "GDSC2_fitted_dose_response.xlsx"
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


def _boot_ci(x, y, n=1000):
    rng = np.random.default_rng(SEED)
    x, y = np.asarray(x, float), np.asarray(y, float)
    idx = np.arange(len(x))
    rs = [spearmanr(x[b], y[b]).statistic
          for b in (rng.choice(idx, len(idx), replace=True) for _ in range(n))]
    return float(np.nanpercentile(rs, 2.5)), float(np.nanpercentile(rs, 97.5))


def _predictors(expr, mutations):
    z = features.zscore_expression(expr)
    blocks = features.build_feature_blocks(expr, mutations)
    sc = scoring.SusceptibilityModel().score(blocks)
    el = features.executioner_loss_score(expr, mutations)
    return pd.DataFrame({
        "BCL2": z["BCL2"], "BCL2-MCL1": z["BCL2"] - z["MCL1"],
        "composite": sc["venetoclax_score"].values,
        "executioner": el["executioner_loss_score"].values,
    }, index=expr.index)


def build_frames():
    frames = {}
    # BeatAML
    auc = (pd.read_csv(AUC_PATH, sep="\t", low_memory=False)
           .query("inhibitor.str.fullmatch('Venetoclax', case=False, na=False)", engine="python"))
    auc["ba"] = auc["dbgap_rnaseq_sample"].map(_ba)
    auc = auc.dropna(subset=["ba"]).groupby("ba")["auc"].median()
    co = data.load_cbioportal(STUDY)
    pr = _predictors(co.expr, co.mutations)
    pr.index = [_ba(i) for i in pr.index]; pr = pr[~pr.index.duplicated()]
    mono = features.zscore_expression(_fetch_genes(MONOCYTIC)).mean(axis=1)
    mono.index = [_ba(i) for i in mono.index]; mono = mono[~mono.index.duplicated()]
    pr["monocytic"] = mono.reindex(pr.index)
    frames["BeatAML-venetoclax"] = pr.join(auc.rename("AUC"), how="inner")
    # GDSC (DepMap heme expr x GDSC dose-response)
    gdsc = pd.read_excel(GDSC)
    codm = data.load_depmap(heme_only=True)
    prd = _predictors(codm.expr, codm.mutations)
    model = pd.read_csv(ROOT / "data" / "raw" / "depmap" / "Model.csv").set_index("ModelID")
    prd["SangerModelID"] = model["SangerModelID"].reindex(prd.index).values
    prd = prd.dropna(subset=["SangerModelID"]).set_index("SangerModelID")
    for drug in ("Venetoclax", "Navitoclax"):
        d = gdsc[gdsc["DRUG_NAME"].astype(str).str.contains(drug, case=False, na=False)]
        resp = d.groupby("SANGER_MODEL_ID")[["LN_IC50", "AUC"]].median()
        frames[f"GDSC-{drug.lower()}"] = prd.join(resp, how="inner")
    return frames


def main() -> None:
    frames = build_frames()
    specs = []
    for cohort, df in frames.items():
        metrics = [c for c in ("AUC", "LN_IC50") if c in df.columns]
        has_mono = "monocytic" in df.columns and df["monocytic"].notna().any()
        for pred in ("BCL2", "BCL2-MCL1", "composite", "executioner", "monocytic"):
            if pred not in df.columns:
                continue
            for metric in metrics:
                for covar in (["raw"] + (["mono-ctrl"] if has_mono and pred != "monocytic" else [])):
                    d = df[[pred, metric] + (["monocytic"] if covar == "mono-ctrl" else [])].dropna()
                    if len(d) < 20:
                        continue
                    x, y = d[pred].values.astype(float), d[metric].values.astype(float)
                    if covar == "mono-ctrl":  # residualize both on monocytic (rank)
                        mono = d["monocytic"].rank().values
                        def rr(v):
                            b = np.polyfit(mono, pd.Series(v).rank().values, 1)
                            return pd.Series(v).rank().values - (b[0] * mono + b[1])
                        x, y = rr(x), rr(y)
                    rho = spearmanr(x, y).statistic
                    lo, hi = _boot_ci(x, y)
                    specs.append({"cohort": cohort, "predictor": pred, "metric": metric,
                                  "covar": covar, "n": len(d), "rho": rho, "lo": lo, "hi": hi})
    sp = pd.DataFrame(specs).sort_values("rho").reset_index(drop=True)
    (ROOT / "outputs" / "tables").mkdir(parents=True, exist_ok=True)
    sp.to_csv(ROOT / "outputs" / "tables" / "spec_curve.csv", index=False)
    print(f"specifications: {len(sp)}")

    # conclusion stability
    guard = sp[sp.predictor.isin(["BCL2", "BCL2-MCL1"])]
    c1 = ((guard.rho < 0) & (guard.hi < 0)).mean()
    exe = sp[sp.predictor == "executioner"]
    c2 = ((exe.lo < 0) & (exe.hi > 0)).mean()  # CI includes 0 = null
    c3_hits = []
    for (coh, met), g in sp.groupby(["cohort", "metric"]):
        b = g[g.predictor == "BCL2"]["rho"]
        c = g[g.predictor == "composite"]["rho"]
        if len(b) and len(c):
            c3_hits.append(abs(c.iloc[0]) > abs(b.iloc[0]))
    c3 = float(np.mean(c3_hits)) if c3_hits else float("nan")
    print(f"C1 guardian negative & significant: {c1:.0%} of {len(guard)} guardian specs (expect ~100%)")
    print(f"C2 executioner null (CI incl 0):     {c2:.0%} of {len(exe)} executioner specs (expect ~100%)")
    print(f"C3 composite beats BCL2 alone:       {c3:.0%} of {len(c3_hits)} cohort/metrics (expect ~0%)")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    color = {"BCL2": "#1a9850", "BCL2-MCL1": "#66bd63", "composite": "#d1495b",
             "executioner": "#7b3294", "monocytic": "#2b83ba"}
    fig, ax = plt.subplots(figsize=(9, 5))
    xx = np.arange(len(sp))
    ax.errorbar(xx, sp["rho"], yerr=[sp["rho"] - sp["lo"], sp["hi"] - sp["rho"]],
                fmt="none", ecolor="#ccc", zorder=1)
    ax.scatter(xx, sp["rho"], c=[color[p] for p in sp["predictor"]], s=28, zorder=2)
    ax.axhline(0, color="#888", lw=1)
    ax.set_xlabel("specification (sorted by effect)")
    ax.set_ylabel("Spearman rho vs drug resistance\n(negative = predicts sensitivity)")
    ax.set_title(f"Specification curve across {len(sp)} analytic choices "
                 "(predictor x cohort x drug x metric x covariate)", fontsize=10)
    handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=c, label=p, markersize=7)
               for p, c in color.items()]
    ax.legend(handles=handles, fontsize=8, loc="upper left", title="predictor")
    ax.text(0.98, 0.03,
            f"C1 guardian robust: {c1:.0%}\nC2 executioner null: {c2:.0%}\nC3 composite>BCL2: {c3:.0%}",
            transform=ax.transAxes, fontsize=8, ha="right", va="bottom",
            bbox=dict(boxstyle="round", fc="#f7f7f7", ec="#ccc"))
    fig.tight_layout()
    out = ROOT / "figures" / "spec_curve.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    print(f"wrote {out.relative_to(ROOT)} and outputs/tables/spec_curve.csv")
    print("READ: guardian-axis effect robust across nearly all specs; executioner null robust; "
          "composite does not consistently beat BCL2 (mixed: worse in patients, competitive in cell lines) -> conclusions are stable, the composite's value is "
          "fragile. No efficacy claim.")


if __name__ == "__main__":
    main()
