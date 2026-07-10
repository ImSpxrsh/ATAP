# M8 report — method validation (SYNTHETIC — never a biological result)

> Every number here is method validation on simulated data (GUARDRAILS §1a). None is a biological finding.

## 1. Ground-truth recovery
- 1600 synthetic spots; known bypass region (executioners low + guardians high).
- Routing pipeline **ROC-AUC = 1.000**, accuracy 0.902 vs ground truth.
- Mean per-spot stability inside region 1.00 vs background 0.69.

## 2. Power analysis
- See M8_power_curve.csv: ROC-AUC vs #spots × effect size (8 reps each). At effect≥1.5 the pipeline recovers the gradient with high power even at modest spot counts.

## 3. Permutation null (spatial structure)
- Join-count of bypass-required spots: observed 0.106 vs null 0.039 ± 0.002, permutation p = 0.000999 (1000 perms) — the recovered region is spatially clustered far beyond chance (validates the method detects real spatial structure when present).
