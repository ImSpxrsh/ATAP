# Prognostic layer — mechanistic score vs overall survival (Beat AML)

n = 649 patients with overall survival + score. Beat AML is largely pre-venetoclax-era with heterogeneous treatment — this is a prognostic/biological association, not evidence the score guides therapy.

## Kaplan-Meier (susceptibility tertiles)
- Median OS (months): low=470.0 (n=217), mid=455.0 (n=215), high=520.0 (n=217).
- Log-rank across tertiles: p = 0.355.

## Cox proportional-hazards (HR per +1 SD; >1 = worse survival)
| axis | HR (unadj) [95% CI] | p | HR (adj: age+ELN2017) [95% CI] | p |
|------|---------------------|---|-------------------------------|---|
| susceptibility | 1.04 [0.94,1.15] | 0.415 | 0.98 [0.88,1.08] | 0.632 |
| guardian_dependence | 0.93 [0.84,1.03] | 0.144 | 0.92 [0.83,1.02] | 0.109 |
| executioner_availability | 0.86 [0.78,0.95] | 0.00409 | 0.94 [0.85,1.04] | 0.254 |

**Reading:** interpret the adjusted HR (controls for ELN2017 risk + age). A significant guardian/susceptibility HR would mean the mechanistic axis carries prognostic information beyond standard risk; a null means it is a drug-response axis, not a prognostic one — both are honest, reportable outcomes. No efficacy claim.
