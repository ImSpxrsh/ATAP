# M3 report — confounder decomposition (venetoclax LN_IC50)

Nested OLS on z-scored venetoclax LN_IC50, lineage-adjusted. Confounders:
MCL1 expression, BCL2/BCL-xL log-ratio, BCL2 hotspot mutation.

| model | n | R² | adj R² | AIC | ΔR² | ΔAIC |
|-------|---|-----|--------|-----|-----|------|
| base (lineage) | 116 | 0.014 | 0.006 | 331.5 | nan | nan |
| +confounders | 116 | 0.445 | 0.430 | 268.9 | 0.4305 | -62.58 |
| +executioner loss | 116 | 0.445 | 0.425 | 270.8 | 0.0006 | 1.87 |

**Partial effect of executioner loss (full model):** β = 0.025 [-0.116, 0.167], p = 0.725.

**Confounder partials (full model):** mcl1_z: β=0.382 (p=3.8e-06); bcl2_bclxl_ratio_z: β=-0.485 (p=1.1e-09); bcl2_hotspot: β=0.000 (p=nan)

**Interpretation (reported as-is, not massaged — spec M3):** guardian-dependence confounders dominate venetoclax sensitivity in cell lines (R² 0.01→0.45): MCL1 expression and the BCL2/BCL-xL ratio are both strong (the ratio tracks the expected BCL2-dependence→venetoclax-sensitivity axis in this cohort, even though it is an unreliable predictor in the broader literature). **Executioner loss adds essentially no incremental signal beyond these confounders** (ΔR²≈0.0006, ΔAIC worse by ~1.9, partial p≈0.7). This is a negative result for the cell-line backbone and is carried forward honestly: the executioner-loss construct is mechanistically motivated but is NOT a strong statistical predictor of venetoclax resistance in DepMap once guardian dependence is controlled. BCL2 hotspot mutations are absent in this heme cell-line subset (rare in lines), so that arm is uninformative here.
