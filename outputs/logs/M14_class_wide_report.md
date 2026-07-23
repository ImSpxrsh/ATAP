# M14 — Class-wide extension with power accounting (issue #40)

**Script:** `src/analysis/class_wide.py` · **Table:** `outputs/tables/M14_class_wide_power.csv`
**Figure:** `figures/cross_agent_generalization.svg` · **Seed:** 20260710 · **No efficacy claim.**

Pre-registered family (declared before running): **3 drugs × 2 axes = 6 tests**.
Drugs: venetoclax (GDSC2, BCL2i), navitoclax (GDSC2, BCL2/BCL-xLi), S63845 (PRISM 24Q2, MCL1i).
Axes: `guardian_BCL2_minus_MCL1` (best guardian predictor, #10), `executioner_loss_score` (ATAP axis).
Power = achievable power to detect Spearman |ρ|=0.30 at α=0.05 (Fisher-z). FWER = Holm across all 6.

## Results
| drug (target) | n | power | axis | ρ | p_raw | p_Holm | verdict |
|---|---|---|---|---|---|---|---|
| venetoclax (BCL2) | 113 | 0.90 | guardian | −0.636 | <1e-4 | <1e-4 | **sig** |
| venetoclax | 113 | 0.90 | executioner | −0.004 | 0.96 | 1.00 | ns |
| navitoclax (BCL2/BCL-xL) | 115 | 0.91 | guardian | −0.699 | <1e-4 | <1e-4 | **sig** |
| navitoclax | 115 | 0.91 | executioner | +0.034 | 0.72 | 1.00 | ns |
| S63845 (MCL1) | 106 | 0.88 | guardian | −0.080 | 0.41 | 1.00 | ns |
| S63845 (MCL1) | 106 | 0.88 | executioner | +0.257 | 0.008 | 0.031 | sig* |

All three drugs are **adequately powered** (≥0.88) for a |ρ|=0.3 effect, so the nulls here are
informative, not just "too small to tell."

## Honest read (applying the issue's own discipline)
1. **The guardian axis generalizes across the two BCL2-class agents** — strong, powered, replicated
   (venetoclax & navitoclax). It is correctly **null for the MCL1 inhibitor**: a BCL2−MCL1 contrast
   should not predict MCL1-inhibitor response, and it doesn't. This is a coherent, expected pattern.
2. **The executioner axis is null for both BCL2-class agents**, as pre-registered — consistent with
   every prior module.
3. **The one executioner "hit" (S63845, ρ=+0.26, Holm p=0.031) is flagged, not celebrated.** It is a
   *single* positive out of six tests, on PRISM **single-dose** viability (noisier than dose-response
   AUC), for a different drug class. Its direction (higher executioner-loss score → more MCL1i
   resistance) is *consistent* with the ATAP premise (loss of executioners → BH3-mimetic-class
   resistance), which makes it interesting — but per this issue's rule, **a lone unreplicated hit is
   hypothesis-generating at most.** It needs dose-response confirmation and a second MCL1i cohort
   before any class-wide claim. It does **not** overturn the executioner-axis null.

## Acceptance criteria (issue #40)
- [x] Drug list registered in the test family before running.
- [x] Per-drug sample size and achievable power reported alongside every result.
- [x] Family-wise correction (Holm) across drugs × axes.
- [x] Explicit caution against interpreting a lone significant result (the S63845 executioner hit).

**Provenance caveat:** S63845 uses PRISM Repurposing 24Q2 (figshare 25917643), read directly; that
fetch is not yet wired into this repo's `fetch_data.py` (tracked separately). GDSC drugs are fully
in-repo. Without PRISM the script runs venetoclax+navitoclax self-contained.
