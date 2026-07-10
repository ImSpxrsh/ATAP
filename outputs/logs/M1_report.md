# M1 report — gene panel + executioner-loss logic

**Code:** `src/panels.py` · **Applied in:** `src/data/harmonize.py` ·
**Figure:** `outputs/figures/F_M1_executioner_distribution.{png,pdf}`

## Panel (config.yaml)
- Executioners: BAX, BAK1
- Guardians: BCL2, MCL1, BCL2L1 (Bcl-xL), BCL2A1 (Bfl-1), BCL2L2 (Bcl-w)
- Sensitizers: PMAIP1 (NOXA), BBC3 (PUMA), BID, BCL2L11 (BIM), BAD
- ATAP-signature extras: mito import (TIMM/TOMM family), cardiolipin synthase CRLS1

## Executioner-loss rule (BAX/BAK1 state only — no drug/ATAP data)
Binary call = TRUE if ANY of:
1. damaging (LOF) mutation in BAX or BAK1 (VEP/MAF LOF consequence tokens), OR
2. deep/homozygous deletion (DepMap relative CN ≤ 0.25; TCGA GISTIC = −2), OR
3. bottom-decile expression of **both** BAX and BAK1 (within-cohort quantile).

Continuous `executioner_loss_score` ∈ [0,1] = fraction of available components firing.
`components_used` is recorded per sample so downstream code stays honest about which
layers a dataset actually had.

**Acceptance met:** the score is constructed purely from BAX/BAK1 genomic/expression
state, with zero reference to venetoclax response or ATAP — so using it later to predict
resistance is not circular.

## Prevalence (this run)
| cohort | n | executioner-loss calls | components available |
|--------|---|------------------------|----------------------|
| DepMap heme cell lines | 348 (260 lymphoid, 88 myeloid) | 16 (4.6%) | expr + CN + mut |
| Beat AML patients | 707 | 15 (2.1%) | expr + mut |
| TCGA-LAML | 173 | see tcga_LAML.csv | expr + GISTIC + mut |
| TCGA-DLBC | 48 | see tcga_DLBC.csv | expr + GISTIC + mut |

- **0 BAX/BAK1 deep deletions** in 348 heme cell lines — biologically expected
  (executioner homozygous deletion is rare). CN arm is implemented and correct but does
  not fire in this cohort; loss is driven by the expression and mutation arms.
- Executioner loss is a **rare** state. This limits binary-call statistical power in M2;
  the continuous expression gradient is the primary predictor. Logged in DECISIONS.md
  and carried to methods.md Limitations.
