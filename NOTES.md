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

## Cycle 2 — 2026-07-09 (first real-patient run, Adharv's machine)

- **Ran the ATAP model on real patients for the first time.** Added `atap.data.load_cbioportal()`
  (live cBioPortal REST API, no download/registration — pulls only the ~39-gene panel, so it's
  small/fast) and `scripts/03_score_real.py`. Fetched **671 real BeatAML AML patients**
  (`aml_ohsu_2022`), scored them with the existing mechanistic model.
- **Real result (671 patients):** predicted quadrants — `standard_of_care` 60.1%,
  **`salvage_target` 20.7% (139 patients)**, `hard_escape` 19.2%. Internal mechanistic check
  **holds on real expression**: salvage_target patients carry a substantially lower BAX/BAK
  effector axis than the rest (**−0.82 vs −0.17**), which is exactly the mechanism the priors
  encode (low effector competence → ATAP-favored). So the model behaves correctly on real data,
  not just on the simulator.
- **What this is NOT (stated plainly):** this is *prediction*, not validation. Two honest limits:
  (1) **cBioPortal's BeatAML has no venetoclax ex-vivo response** — only clinical induction-chemo
  response (`RESPONSE_TO_INDUCTION_TX`), the wrong readout — so I cannot yet confirm these 139
  predicted salvage_targets are actually venetoclax-resistant. That validation needs the
  Vizome/Bottomly-2022 drug-response supplement (a separate source). (2) The quadrant thresholds
  are within-cohort percentiles (VENETO_LOW=0.40, ATAP_HIGH=0.60), so the ~20% salvage prevalence
  is partly threshold geometry, not a strong standalone claim — the **meaningful** real-data
  finding is the internal-consistency one (salvage_target ⟺ genuinely lower BAX/BAK), not the raw
  fraction.
- **Also real and biologically correct:** only **1 BAX/BAK1 loss-of-function mutation** across 671
  patients — genetic BAX/BAK loss is rare in AML; the common resistance route is expression/
  functional loss, which is exactly what drives the effector axis here. The model doesn't lean on
  rare mutations.
- 4/4 tests still pass; nothing under `data/raw` committed (all fetched live, in memory).
- **Next:** the make-or-break venetoclax-response validation needs the Vizome supplement — attempt
  to fetch the Bottomly-2022 ex-vivo AUC table (vizome.org / paper supplement) and join it to
  these 671 samples, then test whether predicted salvage_targets / low-veneto-axis patients really
  are the venetoclax-resistant ones, with a permutation null + bootstrap CI. If that table isn't
  cleanly fetchable, the DepMap CRISPR-BAX-dependency route is the honest alternative validation.

## Cycle 3 — 2026-07-09 (M2 backbone VALIDATED on real patients, Adharv's machine)

- **Got the make-or-break real-data validation, and it holds.** This is module **M2** (the
  falsifiable core) from the build spec, on the **primary external cohort (BeatAML)**.
- **What I did:** fetched the BeatAML2 venetoclax **ex-vivo dose-response AUC** table (Bottomly
  et al. 2022, `biodev/beataml2.0_data`, via the GitHub media/LFS endpoint), reconciled sample IDs
  cleanly on the `BA####` barcode (cBioPortal `aml_ohsu_2022_2000_BA2123` ↔ drug-table
  `BA2123R`), and joined it to the model's mechanistic scores. **367 real AML patients** have both
  the ~39-gene expression panel and a venetoclax AUC. Committed as `scripts/04_validate_beataml.py`.
- **Real result (the model is NOT fit to the drug data — pure BCL-2-biology prior, so this is
  genuine out-of-the-box prediction):**
  - `venetoclax_score` vs venetoclax ex-vivo AUC: **Spearman rho = −0.275, permutation p = 0.0005,
    95% bootstrap CI [−0.362, −0.183]** — negative exactly as the mechanism predicts (higher
    predicted-sensitivity axis → lower AUC → genuinely more sensitive), CI excludes zero.
  - `salvage_index` vs AUC: **rho = +0.278, p = 0.0005, CI [+0.182, +0.366]** — the patients the
    model flags as ATAP-favored are genuinely the venetoclax-resistant ones.
  - Responder-vs-resistant separation (outer tertiles): venetoclax_score median **+0.19
    (sensitive) vs −0.82 (resistant), Mann-Whitney p = 1.1e-07**.
  - Figure: `results/figures/beataml_backbone.png`.
