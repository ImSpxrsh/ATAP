# RESULTS SUMMARY — ATAP susceptibility, honestly

One-page plain summary of the computational analysis. Every number below was produced by a
committed script on real public data (BeatAML, DepMap 24Q2, GDSC2); provenance in
`data/raw/MANIFEST.md`; guardrails in `GUARDRAILS.md`; biases in `LIMITATIONS.md`; full log in
`NOTES.md`. **No efficacy claims — this predicts susceptibility/rationale, never that ATAP-M8
kills anything. Zero ATAP-response data was used (none exists).**

## What the project set out to test
ATAP-M8 permeabilizes mitochondria **without BAX/BAK**, so it is mechanistically rational
salvage exactly where BH3-mimetics (venetoclax) fail — in tumors that have lost the executioner
BAX/BAK. The computational goal: predict *which* venetoclax-resistant blood cancers are
executioner-loss-driven (ATAP-relevant), from mechanism.

## What the data actually shows

**1. Real, replicated, but NOT novel — the guardian axis.**
The BCL2 / BCL2–MCL1 axis predicts real venetoclax (and navitoclax) ex-vivo resistance, and it
**replicates across two independently-biased cohorts**: BeatAML patients (BCL2 Spearman rho =
−0.57 vs venetoclax AUC, n=367) and independent GDSC heme cell lines (BCL2 −0.45/−0.51,
BCL2−MCL1 −0.64/−0.66, n=113). Every association ships a permutation null + bootstrap CI.
The specification curve (`figures/spec_curve.png`, 25 analytic choices) finds this **negative &
significant in 100%** of guardian specifications. → This is real biology, but it is **established
venetoclax-biomarker biology** (Pei et al. monocytic resistance; BCL2/MCL1-ratio biomarkers;
`outputs/logs/priorart_log.md`), **confirmatory, not a discovery**. Correctness reassurance: the
pipeline recovers known biology.

**2. Robust NULL — the executioner axis (the ATAP-relevant variable).**
`executioner_loss_score` does **not** predict general venetoclax resistance in ANY cohort
(rho ≈ 0; **null in 100%** of executioner specifications, CI always includes zero). It also does
not track CRISPR BAX/BAK dependency (and CRISPR fitness is a poor readout of apoptotic
dependency anyway). → Executioner loss is not a general-resistance driver.

**3. Rare phenotype — everywhere.**
Genetic/expression executioner loss is rare: **1 LoF / 671** BeatAML patients; **6 / 228** DepMap
heme lines (~1–2%). Primary AML (diagnosis-heavy) structurally under-samples the *acquired*
BAX/BAK loss ATAP targets (that arises after venetoclax failure). → No unselected public cohort
can "map the salvage population."

**4. The composite model does not earn its complexity.**
The hand-weighted two-axis composite is **beaten by BCL2 alone** in patients (−0.27 vs −0.57), its
biological weighting is **indistinguishable from random** (sign-scramble rank 10/32; random-weights
p=0.32), and the dominant real predictor is a **monocytic-differentiation signature** (rho=+0.72)
it only weakly proxies. (Honest nuance: the composite is competitive in cell lines — spec-curve C3
= 40%, not 0% — so "adds nothing" is too strong; "not consistently better than BCL2, clearly worse
in patients" is correct.)

## The honest candidate novelty (human-verification-gated)
Screening prior-art search found **no** published application of ATAP to hematologic malignancy /
BH3-mimetic resistance (all ATAP work is solid-tumor/prostate; Rutgers-patented). So the ATAP
**heme indication** is plausibly unexplored — but because the target phenotype is rare and
unmappable in available data, the defensible claim is narrow: *a mechanistically-rational
hypothesis for the specific, rare acquired-executioner-loss subset, to be tested at the bench* —
not a validated susceptibility map. A human + fuller-database + IP-professional review is required
before any novelty/FTO claim.

## Figures & scripts
- `figures/model_comparison.png` (scripts/09) — what actually predicts venetoclax resistance.
- `figures/spec_curve.png` + `outputs/tables/spec_curve.csv` (scripts/11) — robustness of every conclusion.
- scripts/04 M2 backbone · 05 M3 confounders · 06 M1 executioner subgroup · 07 DepMap · 08 discrimination · 10 GDSC replication.
- `outputs/logs/priorart_log.md` — M9 gate.

## Key limitations (full list in LIMITATIONS.md)
Diagnosis cohort cannot sample acquired BAX/BAK loss; ex-vivo AUC ≠ clinical response; mRNA ≠
functional executioner state; cell-line culture artifact; drug-testable-subset selection.

## Bottom line
A rigorous, honest characterization: the analysis correctly recovers established venetoclax
biology and, in doing so, shows the ATAP-relevant executioner-loss phenotype is rare and separable
— which makes **a single wet-lab test on an engineered BAX-deficient, venetoclax-resistant line**,
not more computation, the necessary next step. The value here is the honest map of what is real,
what is confirmatory, what is null, and what remains an untested hypothesis.
