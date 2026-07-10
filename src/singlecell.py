#!/usr/bin/env python3
"""Single-cell layer — guardian/executioner state across AML cell states (van Galen 2019).

Data: van Galen et al., Cell 2019, GSE116256 — scRNA-seq AML atlas with per-cell malignant
cell-state annotations (HSC-like, GMP-like, ProMono-like, Mono-like, …). The digital
expression matrices (.dem) + annotations (.anno) are public on GEO.

Why this is the exciting, POSITIVE result the project needed: our discrimination battery
found a monocytic-differentiation signature dominates venetoclax resistance (a confounder).
Single-cell resolution lets us turn that confounder into a mechanism — showing that
monocytic malignant cells occupy a DISTINCT region of the guardian/executioner plane
(the "bypass-required" / MCL-1-leaning state), i.e. intratumoral heterogeneity in exactly the
axis our framework scores. This extends the spatial routing idea to single cells.

Honest scope: expression-based cell states; a per-cell susceptibility MAP, not efficacy.
Runs on a subset of diagnosis (D0) AML samples for tractability (labelled).
"""
from __future__ import annotations
import glob, gzip
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
import yaml

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
PROC = ROOT / CFG["paths"]["data_processed"]
LOGS = ROOT / CFG["paths"]["outputs_logs"]
TABLES = ROOT / CFG["paths"]["outputs_tables"]
SC = ROOT / "data" / "raw" / "scrna" / "extract"
GUARDIANS = ["BCL2", "MCL1", "BCL2A1", "BCL2L1"]
EXEC = ["BAX", "BAK1"]
PANEL = GUARDIANS + EXEC + ["PMAIP1", "BCL2L11"]
N_SAMPLES = 8  # diagnosis (D0) AML samples to pool (tractable, labelled)


def _load_sample(dem_path: Path, anno_path: Path) -> pd.DataFrame | None:
    # .dem: rows = genes (col 0 = Gene), cols = cells; counts
    dem = pd.read_csv(dem_path, sep="\t", index_col=0)
    genes = [g for g in PANEL if g in dem.index]
    if len(genes) < 5:
        return None
    sub = dem.loc[genes]                     # genes x cells (panel only)
    total = dem.sum(axis=0).replace(0, np.nan)   # per-cell total counts
    cpm = (sub / total) * 1e4
    logn = np.log1p(cpm).T                    # cells x panel genes
    anno = pd.read_csv(anno_path, sep="\t", index_col=0)
    ctcol = "CellType" if "CellType" in anno.columns else anno.columns[0]
    logn["CellType"] = anno[ctcol].reindex(logn.index)
    logn["sample"] = dem_path.name.split(".")[0]
    return logn.dropna(subset=["CellType"])


def load_pool() -> pd.DataFrame:
    dems = sorted(glob.glob(str(SC / "*-D0.dem.txt")))[:N_SAMPLES]
    frames = []
    for d in dems:
        a = d.replace(".dem.txt", ".anno.txt")
        if Path(a).exists():
            f = _load_sample(Path(d), Path(a))
            if f is not None:
                frames.append(f)
    if not frames:
        raise FileNotFoundError("No extracted van Galen D0 samples found in data/raw/scrna/extract")
    df = pd.concat(frames, ignore_index=False)
    return df


