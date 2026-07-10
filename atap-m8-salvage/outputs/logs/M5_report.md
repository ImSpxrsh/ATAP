# M5 report — ATAP-susceptibility stratifier (PREDICTED, not measured)

> Predicted susceptibility score from mechanism (BCL-2-family state only). NOT validated against ATAP response data. Not a kill rate. (GUARDRAILS §3)

susceptibility = sqrt(guardian_dependence × executioner_deficiency), each a within-cohort rank in [0,1].

## Validation against observed venetoclax resistance

- **DepMap (venetoclax LN_IC50)** (n=116): Spearman ρ = 0.342 (p = 0.00017) between susceptibility and resistance.
  - executioner-loss-called cases (n=6): median resistance 1.30 vs 0.76 (others); Mann-Whitney one-sided p = 0.14.
- **BeatAML (ex vivo venetoclax AUC)** (n=367): Spearman ρ = 0.233 (p = 6.4e-06) between susceptibility and resistance.
  - executioner-loss-called cases (n=3): median resistance 164.13 vs 157.89 (others); Mann-Whitney one-sided p = 0.33.

## Construct limits (stated explicitly, spec M5)
- The composite rewards BOTH high guardian dependence AND low executioner availability, so it is not circular with executioner loss alone.
- M3 showed executioner loss adds little beyond guardian dependence for venetoclax; therefore the score's correlation with venetoclax resistance is expected to be modest and is driven substantially by the guardian-dependence term. The score's intended use is to flag the *bypass-rational* subset (dependent yet unable to execute), not to predict venetoclax response.
- No ATAP data exists to validate the executioner-deficiency half; that half is mechanistic hypothesis only.
