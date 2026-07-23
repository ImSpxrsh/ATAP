# MODEL CARD — ATAP-M8 susceptibility pipeline (v1.0-frozen)

**Issue #1 — freeze & provenance lock.** This card documents the exact model, features,
hyperparameters, data versions, and seeds as of the `v1.0-frozen` tag. It is the "before we
looked at any new data" snapshot that makes downstream validation prospective in spirit.
Companion machine-readable pin: [`data/DATA_VERSIONS.lock`](data/DATA_VERSIONS.lock).

> **Honesty boundary (GUARDRAILS).** Every susceptibility output is *predicted from mechanism*,
> not measured. The pipeline uses **zero ATAP response data**. **No efficacy is claimed.** The
> composite score below is a **hypothesis**, and is documented as one — it is beaten by BCL2
> expression alone in patients (see Baselines / issue #10).

## 1. What the model is
Two mechanistically-motivated, rule-based scores over a fixed BCL-2-family gene panel — **not**
a fitted/learned classifier. Nothing is trained on the drug-response labels it is evaluated
against, so there is no train/test leakage to control; the "freeze" pins the *feature
definitions, thresholds, and weights*, which are the only tunable quantities.

- **Executioner-loss score** (`src/atap/features.py:executioner_loss_score`): a per-sample call
  and continuous score for BAX/BAK1 functional loss from expression + copy number + LoF mutation.
- **Composite susceptibility (venetoclax vs ATAP) score** (`src/atap/scoring.py`): a weighted sum
  over mechanistic feature blocks producing a two-axis (venetoclax-efficacy, ATAP-efficacy) map.
- **Guardian axis** (BCL2 / BCL2−MCL1) — the term that actually carries the measured
  venetoclax-resistance signal; reported separately and against baselines.

## 2. Feature set (frozen)
Gene panel (HGNC symbols, from `config.yaml:panels`):
- **Executioners:** BAX, BAK1
- **Guardians:** BCL2, MCL1, BCL2L1 (BCL-xL), BCL2A1 (Bfl-1), BCL2L2 (Bcl-w)
- **Sensitizers / activators:** PMAIP1 (NOXA), BBC3 (PUMA), BID, BCL2L11 (BIM), BAD
- **ATAP-signature extras:** mito-import [TIMM23, TIMM17A, TIMM17B, TIMM50, TOMM20, TOMM22,
  TOMM40, TOMM70]; cardiolipin [CRLS1]
- **Monocytic-confound signature:** LYZ, CD14, CSF1R, FCN1, MAFB, VCAN, CD68, ITGAM
- **Execution machinery / IAPs / mito-mass:** defined in `src/atap/biology.py`

Feature blocks consumed by the composite (`biology.FEATURE_BLOCKS`): `bcl2_dependence`,
`mcl1_bclxl_backup`, `priming_activators`, `effector_competence`, `execution_competence`,
`mito_mass`.

## 3. Hyperparameters (frozen — all from `config.yaml`, no magic numbers in code)
**Executioner-loss thresholds**
| param | value | meaning |
|---|---|---|
| `expr_low_quantile` | 0.10 | bottom-decile expression = "low" (both BAX & BAK1 must be low) |
| `cn_deep_del_relative` | 0.25 | relative CN ≤ 0.25 (~log2 −2) = deep/homozygous deletion |
| `damaging_classes` | VEP + MAF LoF tokens | stop_gained, frameshift, splice_acceptor/donor, start_lost, stop_lost, Nonsense, Frame_Shift_Del/Ins, Splice_Site, Translation_Start_Site, Nonstop (missense excluded) |
| `score_components` | [mutation, cn, expression] | continuous score = mean of present components |

**Composite block weights** (`config.yaml:block_weights`)
| block | weight |
|---|---|
| bcl2_dependence | 1.0 |
| mcl1_bclxl_backup | 1.0 |
| priming_activators | 1.0 |
| **effector_competence** | **1.6** (up-weighted: the mechanistic crux, opposite signs across agents) |
| execution_competence | 1.0 |
| mito_mass | 0.8 |

**Two-axis quadrant thresholds:** `veneto_low = 0.40`, `atap_high = 0.60` (percentile cutoffs).

**Statistics:** `n_perm = 2000` permutation draws, `n_boot = 2000` bootstrap draws,
95% CI = [2.5, 97.5] percentiles. (Spec-curve uses 1000 perms for runtime.)

**Pre-registered primary spec (M2 backbone):** drug = venetoclax, metric = LN_IC50,
hypothesis direction = positive (executioner loss → resistance → higher LN_IC50).

## 4. Seeds
Global seed **`20260710`** (`config.yaml:seed`), applied to every stochastic step
(permutation nulls, bootstraps, any resampling). Individual analysis scripts additionally use
local seeds (e.g. 7) documented in their headers.

## 5. Data source versions (see `data/DATA_VERSIONS.lock` for full pins + hashes)
| dataset | release | route | download |
|---|---|---|---|
| DepMap | Public 24Q4 (figshare 27993248) | figshare file ids | 2026-07-10 |
| GDSC | release-8.4 (24Jul22) | Sanger FTP | 2026-07-10 |
| Beat AML 2.0 | biodev/beataml2.0_data @ main | GitHub raw | 2026-07-10 |
| Beat AML (cBioPortal) | aml_ohsu_2022 | REST API | live |
| TCGA | LAML + DLBC PanCancer Atlas | REST API | live |
| 10x Visium | V1 Human Lymph Node (SR 1.1.0) | scanpy visium_sge | 2026-07-10 |

## 6. Intended use & out-of-scope
- **Intended:** rank/where-analysis of *mechanistically rational* target populations for a
  BAX-independent agent, and hypothesis generation for functional (BH3-profiling) follow-up.
- **Out of scope:** any efficacy statement, any clinical decision, any claim that a mismatch
  proves ATAP will work. The executioner axis (ATAP's target) is a robust null in all public
  cell-line data and is explicitly flagged as untestable without functional priming data.

## 7. Known limitations (summary; full analysis in `docs/failure_modes.md`, issue #14)
Composite is beaten by BCL2 alone in patients; monocytic-identity confound; spatial layer is
lymphoid proof-of-concept, not marrow; executioner-loss is rare (~2–5%) so its association is
underpowered by construction.

## 8. Freeze reference
- Tag: `v1.0-frozen` (this commit).
- To reproduce exactly: `git checkout v1.0-frozen`, then follow the "Reproduce from scratch"
  steps (issue #2 / Makefile) with the versions pinned in `data/DATA_VERSIONS.lock`.
