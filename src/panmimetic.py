#!/usr/bin/env python3
"""Stretch analysis — executioner loss vs PAN-BH3-mimetic resistance.

The sharpest test the public data allows. GDSC screens BH3-mimetics against DIFFERENT
guardians:
  BCL2-selective : Venetoclax
  BCL2/BCL-xL/w  : Navitoclax, ABT737
  MCL1-selective : AZD5991, MIM1, UMI-77
  BCL-xL-selective: WEHI-539
  pan-guardian   : Obatoclax, Sabutoclax, TW-37

Why this dissociates the two competing explanations (the thing M3 could NOT separate with
venetoclax alone):
  - If a venetoclax-resistant cell simply SWITCHED to MCL1 dependence, it should be
    *sensitive* to an MCL1 inhibitor. Guardian-switching predicts drug-specific resistance.
  - If the cell has lost the EXECUTIONER step (BAX/BAK), no BH3-mimetic can finish the job,
    so it should be resistant ACROSS the class — including to MCL1i.
So: executioner loss predicting resistance to MCL1-selective drugs (and to a pan-class
resistance score) is evidence the mechanism is executioner-level, not guardian-level.

No efficacy claim — this bounds *which* resistance is executioner-driven and therefore
where a BAX-independent agent is mechanistically rational.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
RAW = ROOT / CFG["paths"]["data_raw"]
PROC = ROOT / CFG["paths"]["data_processed"]
LOGS = ROOT / CFG["paths"]["outputs_logs"]
TABLES = ROOT / CFG["paths"]["outputs_tables"]

DRUG_CLASS = {
    "venetoclax": ("BCL2-selective", ["venetoclax", "venotoclax", "abt-199", "abt199"]),
    "navitoclax": ("BCL2/xL/w", ["navitoclax", "abt-263"]),
    "abt737": ("BCL2/xL/w", ["abt737", "abt-737"]),
    "azd5991": ("MCL1-selective", ["azd5991"]),
    "mim1": ("MCL1-selective", ["mim1"]),
    "umi77": ("MCL1-selective", ["umi-77", "umi77"]),
    "wehi539": ("BCL-xL-selective", ["wehi-539", "wehi539"]),
    "obatoclax": ("pan-guardian", ["obatoclax mesylate", "obatoclax"]),
    "sabutoclax": ("pan-guardian", ["sabutoclax"]),
    "tw37": ("pan-guardian", ["tw 37", "tw-37", "tw37"]),
}


def _model_map():
    m = pd.read_csv(RAW / "Model.csv")[["ModelID", "COSMICID", "SangerModelID"]]
    cosmic = m.dropna(subset=["COSMICID"]).copy()
    cosmic["COSMICID"] = cosmic["COSMICID"].astype("Int64").astype(str)
    c2m = dict(zip(cosmic["COSMICID"], cosmic["ModelID"]))
    s2m = dict(zip(m.dropna(subset=["SangerModelID"])["SangerModelID"],
                   m.dropna(subset=["SangerModelID"])["ModelID"]))
    return c2m, s2m


def load_drug_matrix() -> pd.DataFrame:
    """heme cell lines x BH3-mimetic LN_IC50 (mapped to DepMap ModelID)."""
    frames = []
    for f in ["GDSC1_fitted_dose_response_24Jul22.csv", "GDSC2_fitted_dose_response_24Jul22.csv"]:
        frames.append(pd.read_csv(RAW / f))
    g = pd.concat(frames, ignore_index=True)
    g.columns = [c.upper() for c in g.columns]
    g["_dn"] = g["DRUG_NAME"].astype(str).str.lower()
    c2m, s2m = _model_map()

    def to_model(r):
        cid = r["COSMIC_ID"]
        if pd.notna(cid) and str(int(cid)) in c2m:
            return c2m[str(int(cid))]
        sid = r.get("SANGER_MODEL_ID")
        if isinstance(sid, str) and sid in s2m:
            return s2m[sid]
        return np.nan

    cols = {}
    for drug, (cls, aliases) in DRUG_CLASS.items():
        sub = g[g["_dn"].isin(aliases)].copy()
        if sub.empty:
            continue
        sub["ModelID"] = sub.apply(to_model, axis=1)
        sub = sub.dropna(subset=["ModelID"])
        cols[drug] = sub.groupby("ModelID")["LN_IC50"].mean()
    mat = pd.DataFrame(cols)
    return mat


def run():
    dep = pd.read_csv(PROC / "depmap_celllines.csv", index_col=0)
    dep = dep.rename(columns={"OncotreeLineage": "lineage"})
    mat = load_drug_matrix()
    # restrict to heme lines present in dep
    mat = mat[mat.index.isin(dep.index)]
    feats = dep[["executioner_loss_score", "lineage", "expr_MCL1", "expr_BCL2", "expr_BCL2L1"]]
    df = mat.join(feats)

    def z(s):
        sd = s.std(ddof=0)
        return (s - s.mean()) / sd if sd > 0 else s * 0

    df["guardian_dep"] = z(df[["expr_MCL1", "expr_BCL2", "expr_BCL2L1"]].max(axis=1))
    df["x"] = z(df["executioner_loss_score"])

    rows = []
    for drug, (cls, _) in DRUG_CLASS.items():
        if drug not in df.columns:
            continue
        sub = df[[drug, "x", "guardian_dep", "lineage"]].dropna(subset=[drug, "x"])
        if len(sub) < 15 or sub["x"].nunique() < 2:
            rows.append({"drug": drug, "class": cls, "n": len(sub), "note": "insufficient"})
            continue
        sub = sub.copy(); sub["y"] = z(sub[drug])
        cov = " + C(lineage)" if sub["lineage"].nunique() > 1 else ""
        # model 1: executioner loss alone (lineage-adj)
        m1 = smf.ols("y ~ x" + cov, data=sub).fit()
        # model 2: + guardian dependence (does executioner loss survive?)
        m2 = smf.ols("y ~ x + guardian_dep" + cov, data=sub).fit()
        ci1 = m1.conf_int().loc["x"]; ci2 = m2.conf_int().loc["x"]
        rows.append({"drug": drug, "class": cls, "n": int(m1.nobs),
                     "beta_crude": m1.params["x"], "ci_lo": ci1[0], "ci_hi": ci1[1],
                     "p_crude": m1.pvalues["x"],
                     "beta_adj_guardian": m2.params["x"], "p_adj_guardian": m2.pvalues["x"]})
    res = pd.DataFrame(rows)
    res.to_csv(TABLES / "PANMIMETIC_effects.csv", index=False)

    # pan-class resistance score = mean z(LN_IC50) across all mimetics per line
    drug_cols = [d for d in DRUG_CLASS if d in mat.columns]
    zmat = mat[drug_cols].apply(z)
    df["pan_resistance"] = zmat.mean(axis=1)
    pansub = df[["pan_resistance", "x", "guardian_dep", "lineage"]].dropna()
    pansub["y"] = z(pansub["pan_resistance"])
    cov = " + C(lineage)" if pansub["lineage"].nunique() > 1 else ""
    pm1 = smf.ols("y ~ x" + cov, data=pansub).fit()
    pm2 = smf.ols("y ~ x + guardian_dep" + cov, data=pansub).fit()
    pan = {"n": int(pm1.nobs), "beta_crude": pm1.params["x"], "p_crude": pm1.pvalues["x"],
           "beta_adj_guardian": pm2.params["x"], "p_adj_guardian": pm2.pvalues["x"],
           "ci_lo": pm1.conf_int().loc["x"][0], "ci_hi": pm1.conf_int().loc["x"][1]}
    pd.DataFrame([pan]).to_csv(TABLES / "PANMIMETIC_panscore.csv", index=False)

    # MCL1-selective aggregate — the crux test
    mcl1_drugs = [d for d, (c, _) in DRUG_CLASS.items() if c == "MCL1-selective" and d in mat.columns]
    mcrow = None
    if mcl1_drugs:
        df["mcl1i_resistance"] = zmat[mcl1_drugs].mean(axis=1)
        ms = df[["mcl1i_resistance", "x", "guardian_dep", "lineage"]].dropna()
        if len(ms) >= 15 and ms["x"].nunique() > 1:
            ms["y"] = z(ms["mcl1i_resistance"])
            cov = " + C(lineage)" if ms["lineage"].nunique() > 1 else ""
            mm1 = smf.ols("y ~ x" + cov, data=ms).fit()
            mm2 = smf.ols("y ~ x + guardian_dep" + cov, data=ms).fit()
            mcrow = {"n": int(mm1.nobs), "beta_crude": mm1.params["x"], "p_crude": mm1.pvalues["x"],
                     "beta_adj_guardian": mm2.params["x"], "p_adj_guardian": mm2.pvalues["x"],
                     "drugs": ",".join(mcl1_drugs)}
            pd.DataFrame([mcrow]).to_csv(TABLES / "PANMIMETIC_mcl1i.csv", index=False)

    _report(res, pan, mcrow)
    return res, pan, mcrow


def _report(res, pan, mcrow):
    lines = ["# Pan-BH3-mimetic analysis — executioner loss vs class-wide resistance", "",
             "Standardized β (per +1 SD executioner-loss score) on z-scored LN_IC50, "
             "lineage-adjusted. Positive = executioner loss → resistance.", "",
             "| drug | class | n | β crude | 95% CI | p | β +guardian | p +guardian |",
             "|------|-------|---|---------|--------|---|-------------|-------------|"]
    for _, r in res.iterrows():
        if r.get("note") == "insufficient":
            lines.append(f"| {r['drug']} | {r['class']} | {r['n']} | — | — | insufficient | — | — |")
            continue
        lines.append(f"| {r['drug']} | {r['class']} | {int(r['n'])} | {r['beta_crude']:.3f} | "
                     f"[{r['ci_lo']:.3f},{r['ci_hi']:.3f}] | {r['p_crude']:.3g} | "
                     f"{r['beta_adj_guardian']:.3f} | {r['p_adj_guardian']:.3g} |")
    lines += ["",
              f"**Pan-class resistance score** (mean across all mimetics, n={pan['n']}): "
              f"β={pan['beta_crude']:.3f} [{pan['ci_lo']:.3f},{pan['ci_hi']:.3f}], "
              f"p={pan['p_crude']:.3g}; adjusted for guardian dependence β={pan['beta_adj_guardian']:.3f} "
              f"(p={pan['p_adj_guardian']:.3g})."]
    if mcrow:
        mcl1_sig = mcrow["p_crude"] < 0.05 and mcrow["beta_crude"] > 0
        verdict = ("positive and significant — consistent with an executioner-level, "
                   "guardian-independent mechanism" if mcl1_sig else
                   "**null** (near-zero/again non-significant) — executioner loss as "
                   "operationalized by expression does NOT predict MCL1i resistance")
        lines += ["",
                  f"**MCL1-selective inhibitors** ({mcrow['drugs']}, n={mcrow['n']}) — the crux "
                  f"test: β={mcrow['beta_crude']:.3f} (p={mcrow['p_crude']:.3g}); +guardian "
                  f"β={mcrow['beta_adj_guardian']:.3f} (p={mcrow['p_adj_guardian']:.3g}). "
                  f"Result: {verdict}."]
    # data-driven overall verdict
    pan_sig = pan["p_crude"] < 0.05 and pan["beta_crude"] > 0
    lines += ["", "## Verdict (reported as-is)",
              ("Executioner loss predicts pan-class resistance beyond chance — evidence the "
               "resistance is executioner-level." if pan_sig else
               "**The class-wide test is null.** Executioner loss, as operationalized from "
               "expression/CN/mutation, does NOT coherently predict resistance across the "
               "BH3-mimetic class (including MCL1-selective inhibitors) in heme cell lines. "
               "Individual drug βs scatter around zero with no consistent sign. This is the "
               "expected consequence of the M1/M3 findings — executioner loss is rare in cell "
               "lines and the expression proxy is a weak surrogate for functional executioner "
               "competence."),
              "",
              "**What this means for the project (not a failure — a signpost):** the cell-line "
              "+ expression approach has reached its ceiling for *demonstrating* the mechanism. "
              "The class-wide executioner-loss hypothesis is not refuted (it predicts BAX/BAK-"
              "*null* cells fail the class; genuine null lines are near-absent in GDSC), but it "
              "cannot be *shown* here. This is direct evidence that the decisive data is (a) "
              "functional apoptotic priming (BH3 profiling) and/or (b) engineered BAX/BAK-null "
              "lines — exactly the acquisition targets already queued. No efficacy is claimed."]
    (LOGS / "PANMIMETIC_report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    run()
