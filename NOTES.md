# Overnight run log — ATAP

Honest, no-overclaiming log for the autonomous iteration on the ATAP-M8 salvage-prediction
project. Source of truth for the science is `README.md` + `docs/DATA.md`; this file records what
each work cycle actually did and what the real numbers were (including nulls).

## Cycle 0 — 2026-07-09 (baseline, Adharv's machine)

- **Cloned fresh** (single `init` commit) and set up the environment: Python 3.12 venv,
  installed `requirements.txt` (numpy/pandas/scipy/scikit-learn/matplotlib — all lightweight).
- **Verified the pipeline reproduces its stated numbers on the simulated cohort** (nothing
  invented):
  - Bulk `salvage_target`: **precision 0.81, recall 0.72** (TP=48 FP=11 FN=19) vs the hidden
    BAX/BAK-loss, execution-intact ground truth.
  - Spatial: predicted ATAP-need hotspot recovers the planted resistant clone at **Jaccard 0.88,
    precision 0.88, recall 1.00**; Moran's I of the salvage index = **0.782, p=0.005**.
  - Tests: **4/4 pass** (`test_bax_loss_flips_axes`, `test_hard_escape_not_called_salvage`,
    `test_simulated_recovery`, `test_spatial_hotspot_recovers_clone`).
- **Honest framing established, carried from the MOSAIC work:** the current validation is
  entirely on a *schema-faithful simulator whose covariance structure encodes the hypothesis*.
  The README is upfront about this; it means the recovery numbers verify that the **code
  correctly implements the model**, not that the **model is true of real tumor biology**. That
  distinction matters and will not be blurred in any write-up.
- **Highest-value next step (per the project's own README):** move off the simulator onto real
  data — BeatAML is the key cohort (matched RNA-seq + venetoclax ex-vivo AUC) because it can
  actually test whether predicted `salvage_target`s are the venetoclax-resistant patients. DepMap
  is the most likely to be programmatically fetchable. If real-data access is blocked in this
  environment (same hurdle hit for MOSAIC's hosted datasets), the honest fallback is rigor work on
  the model itself: noise-robustness of the synthetic recovery, per-block ablations, permutation
  nulls + bootstrap CIs on the recovery metrics, and sensitivity of the quadrant thresholds — none
  of which require new data and all of which strengthen the computational spine.
- **No breakthrough claimed.** A working, reproducible mechanistic predictor validated on
  synthetic data is a real starting point, not a result about real cancer yet.
