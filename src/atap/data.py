"""
data.py — loaders for the real public cohorts plus a schema-faithful simulator.

The loaders expect files downloaded into data/raw/ (see docs/DATA.md for exact URLs
and filenames). Each returns the *same* canonical objects the rest of the pipeline
consumes, so DepMap, BeatAML, TCGA and the simulator are interchangeable:

    Cohort(
        expr       : DataFrame  samples x genes, log-scale expression
        mutations  : DataFrame  long: sample, gene, variant_class, protein_change
        meta       : DataFrame  sample x [lineage, disease, ...]
        response   : DataFrame  optional sample x [venetoclax_sensitive, ...]
        dependency : DataFrame  optional samples x genes CRISPR gene-effect (DepMap)
    )

The simulator embeds ground truth (a hidden BAX/BAK-loss flag and a downstream-
execution flag) so that recovering the 'salvage_target' population is a real check on
the scoring logic, not a tautology. Replace `load_simulated` with `load_depmap` /
`load_beataml` / `load_tcga` once the files are in place — nothing else changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from . import biology

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"


@dataclass
class Cohort:
    name: str
    expr: pd.DataFrame
    mutations: pd.DataFrame
    meta: pd.DataFrame
    response: pd.DataFrame | None = None
    dependency: pd.DataFrame | None = None

    def __repr__(self) -> str:
        return (f"Cohort(name={self.name!r}, n_samples={self.expr.shape[0]}, "
                f"n_genes={self.expr.shape[1]}, "
                f"n_mutations={0 if self.mutations is None else len(self.mutations)}, "
                f"has_response={self.response is not None})")


# ======================================================================================
# Simulator — scientifically structured synthetic cohort
# ======================================================================================

def load_simulated(
    n: int = 400,
    seed: int = 7,
    heme_only: bool = True,
) -> Cohort:
    """
    Generate a cohort whose covariance structure encodes the ATAP hypothesis, so the
    pipeline can be validated end-to-end before real data lands.

    Latent ground-truth per sample (returned in meta, prefixed 'gt_'):
      gt_effector_loss : BAX/BAK functionally lost -> venetoclax class fails
      gt_exec_loss     : apoptosome/caspase silenced -> BOTH agents fail (hard escape)
      gt_mcl1_switch   : leans on MCL1/BCL-XL -> venetoclax fails, effectors intact
      gt_class         : the true label {standard_of_care, salvage_target, hard_escape}

    Expected recovery: samples with gt_effector_loss & intact execution should land in
    'salvage_target'; gt_exec_loss should land in 'hard_escape'.
    """
    rng = np.random.default_rng(seed)
    genes = biology.all_genes()
    samples = [f"SIM_{i:04d}" for i in range(n)]

    # Latent states with clinically plausible prevalence.
    effector_loss = rng.random(n) < 0.18     # BAX/BAK loss ~ resistant subset
    mcl1_switch = rng.random(n) < 0.22        # guardian switching
    exec_loss = rng.random(n) < 0.10          # downstream silencing
    primed = rng.random(n) < 0.55             # priming tone
    bcl2_high = (rng.random(n) < 0.45) & (~mcl1_switch)

    # Baseline log-expression ~ N(4, 1) per gene, then shift by latent state.
    base = rng.normal(4.0, 1.0, size=(n, len(genes)))
    expr = pd.DataFrame(base, index=samples, columns=genes)

    def shift(gene, mask, delta):
        if gene in expr.columns:
            expr.loc[mask, gene] += delta

    # BCL2-dependence axis
    shift("BCL2", bcl2_high, +2.2)
    for g in ("MCL1", "BCL2L1"):
        shift(g, mcl1_switch, +2.0)
    # Priming
    for g in biology.BH3_ACTIVATORS:
        shift(g, primed, +1.6)
    shift("PMAIP1", mcl1_switch, +1.2)  # NOXA up marks MCL1 dependence
    # Effector competence (expression component; LoF added via mutations below too)
    for g in ("BAX", "BAK1"):
        shift(g, effector_loss, -2.6)
    # Downstream execution
    for g in biology.EXECUTION_PRO:
        shift(g, exec_loss, -2.4)
    for g in biology.EXECUTION_ANTI:
        shift(g, exec_loss, +1.5)  # IAPs up when execution suppressed
    # Mito mass — mild independent variation, slightly lower in exec_loss
    for g in biology.MITO_MASS:
        shift(g, exec_loss, -0.6)

    expr = expr.clip(lower=0.0)

    # Mutations: give ~60% of effector-loss samples a bona fide BAX/BAK LoF call so
    # the mutation-override path in features.py is exercised.
    mut_records = []
    for i, s in enumerate(samples):
        if effector_loss[i] and rng.random() < 0.6:
            gene = "BAX" if rng.random() < 0.7 else "BAK1"
            vclass = rng.choice(["frameshift", "nonsense", "splice"])
            mut_records.append({"sample": s, "gene": gene, "variant_class": vclass,
                                "protein_change": ""})
        # a few BCL2 gatekeeper mutations (venetoclax-binding resistance, BAX intact)
        if (not effector_loss[i]) and bcl2_high[i] and rng.random() < 0.05:
            mut_records.append({"sample": s, "gene": "BCL2",
                                "variant_class": "missense",
                                "protein_change": "G101V"})
    mutations = pd.DataFrame(
        mut_records, columns=["sample", "gene", "variant_class", "protein_change"])

    # Ground-truth class for validation.
    gt_class = np.where(
        exec_loss, "hard_escape",
        np.where(effector_loss, "salvage_target",
                 np.where(mcl1_switch, "venetoclax_resistant_other", "standard_of_care")))

    lineage = rng.choice(["AML", "DLBCL", "CLL", "ALL"], size=n) if heme_only else \
        rng.choice(["AML", "DLBCL", "Lung", "Prostate"], size=n)
    meta = pd.DataFrame({
        "lineage": lineage,
        "disease": lineage,
        "gt_effector_loss": effector_loss.astype(int),
        "gt_mcl1_switch": mcl1_switch.astype(int),
        "gt_exec_loss": exec_loss.astype(int),
        "gt_primed": primed.astype(int),
        "gt_class": gt_class,
    }, index=samples)

    # Simulated venetoclax response readout (1 = sensitive): needs functional effectors,
    # execution, and BCL2-dependence; killed by MCL1 switch, effector loss, exec loss.
    p_sens = (0.85 * bcl2_high * (~effector_loss) * (~exec_loss) * (~mcl1_switch)
              + 0.15 * primed * (~effector_loss))
    veneto_sensitive = (rng.random(n) < np.clip(p_sens, 0, 1)).astype(int)
    response = pd.DataFrame({"venetoclax_sensitive": veneto_sensitive}, index=samples)

    return Cohort("simulated", expr, mutations, meta, response=response)


# ======================================================================================
# Real cohort loaders — activate once files are in data/raw/ (see docs/DATA.md)
# ======================================================================================

def _require(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. See docs/DATA.md for the download URL and expected name.")
    return path


def load_depmap(heme_only: bool = True) -> Cohort:
    """
    DepMap (23Q4+ schema). Expected files in data/raw/depmap/:
        OmicsExpressionProteinCodingGenesTPMLogp1.csv   (ModelID x gene, "GENE (id)")
        OmicsSomaticMutations.csv
        Model.csv                                       (lineage / OncotreeLineage)
        CRISPRGeneEffect.csv                            (optional)
    """
    d = RAW / "depmap"
    expr = _read_depmap_expression(_require(d / "OmicsExpressionProteinCodingGenesTPMLogp1.csv"))
    model = pd.read_csv(_require(d / "Model.csv")).set_index("ModelID")
    meta = model.rename(columns={"OncotreeLineage": "lineage"})
    if "lineage" not in meta.columns and "lineage_1" in model.columns:
        meta["lineage"] = model["lineage_1"]
    meta["disease"] = meta.get("OncotreePrimaryDisease", meta.get("lineage"))

    if heme_only:
        heme = meta["lineage"].astype(str).str.contains(
            "Myeloid|Lymph|Leuk|Blood|Plasma", case=False, na=False)
        keep = meta.index[heme]
        expr = expr.reindex(keep).dropna(how="all")
        meta = meta.loc[expr.index]

    muts = _read_depmap_mutations(d / "OmicsSomaticMutations.csv", set(expr.index))

    dep = None
    dep_path = d / "CRISPRGeneEffect.csv"
    if dep_path.exists():
        dep = _read_depmap_expression(dep_path).reindex(expr.index)

    return Cohort("depmap", expr, muts, meta, dependency=dep)


def load_beataml() -> Cohort:
    """
    BeatAML (Tyner et al., Vizome). Expected in data/raw/beataml/:
        beataml_expression.tsv     (genes x samples or samples x genes CPM/TPM)
        beataml_mutations.tsv
        beataml_drug_response.tsv  (inhibitor, auc/ic50 per sample; venetoclax rows)
        beataml_clinical.tsv       (optional)
    Wraps venetoclax ex-vivo AUC into a binary `venetoclax_sensitive` (low AUC = sensitive).
    """
    d = RAW / "beataml"
    expr = _read_matrix_auto(_require(d / "beataml_expression.tsv"))
    muts = _read_beataml_mutations(d / "beataml_mutations.tsv", set(expr.index))
    meta = pd.DataFrame(index=expr.index)
    meta["lineage"] = "AML"; meta["disease"] = "AML"
    resp = _read_beataml_response(d / "beataml_drug_response.tsv", set(expr.index))
    return Cohort("beataml", expr, muts, meta, response=resp)


def load_tcga(project: str = "TCGA-LAML") -> Cohort:
    """
    TCGA via GDC. Expected in data/raw/tcga/<project>/:
        expression.tsv   (samples x genes, log2(TPM+1) or FPKM-UQ)
        mutations.maf     (MAF; Hugo_Symbol, Variant_Classification, HGVSp_Short)
    """
    d = RAW / "tcga" / project
    expr = _read_matrix_auto(_require(d / "expression.tsv"))
    muts = _read_maf(d / "mutations.maf", set(expr.index))
    meta = pd.DataFrame(index=expr.index)
    meta["lineage"] = project; meta["disease"] = project
    return Cohort(f"tcga:{project}", expr, muts, meta)


# ---- format adapters -----------------------------------------------------------------

def _read_depmap_expression(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0)
    # DepMap columns are "SYMBOL (entrez)" -> strip to SYMBOL, keep only our genes.
    df.columns = [c.split(" (")[0] for c in df.columns]
    keep = [g for g in biology.all_genes() if g in df.columns]
    return df[keep].astype(float)


def _read_matrix_auto(path: Path) -> pd.DataFrame:
    """Read a gene-expression matrix and orient it as samples x genes for our genes."""
    sep = "\t" if path.suffix in (".tsv", ".txt") else ","
    df = pd.read_csv(path, sep=sep, index_col=0)
    ours = set(biology.all_genes())
    if len(ours & set(df.index)) > len(ours & set(df.columns)):
        df = df.T  # genes were rows -> transpose to samples x genes
    keep = [g for g in biology.all_genes() if g in df.columns]
    return df[keep].astype(float)


def _read_depmap_mutations(path: Path, samples: set[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["sample", "gene", "variant_class", "protein_change"])
    m = pd.read_csv(path, usecols=lambda c: c in {
        "ModelID", "HugoSymbol", "VariantInfo", "VariantType",
        "ProteinChange", "VepImpact"}, low_memory=False)
    m = m.rename(columns={"ModelID": "sample", "HugoSymbol": "gene",
                          "VariantInfo": "variant_class", "ProteinChange": "protein_change"})
    m = m[m["gene"].isin(biology.all_genes()) & m["sample"].isin(samples)]
    for c in ("variant_class", "protein_change"):
        if c not in m.columns:
            m[c] = ""
    return m[["sample", "gene", "variant_class", "protein_change"]].reset_index(drop=True)


def _read_beataml_mutations(path: Path, samples: set[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["sample", "gene", "variant_class", "protein_change"])
    m = pd.read_csv(path, sep="\t")
    ren = {}
    for cand, std in [("dbgap_sample_id", "sample"), ("sample", "sample"),
                      ("symbol", "gene"), ("hgvsp", "protein_change"),
                      ("consequence", "variant_class"), ("variant_class", "variant_class")]:
        if cand in m.columns:
            ren[cand] = std
    m = m.rename(columns=ren)
    for c in ("sample", "gene", "variant_class", "protein_change"):
        if c not in m.columns:
            m[c] = ""
    m = m[m["gene"].isin(biology.all_genes())]
    return m[["sample", "gene", "variant_class", "protein_change"]].reset_index(drop=True)


def _read_maf(path: Path, samples: set[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["sample", "gene", "variant_class", "protein_change"])
    m = pd.read_csv(path, sep="\t", comment="#", low_memory=False)
    m = m.rename(columns={"Hugo_Symbol": "gene",
                          "Variant_Classification": "variant_class",
                          "HGVSp_Short": "protein_change",
                          "Tumor_Sample_Barcode": "sample"})
    m["sample"] = m["sample"].astype(str).str[:15]  # patient/sample barcode
    m = m[m["gene"].isin(biology.all_genes())]
    for c in ("variant_class", "protein_change"):
        if c not in m.columns:
            m[c] = ""
    return m[["sample", "gene", "variant_class", "protein_change"]].reset_index(drop=True)


def _read_beataml_response(path: Path, samples: set[str]) -> pd.DataFrame | None:
    if not path.exists():
        return None
    r = pd.read_csv(path, sep="\t")
    cols = {c.lower(): c for c in r.columns}
    inh = cols.get("inhibitor") or cols.get("drug")
    auc = cols.get("auc") or cols.get("area_under_curve")
    smp = cols.get("dbgap_sample_id") or cols.get("sample")
    if not (inh and auc and smp):
        return None
    ven = r[r[inh].astype(str).str.contains("Venetoclax|ABT-199|ABT199", case=False, na=False)]
    if not len(ven):
        return None
    a = ven.groupby(smp)[auc].median()
    # Low AUC = sensitive. Split at cohort median.
    sensitive = (a < a.median()).astype(int)
    return pd.DataFrame({"venetoclax_sensitive": sensitive})
