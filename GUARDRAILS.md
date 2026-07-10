# GUARDRAILS — non-negotiable rigor + honesty constraints

Restated verbatim from the master build specification (§1). These are load-bearing hard
constraints. Violating any one is a defect. Every empirical claim in this project is bound by them.

1. **Real data for every empirical claim.** All quantitative findings come from DepMap, GDSC,
   BeatAML, TCGA, and public spatial datasets. Synthetic data is permitted ONLY for the uses
   enumerated in §1a. If a figure or sentence makes a biological claim, it must trace to real data.

2. **Synthetic data can validate methods, never establish biology.** See §1a for the exhaustive
   allow-list. Any synthetic-derived number that appears in a results claim is a defect.

3. **No efficacy claims. Ever.** This project predicts *susceptibility* and *rationale*. It does
   not, and computationally cannot, show that ATAP-M8 kills anything. Banned phrasings: "ATAP-M8
   kills," "we show ATAP is effective," "confirms ATAP therapy." Allowed framing: "predicted to be
   susceptible," "mechanistically rational," "identifies the target population."

4. **Every predictive claim ships with three companions:** (a) a confounder-adjusted model, (b) a
   null/permutation baseline, (c) a specification-curve robustness panel. A point estimate with
   none of these does not go on a figure.

5. **Novelty is an output, not an input.** The "nobody has connected this" claim only appears after
   the prior-art gate (M9) runs and logs a negative result with a dated, reproducible search
   protocol.

6. **Reproducibility is mandatory.** Pin every package version. Record the exact data release
   (DepMap release ID, GDSC version, BeatAML data freeze, TCGA download date). Seed every
   stochastic step. One `environment.yml`, one `config.yaml` holding all paths/seeds/thresholds.
   No hard-coded magic numbers in analysis code — they live in `config.yaml`.

## §1a — Synthetic data: the ONLY legitimate uses

- **Pipeline validation:** simulate spatial/single-cell data with a *known* ground-truth BAX/BAK
  spatial pattern and a *known* response rule; confirm the pipeline and the stability score
  recover it.
- **Power analysis:** estimate spots/cells/samples needed to detect a priming gradient at a given
  effect size.
- **Null models:** permutation nulls establishing that observed spatial structure or association
  exceeds chance.
- **Robustness stress-tests:** simulated dropout, batch effect, and technical noise to test method
  stability.

Anything else synthetic is out of scope and must be rejected.

## Stop conditions

Do NOT: fabricate ATAP-response data; state an efficacy conclusion; assert novelty before M9 logs
it; report any synthetic-derived number as a biological result. If a task would require any of
these, halt and flag for Sparsh.
