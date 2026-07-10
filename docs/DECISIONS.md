# DECISIONS.md — every threshold, cutoff, gene choice, and mapping, with its reason.

Format: `YYYY-MM-DD — [module] decision → reason`.

## 2026-07-10 — Foundation
- **[repo] Use system Python 3.14 venv, not conda.** → Conda env unavailable in the run
  environment; core scientific stack (pandas 3.0, numpy 2.4, scipy 1.17, sklearn 1.9,
  statsmodels, lifelines) is installed and version-locked to
  `outputs/logs/environment_lock.txt`. Reproducibility preserved via the lock file +
  `environment.yml` spec.

- **[M1] Executioner-loss = mutation OR deep deletion OR bottom-decile expression of
  BOTH BAX and BAK1.** → Matches spec §M1. "Both low" (not either) for the expression
  arm because losing one executioner still leaves a functional pore-forming path; the
  hypothesis concerns loss of the executioner *step*, which requires both to be
  compromised. Binary call = any component true; continuous score = mean of available
  components.

- **[M1] expr_low_quantile = 0.10 (bottom decile).** → Spec names "bottom-decile." Swept
  over {0.05, 0.10, 0.20} in the M4 multiverse so the choice is not load-bearing.

- **[M1] cn_deep_del_log2 = -1.0.** → Provisional. MUST be re-confirmed against the real
  DepMap CN distribution before use (relative vs absolute CN scaling differs by
  release). Flagged; will update this line with the confirmed value + release.

- **[M2] Pre-registered primary spec: venetoclax, LN_IC50, positive coefficient =
  resistance.** → Venetoclax (ABT-199) is the clinically dominant BH3-mimetic and the
  BeatAML anchor. LN_IC50 chosen as primary because it is the direct GDSC potency
  readout; AUC run as secondary. Direction pre-registered BEFORE M4 to prevent the
  multiverse being read as p-hacking (spec §7).

- **[M1] CN deep-deletion cutoff = relative CN ≤ 0.25 on DepMap OmicsCNGene (LINEAR,
  neutral≈1.0), NOT log2 −1.0.** → Confirmed against the real distribution: heme BAX/BAK1
  relative CN is centered at ~1.01 (min 0.49), so the original log2 −1.0 cutoff never
  fired (scale mismatch — a latent bug that happened to give the right count for the
  wrong reason). 0.25 (~log2 −2) is the standard deep/homozygous-deletion bar. For
  TCGA/cBioPortal GISTIC, deep deletion = −2 (separate arm in harmonize.py). Result:
  0 BAX/BAK1 deep deletions in 348 heme lines — biologically expected; executioner
  homozygous deletion is rare. Executioner loss in cell lines is therefore driven by
  the expression (bottom-decile-both) and mutation arms.

- **[M1] Executioner loss is rare (16/348 DepMap heme lines ≈ 4.6%; 15/707 BeatAML).**
  → Recorded as a real cohort characteristic, not massaged. Low prevalence limits binary
  power in M2; the continuous expression-based gradient is the primary predictor and the
  binary call is secondary. This caveat propagates to methods.md Limitations.

- **[M0] BeatAML mutation calls keyed by DNA sample (…D); expression/AUC by RNA sample
  (…R). Crosswalk built from the probit file's paired dnaseq/rnaseq columns.** → Without
  it the mutation arm silently contributed nothing. BCL-2-family LOF is rare in AML so
  impact is small, but the join is now correct.

- **[M7] Spatial section = 10x Genomics V1_Human_Lymph_Node Visium (real, downloadable).**
  → Candidates considered (≥3, spec §3): (1) 10x V1_Human_Lymph_Node (Visium, lymphoid) —
  CHOSEN; (2) 10x V1_Breast_Cancer_Block_A (solid-tumor fallback); (3) 10x
  V1_Mouse_Brain / Parent_Visium_Human_* demos. Lymph node chosen because it is a
  secondary lymphoid organ (tissue of origin for lymphomas) and all six BCL-2-family panel
  genes are detectably expressed (BAX 82%, BAK1 61%, BCL2 64%, MCL1 99%, BCL2A1 72%,
  BCL2L1 56% of spots nonzero) → clears QC as a heme-relevant section. Downloaded via
  `scanpy.datasets.visium_sge`. Not bone-marrow niche data (see BLOCKERS) — it is
  lymphoid, so the routing map is a lymphoid-tissue proof-of-concept, honestly scoped.

- **[M7] Routing thresholds: guardian_hi=0.6, exec_lo=0.4 rank cutoffs (primary); swept
  over {0.5,0.6,0.7}×{0.3,0.4,0.5}×norm{rank,zscore,minmax}×k{0,6,12} = 81 specs for the
  per-spot S³ stability.** → All in src/spatial.py MULTIVERSE; no magic numbers in figures.

<!-- Append new decisions below as modules run. Never edit a past entry; add a new dated line. -->
