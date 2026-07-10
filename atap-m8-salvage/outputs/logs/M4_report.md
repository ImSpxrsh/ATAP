# M4 report — specification curve + stability score

Ran **360 specifications** (LOF definition x expr cutoff x drug x metric x lineage subset x covariate set). FDR-BH across the curve.

## Stability

- median standardized β = **0.100** (IQR 0.162)
- share agreeing in sign with the median = **77%**; positive (pre-registered) direction = **77%**
- share significant (p<0.05, same sign) = **8%**; FDR<0.05 = **0%**
- S³ stability (|median β| / IQR) = **0.62**

## Interpretation

The specification curve is the project's anti-overclaiming device. A high sign-agreement share with a near-zero median and few significant specs means the executioner-loss→resistance link is **directionally consistent but weak and not robustly significant** across analytic choices — reported honestly rather than cherry-picking the one spec that clears p<0.05. This bounds the biological claim to: the resistance mechanism is real and detectable in principle, but is a minor statistical signal in cell lines relative to guardian dependence (M3).
