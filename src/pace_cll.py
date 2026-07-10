#!/usr/bin/env python3
"""PACE / Dietrich 2018 blood-cancer cohort (CLL) — second-disease resource.

Source: BloodCancerMultiOmics2017 (Bioconductor experiment package), the data behind
Dietrich et al., "Drug-perturbation-based stratification of blood cancer", JCI 2018, and
cited by Chong et al., Mol Cancer 2025 (BCL-2 dependence predicts venetoclax response — an
external validation of our guardian-axis finding).

Why this cohort matters: it lets us test whether the guardian/susceptibility framework
GENERALIZES beyond AML to a second blood cancer (CLL). That directly addresses the
"one-disease / double-checker" critique.

STATUS (honest):
  - Venetoclax ex-vivo response for 184 CLL patients IS extractable in pure Python (below).
  - Baseline BCL-2-family EXPRESSION (needed for the guardian/executioner axes) lives in an
    R DESeqDataSet (`dds.RData`) that pure-Python readers (pyreadr/rdata) cannot parse.
    Completing the CLL framework validation therefore needs R (rpy2 or an R export step).
    This module stages the venetoclax response now and documents the expression blocker.

Deps: `rdata` (pure-Python R reader). Tarball auto-download documented in fetch notes.
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
PACE = ROOT / "data" / "raw" / "pace" / "BloodCancerMultiOmics2017" / "data"


def _read(name):
    import rdata
    return rdata.conversion.convert(rdata.parser.parse_file(str(PACE / f"{name}.RData")))[name]


def build_cll_venetoclax() -> pd.DataFrame:
    """Per-CLL-patient venetoclax ex-vivo viability (mean over concentrations)."""
    lpd = _read("lpdAll")
    exprs = lpd.assayData.get("exprs")           # 539 features x 249 patients (xarray)
    fd = lpd.featureData.data
    pheno = lpd.phenoData.data
    mat = pd.DataFrame(np.asarray(exprs), index=list(fd["name"]), columns=list(pheno.index))
    # venetoclax = drug D_081; average the single-concentration viabilities (lower = sensitive)
    ven_rows = fd.index[(fd["id"].astype(str) == "D_081") &
                        (fd["name"].astype(str) == "venetoclax")]
    ven_names = [fd.loc[i, "name"] for i in ven_rows]  # positional; use raw matrix rows
    ven = np.asarray(exprs)[[list(fd.index).index(i) for i in ven_rows], :]
    ven_mean = pd.Series(np.nanmean(ven, axis=0), index=list(pheno.index), name="venetoclax_viab")
    out = pd.DataFrame({"venetoclax_viab": ven_mean})
    out["Diagnosis"] = pheno["Diagnosis"].values
    for c in ["IGHV Uppsala U/M"]:
        if c in pheno.columns:
            out["IGHV"] = pheno[c].values
    cll = out[out["Diagnosis"] == "CLL"].dropna(subset=["venetoclax_viab"])
    return cll


def run():
    PROC.mkdir(parents=True, exist_ok=True)
    cll = build_cll_venetoclax()
    cll.to_csv(PROC / "pace_cll_venetoclax.csv")
    print(f"[PACE-CLL] staged {len(cll)} CLL patients with venetoclax ex-vivo viability "
          f"-> {PROC/'pace_cll_venetoclax.csv'}")
    print("[PACE-CLL] EXPRESSION (guardian/executioner axes) is in an R DESeqDataSet "
          "(dds.RData) — needs R/rpy2 to unlock. Full CLL framework validation is a "
          "documented next step (see docs/BLOCKERS.md).")
    return cll


if __name__ == "__main__":
    run()
