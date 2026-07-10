# ATAP-M8 susceptibility map — BAX-independent salvage for BH3-mimetic-resistant blood cancers

A **computational, hypothesis-driven susceptibility map** predicting which
BH3-mimetic-resistant (executioner-deficient) blood cancers *should* be vulnerable to a
BAX/BAK-independent mitochondrial pore-former (ATAP-M8), using only public data.

> **Read [`GUARDRAILS.md`](GUARDRAILS.md) first.** This project predicts *susceptibility
> from mechanism*. It uses **zero ATAP response data**. Every susceptibility result is
> *predicted, not measured*. **No efficacy is claimed or shown.**

## TL;DR of findings
See [`RESULTS_SUMMARY.md`](RESULTS_SUMMARY.md). Short version: the mechanism is sound; the
mechanistic **susceptibility score tracks observed venetoclax resistance** in real cell
lines (ρ=0.34) and Beat AML patients (ρ=0.23); a **novel spatial routing map** on real
lymph-node Visium flags where a BAX-independent agent is rational (16% of spots); the
cell-line executioner-loss→resistance association is **weak and the specification curve
says so** (0% of 360 specs significant after FDR).

## Layout
```
config.yaml        all paths, seeds, thresholds, gene panels (no magic numbers in code)
GUARDRAILS.md      §1 verbatim — load-bearing honesty constraints
DECISIONS.md       every threshold/cutoff/mapping choice + reason
BLOCKERS.md        ranked human-must-decide items
methods.md         dataset-by-dataset methods + Limitations
RESULTS_SUMMARY.md one-page summary + figure index
data/raw/          untouched downloads (gitignored) + MANIFEST.md (provenance)
data/processed/    analysis-ready tables
src/               fetch_data, harmonize, panels(M1), backbone(M2), confounders(M3),
                   multiverse(M4), stratify(M5/M6), spatial(M7), validation(M8), priorart(M9)
figures/           one script per figure -> outputs/figures/*.png,*.pdf
outputs/           figures/, tables/, logs/ (M*_report.md, priorart_log.md, nulls, env lock)
paper/             manuscript.md (with pre-registration), poster.md (claim map)
```

## Reproduce
```bash
python3 src/data/fetch_data.py            # download all real datasets -> data/raw + MANIFEST
python3 src/data/harmonize.py             # build data/processed tables
python3 src/backbone.py                   # M2
python3 src/confounders.py                # M3
python3 src/multiverse.py                 # M4
python3 src/stratify.py                   # M5 + M6
python3 src/spatial_run.py                # M7 (real lymph-node Visium)
python3 src/validation.py                 # M8 (synthetic)
python3 src/priorart.py                   # M9
for f in figures/fig_*.py; do python3 "$f"; done
```
Seed = 20260710 (config.yaml). Package versions: `outputs/logs/environment_lock.txt`.

## Data releases used
DepMap Public 24Q4 · GDSC 8.4 (24Jul22) · TCGA-LAML/DLBC (cBioPortal PanCancer Atlas) ·
Beat AML 2.0 (Bottomly 2022, ex vivo venetoclax AUC) · 10x Human Lymph Node Visium.