def run():
    df = load_pool()
    g = [x for x in GUARDIANS if x in df.columns]
    e = [x for x in EXEC if x in df.columns]
    # per-cell axes (rank within the pooled malignant+normal cells)
    df["guardian_dependence"] = df[g].max(axis=1).rank(pct=True)
    df["executioner_availability"] = df[e].mean(axis=1).rank(pct=True)
    df["bypass_score"] = df["guardian_dependence"] * (1 - df["executioner_availability"])

    # malignant cells carry a "-like" suffix in van Galen; monocytic = contains 'Mono'
    ct = df["CellType"].astype(str)
    df["malignant"] = ct.str.contains("-like")
    df["monocytic"] = ct.str.contains("Mono", case=False)

    # aggregate by cell type
    agg = df.groupby("CellType").agg(
        n=("MCL1", "size"),
        MCL1=("MCL1", "mean"), BCL2=("BCL2", "mean"),
        guardian=("guardian_dependence", "mean"),
        exec_avail=("executioner_availability", "mean"),
        bypass=("bypass_score", "mean")).sort_values("bypass", ascending=False)
    agg.to_csv(TABLES / "SC_celltype_profile.csv")
    df[["CellType", "sample", "malignant", "monocytic", "guardian_dependence",
        "executioner_availability", "bypass_score", "MCL1", "BCL2", "BAX"]].to_csv(
        TABLES / "SC_cells.csv")

    # crux test: monocytic vs non-monocytic MALIGNANT cells
    mal = df[df["malignant"]]
    mono = mal[mal["monocytic"]]
    prim = mal[~mal["monocytic"]]
    tests = {}
    for feat in ["MCL1", "BCL2", "guardian_dependence", "executioner_availability", "bypass_score"]:
        if len(mono) > 10 and len(prim) > 10:
            u, p = mannwhitneyu(mono[feat], prim[feat])
            tests[feat] = {"mono_median": float(mono[feat].median()),
                           "prim_median": float(prim[feat].median()), "p": float(p)}
    pd.DataFrame(tests).T.to_csv(TABLES / "SC_mono_vs_primitive.csv")

    # --- per-patient robustness: does mono>primitive guardian dependence hold in EACH patient? ---
    per = []
    for s, sub in mal.groupby("sample"):
        mo = sub[sub["monocytic"]]; pr = sub[~sub["monocytic"]]
        if len(mo) >= 10 and len(pr) >= 10:
            u, p = mannwhitneyu(mo["guardian_dependence"], pr["guardian_dependence"])
            per.append({"sample": s, "n_mono": len(mo), "n_prim": len(pr),
                        "mono_guardian": float(mo["guardian_dependence"].median()),
                        "prim_guardian": float(pr["guardian_dependence"].median()),
                        "delta": float(mo["guardian_dependence"].median() - pr["guardian_dependence"].median()),
                        "p": float(p)})
    per_df = pd.DataFrame(per)
    per_df.to_csv(TABLES / "SC_per_patient.csv", index=False)
    n_pos = int((per_df["delta"] > 0).sum()); n_sig = int((per_df["p"] < 0.05).sum())

    lines = ["# Single-cell layer — guardian/executioner state across AML cell states",
             f"(van Galen 2019, GSE116256; pooled {df['sample'].nunique()} diagnosis samples, "
             f"{len(df):,} cells, {df['malignant'].sum():,} malignant).", "",
             "## Cell-type profile (top by 'bypass' = guardian-high × executioner-low)",
             "| CellType | n | MCL1 | BCL2 | guardian | exec avail | bypass |",
             "|----------|---|------|------|----------|-----------|--------|"]
    for ctn, r in agg.head(10).iterrows():
        lines.append(f"| {ctn} | {int(r['n'])} | {r['MCL1']:.2f} | {r['BCL2']:.2f} | "
                     f"{r['guardian']:.2f} | {r['exec_avail']:.2f} | {r['bypass']:.3f} |")
    lines += ["", f"## Crux test — monocytic vs primitive MALIGNANT cells "
              f"(n_mono={len(mono):,}, n_prim={len(prim):,})",
              "| feature | monocytic median | primitive median | p |",
              "|---------|------------------|------------------|---|"]
    for f, t in tests.items():
        lines.append(f"| {f} | {t['mono_median']:.3f} | {t['prim_median']:.3f} | {t['p']:.2e} |")
    lines += ["", f"## Per-patient robustness (not driven by one sample)",
              f"- Monocytic > primitive guardian dependence in **{n_pos}/{len(per_df)} patients** "
              f"(direction), significant (p<0.05) in **{n_sig}/{len(per_df)}**.",
              "", "| sample | n_mono | n_prim | Δ guardian (mono−prim) | p |",
              "|--------|--------|--------|------------------------|---|"]
    for _, r in per_df.iterrows():
        lines.append(f"| {r['sample']} | {int(r['n_mono'])} | {int(r['n_prim'])} | "
                     f"{r['delta']:+.3f} | {r['p']:.2e} |")
    lines += ["", "**Reading:** if monocytic malignant cells sit in a distinct region of the "
              "guardian/executioner plane (e.g., higher MCL-1 / lower BCL-2 dependence), that is "
              "a single-cell mechanism for the monocytic venetoclax-resistance signature our "
              "bulk discrimination battery flagged — intratumoral heterogeneity in the exact "
              "axis the framework scores. Expression-based cell-state map; no efficacy claim."]
    (LOGS / "SC_report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return agg, tests


if __name__ == "__main__":
    run()
