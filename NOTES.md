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

## Cycle 1 — 2026-07-09 (real-data access de-risked, Adharv's machine)

- **Probed whether real cohort data is fetchable in this environment — it is.** This was the open
  question blocking the project's key next step. Findings from live probes (not assumptions):
  - **cBioPortal REST API is reachable** (`https://www.cbioportal.org/api/studies` returns valid
    JSON) and contains the BeatAML studies: **`aml_ohsu_2018`** (Tyner et al. 2018) and
    **`aml_ohsu_2022`** (Bottomly et al. 2022). The 2022 study is the one carrying **venetoclax
    ex-vivo drug response** — i.e. the cohort that can actually test whether predicted
    `salvage_target`s are the venetoclax-resistant patients (the make-or-break experiment).
  - The bulk `*.tar.gz` datahub downloads 403 (not usable), but the **API path is viable and, in
    fact, well-suited here**: the gene panel is only ~39 genes (`atap.biology.all_genes()`), so
    fetching expression for that panel across all samples via the cBioPortal molecular-data API is
    small and fast — no need to download multi-GB matrices.
  - **DepMap figshare direct downloads also work** (a HEAD on a known file 302-redirects to a
    valid signed S3 URL), so DepMap cell-line expression/mutations/CRISPR-dependency is a viable
    second real cohort — useful for validating the `effector_competence` axis against real CRISPR
    BAX/BAK dependency.
- **Nothing fabricated or downloaded yet** — this cycle only established reachability and the exact
  route, deliberately not rushing a data loader at the end of a long session where an error could
  silently corrupt a "real data" result.
- **Next cycle (concrete handoff):** write `atap.data.load_cbioportal(study="aml_ohsu_2022")` — fetch
  the ~39-gene expression panel + BAX/BAK1 mutations + the venetoclax drug-response profile via the
  cBioPortal API, wire it behind the existing `--cohort` flag, run the mechanistic scorer, and test
  the real question: **do samples the model scores as `salvage_target` / low-venetoclax-axis
  actually have worse (higher-AUC) venetoclax ex-vivo response?** Ship it with a permutation null
  (shuffle response labels) and a bootstrap CI on the effect, and — critically — **report a null
  plainly if the mechanistic score does not separate responders from resistant on real patients.**
  That negative result would itself be honest, publishable-caliber information.
