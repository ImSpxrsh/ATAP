#!/usr/bin/env python3
"""M0 harmonization — build analysis-ready tables in data/processed/ from raw downloads.

Outputs (one row per sample, panel-gene features + executioner-loss + drug response):
  data/processed/depmap_celllines.csv   heme cell lines: expr/CN/mut panel + GDSC ven/navi
  data/processed/beataml_patients.csv    Beat AML patients: expr/mut panel + ex vivo ven AUC
  data/processed/tcga_LAML.csv           TCGA-LAML: expr/CN/mut panel + clinical
  data/processed/tcga_DLBC.csv           TCGA-DLBC: expr/CN/mut panel + clinical

Gene symbols are the harmonization key within each dataset; cross-dataset joins use the
panel symbols directly. Cell-line identifiers harmonize to DepMap ModelID (GDSC mapped
via COSMIC ID / Sanger model ID from Model.csv). Never edits raw files in place.
"""
from __future__ import annotations
import re, sys
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import panels  # noqa: E402

CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
RAW = ROOT / CFG["paths"]["data_raw"]
PROC = ROOT / CFG["paths"]["data_processed"]
PROC.mkdir(parents=True, exist_ok=True)
SIG = panels.all_signature_genes()
HEME = set(CFG["heme_lineages"])


def _depmap_wide_panel(path: Path, genes: list[str]) -> pd.DataFrame:
    """Read only panel-gene columns from a DepMap 'SYMBOL (ENTREZ)' wide matrix."""
    header = pd.read_csv(path, nrows=0)
    cols = list(header.columns)
    sym = {c: re.sub(r"\s*\(\d+\)$", "", c) for c in cols[1:]}
    keep = {c: s for c, s in sym.items() if s in set(genes)}
    use = [cols[0]] + list(keep)
    df = pd.read_csv(path, usecols=use, index_col=0)
    df.columns = [keep[c] for c in df.columns]
    df.index.name = "ModelID"
    return df


def build_depmap() -> pd.DataFrame:
    model = pd.read_csv(RAW / "Model.csv")
    heme = model[model["OncotreeLineage"].isin(HEME)
                 | model["OncotreePrimaryDisease"].str.contains(
                     "Leukemia|Lymphoma|Myeloma", case=False, na=False)].copy()
    heme_ids = set(heme["ModelID"])
    print(f"  DepMap heme models: {len(heme_ids)} / {len(model)}")

    expr = _depmap_wide_panel(RAW / "OmicsExpressionProteinCodingGenesTPMLogp1.csv", SIG)
    cn = _depmap_wide_panel(RAW / "OmicsCNGene.csv", SIG)
    expr_h = expr[expr.index.isin(heme_ids)]
    cn_h = cn[cn.index.isin(heme_ids)]

    mut = pd.read_csv(RAW / "OmicsSomaticMutations.csv",
                      usecols=["HugoSymbol", "ModelID", "VariantInfo", "ProteinChange"],
                      low_memory=False)
    mut_h = mut[mut["ModelID"].isin(heme_ids)]

    # Executioner loss computed on heme cohort (quantiles are within-heme).
    elt = panels.executioner_loss_table(
        expr=expr_h, cn=cn_h, mut=mut_h,
        mut_cols={"gene": "HugoSymbol", "sample": "ModelID", "cls": "VariantInfo"},
    )

    out = heme.set_index("ModelID")[["StrippedCellLineName", "OncotreeLineage",
                                     "OncotreePrimaryDisease", "COSMICID", "SangerModelID"]]
    out = out.join(expr_h.add_prefix("expr_"))
    out = out.join(cn_h.add_prefix("cn_"))
    out = out.join(elt)

    # GDSC drug response -> map to ModelID
    gdsc = _load_gdsc()
    if gdsc is not None:
        out = out.join(gdsc, how="left")
    out.to_csv(PROC / "depmap_celllines.csv")
    print(f"  wrote depmap_celllines.csv: {out.shape[0]} lines x {out.shape[1]} cols")
    return out


