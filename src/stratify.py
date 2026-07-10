#!/usr/bin/env python3
"""M5 — ATAP-susceptibility stratifier (mechanistic composite) + M6 — subtype ranking.

>>> This is a PREDICTED susceptibility score derived from mechanism. It is NOT validated
>>> against ATAP response data (there is none). It predicts the population where a
>>> BAX-independent agent is mechanistically rational, NOT a kill rate. (GUARDRAILS §3)

Susceptibility (continuous, function of BCL-2-family state ONLY — no drug/ATAP data):
  guardian_dependence = cohort rank of max(BCL2, MCL1, BCL2A1, BCL2L1) expression
                        (a would-be BH3-mimetic target — the cell leans on a guardian)
  executioner_deficiency = 1 - cohort rank of mean(BAX, BAK1) expression
                        (low executioners -> the class cannot execute)
  susceptibility = sqrt(guardian_dependence * executioner_deficiency)   [geometric mean;
                   BOTH must be high to score high — this is the circularity-safe part:
                   it is NOT executioner loss alone, and NOT guardian rebalancing alone.]

Validation (spec M5): does the composite track observed venetoclax resistance in GDSC /
BeatAML? Reported honestly whether it does or does not (it partly does / does not).
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
PROC = ROOT / CFG["paths"]["data_processed"]
LOGS = ROOT / CFG["paths"]["outputs_logs"]
TABLES = ROOT / CFG["paths"]["outputs_tables"]
RAW = ROOT / CFG["paths"]["data_raw"]

GUARDIANS = ["BCL2", "MCL1", "BCL2A1", "BCL2L1"]
EXEC = ["BAX", "BAK1"]


def _rank01(s: pd.Series) -> pd.Series:
    return s.rank(pct=True)


def susceptibility(df: pd.DataFrame) -> pd.DataFrame:
    g = [f"expr_{x}" for x in GUARDIANS if f"expr_{x}" in df.columns]
    e = [f"expr_{x}" for x in EXEC if f"expr_{x}" in df.columns]
    out = pd.DataFrame(index=df.index)
    out["guardian_dependence"] = _rank01(df[g].max(axis=1))
    out["executioner_deficiency"] = 1 - _rank01(df[e].mean(axis=1))
    out["susceptibility_score"] = np.sqrt(out["guardian_dependence"]
                                          * out["executioner_deficiency"])
    for c in ["executioner_loss_call", "executioner_loss_score"]:
        if c in df.columns:
            out[c] = df[c]
    return out


def validate(name, sus, resistance: pd.Series, higher_is_resistant=True):
    j = sus.join(resistance.rename("resistance")).dropna(
        subset=["resistance", "susceptibility_score"])
    if len(j) < 10:
        return {"cohort": name, "n": len(j), "note": "insufficient"}
    r = resistance if higher_is_resistant else -resistance
    rho, p = stats.spearmanr(j["susceptibility_score"], j["resistance"])
    # also: are executioner-loss-called cases in the resistant tail?
    tail = None
    if "executioner_loss_call" in j and j["executioner_loss_call"].sum() >= 3:
        called = j[j["executioner_loss_call"].astype(bool)]["resistance"]
        rest = j[~j["executioner_loss_call"].astype(bool)]["resistance"]
        u, pu = stats.mannwhitneyu(called, rest, alternative="greater" if higher_is_resistant else "less")
        tail = {"called_median": float(called.median()), "rest_median": float(rest.median()),
                "mwu_p": float(pu), "n_called": int(len(called))}
    return {"cohort": name, "n": len(j), "spearman_rho": float(rho), "spearman_p": float(p),
            "exec_loss_tail": tail}


def run_m5():
    results = []
    scored = {}
    # DepMap: validate vs venetoclax LN_IC50 (higher = resistant)
    dep = pd.read_csv(PROC / "depmap_celllines.csv", index_col=0)
    sdep = susceptibility(dep); scored["depmap"] = sdep
    results.append(validate("DepMap (venetoclax LN_IC50)", sdep, dep["venetoclax_LN_IC50"]))
    # BeatAML: validate vs ex vivo venetoclax AUC (higher = resistant)
    bea = pd.read_csv(PROC / "beataml_patients.csv", index_col=0)
    sbea = susceptibility(bea); scored["beataml"] = sbea
    results.append(validate("BeatAML (ex vivo venetoclax AUC)", sbea, bea["venetoclax_AUC"]))
    for lab in ("LAML", "DLBC"):
        t = pd.read_csv(PROC / f"tcga_{lab}.csv", index_col=0)
        scored[f"tcga_{lab}"] = susceptibility(t)

    for k, v in scored.items():
        v.to_csv(TABLES / f"M5_susceptibility_{k}.csv")

    lines = ["# M5 report — ATAP-susceptibility stratifier (PREDICTED, not measured)", "",
             "> Predicted susceptibility score from mechanism (BCL-2-family state only). "
             "NOT validated against ATAP response data. Not a kill rate. (GUARDRAILS §3)", "",
             "susceptibility = sqrt(guardian_dependence × executioner_deficiency), each a "
             "within-cohort rank in [0,1].", "",
             "## Validation against observed venetoclax resistance", ""]
    for r in results:
        if r.get("note") == "insufficient":
            lines.append(f"- **{r['cohort']}**: n={r['n']} insufficient"); continue
        lines.append(f"- **{r['cohort']}** (n={r['n']}): Spearman ρ = {r['spearman_rho']:.3f} "
                     f"(p = {r['spearman_p']:.2g}) between susceptibility and resistance.")
        if r.get("exec_loss_tail"):
            t = r["exec_loss_tail"]
            lines.append(f"  - executioner-loss-called cases (n={t['n_called']}): median "
                         f"resistance {t['called_median']:.2f} vs {t['rest_median']:.2f} "
                         f"(others); Mann-Whitney one-sided p = {t['mwu_p']:.2g}.")
    lines += ["", "## Construct limits (stated explicitly, spec M5)",
              "- The composite rewards BOTH high guardian dependence AND low executioner "
              "availability, so it is not circular with executioner loss alone.",
              "- M3 showed executioner loss adds little beyond guardian dependence for "
              "venetoclax; therefore the score's correlation with venetoclax resistance is "
              "expected to be modest and is driven substantially by the guardian-dependence "
              "term. The score's intended use is to flag the *bypass-rational* subset "
              "(dependent yet unable to execute), not to predict venetoclax response.",
              "- No ATAP data exists to validate the executioner-deficiency half; that half "
              "is mechanistic hypothesis only."]
    (LOGS / "M5_report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    import json
    (TABLES / "M5_validation.json").write_text(json.dumps(results, indent=2))
    return scored


def run_m6(scored):
    """Rank hematologic subtypes by susceptibility + executioner-loss prevalence."""
    rows = []
    # BeatAML subtypes via ELN2017 + fusion
    clin = pd.read_excel(RAW / "beataml_wv1to4_clinical.xlsx")
    clin = clin.dropna(subset=["dbgap_rnaseq_sample"]).drop_duplicates("dbgap_rnaseq_sample")
    clin = clin.set_index("dbgap_rnaseq_sample")
    sbea = scored["beataml"].join(clin[["ELN2017", "consensusAMLFusions", "fabBlastMorphology"]])
    for field in ["ELN2017", "consensusAMLFusions"]:
        for lvl, grp in sbea.groupby(field):
            if len(grp) < 8:
                continue
            rows.append({"cohort": "BeatAML", "grouping": field, "subtype": str(lvl),
                         "n": len(grp), "mean_susceptibility": grp["susceptibility_score"].mean(),
                         "exec_loss_prev_%": 100 * grp["executioner_loss_call"].mean()})
    # TCGA LAML / DLBC as cohort-level rows
    for lab in ("LAML", "DLBC"):
        g = scored[f"tcga_{lab}"]
        rows.append({"cohort": f"TCGA-{lab}", "grouping": "cohort", "subtype": lab,
                     "n": len(g), "mean_susceptibility": g["susceptibility_score"].mean(),
                     "exec_loss_prev_%": 100 * g["executioner_loss_call"].mean()})
    # DepMap lineages
    dep = pd.read_csv(PROC / "depmap_celllines.csv", index_col=0)
    sdep = scored["depmap"].join(dep["OncotreeLineage"])
    for lin, grp in sdep.groupby("OncotreeLineage"):
        rows.append({"cohort": "DepMap", "grouping": "lineage", "subtype": lin,
                     "n": len(grp), "mean_susceptibility": grp["susceptibility_score"].mean(),
                     "exec_loss_prev_%": 100 * grp["executioner_loss_call"].mean()})
    tbl = pd.DataFrame(rows).sort_values("mean_susceptibility", ascending=False)
    tbl.to_csv(TABLES / "M6_subtype_ranking.csv", index=False)

    lines = ["# M6 report — subtype stratification by predicted susceptibility", "",
             "> Predicted, not measured. Ranks the addressable (bypass-rational) population; "
             "not ATAP benefit.", "",
             "Ranked by mean susceptibility score (BCL-2-family mechanistic composite):", "",
             "| cohort | grouping | subtype | n | mean susceptibility | executioner-loss % |",
             "|--------|----------|---------|---|--------------------|--------------------|"]
    for _, r in tbl.iterrows():
        lines.append(f"| {r['cohort']} | {r['grouping']} | {r['subtype']} | {int(r['n'])} | "
                     f"{r['mean_susceptibility']:.3f} | {r['exec_loss_prev_%']:.1f} |")
    lines += ["", "Cross-reference: venetoclax is used clinically in AML, CLL, and MM. The "
              "predicted bypass-rational population is largest where high guardian dependence "
              "co-occurs with low executioner availability; see table. This is a hypothesis "
              "for prioritization, not evidence of ATAP efficacy."]
    (LOGS / "M6_report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:20]))
    return tbl


if __name__ == "__main__":
    sc = run_m5()
    run_m6(sc)
