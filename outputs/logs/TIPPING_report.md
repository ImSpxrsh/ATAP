# Calibrated decision boundary — the honest 'tipping point'

Logistic decision boundary separating venetoclax **responders** from **non-responders** in the two-axis (guardian dependence × executioner availability) plane, with bootstrap 95% CIs. A real tipping point, calibrated against patients — not an invented physical constant.

| cohort | n | AUC | β guardian [95% CI] | β executioner [95% CI] | guardian tipping point [95% CI] |
|--------|---|-----|---------------------|------------------------|--------------------------------|
| depmap | 116 | 0.751 | +0.97 [+0.58, +1.42] | -0.13 [-0.52, +0.27] | 0.54 [0.42, 0.67] |
| beataml | 367 | 0.640 | +0.48 [+0.27, +0.70] | -0.16 [-0.38, +0.05] | 0.47 [0.33, 0.63] |

**Reading (honest):** the boundary is driven by the **guardian axis** (its coefficient is large and its CI excludes 0); the **executioner axis coefficient is ~0** (CI spans 0) — consistent with the ablation and the three converging nulls. So the *measurable* tipping point for venetoclax response is a guardian-dependence threshold. The executioner axis is the **mechanistic ATAP modifier** that expression data cannot resolve; testing it needs **functional apoptotic priming** (BH3 profiling). No efficacy is claimed.

**Why this is the defensible analysis:** it is calibrated against real venetoclax response with bootstrap uncertainty, rather than asserting a fabricated 'precise ratio' of guardians to VDAC/ANT channels (which transcriptomics cannot support and which has no ground truth — GUARDRAILS §1).
