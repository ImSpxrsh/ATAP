# M13 — Calibration & uncertainty for the composite score (issue #12)

**Script:** `src/analysis/calibration.py` · **Figure:** `figures/calibration_curve.svg`
**Table:** `outputs/tables/M13_calibration_curve.csv` · **Summary:** `outputs/logs/M13_calibration_summary.json`
**Cohort:** DepMap heme × GDSC2 venetoclax (n=113) · **Seed:** 20260710 · **No efficacy claim.**

## Result
The composite `venetoclax_pct` **discriminates** venetoclax sensitivity well and is **roughly
calibrated**:

| quantity | value | 95% CI |
|---|---|---|
| Discrimination AUC | 0.784 | [0.697, 0.865] |
| Spearman (score vs sensitivity) | +0.492 | [0.338, 0.629] |
| Brier score | 0.194 | [0.151, 0.237] |
| Expected Calibration Error | 0.068 | [0.038, 0.163] |
| Calibration slope (1 = ideal) | 0.67 | [0.41, 1.09] |
| Calibration intercept (0 = ideal) | −0.08 | — |

Reliability curve (quintiles) is monotonic and close to the diagonal: mean predicted
(0.09, 0.31, 0.51, 0.73, 0.92) vs observed sensitive-fraction (0.13, 0.36, 0.52, 0.59, 0.87).

## Honest read
- **Discrimination and calibration are separate properties.** The composite ranks lines well
  (AUC 0.78) — consistent with #10, where it is a real predictor even though a simpler
  `BCL2 − MCL1` baseline out-ranks it.
- **Calibration slope 0.67 (<1)** indicates mild over-confidence at the extremes: the top/bottom
  bins are slightly less separated in reality than the score implies. The CI includes 1, so this
  is a mild, not decisive, miscalibration.
- **Small bins (~23/bin) → wide per-bin CIs.** Reported, not hidden.

## Uncertainty-propagation note
The composite is deterministic given expression, so its per-line point value carries no sampling
noise of its own. The uncertainty reported here is **cohort (finite-sample) uncertainty**,
propagated by nonparametric bootstrap over cell lines (2000 resamples, seeded). That is the
honest uncertainty a ranking over this many lines actually carries; it is a genuinely
computational contribution (uncertainty-aware ranking) a single wet-lab readout cannot give.

## Acceptance criteria (issue #12)
- [x] Calibration curve for the composite score (`figures/calibration_curve.svg`).
- [x] Bootstrap CIs on the key rank correlation and on performance (AUC, Brier, ECE, slope).
- [x] Short methods note on how uncertainty is propagated (above + script docstring).
