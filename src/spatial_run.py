#!/usr/bin/env python3
"""M7 driver — apply the routing pipeline to the REAL 10x Human Lymph Node Visium section.

Lymph node is a secondary lymphoid organ (the tissue of origin for many lymphomas) and all
six BCL-2-family panel genes are detectably expressed, so it clears QC as a heme-relevant
spatial section (spec §3). Output: per-spot executioner/guardian state, routing category,
and per-spot S³ stability. Expression-based inference only; a PREDICTED routing map, not a
treatment map (GUARDRAILS §3).
"""
from __future__ import annotations
import sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import scanpy as sc
import yaml

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import spatial  # noqa: E402

CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
PROC = ROOT / CFG["paths"]["data_processed"]
LOGS = ROOT / CFG["paths"]["outputs_logs"]
H5AD = ROOT / "data" / "interim" / "spatial_lymphnode.h5ad"
PANEL = ["BAX", "BAK1", "BCL2", "MCL1", "BCL2A1", "BCL2L1"]


def run():
    ad = sc.read_h5ad(H5AD)
    ad.var_names_make_unique()
    n0 = ad.n_obs
    qc = CFG["spatial"]["qc"]
    sc.pp.calculate_qc_metrics(ad, inplace=True, percent_top=None)
    ad = ad[(ad.obs["total_counts"] >= qc["min_counts_per_spot"]) &
            (ad.obs["n_genes_by_counts"] >= qc["min_genes_per_spot"])].copy()
    # normalize + log
    sc.pp.normalize_total(ad, target_sum=1e4)
    sc.pp.log1p(ad)

    genes = [g for g in PANEL if g in ad.var_names]
    X = ad[:, genes].X
    X = X.toarray() if hasattr(X, "toarray") else np.asarray(X)
    expr = pd.DataFrame(X, columns=genes, index=ad.obs_names)
    coords = pd.DataFrame(ad.obsm["spatial"], columns=["x", "y"], index=ad.obs_names)
    # Visium y axis: flip so images read naturally
    coords["y"] = coords["y"].max() - coords["y"]

    r = spatial.routing_with_stability(expr, coords)
    out = expr.add_prefix("expr_").join(coords).join(r)
    out.to_csv(PROC / "spatial_lymphnode_routing.csv")

    counts = out["routing"].value_counts()
    lines = ["# M7 report — spatial priming + routing (REAL 10x Human Lymph Node Visium)", "",
             "> Expression-based inference. A PREDICTED routing map, not a treatment map "
             "(GUARDRAILS §3). Lymph node = lymphoid tissue of origin for lymphomas.", "",
             f"- Spots after QC: {ad.n_obs} / {n0} "
             f"(min counts {qc['min_counts_per_spot']}, min genes {qc['min_genes_per_spot']}).",
             f"- Panel genes mapped: {genes}", "",
             "## Routing distribution (per spot)", "",
             "| category | spots | % |", "|----------|-------|---|"]
    for cat, n in counts.items():
        lines.append(f"| {cat} | {n} | {100*n/len(out):.1f} |")
    lines += ["",
              f"- Mean per-spot stability (S³): {out['stability'].mean():.2f} "
              f"(across {int(out['n_specs'].iloc[0])} spatial analytic choices).",
              f"- Bypass-required spots mean stability {out.loc[out.routing=='bypass-required','stability'].mean():.2f}.",
              "",
              "**Interpretation:** intratumoral/inter-niche heterogeneity in "
              "executioner-vs-guardian state is quantifiable in real lymphoid tissue. "
              "'Bypass-required' spots (guardian-dependent yet executioner-low) are where a "
              "BAX-independent agent is *mechanistically rational*; 'venetoclax-sufficient' "
              "spots retain executioners. This poses executioner availability as a spatial "
              "routing question — an expression-based hypothesis, not evidence of efficacy."]
    (LOGS / "M7_report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return out


if __name__ == "__main__":
    run()
