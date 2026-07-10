# LIMITATIONS & DATA BIASES

Stating these proactively is required by GUARDRAILS.md and is what makes the project defensible.
Ranked by how much each threatens the central claims, not by comfort. Every item here is a real
property of the data or method, established from the analyses in `NOTES.md`, not a hypothetical.

## 1. The primary cohort barely contains the target phenotype (most important)

BeatAML (the validation cohort) is overwhelmingly **diagnosis / treatment-naive primary AML**.
But genetic BAX/BAK loss is largely a mechanism of **acquired** resistance — it emerges after
prolonged BH3-mimetic pressure, in relapsed/refractory patients who have already failed
venetoclax. Those samples are **underrepresented** here. Measured directly: only **1 BAX/BAK1
loss-of-function mutation in 671 patients** (cycle 2) and **5 executioner-low cases in 367**
(cycle 5). Consequence: the M3/M1 nulls are *partly a statement about the cohort*, not only about
biology — a diagnosis-heavy cohort structurally cannot test an acquired-resistance mechanism. This
is the honest justification for the DepMap route (cell lines carry genetic BAX/BAK loss) and,
ultimately, for a wet-lab test on an engineered BAX-deficient, venetoclax-resistant line.

## 2. The validation target is a proxy, not clinical outcome

M2 validates against BeatAML **ex-vivo** venetoclax AUC — patient cells plated and dosed in a dish
— **not** the patient's clinical response to venetoclax therapy. Ex-vivo sensitivity correlates
with but is not identical to in-vivo benefit (drug PK, marrow microenvironment, combination
regimens, adaptive resistance are all absent). All M2/M3 claims are therefore about *ex-vivo*
resistance and must never be phrased as predicting clinical response.

## 3. mRNA is a noisy proxy for functional executioner loss (measurement bias)

Executioner "availability" is inferred from RNA-seq expression. But BAX/BAK function can be lost
with normal mRNA (protein degradation, sequestration, conformational inactivation,
post-translational modification), and low mRNA does not guarantee a non-functional pore. The
bottom-decile-expression definition (M1) is a genuinely noisy stand-in for the functional state
that actually determines whether venetoclax can execute. DepMap CRISPR gene-effect is a closer
functional readout and is why that cohort is a fairer test.

## 4. Stacked selection biases

- **Drug-testable subset:** only 367 of 671 cBioPortal BeatAML samples had a matched venetoclax
  AUC; ex-vivo testing requires enough viable, high-blast material, so the validation runs on a
  selected subpopulation, not all-comers.
- **Academic-center ascertainment:** BeatAML samples are consented patients at consortium centers,
  not a population-representative AML sample.
- **Cell-line artificiality (applies to the DepMap route):** cell lines are the subset of tumors
  that survive immortalization and culture — selecting for aggressive, often TP53-mutant,
  plastic-adapted genotypes. If DepMap shows more BAX/BAK loss, that may partly reflect culture
  artifact, not patient biology. The DepMap route trades the "phenotype-too-rare" bias for a
  "phenotype-may-be-culture-artifact" bias; both must be stated.

## 5. Quieter biases (real, lower threat)

- **Prior/publication bias in the model itself:** the ~39-gene panel and the directional priors
  encode well-studied BCL-2 biology; heavily-characterized genes (BCL2, MCL1, BAX) are richer than
  minor players. The panel reflects what has been published, not necessarily what is mechanistically
  complete.
- **Residual confounding:** M3 controls MCL1 and the BCL2:BCL-XL ratio, but genetic subtype
  (NPM1/FLT3/TP53), blast percentage, and prior therapy are not fully captured.
- **Cross-platform harmonization:** cBioPortal log2-RPKM vs the drug set's RNA-seq; mitigated by
  within-cohort rank/z-scoring, but imperfect.

## What this means for the framing (not a disclaimer — a design consequence)

The M3/M1 nulls are honest and correct: at the population level in primary AML, executioner loss
does not drive venetoclax resistance (the guardian/MCL1 axis does), and the executioner-loss subset
is too rare to test. This does not refute the ATAP mechanism — it **locates where the hypothesis
can be tested** (cell lines with genetic loss; relapsed-post-venetoclax samples; a single
engineered BAX-deficient line at the bench) and prevents the overclaim that executioner loss
explains general venetoclax resistance. The strongest, most honest version of this project reports
these limitations up front and frames the wet-lab step as testing the specific, rare phenotype the
computational cohorts cannot.
