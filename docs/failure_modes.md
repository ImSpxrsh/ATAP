# Failure modes — where ATAP-M8 predictions are unreliable (issue #14)

Naming our own failure modes before a judge does. Every entry is concrete, and where possible
quantified from this repo's own analyses. Nothing here is hedging for its own sake — each item
changes how a specific prediction should (or should not) be used.

> Honesty boundary: all outputs are *predicted susceptibility from mechanism*, never measured
> efficacy. These failure modes bound the **prediction**, not an efficacy claim (there is none).

## 1. The composite score is not the best predictor of its own target
**Condition:** any use that treats the hand-weighted composite as a validated predictor of
venetoclax response.
**Evidence (issue #10, `outputs/tables/M12_baseline_battery.csv`):** on DepMap heme × GDSC2, a
trivial two-gene `BCL2 − MCL1` difference (cross-validated |ρ| 0.61–0.69) beats the 6-block
composite on **every** spec; the composite only marginally beats `BCL2` alone for venetoclax
(0.51 vs 0.43) and **loses** to it for navitoclax (0.40 vs 0.44).
**Implication:** use the composite as a mechanistic *hypothesis generator*, not a performance-
optimal model. Report `BCL2 − MCL1` alongside it. The block weights (esp. `effector_competence
= 1.6`) are mechanistically motivated, not performance-justified.

## 2. Monocytic-differentiation identity confound (explicitly analyzed and quantified)
**Condition:** predicting venetoclax resistance in samples that vary in myeloid differentiation
state — the confound behaves **oppositely across cohorts**, so a model tuned on one can mislead
on the other.
**Evidence:**
- **Patients (Beat AML):** monocytic differentiation is the *dominant* real predictor of
  venetoclax ex-vivo resistance (Spearman ≈ **+0.72**; Pei et al. biology), and the BCL2 signal
  only partially survives partialling it out (partial ρ ≈ −0.20). The composite is a *weaker*
  predictor than the monocytic signature in patients — a differentiation-state proxy risk.
- **Cell lines (DepMap × GDSC, issue #10):** the same monocytic signature sits **at the random
  floor** (cv |ρ| ≈ 0.17, perm p ≈ 0.9) — cell lines lack the differentiation-state heterogeneity
  that drives the patient signal.
**Implication:** the confound is real and **cohort-specific**. Never assume a monocytic
adjustment learned in patients transfers to cell lines (or vice versa). For patient predictions,
always co-report the monocytic signature; a "BCL2-high → sensitive" call in a monocytic-high
sample is low-confidence.

## 3. The executioner-loss axis (ATAP's actual target) is untestable in public cell-line data
**Condition:** any attempt to *validate* the ATAP-relevant BAX/BAK-loss axis from public
genomics or cell-line drug screens.
**Evidence:** the executioner-loss score is a robust null for general venetoclax resistance
across **expression** (M3 ΔR² ≈ 0.0006), **functional CRISPR dependency**, and **two independent
drug platforms** (GDSC; PRISM S63845). BAX/BAK CRISPR gene-effect is near-zero (medians ≈ +0.12 /
−0.32) because pro-apoptotic effectors are growth-neutral, so a proliferation screen structurally
cannot read them.
**Implication:** predictions *about the executioner axis specifically* are not supported by any
public dataset and must be flagged as hypotheses requiring functional BH3 profiling or engineered
BAX/BAK-null lines. Do not present an executioner-loss ranking as validated.

## 4. Rare-event / small-subset regime
**Condition:** any claim about the executioner-loss *subpopulation*.
**Evidence:** executioner-loss is rare — 6/228 DepMap heme lines (2.6%), 5/367 Beat AML (1.4%).
Associations computed on ≤6 positives are underpowered by construction; CIs are wide and unstable.
**Implication:** subgroup effect sizes for the loss subset are indicative only; never report a
subgroup p-value without its n and CI, and never binarize decisions on it.

## 5. Calibration breaks at the extremes
**Condition:** interpreting the composite `venetoclax_pct` as a literal probability, especially in
the top/bottom bins.
**Evidence (issue #12):** calibration slope **0.67** (CI [0.41, 1.09]) — mild over-confidence;
the most-extreme bins are less separated in reality than the score implies. Discrimination is
fine (AUC 0.78); calibration is only approximate (ECE 0.068).
**Implication:** use the score for *ranking*, not as a probability. A `venetoclax_pct = 0.95` does
not mean 95% sensitive.

## 6. Spatial layer is a lymphoid proof-of-concept, NOT a bone-marrow claim
**Condition:** reading the spatial routing map as a statement about the AML/marrow niche.
**Evidence:** the spatial analysis runs on **10x V1 Human Lymph Node Visium** (normal lymphoid
tissue), a demonstration that executioner-availability can be posed as a per-spot routing
question — it is **not** marrow, not malignant, and carries no venetoclax response labels.
**Implication:** the spatial contribution is methodological (a routing formulation + per-spot
stability), explicitly proof-of-concept. Any endosteal/vascular-niche interpretation requires a
real bone-marrow spatial dataset (see `docs/BLOCKERS.md`). Do not state a marrow localization claim.

## 7. Cell-line culture bias (whole-cohort caveat)
**Condition:** extrapolating any cell-line association to patients.
**Evidence/reasoning:** immortalized lines are selected for proliferation and drift from primary
biology; GDSC/PRISM culture artifacts are shared within-platform. Cross-platform replication
(GDSC↔PRISM, cell-line↔patient) is the mitigation, and where it fails (e.g. monocytic confound,
item 2) that is itself a documented failure mode.
**Implication:** treat cell-line results as discovery/mechanistic support, always seeking a
patient-cohort echo before any translational framing.

---
### Summary table
| # | Failure mode | Quantified? | Where it bites |
|---|---|---|---|
| 1 | composite ≠ best predictor | yes (#10) | venetoclax/navitoclax ranking |
| 2 | monocytic confound (cohort-specific) | yes (patients +0.72 / lines ~random) | patient predictions |
| 3 | executioner axis untestable publicly | yes (multi-platform null) | ATAP-target claims |
| 4 | rare-event small-n | yes (2.6% / 1.4%) | loss-subset subgroups |
| 5 | calibration slips at extremes | yes (slope 0.67) | probability reading |
| 6 | spatial = lymphoid PoC | n/a (design) | marrow-niche claims |
| 7 | cell-line culture bias | qualitative | any line→patient jump |
