# M12 — Baseline model battery (issue #10)

**Script:** `src/analysis/baselines.py` · **Table:** `outputs/tables/M12_baseline_battery.csv`
**Figure:** `figures/baseline_comparison.svg` · **Cohort:** DepMap heme cell lines × GDSC2
venetoclax/navitoclax (local, reproducible) · **Seed:** 20260710 · **No efficacy claim.**

Every predictive claim is measured against dumb baselines with the **same metric**
(cross-validated Spearman |ρ|, repeated 5-fold × 20) and against a **random-feature floor**.
Predictors are precomputed, *unfitted* scores, so CV quantifies out-of-fold stability.

## The headline (reported front-and-centre, whichever way it falls)
**A trivial two-gene `BCL2 − MCL1` difference is the best predictor on every spec, beating the
hand-weighted 6-block composite.** The composite only marginally beats `BCL2` alone for
venetoclax, and is beaten by `BCL2` alone for navitoclax. The composite's extra machinery is
therefore **not justified by predictive performance** — treat it as a mechanistic hypothesis,
not a validated predictor.

| spec | composite | BCL2 alone | BCL2−MCL1 | MCL1−BCL2L1 | monocytic | random floor |
|---|---|---|---|---|---|---|
| Venetoclax LN_IC50 | 0.514 | 0.430 | **0.614** | 0.132 (~rand) | 0.173 (~rand) | 0.193 |
| Venetoclax AUC | 0.511 | 0.486 | **0.636** | 0.145 (~rand) | 0.174 (~rand) | 0.184 |
| Navitoclax LN_IC50 | 0.434 | 0.442 | **0.686** | 0.528 | 0.170 (~rand) | 0.189 |
| Navitoclax AUC | 0.396 | 0.404 | **0.644** | 0.515 | 0.193 (~rand) | 0.188 |

(values = cross-validated |ρ|; **bold** = best in row; "~rand" = at/below the random 95% floor)

## Where the composite does / does not beat baselines
- **Beats `BCL2` alone:** venetoclax only (LN_IC50 0.514 vs 0.430; AUC 0.511 vs 0.486) — a
  modest edge, and the bootstrap/fold CIs overlap.
- **Does NOT beat `BCL2` alone:** navitoclax (0.434 vs 0.442; 0.396 vs 0.404).
- **Never beats `BCL2 − MCL1`** on any spec.

## Honest secondary observations
- **`MCL1 − BCL2L1` is signal for navitoclax (0.53) but noise for venetoclax (~random).**
  Mechanistically correct: navitoclax also targets BCL-xL, so the MCL1/BCL-xL contrast matters
  there and not for BCL2-only venetoclax.
- **The monocytic-differentiation signature is at the random floor in cell lines** (|ρ|≈0.17,
  p≈0.9). The monocytic confound that dominates in *patients* (BeatAML) does not appear in cell
  lines — a real cohort difference (cell lines lack the differentiation-state heterogeneity),
  and a caution against assuming the confound transfers across cohorts.

## Acceptance criteria (issue #10)
- [x] Baselines implemented: BCL2 alone, MCL1/BCL2L1 ratio, monocytic signature, random control.
- [x] Every predictive claim vs these baselines, same metric + CV scheme.
- [x] Single honest table (`M12_baseline_battery.csv`) + colorblind-safe figure.
- [x] Narrative explicitly states where the composite does and does not beat baselines (above).