def _load_gdsc() -> pd.DataFrame | None:
    frames = []
    for f, ver in [("GDSC1_fitted_dose_response_24Jul22.csv", "GDSC1"),
                   ("GDSC2_fitted_dose_response_24Jul22.csv", "GDSC2")]:
        p = RAW / f
        if not p.exists():
            continue
        d = pd.read_csv(p)
        d["GDSC_VERSION"] = ver
        frames.append(d)
    if not frames:
        print("  GDSC not present yet — skipping drug-response merge")
        return None
    g = pd.concat(frames, ignore_index=True)
    g.columns = [c.upper() for c in g.columns]
    name_col = "DRUG_NAME"
    drug_map = {"venetoclax": ["venetoclax", "abt-199", "abt199", "gdc-0199"],
                "navitoclax": ["navitoclax", "abt-263", "abt263"]}
    g["_dn"] = g[name_col].astype(str).str.lower()
    model = pd.read_csv(RAW / "Model.csv")[["ModelID", "COSMICID", "SangerModelID"]]
    cosmic2model = model.dropna(subset=["COSMICID"]).assign(
        COSMICID=lambda d: d["COSMICID"].astype("Int64").astype(str))
    cosmic2model = dict(zip(cosmic2model["COSMICID"], cosmic2model["ModelID"]))
    sanger2model = dict(zip(model.dropna(subset=["SangerModelID"])["SangerModelID"],
                            model.dropna(subset=["SangerModelID"])["ModelID"]))
    rows = {}
    for drug, aliases in drug_map.items():
        sub = g[g["_dn"].isin(aliases)]
        if sub.empty:
            print(f"  GDSC: no rows for {drug}")
            continue
        # map COSMIC_ID / SANGER_MODEL_ID to ModelID
        def to_model(r):
            cid = r.get("COSMIC_ID")
            if pd.notna(cid) and str(int(cid)) in cosmic2model:
                return cosmic2model[str(int(cid))]
            sid = r.get("SANGER_MODEL_ID")
            if isinstance(sid, str) and sid in sanger2model:
                return sanger2model[sid]
            return np.nan
        sub = sub.copy()
        sub["ModelID"] = sub.apply(to_model, axis=1)
        sub = sub.dropna(subset=["ModelID"])
        agg = sub.groupby("ModelID").agg(LN_IC50=("LN_IC50", "mean"), AUC=("AUC", "mean"))
        rows[f"{drug}_LN_IC50"] = agg["LN_IC50"]
        rows[f"{drug}_AUC"] = agg["AUC"]
        print(f"  GDSC {drug}: {agg.shape[0]} heme+non-heme lines mapped")
    if not rows:
        return None
    return pd.DataFrame(rows)


def build_beataml() -> pd.DataFrame:
    # normalized expression: genes in rows? Detect orientation.
    exp = pd.read_csv(RAW / "beataml_waves1to4_norm_exp_dbgap.txt", sep="\t")
    # first columns are gene identifiers; sample columns are BA####
    id_cols = [c for c in exp.columns if not re.match(r"^BA\d", str(c))][:5]
    gene_key = "display_label" if "display_label" in exp.columns else exp.columns[0]
    sample_cols = [c for c in exp.columns if re.match(r"^BA\d", str(c))]
    e = exp[exp[gene_key].isin(SIG)].set_index(gene_key)[sample_cols]
    expr = e.T  # samples x genes
    expr.index.name = "rnaseq_sample"

    auc = pd.read_csv(RAW / "beataml_probit_curve_fits_v4_dbgap.txt", sep="\t")
    ven = auc[auc["inhibitor"].astype(str).str.contains("Venetoclax", case=False, na=False)]
    ven = ven.dropna(subset=["dbgap_rnaseq_sample"])
    ven_auc = ven.groupby("dbgap_rnaseq_sample")["auc"].mean()
    ven_ic50 = ven.groupby("dbgap_rnaseq_sample")["ic50"].mean()

    # DNA-sample -> RNA-sample crosswalk (mutations are keyed by DNA sample, expression
    # by RNA sample). The probit file carries both per row; build the map from it.
    xwalk = (auc.dropna(subset=["dbgap_dnaseq_sample", "dbgap_rnaseq_sample"])
                .drop_duplicates("dbgap_dnaseq_sample")
                .set_index("dbgap_dnaseq_sample")["dbgap_rnaseq_sample"].to_dict())

    mut = pd.read_csv(RAW / "beataml_wes_wv1to4_mutations_dbgap.txt", sep="\t", low_memory=False)
    # find gene + sample + consequence columns
    gcol = _pick(mut, ["symbol", "hgnc_symbol", "gene", "Hugo_Symbol"])
    dna_scol = _pick(mut, ["dbgap_dnaseq_sample", "dbgap_sample_id", "sample", "labId"])
    ccol = _pick(mut, ["consequence", "variant_classification", "so_term", "type"])
    if dna_scol:
        mut = mut.copy()
        mut["rnaseq_sample"] = mut[dna_scol].map(xwalk)
    scol = "rnaseq_sample"

    elt = panels.executioner_loss_table(
        expr=expr,
        mut=mut if (gcol and scol and ccol) else None,
        mut_cols={"gene": gcol, "sample": scol, "cls": ccol} if (gcol and scol and ccol) else None,
        samples=expr.index,
    )
    out = expr.add_prefix("expr_").join(elt)
    out = out.join(ven_auc.rename("venetoclax_AUC"))
    out = out.join(ven_ic50.rename("venetoclax_IC50"))
    out.to_csv(PROC / "beataml_patients.csv")
    print(f"  wrote beataml_patients.csv: {out.shape[0]} patients x {out.shape[1]} cols; "
          f"{out['venetoclax_AUC'].notna().sum()} with venetoclax AUC")
    return out


