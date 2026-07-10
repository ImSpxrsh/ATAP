# RESULTS SUMMARY — ATAP-M8 susceptibility map (predict-and-map)

> **Honesty boundary:** everything below is *predicted susceptibility from mechanism*.
> **Zero ATAP response data** was used. No efficacy is claimed or shown. "Susceptibility"
> = mechanistically rational target population, not demonstrated kill.

## What was built
A reproducible, documented pipeline that (1) defines executioner (BAX/BAK) loss from real
genomics, (2) tests whether it tracks BH3-mimetic (venetoclax/navitoclax) resistance,
(3) builds a mechanistic ATAP-susceptibility score and validates it against **observed**
venetoclax resistance, (4) ranks heme subtypes, (5) maps the routing decision
(venetoclax-sufficient vs bypass-required) across a **real** lymphoid tissue section, and
(6) validates the methods synthetically with power curves and permutation nulls. Prior-art
gate logged.

Real data: DepMap 24Q4, GDSC 8.4, TCGA-LAML/DLBC, Beat AML 2.0 (ex vivo venetoclax AUC),
10x Human Lymph Node Visium. 348 heme cell lines, 707 Beat AML patients (367 with ex vivo
venetoclax), 221 TCGA cases, 4032 QC-passed spatial spots.

## Headline findings (all traceable to a saved figure/table)
- **The resistance mechanism is real but a weak cell-line predictor.** Executioner loss →
  venetoclax resistance is directionally consistent (venetoclax LN_IC50 β=+0.10; **77% of
  360 specifications positive**) but **not robustly significant (0% after FDR)**, and adds
  ~no signal beyond guardian dependence (M3 ΔR²≈0.0006). Reported honestly, not massaged.
  [F4, F5, F6]
- **The mechanistic susceptibility score does track observed venetoclax resistance** in
  real data: DepMap Spearman ρ=0.34 (p=2e-4), Beat AML ex vivo ρ=0.23 (p=6e-6) — but this
  is driven substantially by the guardian-dependence term. [F7, F8]
- **Executioner loss is a rare state** (~4.6% heme cell lines; 2–6% across cohorts) —
  small but mechanistically critical population. [F3, F_M1]
- **Novel spatial routing:** on real lymph-node Visium, 60% of spots are
  venetoclax-sufficient, **16% are "bypass-required"** (guardian-dependent yet
  executioner-low), with a per-spot stability map. Posing executioner availability as a
  spatial routing question is the novel contribution. [F9, F10]
- **Methods validated:** synthetic ground-truth recovery ROC-AUC=1.0; spatial structure
  beats a permutation null (p=0.001). [F11, F12]
- **Prior-art:** heme indication appears open in the literature (all prior ATAP work is
  solid-tumor); patent scope unresolved and flagged. [priorart_log.md]

## Figure index
F1 mechanism · F2 study design · F3 prevalence · F4 backbone · F5 confounders ·
F6 specification curve · F7 stratifier · F8 Beat AML patient-level · F9 spatial
heterogeneity · F10 spatial routing+stability · F11 synthetic validation · F12 power+nulls
· F13 wet-lab gate · F_M1 executioner-loss distribution. (`outputs/figures/*.png/.pdf`)

## Ranked blockers / human-must-decide (see BLOCKERS.md for detail)
1. **IP:** confirm ATAP patent claim scope for hematologic malignancies (IP professional).
2. **Spatial:** find a real bone-marrow niche (endosteal/vascular) dataset if a marrow
   routing claim is wanted; current spatial layer is lymphoid proof-of-concept.
3. **Framing:** lead with mechanism + spatial-routing novelty, not the weak cell-line
   association (recommended). Decide whether to pursue a cohort richer in executioner-loss
   events.
4. **Gene panel:** confirm whether TIMM/TOMM + CRLS1 should enter the susceptibility
   composite (currently defined but not scored) with a mentor.
5. **Assumptions:** review DECISIONS.md thresholds (executioner-loss cutoffs, composite
   form) that materially affect results.

## What a person should verify next
- Re-pull the ATAP patent family and read claims.
- Point the pipeline at a verified marrow-niche spatial object (schema already supported by
  `src/spatial.py` — it is dataset-agnostic).
- Consider functional BH3-profiling data to strengthen the executioner-loss construct
  beyond expression.
