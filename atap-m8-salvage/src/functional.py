#!/usr/bin/env python3
"""Functional apoptotic-priming ingestion (BH3 profiling / dynamic BH3 profiling).

>>> SCHEMA STUB — PENDING REAL DATA. Emits NO numbers until a real priming table is placed
>>> at data/raw/bh3_profiling.csv. This is the hook that upgrades the executioner-loss
>>> construct from an EXPRESSION proxy (weak, per M3) to a FUNCTIONAL readout.

Why this is the key upgrade: the thesis is "the cell cannot execute MOMP." BH3 profiling
measures that directly. When real priming data lands, a functional executioner-competence
feature feeds:
  - M1 as a 4th executioner-loss component (functional, not expression),
  - M2/M3 as a predictor expected to carry far more signal than expression,
  - M5 as the executioner-deficiency half of the susceptibility score.

Expected schema (data/raw/bh3_profiling.csv), one row per sample:
  sample_id            join key to expression/drug tables (dbGaP RNA sample id, etc.)
  overall_priming      % response to a promiscuous BH3 peptide (BIM/PUMA) in [0,100]
  bad_response         % to BAD  -> BCL2/BCL-xL dependence
  ms1_response         % to MS1  -> MCL1 dependence
  hrk_response         % to HRK  -> BCL-xL dependence   (optional)
  venetoclax_auc       optional, for direct validation

Executioner-competence (functional loss) is inferred as LOW overall priming DESPITE HIGH
guardian dependence: a cell that is 'primed to depend' but 'cannot execute'. Threshold in
config (added when data arrives), not hard-coded here.
"""
from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
RAW = ROOT / CFG["paths"]["data_raw"]
PRIMING = RAW / "bh3_profiling.csv"

REQUIRED = ["sample_id", "overall_priming", "bad_response", "ms1_response"]


def available() -> bool:
    return PRIMING.exists()


def load() -> pd.DataFrame:
    if not available():
        raise FileNotFoundError(
            f"{PRIMING} not present. This is expected until BH3-profiling data is acquired "
            "(see acquisition/functional_priming_targets.md). No numbers are produced."
        )
    df = pd.read_csv(PRIMING)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"bh3_profiling.csv missing required columns: {missing}")
    return df.set_index("sample_id")


def functional_executioner_deficiency(df: pd.DataFrame, priming_lo=25.0,
                                      dependence_hi=25.0) -> pd.Series:
    """LOW overall priming DESPITE HIGH guardian dependence = 'cannot execute' → the
    functional analogue of executioner loss. Thresholds are placeholders; move to
    config.yaml (executioner_loss.functional_*) when real data defines them."""
    guardian_dep = df[["bad_response", "ms1_response"]].max(axis=1)
    can_depend = guardian_dep >= dependence_hi
    cannot_execute = df["overall_priming"] <= priming_lo
    return (can_depend & cannot_execute).astype(float)


def report_status():
    if available():
        df = load()
        print(f"[functional] BH3-profiling present: {df.shape[0]} samples. "
              "Wire into M1/M2/M3/M5 (see module docstrings).")
    else:
        print("[functional] PENDING REAL DATA — no BH3-profiling table found. "
              "Schema + ingestion ready (see acquisition/functional_priming_targets.md).")


if __name__ == "__main__":
    report_status()