def build_tcga(label: str) -> pd.DataFrame:
    expr = pd.read_csv(RAW / f"cbio_{label}_expression.csv", index_col=0)
    cn_p = RAW / f"cbio_{label}_cna.csv"
    cn = pd.read_csv(cn_p, index_col=0) if cn_p.exists() else None
    mut = pd.read_csv(RAW / f"cbio_{label}_mutations.csv")
    # cBioPortal mutations store entrezGeneId (symbol was nested); map back to symbol.
    entrez2sym = {v: k for k, v in CFG["entrez_ids"].items()}
    if "hugoGeneSymbol" not in mut.columns and "entrezGeneId" in mut.columns:
        mut = mut.copy()
        mut["hugoGeneSymbol"] = mut["entrezGeneId"].map(entrez2sym)
    # cBioPortal expression is linear RSEM; log2 for quantile stability
    expr_l = np.log2(expr.clip(lower=0) + 1)
    # cBioPortal gistic CN: -2 deep del. Map to our log2 cutoff via a gistic rule.
    elt = panels.executioner_loss_table(
        expr=expr_l, cn=None,  # gistic handled separately below
        mut=mut, mut_cols={"gene": "hugoGeneSymbol", "sample": "sampleId", "cls": "mutationType"},
        samples=expr_l.index,
    )
    if cn is not None:
        # gistic: executioner deep deletion = -2 in BAX or BAK1
        ex = [g for g in CFG["panels"]["executioners"] if g in cn.columns]
        deep = (cn[ex] <= -2).any(axis=1).reindex(elt.index).fillna(False)
        elt["cn_del_gistic"] = deep
        elt["executioner_loss_call"] = elt["executioner_loss_call"] | deep
    clin_p = RAW / f"cbio_{label}_clinical.csv"
    clin = pd.read_csv(clin_p, index_col=0) if clin_p.exists() else None
    out = expr_l.add_prefix("expr_").join(elt)
    if cn is not None:
        out = out.join(cn.add_prefix("cn_"))
    if clin is not None:
        keep = [c for c in clin.columns if c in ("SUBTYPE", "CANCER_TYPE_DETAILED",
                "AJCC_PATHOLOGIC_TUMOR_STAGE", "OS_STATUS", "OS_MONTHS")]
        out = out.join(clin[keep])
    out.to_csv(PROC / f"tcga_{label}.csv")
    print(f"  wrote tcga_{label}.csv: {out.shape[0]} x {out.shape[1]}")
    return out


def _pick(df, candidates):
    lower = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    return None


def main():
    which = sys.argv[1:] or ["depmap", "beataml", "tcga"]
    if "depmap" in which:
        print("[DepMap]"); build_depmap()
    if "beataml" in which:
        print("[BeatAML]"); build_beataml()
    if "tcga" in which:
        print("[TCGA]")
        build_tcga("LAML")
        build_tcga("DLBC")


if __name__ == "__main__":
    main()
