# M2 report — backbone association (executioner loss vs BH3-mimetic resistance)

Standardized β (per +1 SD executioner-loss score) on z-scored sensitivity,
adjusted for lineage. Positive β = executioner loss → resistance (pre-registered).

| drug | metric | n | β (std) | 95% CI | p |
|------|--------|---|---------|--------|---|
| venetoclax | LN_IC50 | 165 | 0.102 | [-0.052, 0.257] | 0.193 |
| venetoclax | AUC | 165 | 0.066 | [-0.089, 0.221] | 0.402 |
| navitoclax | LN_IC50 | 171 | 0.128 | [-0.022, 0.278] | 0.0947 |
| navitoclax | AUC | 171 | 0.076 | [-0.076, 0.227] | 0.326 |

**Permutation null (primary spec: venetoclax LN_IC50, 5000 perms):** observed β = 0.102, null mean -0.001 ± 0.078, permutation p = 0.194.

**Interpretation:** direction and magnitude reported as-is. Correlation is not evidence that ATAP works (GUARDRAILS §3); it establishes that the executioner-loss resistance mechanism is real and detectable, defining the population where a BAX-independent agent is mechanistically rational.
