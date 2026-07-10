# Methods

All analysis is computational and uses only public data. **Zero ATAP response data** is
used anywhere (there is none for blood cancer). Every susceptibility result is *predicted
from mechanism, not measured*. No efficacy is claimed (GUARDRAILS §3).

Reproducibility: one `config.yaml` holds every path, seed (20260710), threshold, and gene
panel. Package versions are locked in `outputs/logs/environment_lock.txt`. Run order:
`src/data/fetch_data.py` → `src/data/harmonize.py` → `src/panels.py` (imported) →
`src/backbone.py` → `src/confounders.py` → `src/multiverse.py` → `src/stratify.py` →
`src/spatial_run.py` → `src/validation.py` → `src/priorart.py` → `figures/*`.

## Datasets (dataset-by-dataset, with versions/accessions)

| dataset | source / accession | release | what was pulled | download date |
|---------|--------------------|---------|-----------------|---------------|
| DepMap | figshare article 27993248 (ndownloader) | **Public 24Q4** | Model.csv, OmicsExpressionProteinCodingGenesTPMLogp1, OmicsCNGene, OmicsSomaticMutations, CRISPRGeneEffect | 2026-07-10 |
| GDSC | Sanger FTP `release-8.4` | **8.4, fitted dose response 24Jul22** | GDSC1+GDSC2 fitted dose response (venetoclax, navitoclax: LN_IC50 + AUC), screened compounds, cell-line details | 2026-07-10 |
| TCGA-LAML | cBioPortal REST API | `laml_tcga_pan_can_atlas_2018` (PanCancer Atlas) | panel-gene mRNA (RSEM), GISTIC CNA, mutations, clinical | 2026-07-10 |
| TCGA-DLBC | cBioPortal REST API | `dlbc_tcga_pan_can_atlas_2018` | panel-gene mRNA, GISTIC CNA, mutations, clinical | 2026-07-10 |
| Beat AML | biodev/beataml2.0_data (GitHub, main) | **waves 1–4 (Bottomly, Cancer Cell 2022)** | normalized RNA-seq, WES mutations, ex vivo **inhibitor AUC (venetoclax)**, clinical (ELN2017, fusions, FAB) | 2026-07-10 |
| Beat AML (x-check) | cBioPortal `aml_ohsu_2022` | PanCancer | panel-gene mRNA + clinical (no ex vivo drug response there) | 2026-07-10 |
| Spatial | 10x Genomics `V1_Human_Lymph_Node` Visium (`scanpy.datasets.visium_sge`) | Space Ranger 1.1.0 demo | 4035 spots × 36601 genes; all 6 BCL-2-family genes expressed | 2026-07-10 |

Provenance for every raw file (source, size, sha256) is in `data/raw/MANIFEST.md`.

## Panel + executioner-loss (M1)
BCL-2-family panel in `config.yaml`. Executioner loss (BAX/BAK1 state only): damaging
(LOF) mutation OR deep deletion (DepMap relative CN ≤ 0.25; TCGA GISTIC = −2) OR
bottom-decile expression of both BAX and BAK1. Continuous score = fraction of available
components firing. Constructed with no reference to drug/ATAP data (non-circular).

## Backbone association (M2)
OLS of z-scored sensitivity (LN_IC50, AUC separately) on z-scored executioner-loss score,
lineage-adjusted, in heme DepMap+GDSC. Standardized β + 95% CI + p per drug × metric.
5000-permutation null on the pre-registered primary spec (venetoclax LN_IC50).

## Confounders (M3)
Nested OLS: base(lineage) → +MCL1 expression, BCL2/BCL-xL log-ratio, BCL2 hotspot →
+executioner loss. Incremental ΔR²/ΔAIC and the partial effect of executioner loss.

## Multiverse (M4)
360 specifications over {LOF definition × expr cutoff × drug × metric × lineage subset ×
covariate set}. Specification curve + FDR-BH + a transparent stability score (median β,
sign-agreement share, significance share, S³ = |median β|/IQR).

## Susceptibility stratifier + subtypes (M5, M6)
Susceptibility = √(guardian_dependence × executioner_deficiency), each a within-cohort
rank; BCL-2-family state only. Validated (Spearman) against observed venetoclax resistance
in DepMap and Beat AML ex vivo. Subtypes ranked by mean susceptibility (BeatAML ELN2017 /
fusions; TCGA; DepMap lineages).

## Spatial routing (M7)
10x Human Lymph Node Visium, QC (≥200 counts, ≥100 genes/spot), normalize_total+log1p.
Per-spot guardian dependence vs executioner availability → routing category
(bypass-required / venetoclax-sufficient / low-signal) + per-spot S³ stability over 81
spatial analytic choices. Expression-based inference.

## Method validation (M8, synthetic only)
Simulated spatial field with a known bypass region: routing pipeline ROC-AUC vs ground
truth; power curves over #spots × effect size; permutation nulls (spatial join-count;
backbone β). Labelled method validation; never a biological result (GUARDRAILS §1a).

## Prior-art gate (M9)
Dated PROSPERO-style search log (`outputs/logs/priorart_log.md`).

---

## Limitations
1. **Predicted, not validated susceptibility.** The susceptibility score and routing map
   are mechanistic hypotheses. No ATAP response data exists for blood cancer; the
   executioner-deficiency half of the score is unvalidated by construction.
2. **No ATAP data used.** The project cannot and does not show ATAP efficacy.
3. **Backbone is weak in cell lines.** Executioner loss is rare (~4.6% of heme lines) and,
   once guardian dependence (MCL1, BCL2/BCL-xL) is controlled, adds ~no incremental signal
   for venetoclax resistance (M3: ΔR²≈0.0006; M4: 0% of specs significant after FDR).
   The association is directionally consistent (77% positive) but not robust. The
   susceptibility *composite* does track observed venetoclax resistance (DepMap ρ=0.34,
   BeatAML ρ=0.23), but that signal is driven substantially by the guardian-dependence
   term, not executioner loss.
4. **Cohort/selection caveats.** BCL-2-family LOF mutations are rare in cell lines and
   patients, so the mutation arm is near-empty; expression drives the score. GDSC venetoclax
   is GDSC2-only. Expression-based executioner inference ≠ functional loss.
5. **Spatial layer is lymphoid proof-of-concept, not bone-marrow niche.** No verified,
   downloadable endosteal-vs-vascular bone-marrow spatial dataset was found (see BLOCKERS);
   the lymph-node Visium demonstrates the routing method on real heme-relevant tissue but
   does not resolve marrow niches.
6. **Assumptions that materially affect results** (all in DECISIONS.md): executioner-loss
   thresholds (bottom-decile-both expression; CN ≤ 0.25), the "both low" expression rule,
   and the susceptibility composite form (geometric mean of two rank terms).
