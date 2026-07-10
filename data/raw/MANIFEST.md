# data/raw MANIFEST — source, version, date for every real dataset

Nothing in `data/raw/` is committed (gitignored, large public files). This manifest records exactly
what was downloaded so every empirical result is reproducible (GUARDRAILS.md #6).

## BeatAML — ex-vivo venetoclax drug response (M2/M3/M1 validation)
- **Source:** `biodev/beataml2.0_data` GitHub repo (Bottomly et al., *Cancer Cell* 2022), via the
  Git-LFS media endpoint `https://media.githubusercontent.com/media/biodev/beataml2.0_data/main/`.
- **File:** `beataml_probit_curve_fits_v4_dbgap.txt` (per-sample per-inhibitor probit fits incl.
  venetoclax `auc`), saved as `data/raw/beataml/beataml_probit_curve_fits_v4.txt`.
- **Downloaded:** 2026-07-09. Venetoclax rows: 430; unique RNA-seq samples with AUC: 382.
- **Expression + mutations** for the same study come live from the cBioPortal REST API
  (`aml_ohsu_2022`), not a local file — see `atap.data.load_cbioportal`.

## DepMap 24Q2 Public — cell-line expression / mutations / CRISPR (M1 fair test bed)
- **Source:** figshare article **25880521** ("DepMap 24Q2 Public"), files via
  `https://ndownloader.figshare.com/files/<id>`.
- **Downloaded:** 2026-07-09 into `data/raw/depmap/`.

  | File | figshare id | size |
  |------|-------------|------|
  | `Model.csv` | 46489732 | 0.6 MB |
  | `CRISPRGeneEffect.csv` | 46489063 | 419 MB |
  | `OmicsExpressionProteinCodingGenesTPMLogp1.csv` | 46490878 | 461 MB |
  | `OmicsSomaticMutations.csv` | 46500367 | 314 MB |

- **Heme subset:** 296 cell lines with `OncotreeLineage` in {Myeloid, Lymphoid} (of 1959).
- **Drug sensitivity (venetoclax/navitoclax):** PRISM Repurposing / GDSC ABT-199/ABT-263 not yet
  fetched — separate figshare article / GDSC download; TODO next cycle.

## GDSC2 — cell-line BH3-mimetic dose-response (cross-cohort replication)
- **Source:** cancerrxgene.org release 8.5,
  `https://cog.sanger.ac.uk/cancerrxgene/GDSC_release8.5/GDSC2_fitted_dose_response_27Oct23.xlsx`
  saved as `data/raw/gdsc/GDSC2_fitted_dose_response.xlsx` (~21 MB).
- **Downloaded:** 2026-07-09. 242,036 curve fits; Venetoclax 958 lines, Navitoclax 967 lines
  (LN_IC50, AUC per SANGER_MODEL_ID). Joined to DepMap heme expression via SangerModelID:
  **113 heme lines** with venetoclax + expression (115 for navitoclax).

## Not yet acquired (see docs/DATA.md)
- GDSC1/GDSC2 dose-response, TCGA (LAML/DLBC), public heme spatial section for M7.
