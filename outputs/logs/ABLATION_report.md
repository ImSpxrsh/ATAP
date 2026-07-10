# Ablation — which half of the susceptibility score carries the signal?

Spearman ρ of each score component vs observed venetoclax resistance.

| cohort | n | guardian-only ρ (p) | executioner-only ρ (p) | combined ρ (p) |
|--------|---|---------------------|------------------------|----------------|
| DepMap (venetoclax LN_IC50) | 116 | 0.497 (1.3e-08) | 0.032 (7.3e-01) | 0.342 (1.7e-04) |
| BeatAML (ex vivo venetoclax AUC) | 367 | 0.265 (2.5e-07) | 0.008 (8.8e-01) | 0.233 (6.4e-06) |

**Reading:** the guardian-dependence term carries the venetoclax-resistance correlation; the executioner-deficiency term is the *mechanistic hypothesis* (where a BAX-independent agent is rational) and is not expected to — and does not — drive the venetoclax-resistance signal on its own. This precisely bounds the M5 claim: the score identifies the guardian-dependent population and flags the executioner-low subset within it as the ATAP-rational target. No efficacy is claimed; the executioner half awaits functional validation (BH3 profiling / engineered null lines).
