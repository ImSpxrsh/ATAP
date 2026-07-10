# ATAP-M8 — a computational susceptibility map for BAX-independent salvage in BH3-mimetic-resistant blood cancers

> **Honesty boundary (load-bearing).** This project predicts *susceptibility from mechanism*.
> It uses **zero ATAP response data** (none exists for blood cancer). Every susceptibility
> statement is **predicted, not measured**. **No efficacy is claimed or shown.** See
> [`GUARDRAILS.md`](GUARDRAILS.md).

## The idea in one paragraph
BH3-mimetics (venetoclax, MCL-1 inhibitors) kill cancer cells by freeing the executioners
**BAX/BAK** to permeabilize mitochondria. When a tumor loses BAX/BAK (mutation, deletion, or
silencing), the **entire BH3-mimetic class fails at the executioner step**. **ATAP-M8** — an
amphipathic tail-anchoring peptide from Bfl-1 (BCL2A1 aa 147–175) — forms the mitochondrial
pore **directly, without BAX/BAK**. This repo asks, computationally and from public data
only: *which blood cancers are executioner-deficient and guardian-dependent, and therefore
mechanistically rational targets for a BAX-independent agent* — and *where inside a tumor*
that need is localized.

## This repo is the union of two independent implementations
The project was built **twice, independently**, and both implementations reached the **same
conclusion** — which is built-in replication, not redundancy:

| Track | Lives in | Strengths |
|-------|----------|-----------|
| **Core library** | `src/atap/` + `scripts/` | Clean OO package (`SusceptibilityModel`, `Cohort`); BeatAML primary-cohort validation; monocytic-confound discrimination battery; glioblastoma spatial |
| **Extended analyses** | `src/*.py` + `figures/` | DepMap+GDSC breadth; real 10x Visium spatial routing + S³ stability; pan-BH3-mimetic test; susceptibility ablation; synthetic method-validation; acquisition roadmap; full F1–F13 figure suite |

**Both agree:** the **guardian-dependence axis** predicts venetoclax resistance (real signal);
the **executioner-loss axis** is **null in cell lines/patients** (rare event, weak expression
proxy) — so ATAP's target is a *rare executioner-deficient subset*, and proving it needs
**functional** data (BH3 profiling) or **engineered BAX/BAK-null lines**, not more correlation.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full tech stack and how each pipeline flows.

## Key findings (every number traces to a saved figure/table)
- **BeatAML primary cohort** (n=367): mechanistic venetoclax_score vs ex-vivo AUC ρ=−0.275,
  permutation p=0.0005 — the model identifies the venetoclax-**resistant** population.
  *(core track; `scripts/04`, `results/figures/beataml_backbone.png`)*
- **Discrimination battery:** that composite is **beaten by BCL2 expression alone** (ρ=−0.567)
  and a **monocytic-differentiation signature dominates** (ρ=+0.721) — reported, not buried.
  *(core track; `scripts/08`)*
- **Susceptibility score** tracks observed venetoclax resistance: DepMap ρ=0.34, BeatAML ρ=0.23.
  *(extended; F7, F8)*
- **Three converging nulls** (M3 confounders, pan-BH3-mimetic MCL1i crux, ablation) show the
  executioner axis is orthogonal to measured venetoclax resistance. *(extended; F5, ablation, PANMIMETIC)*
- **Spatial routing** on real 10x Human Lymph Node Visium: 16% "bypass-required" spots, per-spot
  S³ stability. *(extended; F9, F10)* Plus glioblastoma spatial stability. *(core; `results/glioblastoma/`)*
- **Methods validated** synthetically (recovery ROC-AUC=1.0; permutation nulls). *(extended; F11, F12)*
- **Prior-art gate:** heme indication appears literature-open (all prior ATAP work solid-tumor);
  patent scope flagged for IP counsel. *(both; `outputs/logs/priorart_log.md`)*

## Repository layout
```
README.md              this file
ARCHITECTURE.md        tech stack + how both pipelines work (read this next)
GUARDRAILS.md          non-negotiable honesty constraints (§1–6)
RESULTS_SUMMARY.md     one-page findings (extended track); core track in docs/
config.yaml            single merged source of truth (both pipelines read it)
environment.yml        conda env   |   requirements.txt   pip alternative

src/
  atap/                CORE LIBRARY — importable package (biology, data, features, scoring, spatial)
  *.py                 EXTENDED MODULES — panels, backbone, confounders, multiverse, stratify,
                       spatial, spatial_run, validation, priorart, functional, panmimetic, ablation
  data/                fetch_data.py, harmonize.py (extended-track data layer)
scripts/               core-track runnable pipeline, numbered 01–11
figures/               extended-track figure generators (fig_*.py) + house style
acquisition/           data-acquisition roadmap (dbGaP DAR, BH3-profiling targets, wet-lab plan)
outputs/               extended-track figures/, tables/, logs/
results/               core-track results (glioblastoma spatial, rendered figures)
paper/                 manuscript + poster (claim→figure→guardrail map)
docs/                  methods, DECISIONS, BLOCKERS, LIMITATIONS, NOTES, PROGRESS, DATA
tests/                 core-track pipeline tests
```

## Quickstart
```bash
# environment
conda env create -f environment.yml    # or: pip install -r requirements.txt

# --- core-track pipeline ---  imports src/atap, reads config.yaml
python scripts/04_validate_beataml.py   # M2 backbone on real BeatAML patients
python scripts/08_discrimination.py     # biology-vs-artifact battery
python scripts/11_spec_curve.py         # M4 specification curve

# --- extended-track pipeline ---  reads config.yaml
python src/data/fetch_data.py           # download all datasets -> data/raw + MANIFEST
python src/data/harmonize.py            # build data/processed tables
python src/backbone.py                  # M2   |  src/confounders.py  M3
python src/multiverse.py                # M4   |  src/stratify.py     M5/M6
python src/spatial_run.py               # M7 on real 10x Visium
python src/panmimetic.py                # pan-BH3-mimetic test
python src/ablation.py                  # susceptibility ablation
python src/validation.py                # M8 synthetic validation
for f in figures/fig_*.py; do python "$f"; done   # F1–F13
```
Both pipelines: `ROOT=parents[1]`, `sys.path` includes `src/`, all read the root `config.yaml`.
Raw data (~GBs) is gitignored; provenance is in [`data/raw/MANIFEST.md`](data/raw/MANIFEST.md).

## What a human must still decide
See [`docs/BLOCKERS.md`](docs/BLOCKERS.md): (1) ATAP patent claim scope (IP professional);
(2) a real bone-marrow-niche spatial dataset for a marrow claim; (3) functional BH3-profiling
data to test the executioner axis; (4) the wet-lab single-prediction validation.
