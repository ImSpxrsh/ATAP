# Architecture — tech stack & how the pipelines work

This repo holds **two independent Python pipelines** that answer the same scientific question
from public data and cross-validate each other. This document explains the stack, the data
flow of each pipeline, and how they converge.

---

## 1. Tech stack

**Language:** Python 3.11–3.14 (both tracks are pure Python; no compiled extensions of our own).

**Scientific core**
| Library | Used for |
|---------|----------|
| `pandas`, `numpy` | all tabular omics wrangling, feature matrices |
| `scipy` | Spearman/Mann–Whitney, spatial KD-trees, stats |
| `scikit-learn` | ROC/AUC, ranking, model comparison |
| `statsmodels` | OLS backbone + confounder regressions (M2/M3), nested models |
| `lifelines` | survival hooks (TCGA, hypothesis-generating) |
| `scanpy` + `anndata` | spatial transcriptomics IO/QC/normalization (Visium `.h5ad`) |
| `squidpy` | spatial statistics (neighborhood graphs, Moran's I / Getis-Ord) |
| `matplotlib` | every figure (no seaborn; a shared house style in `figures/style.py`) |
| `pyyaml` | the single `config.yaml` both pipelines read |
| `requests` | data access (figshare, Sanger FTP, cBioPortal REST, GitHub raw) — `requests` not `urllib`, for TLS/cert handling |

**Data sources (all public, no synthetic biology)**
| Source | Release | Gives |
|--------|---------|-------|
| DepMap | 24Q4 (extended) / 24Q2 (core) | expression, CN, mutations, CRISPR, Model metadata |
| GDSC | 8.4 / 8.5 | ex-vivo drug dose-response (venetoclax, navitoclax, ABT-737, MCL1i, …) |
| Beat AML | 2.0 (Bottomly 2022) + cBioPortal `aml_ohsu_2022` | RNA, mutations, **ex-vivo venetoclax AUC** on 671 patients |
| TCGA | LAML, DLBC (cBioPortal PanCancer Atlas) | expression, GISTIC CN, mutations, clinical |
| 10x Genomics | Human Lymph Node Visium; glioblastoma | real spatial transcriptomics sections |

**Reproducibility spine:** one `config.yaml` (seeds, thresholds, gene panels, data-release IDs —
no magic numbers in code), pinned `environment.yml` / `requirements.txt`, seeded stochastic steps,
provenance in `data/raw/MANIFEST.md`. This is GUARDRAILS §6.

---

## 2. The shared scientific model (both tracks implement this)

The BCL-2 family is grouped into **mechanistic blocks**:
- **Guardians** — BCL2, MCL1, BCL2L1 (BCL-xL), BCL2A1 (Bfl-1): keep the cell alive; the drug targets.
- **Executioners** — BAX, BAK1: the pore-formers; **BH3-mimetics need these**.
- **Sensitizers/activators** — BIM, PUMA, NOXA, BID, BAD: push toward death.

Two derived axes drive everything:
1. **Guardian dependence** — how much the cell leans on a specific guardian (→ BH3-mimetic *sensitivity*).
2. **Executioner competence / loss** — whether BAX/BAK are present and functional (→ whether *any*
   BH3-mimetic can finish the job).

**The ATAP window** = guardian-dependent **AND** executioner-deficient: venetoclax predicted to
fail, a BAX-independent pore-former mechanistically rational. The susceptibility score is a
geometric mean of the two axes so both must be high.

---

## 3. Core-track pipeline (`src/atap/` + `scripts/`)

An importable OO library driven by numbered scripts.

```
src/atap/
  biology.py    gene panels + block definitions + prior signs (the fixed biology)
  data.py       Cohort — pulls omics from cBioPortal API / DepMap / GDSC, harmonizes IDs
  features.py   omics -> per-sample mechanistic blocks; z-score within cohort;
                mutation LoF OVERRIDES expression for executioner competence
  scoring.py    SusceptibilityModel — blocks -> venetoclax_score, salvage_index, quadrant call
  spatial.py    per-spot scoring + spatial autocorrelation (Moran's I / Getis-Ord)
```

**Data flow:**
```
cBioPortal API / DepMap / GDSC
      │  data.Cohort
      ▼
raw omics (expr + mutations)  ──features.build_feature_blocks──▶  mechanistic blocks
                                                                        │ scoring.SusceptibilityModel
                                                                        ▼
                            venetoclax_score / salvage_index / two-axis quadrant
                                                                        │  scripts/04
                                                                        ▼
              validate vs REAL BeatAML ex-vivo venetoclax AUC (ρ, permutation null, bootstrap CI)
```

**Scripts (`01`→`11`)** are the guided walkthrough: `01_predict_bulk` → `02_spatial_map` →
`03_score_real` → `04_validate_beataml` (the falsifiable M2 core) → `05_confounders_m3` →
`06_m1_executioner_subgroup` → `07_depmap_executioner` → `08_discrimination` (the
biology-vs-artifact battery) → `09_model_comparison` → `10_gdsc_replication` → `11_spec_curve`.
Run: `python scripts/NN_*.py` (each adds `src/` to path and reads `config.yaml`).

---

## 4. Extended-track pipeline (`src/*.py` + `figures/`)

Flat one-module-per-stage layout mapped to the build-spec modules **M0–M9**.

```
src/data/fetch_data.py   M0  download DepMap/GDSC/TCGA/BeatAML/spatial -> data/raw + MANIFEST
src/data/harmonize.py    M0  -> data/processed/{depmap_celllines,beataml_patients,tcga_*}.csv
src/panels.py            M1  executioner-loss logic (LoF | deep deletion | bottom-decile-both)
src/backbone.py          M2  OLS resistance ~ executioner_loss + lineage; 5k-perm null
src/confounders.py       M3  nested OLS: +MCL1, BCL2:BCL-xL ratio, BCL2 hotspot -> ΔR²/ΔAIC
src/multiverse.py        M4  360-spec specification curve + FDR + S³ stability
src/stratify.py          M5/M6  susceptibility = √(guardian_dep × exec_deficiency); subtype ranks
src/spatial.py           M7  routing() — dataset-agnostic per-spot routing + 81-spec S³ stability
src/spatial_run.py       M7  drive routing on real 10x Human Lymph Node Visium (scanpy)
src/panmimetic.py        (+) executioner loss vs pan-BH3-mimetic resistance (MCL1i crux test)
src/ablation.py          (+) which half of the susceptibility score carries the signal
src/validation.py        M8  SYNTHETIC ground-truth recovery, power curves, permutation nulls
src/priorart.py          M9  dated prior-art + IP gate log
src/functional.py        hook: ingest BH3-profiling data when acquired (PENDING REAL DATA)
figures/fig_*.py         F1–F13 generators (+ style.py house style) -> outputs/figures/
```

**Data flow:**
```
public sources ─fetch_data─▶ data/raw ─harmonize─▶ data/processed
                                                        │
        ┌───────────────────────┬───────────────────────┼───────────────────────┐
      M1 panels              M2 backbone            M5 stratify              M7 spatial_run
   executioner-loss   ─▶  resistance assoc  ─▶   susceptibility   +    real-Visium routing
        │                      │  M3 confounders       │  validate vs           │  S³ stability
        │                      │  M4 multiverse        │  observed venetoclax   │
        ▼                      ▼                       ▼                        ▼
     F3/F_M1               F4/F5/F6              F7/F8 + ablation           F9/F10
                                   M8 synthetic validation (F11/F12) · M9 prior-art
```

---

## 5. How the two tracks converge (the scientific payoff)

Both pipelines, from **different data conventions and different code**, independently find:

| Question | Core track | Extended track | Agreement |
|----------|-----------|----------------|-----------|
| Does guardian dependence predict venetoclax resistance? | ρ=−0.275 (BeatAML, p=5e-4) | ρ=0.50 guardian-only (DepMap), 0.27 (BeatAML) | **yes — real** |
| Does executioner loss add signal in cell lines/patients? | ΔR²≈+0.001, null | M3 ΔR²≈0.0006; pan-mimetic MCL1i null; ablation ρ≈0 | **no — null** |
| Is the composite better than BCL2 alone? | no (BCL2 alone ρ=−0.567) | guardian term carries it (ablation) | **consistent** |
| Is spatial routing detectable? | glioblastoma stability | lymph-node routing + S³ | **method works** |

**Conclusion both reach:** guardian dependence is the real, replicable signal; the
executioner-loss axis — where ATAP is mechanistically rational — is a **rare subset** that
public cell-line/expression data **cannot validate by construction**. The decisive next data is
**functional apoptotic priming (BH3 profiling)** or **engineered BAX/BAK-null lines** (see
`acquisition/`). Two independent implementations agreeing on this is the strongest honesty
guarantee the project can offer.

---

## 6. Conventions
- **Every module:** `ROOT = Path(__file__).resolve().parents[1]`; `sys.path` includes `src/`;
  reads the root `config.yaml`. Works identically for `scripts/` and `src/`.
- **No efficacy language anywhere** (GUARDRAILS §3); susceptibility = *predicted target population*.
- **Synthetic data** appears only in `src/validation.py` and is labelled method-validation, never biology (§1a).
- **Figures** never invent numbers; they read `outputs/tables/*.csv` / `results/*` written by the analysis modules.
