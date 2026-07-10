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

<!-- Append new decisions below as modules run. Never edit a past entry; add a new dated line. -->