- **Honest scope (GUARDRAILS.md #3 — no efficacy claims):** rho ≈ −0.28 is a **real but modest**
  association (~8% of rank variance) — highly significant and CI-bounded, but not huge. And it
  validates only the **venetoclax-resistant target population** (the first half of the
  salvage_target logic). It does **NOT** show ATAP-M8 works on these patients — no ATAP-response
  data exists anywhere; that remains the wet-lab step. Not a "breakthrough," and not framed as one.
- **Also added `GUARDRAILS.md`** (spec §1 verbatim) as the rigor contract for all downstream work.
- **Heads-up / cross-repo issue:** the other instance's commit `1ed0c4e "updated"` pushed **MOSAIC**
  artifacts into THIS repo by mistake — `poster/mosaic_isef_poster.pdf/pptx` and
  `results/glioblastoma/aggregate/*` (MOSAIC glioblastoma spatial output). Left in place (did not
  delete another instance's push), but it's wrong-repo contamination that should be cleaned up.
- **Next (per build spec backlog):** M1 formal executioner_loss score + M3 confounder decomposition
  (does executioner state add signal beyond MCL1 / BCL2:BCL-XL ratio / BCL2 gatekeeper mutations on
  this same BeatAML cohort?), then M4 specification curve over the analytic choices. Foundation
  files (config.yaml, environment.yml) still to add.

## Cycle 4 — 2026-07-09 (M3 confounder decomposition — an honest NULL, Adharv's machine)

- **Ran M3 on the same real BeatAML n=367.** Nested linear models predicting venetoclax ex-vivo
  AUC: base -> +confounders (MCL1 expression, BCL2:BCL2L1/Bcl-xL ratio) -> +executioner (BAX/BAK)
  state. (BCL2 gatekeeper mutations: **0 in the cohort**, dropped.) `scripts/05_confounders_m3.py`.
- **Result — a real, reportable NULL (not massaged, per GUARDRAILS #4 / spec M3):**
  confounders alone explain R²=0.225 of venetoclax-AUC variance; adding executioner state gives
  R²=0.226 — **ΔR²=+0.001, ΔAIC=+1.6 (i.e. the model gets *worse* by AIC), permutation p=0.53,
  partial Spearman(exec, AUC | confounders)=+0.04.** Executioner (BAX/BAK) state adds essentially
  **nothing** beyond the known confounders for predicting venetoclax resistance in this cohort.
  (The raw linear partial coefficient looked large but is unreliable here due to collinearity
  between BAX/BAK and the guardian axis — the rank-based partial Spearman ≈0 and the ΔR²/ΔAIC/perm-p
  all agree: null. I lead with those, not the misleading coefficient.)
- **What this means — and does NOT mean (honest interpretation):** this does *not* refute the ATAP
  mechanism, and it does not weaken the M2 result. It **refines the thesis and prevents an
  overclaim.** M2's composite score predicts venetoclax resistance, but M3 shows that predictive
  power is carried by the **guardian/MCL1 axis** (the dominant, well-established AML venetoclax-
  resistance mechanism), **not** by executioner state specifically. Executioner (BAX/BAK) loss is
  **rare** in AML — only 1 LoF mutation in 671 patients — so at the population level it cannot and
  does not explain general venetoclax resistance. **Correct honest framing going forward:**
  executioner loss defines a *narrow, specific, rare* ATAP-salvage subset that must be identified
  by executioner state directly (this is exactly what M1's executioner_loss_score is for) — it is
  NOT the explanation for common venetoclax resistance. Any claim that "executioner loss explains
  venetoclax resistance" would be false and is now ruled out on real data.
- **Consequence for the roadmap:** M1 (formal executioner_loss_score) becomes more important, not
  less — the value is in cleanly *isolating* the rare executioner-loss subset, then asking whether
  THAT subset is enriched in the venetoclax-resistant tail (a subgroup analysis), rather than
  treating executioner state as a general predictor. Also worth testing on DepMap heme cell lines
  where genetic BAX/BAK loss + CRISPR dependency may be better represented than in primary AML.
- No efficacy claims made. PROGRESS.md M3 updated to done (null).

## Cycle 5 — 2026-07-09 (M1 executioner-loss score + underpowered subgroup, Adharv's machine)

- **Implemented M1** `features.executioner_loss_score()` — a transparent 0–1 per-sample score
  defined purely from BAX/BAK state (redundancy-aware: availability = max of the two effectors'
  within-cohort expression percentiles; a LoF mutation zeroes that gene; binary call = both
  effectors in the bottom decile OR a LoF). Defined WITHOUT any reference to drug/ATAP data, so it
  is a clean independent stratifier. `scripts/06_m1_executioner_subgroup.py`. 4/4 tests still pass.
- **Subgroup test on real BeatAML (n=367) — the honest follow-up to the M3 null:** is the isolated
  executioner-loss subset enriched in the venetoclax-resistant tail? **Result: underpowered, cannot
  conclude.** The executioner-loss subset is **n=5 (1.4%)** — and all 5 are bottom-decile-expression
  calls (essentially zero genetic BAX/BAK loss in primary AML, consistent with cycle 2's 1 LoF/671).
  Direction is *weakly* consistent with the hypothesis (loss median venetoclax AUC 164.1 vs 157.9,
  i.e. slightly more resistant, gap +6.2) but **not significant and not interpretable at n=5**:
  Mann-Whitney p=0.32, permutation p=0.45, Fisher OR=inf but p=0.50 (only 2 loss cases in the
  tested tertiles). Reported as underpowered, not spun into a positive.
- **What this establishes (honestly):** primary AML is the **wrong cohort** to test the specific
  ATAP-salvage subset, because the executioner-loss phenotype is too rare there (~1%). This isn't a
  failure of the hypothesis — it's a correct identification of where the hypothesis *can* be tested.
  The M1 score works and is clean; the cohort just lacks the phenotype.
- **Clear next step (now the top empirical priority):** the **DepMap heme route** — cell lines carry
  genetic BAX/BAK deletions and CRISPR BAX/BAK gene-effect (real functional executioner dependency),
  so the executioner-loss phenotype is far better represented than in primary AML. Test there
  whether executioner state tracks (a) real CRISPR BAX/BAK dependency and (b) venetoclax/navitoclax
  resistance (GDSC/PRISM), with null + CI. DepMap figshare downloads verified reachable in cycle 1.
- PROGRESS.md updated: M1 done (score implemented; BeatAML subgroup underpowered → DepMap next).
