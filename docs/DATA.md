# Data provenance & download instructions

The pipeline runs today on a **schema-faithful simulator** (`atap.data.load_simulated`)
so nothing below is required to reproduce the demo. To run on real cohorts, download
the files into `data/raw/<cohort>/` with the names the loaders expect, then pass
`--cohort depmap|beataml|tcga` to `scripts/01_predict_bulk.py`. No other code changes.

Nothing in `data/raw/` is committed (see `.gitignore`) — these are large public files.

---

## 1. DepMap (cell lines: expression, mutations, CRISPR dependency, drug response)

Portal: https://depmap.org/portal/data_page/ (release 23Q4 or newer)

Put in `data/raw/depmap/`:

| File | Used for |
|------|----------|
| `OmicsExpressionProteinCodingGenesTPMLogp1.csv` | expression (log2 TPM+1) |
| `OmicsSomaticMutations.csv` | BAX/BAK1 LoF + BCL2 gatekeeper mutations |
| `Model.csv` | lineage filter (Myeloid / Lymphoid) |
| `CRISPRGeneEffect.csv` *(optional)* | functional BCL2/MCL1/BAX dependency |
| `PRISM Repurposing` or `sanger-viability` *(optional)* | venetoclax sensitivity for calibration |

Heme lines are selected by `OncotreeLineage` matching Myeloid/Lymphoid/Leukemia/Blood/Plasma.

## 1b. cBioPortal live API (no download, no registration — real patients in seconds)

`atap.data.load_cbioportal(study="aml_ohsu_2022")` fetches expression + mutations for the
~39-gene panel directly from the public cBioPortal REST API — run
`python scripts/03_score_real.py` to score 671 real BeatAML patients live. **Caveat:** the
cBioPortal BeatAML study exposes expression and mutations but **not** the venetoclax *ex-vivo*
AUC (only clinical induction-chemo response). So this route supports real-patient *prediction*
and internal mechanistic checks, but the venetoclax-response *validation* still needs the
ex-vivo drug-response table below (Vizome / Bottomly 2022 supplement).

## 2. BeatAML (primary AML: RNA-seq, WES, ex-vivo venetoclax response)

Tyner et al., *Nature* 2018; Bottomly et al., *Cancer Cell* 2022. Data via the
Vizome portal (http://vizome.org/) and the GDC / cBioPortal `beat_aml` study.

Put in `data/raw/beataml/`:

| File | Used for |
|------|----------|
| `beataml_expression.tsv` | expression (genes × samples or samples × genes) |
| `beataml_mutations.tsv` | BAX/BAK1 LoF |
| `beataml_drug_response.tsv` | **venetoclax ex-vivo AUC** → binary sensitivity (low AUC = sensitive) |
| `beataml_clinical.tsv` *(optional)* | annotation |

BeatAML is the key cohort: it has matched RNA-seq **and** venetoclax response, so it
both trains the calibration layer and tests whether predicted salvage-targets are the
venetoclax-resistant patients.

## 3. TCGA (bulk tumors: expression + mutations) via GDC

GDC Data Portal: https://portal.gdc.cancer.gov/ · API: https://api.gdc.cancer.gov/

Heme-relevant projects: `TCGA-LAML` (AML), `TCGA-DLBC` (DLBCL). Put in
`data/raw/tcga/<PROJECT>/`:

| File | Used for |
|------|----------|
| `expression.tsv` | STAR-counts → TPM or FPKM-UQ, samples × genes |
| `mutations.maf` | MAF (Hugo_Symbol, Variant_Classification, HGVSp_Short) |

TCGA has no venetoclax response, so it is used for prevalence estimation of the
salvage-target phenotype across a large patient set, not for calibration.

---

## Gene panel

All loaders subset to the ~39 genes in `atap.biology.all_genes()` (BCL-2 family,
BH3-only, apoptosome/caspase execution machinery, IAPs, and a mitochondrial-mass
signature). Keeping the panel small makes the loaders fast and platform-portable
(bulk RNA-seq, spatial, and targeted panels all carry these genes).
