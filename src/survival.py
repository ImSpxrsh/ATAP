#!/usr/bin/env python3
"""Prognostic layer — does the mechanistic BCL-2-family score carry survival information?

Top computational-oncology papers don't stop at "predicts drug response in vitro" — they ask
"does it matter for patients?" This module tests whether the guardian/susceptibility axes are
associated with overall survival in Beat AML, adjusted for standard prognostic factors
(ELN2017 risk, age).

HONESTY: Beat AML is a largely pre-venetoclax-era cohort with heterogeneous treatment, so a
survival association is prognostic/biological, NOT proof the score guides venetoclax therapy.
We report Kaplan-Meier + a Cox model with covariate adjustment, and read the result as-is —
including a null, which is itself informative (a drug-response axis need not be prognostic).
No efficacy claim.
"""
from __future__ import annotations
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import yaml

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
PROC = ROOT / CFG["paths"]["data_processed"]
RAW = ROOT / CFG["paths"]["data_raw"]
LOGS = ROOT / CFG["paths"]["outputs_logs"]
TABLES = ROOT / CFG["paths"]["outputs_tables"]
GUARDIANS = ["BCL2", "MCL1", "BCL2A1", "BCL2L1"]
EXEC = ["BAX", "BAK1"]


def _axes(df):
    g = [f"expr_{x}" for x in GUARDIANS if f"expr_{x}" in df.columns]
    e = [f"expr_{x}" for x in EXEC if f"expr_{x}" in df.columns]
    guardian = df[g].max(axis=1).rank(pct=True)
    exec_avail = df[e].mean(axis=1).rank(pct=True)
    suscept = np.sqrt(guardian * (1 - exec_avail))
    return pd.DataFrame({"guardian_dependence": guardian,
                         "executioner_availability": exec_avail,
                         "susceptibility": suscept}, index=df.index)


def load():
    bea = pd.read_csv(PROC / "beataml_patients.csv", index_col=0)
    clin = pd.read_excel(RAW / "beataml_wv1to4_clinical.xlsx")
    clin = clin.dropna(subset=["dbgap_rnaseq_sample"]).drop_duplicates("dbgap_rnaseq_sample")
    clin = clin.set_index("dbgap_rnaseq_sample")
    keep = ["overallSurvival", "vitalStatus", "ageAtDiagnosis", "ELN2017"]
    df = _axes(bea).join(bea[[c for c in bea.columns if c.startswith("expr_")]])
    df = df.join(clin[keep])
    # event: 1 = death
    df["event"] = df["vitalStatus"].astype(str).str.lower().map(
        lambda s: 1 if s in ("dead", "deceased", "1", "true") else (0 if s in ("alive", "0", "false") else np.nan))
    df["OS"] = pd.to_numeric(df["overallSurvival"], errors="coerce")
    df = df.dropna(subset=["OS", "event"])
    df = df[df["OS"] > 0]
    return df


def run():
    from lifelines import KaplanMeierFitter, CoxPHFitter
    from lifelines.statistics import logrank_test, multivariate_logrank_test
    df = load()
    n = len(df)

    # --- Kaplan-Meier by susceptibility tertile ---
    df["tertile"] = pd.qcut(df["susceptibility"], 3, labels=["low", "mid", "high"])
    lr = multivariate_logrank_test(df["OS"], df["tertile"], df["event"])
    km = {}
    kmf = KaplanMeierFitter()
    for t in ["low", "mid", "high"]:
        sub = df[df["tertile"] == t]
        kmf.fit(sub["OS"], sub["event"], label=t)
        km[t] = {"n": len(sub), "median_OS": float(kmf.median_survival_time_)}

    # --- Cox models: each axis, then adjusted for age + ELN2017 ---
    def cox(cols):
        d = df[cols + ["OS", "event"]].copy()
        d = pd.get_dummies(d, columns=[c for c in cols if c == "ELN2017"], drop_first=True)
        d = d.dropna()
        # z-score continuous predictors
        for c in cols:
            if c in d.columns and d[c].dtype.kind in "fi" and c not in ("OS", "event"):
                s = d[c].std(ddof=0)
                if s > 0:
                    d[c] = (d[c] - d[c].mean()) / s
        cph = CoxPHFitter(penalizer=0.01).fit(d, "OS", "event")
        return cph, int(cph._n_examples)

    results = {}
    for axis in ["susceptibility", "guardian_dependence", "executioner_availability"]:
        cph_u, nu = cox([axis])
        cph_a, na = cox([axis, "ageAtDiagnosis", "ELN2017"])
        hr_u = float(np.exp(cph_u.params_[axis])); pu = float(cph_u.summary.loc[axis, "p"])
        ci_u = np.exp(cph_u.confidence_intervals_.loc[axis]).tolist()
        hr_a = float(np.exp(cph_a.params_[axis])); pa = float(cph_a.summary.loc[axis, "p"])
        ci_a = np.exp(cph_a.confidence_intervals_.loc[axis]).tolist()
        results[axis] = {"HR_unadj": hr_u, "ci_unadj": ci_u, "p_unadj": pu, "n_unadj": nu,
                         "HR_adj": hr_a, "ci_adj": ci_a, "p_adj": pa, "n_adj": na}

    pd.DataFrame(results).T.to_csv(TABLES / "SURVIVAL_cox.csv")
    df[["OS", "event", "tertile", "susceptibility", "guardian_dependence",
        "executioner_availability", "ageAtDiagnosis", "ELN2017"]].to_csv(TABLES / "SURVIVAL_data.csv")

    lines = ["# Prognostic layer — mechanistic score vs overall survival (Beat AML)", "",
             f"n = {n} patients with overall survival + score. Beat AML is largely "
             "pre-venetoclax-era with heterogeneous treatment — this is a prognostic/biological "
             "association, not evidence the score guides therapy.", "",
             f"## Kaplan-Meier (susceptibility tertiles)",
             f"- Median OS (months): low={km['low']['median_OS']:.1f} (n={km['low']['n']}), "
             f"mid={km['mid']['median_OS']:.1f} (n={km['mid']['n']}), "
             f"high={km['high']['median_OS']:.1f} (n={km['high']['n']}).",
             f"- Log-rank across tertiles: p = {lr.p_value:.3g}.", "",
             "## Cox proportional-hazards (HR per +1 SD; >1 = worse survival)",
             "| axis | HR (unadj) [95% CI] | p | HR (adj: age+ELN2017) [95% CI] | p |",
             "|------|---------------------|---|-------------------------------|---|"]
    for a, r in results.items():
        lines.append(f"| {a} | {r['HR_unadj']:.2f} [{r['ci_unadj'][0]:.2f},{r['ci_unadj'][1]:.2f}] | "
                     f"{r['p_unadj']:.3g} | {r['HR_adj']:.2f} [{r['ci_adj'][0]:.2f},{r['ci_adj'][1]:.2f}] | "
                     f"{r['p_adj']:.3g} |")
    lines += ["",
              "**Reading:** interpret the adjusted HR (controls for ELN2017 risk + age). A "
              "significant guardian/susceptibility HR would mean the mechanistic axis carries "
              "prognostic information beyond standard risk; a null means it is a drug-response "
              "axis, not a prognostic one — both are honest, reportable outcomes. No efficacy claim."]
    (LOGS / "SURVIVAL_report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return results, km, lr


if __name__ == "__main__":
    run()
