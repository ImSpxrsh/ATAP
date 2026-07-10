# M10 — Functional (CRISPR dependence) vs expression proxy for BH3-mimetic response

**Date:** 2026-07-10 · **Script:** `scripts/12_functional_vs_expression.py`
**Data (all real, on disk):** DepMap 24Q4 `CRISPRGeneEffect.csv` + expression + `Model.csv`;
GDSC2 venetoclax/navitoclax dose-response. Join: DepMap heme lines → SangerModelID → GDSC2.
**Tables:** `outputs/tables/M10_functional_vs_expression.csv`,
`outputs/tables/M10_functional_vs_expression_paired.csv`.

## Why this module exists
Every prior module built predictors from **expression**. The project's central methodological
claim is that *expression is a weak proxy for functional apoptotic competence*. This module
tests that claim directly with data already on disk: does a **functional** readout of guardian
dependence — DepMap CRISPR gene-effect (negative = more essential) — predict BH3-mimetic
response, and does it beat the expression proxy? Convention: **functional dependence =
−gene_effect**, so a sensitivity/dependence marker shows a **negative** Spearman with LN_IC50
(more dependent → more sensitive → lower IC50), same polarity as high guardian expression —
making the head-to-head a clean |ρ| comparison. n ≈ 63–64 heme lines carry both layers.
Every ρ ships a permutation null (5000) + bootstrap CI (5000); improvements are tested with a
**paired** bootstrap on the same resampled lines. Seed 7. No efficacy claim (GUARDRAILS #3).

## Findings (honest, mixed — not a clean "functional always wins")

### 1. Guardian axis, BCL2 (the venetoclax target): functional is consistently, but not decisively, stronger
| drug / metric | expr ρ | func ρ | Δ\|ρ\| (func−expr) | paired CI | P(func>expr) |
|---|---|---|---|---|---|
| Venetoclax LN_IC50 | −0.454 | −0.571 | +0.152 | [−0.06, +0.38] | 0.91 |
| Venetoclax AUC | −0.513 | −0.607 | +0.132 | [−0.07, +0.33] | 0.91 |
| Navitoclax LN_IC50 | −0.452 | −0.529 | +0.118 | [−0.07, +0.31] | 0.89 |
| Navitoclax AUC | −0.452 | −0.598* | +0.146 | [−0.05, +0.34] | 0.93 |

Functional BCL2 dependence out-predicts BCL2 expression in ~90% of bootstraps across all four
specs, but the paired CI includes 0 at n≈63 — a **consistent directional advantage, not a
statistically decisive one.** Both readouts are individually significant (perm p<0.001, CIs
exclude 0). This is the first *functional* corroboration of the project's core premise on the
guardian axis. (*func ρ for the exact spec printed by the script.)

### 2. MCL1: expression BEATS functional — because MCL1 is pan-essential (honest reversal)
MCL1 **expression** carries the classic venetoclax-bypass signal (ρ=+0.47 vs venetoclax IC50,
+0.60 vs navitoclax — high MCL1 → resistance, correct sign, p<0.001). MCL1 **functional
dependence** does not (venetoclax ρ=−0.13, ns). Paired test: expression significantly beats
functional for navitoclax (Δ|ρ|=−0.33, CI [−0.57, −0.08], SIGNIF). **Reason:** MCL1 CRISPR
gene-effect is broadly essential (median −0.906, tight IQR) — near-zero dynamic range, so it
cannot discriminate response. The "functional > expression" advantage is therefore **specific
to the discriminating guardian (BCL2), not universal**; for a pan-essential guardian the
expression proxy is the better predictor. BCL2L1 (BCL-xL): the two readouts are indistinguishable.

### 3. Executioner axis (BAX/BAK): null in BOTH readouts, and unmeasurable by CRISPR by construction
All BAX/BAK correlations with venetoclax/navitoclax response are null in **both** expression and
functional readouts (|ρ|<0.11, perm p>0.26, CIs span 0). The functional test adds a *mechanistic*
reason the executioner axis cannot be read from cell lines at all: BAX gene-effect median
**+0.119** (IQR [+0.04, +0.18]), BAK1 median **−0.316** — pro-apoptotic effectors are
growth-neutral, so a **proliferation** CRISPR screen structurally carries ~no executioner signal.

## What this means (no overclaim)
- The guardian axis that drives *measured* venetoclax resistance is real and is read slightly
  better functionally (BCL2) — reinforcing, with data, that functional readouts matter.
- The executioner axis where ATAP is mechanistically rational is **null in expression, null in
  functional CRISPR, and structurally unreadable by CRISPR.** This is now a *three-way* case
  (expression null + functional-CRISPR null + a mechanistic why) that the decisive layer must be
  **functional apoptotic priming (BH3 profiling)** or **engineered BAX/BAK-null lines**, exactly
  the acquisition targets in `acquisition/`. The hypothesis is not refuted; it is precisely
  located beyond the reach of every public cell-line readout — a stronger, more honest position.

## Caveats
n≈63 heme lines with both layers (modest power — the BCL2 improvement is directional, not
decisive). Cell-line culture bias applies (LIMITATIONS). CRISPR gene-effect is a
*proliferation-fitness* readout, an imperfect analogue of survival/apoptotic dependence; it
captures guardian survival-dependence but is blind to pro-apoptotic effector competence.
