# Pan-BH3-mimetic analysis — executioner loss vs class-wide resistance

Standardized β (per +1 SD executioner-loss score) on z-scored LN_IC50, lineage-adjusted. Positive = executioner loss → resistance.

| drug | class | n | β crude | 95% CI | p | β +guardian | p +guardian |
|------|-------|---|---------|--------|---|-------------|-------------|
| venetoclax | BCL2-selective | 170 | 0.076 | [-0.076,0.228] | 0.325 | 0.016 | 0.849 |
| navitoclax | BCL2/xL/w | 171 | 0.128 | [-0.022,0.278] | 0.0947 | 0.101 | 0.209 |
| abt737 | BCL2/xL/w | 165 | 0.100 | [-0.051,0.251] | 0.194 | 0.047 | 0.581 |
| azd5991 | MCL1-selective | 130 | 0.066 | [-0.098,0.231] | 0.427 | 0.042 | 0.69 |
| mim1 | MCL1-selective | 160 | -0.125 | [-0.277,0.027] | 0.107 | -0.108 | 0.272 |
| umi77 | MCL1-selective | 130 | 0.002 | [-0.161,0.165] | 0.98 | 0.053 | 0.631 |
| wehi539 | BCL-xL-selective | 165 | 0.101 | [-0.061,0.263] | 0.219 | 0.134 | 0.203 |
| obatoclax | pan-guardian | 158 | -0.083 | [-0.244,0.078] | 0.312 | 0.027 | 0.803 |
| sabutoclax | pan-guardian | 158 | 0.005 | [-0.146,0.157] | 0.944 | 0.078 | 0.425 |
| tw37 | pan-guardian | 160 | -0.018 | [-0.181,0.145] | 0.824 | 0.058 | 0.583 |

**Pan-class resistance score** (mean across all mimetics, n=120): β=0.085 [-0.104,0.273], p=0.376; adjusted for guardian dependence β=0.081 (p=0.379).

**MCL1-selective inhibitors** (azd5991,mim1,umi77, n=114) — the crux test: β=-0.043 (p=0.653); +guardian β=-0.042 (p=0.655). Result: **null** (near-zero/again non-significant) — executioner loss as operationalized by expression does NOT predict MCL1i resistance.

## Verdict (reported as-is)
**The class-wide test is null.** Executioner loss, as operationalized from expression/CN/mutation, does NOT coherently predict resistance across the BH3-mimetic class (including MCL1-selective inhibitors) in heme cell lines. Individual drug βs scatter around zero with no consistent sign. This is the expected consequence of the M1/M3 findings — executioner loss is rare in cell lines and the expression proxy is a weak surrogate for functional executioner competence.

**What this means for the project (not a failure — a signpost):** the cell-line + expression approach has reached its ceiling for *demonstrating* the mechanism. The class-wide executioner-loss hypothesis is not refuted (it predicts BAX/BAK-*null* cells fail the class; genuine null lines are near-absent in GDSC), but it cannot be *shown* here. This is direct evidence that the decisive data is (a) functional apoptotic priming (BH3 profiling) and/or (b) engineered BAX/BAK-null lines — exactly the acquisition targets already queued. No efficacy is claimed.
