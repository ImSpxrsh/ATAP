# Claim provenance ledger (issue #30)

Every factual claim in the abstract, poster, research plan, and preprint must trace to **one of**:
a paper a team member has personally opened; a dataset a team member has personally loaded; or an
analysis a team member has personally **run and inspected the output of**. This applies with
particular force to anything an AI assistant produced — AI code can produce plausible-but-wrong
statistics, so each generated script needs a **named human who read its output**, not a green CI check.

**How to use this file**
- `Verified by` / `Date` start as **PENDING** for every AI-generated analysis. A human fills them
  in only after opening the cited output file and confirming the number matches the claim.
- A claim that cannot be sourced is **cut, not softened** (see the Cut list at the bottom).
- Literature claims require a team member to have opened the paper; the citation is not enough on its own.

Legend — Source type: `analysis` (script + output on real data) · `dataset` (raw load) ·
`paper` (external literature) · `external` (fair/ISEF rules — must be confirmed in writing).

## A. Analysis claims (traceable to a script + saved output in this repo)
| # | Claim | Source | File / output | Verified by | Date |
|---|---|---|---|---|---|
| A1 | Guardian axis (BCL2−MCL1) predicts venetoclax resistance, cross-validated | analysis | `src/analysis/baselines.py` → `outputs/tables/M12_baseline_battery.csv` | PENDING | — |
| A2 | The hand-weighted composite is **beaten by** the trivial BCL2−MCL1 baseline on every spec | analysis | same as A1 + `outputs/logs/M12_baseline_report.md` | PENDING | — |
| A3 | Composite discriminates venetoclax sensitivity (AUC 0.78) and is roughly calibrated (ECE 0.068, slope 0.67) | analysis | `src/analysis/calibration.py` → `outputs/logs/M13_calibration_summary.json` | PENDING | — |
| A4 | Guardian axis generalizes across BCL2-class agents (venetoclax, navitoclax); null for the MCL1 inhibitor | analysis | `src/analysis/class_wide.py` → `outputs/tables/M14_class_wide_power.csv` | PENDING | — |
| A5 | Executioner-loss axis is null for venetoclax & navitoclax at adequate power (~0.9) | analysis | same as A4 | PENDING | — |
| A6 | Executioner axis shows ONE unreplicated hit for S63845 (ρ=+0.26) — hypothesis-generating only, not a claim | analysis | same as A4 + `outputs/logs/M14_class_wide_report.md` | PENDING | — |
| A7 | Executioner-loss is a rare state (~2.6% DepMap heme; ~1.4% Beat AML) | analysis | `scripts/07_depmap_executioner.py`, `src/atap/features.py` | PENDING | — |
| A8 | Monocytic-differentiation signature dominates venetoclax resistance in patients but is at the random floor in cell lines | analysis | `scripts/08_discrimination.py`; `outputs/tables/M12_baseline_battery.csv` (cell-line side) | PENDING | — |
| A9 | Spatial routing is a lymphoid **proof-of-concept**, not a marrow claim | analysis + dataset | `src/spatial_run.py`; 10x V1 Human Lymph Node Visium | PENDING | — |
| A10 | Executioner axis is null across expression, functional CRISPR, and two drug platforms | analysis | M3 confounders; `scripts/12_functional_vs_expression.py`; A4 | PENDING | — |

## B. Dataset claims (traceable to a raw load + MANIFEST)
| # | Claim | Source | File | Verified by | Date |
|---|---|---|---|---|---|
| B1 | Cell-line venetoclax/navitoclax response from GDSC release-8.4 (24Jul22) | dataset | `data/raw/gdsc/…`, `data/DATA_VERSIONS.lock` | PENDING | — |
| B2 | Cell-line expression / CN / mutations / CRISPR from DepMap 24Q4 | dataset | `data/raw/depmap/…`, `data/DATA_VERSIONS.lock` | PENDING | — |
| B3 | Patient venetoclax ex-vivo response from Beat AML 2.0 | dataset | `data/raw/beataml/…` | PENDING | — |
| B4 | S63845 (MCL1i) response from PRISM Repurposing 24Q2 (figshare 25917643) | dataset | `data/raw/prism/…` (fetch tracked separately) | PENDING | — |

## C. Literature claims (a team member must have opened the paper)
| # | Claim | Source | Citation | Verified by | Date |
|---|---|---|---|---|---|
| C1 | BAX inactivating mutations arise in ~17% of AML relapsing after venetoclax | paper | Moujalled et al., *Blood* 2023 (PMC10651776) — **open and confirm the exact figure** | PENDING | — |
| C2 | Monocytic AML is venetoclax-resistant via a broad differentiation program | paper | Pei et al. — **open and confirm** | PENDING | — |
| C3 | Clinical stakes figure (incidence / relapse burden of the target population) | paper/external | **source not yet fixed — must be pinned to a specific reference before use** | PENDING | — |

## D. External / competition claims (must be confirmed in writing — see linked issues)
| # | Claim | Source | Status | Verified by | Date |
|---|---|---|---|---|---|
| D1 | TNJSF advancement structure & ISEF trip-award slot count | external | **BLOCKED — email the fair (issue #60); do not cite any number until answered in writing** | PENDING | — |
| D2 | Current-year ISEF form set and display-&-safety rules | external | **must be confirmed against the current-year official ISEF rulebook** (not an older cached copy) | PENDING | — |

## E. AI-generated-script sign-off register (issue #30, final criterion)
Each analysis script must have a named human who ran it and read its output. **All PENDING** until signed.
| Script | Output a human must read | Read & confirmed by | Date |
|---|---|---|---|
| `src/analysis/baselines.py` | `outputs/tables/M12_baseline_battery.csv` + figure | PENDING | — |
| `src/analysis/calibration.py` | `outputs/logs/M13_calibration_summary.json` + curve | PENDING | — |
| `src/analysis/class_wide.py` | `outputs/tables/M14_class_wide_power.csv` + figure | PENDING | — |
| `scripts/12_functional_vs_expression.py` | its printed table | PENDING | — |
| `scripts/07_depmap_executioner.py` | its printed output | PENDING | — |

## Cut list (claims dropped because they cannot currently be sourced)
- Any statement that ATAP **works / kills / is effective** in blood cancer — no such data exists; permanently cut (GUARDRAILS).
- Any TNJSF odds/slot number — cut until D1 is answered in writing.
- The clinical-stakes figure (C3) — cut from the abstract until pinned to a specific citation.

---
*Provenance note: this ledger was drafted by an AI assistant and lists the correct source files, but
every `Verified by` cell is deliberately PENDING. The ledger is not "done" until a human has filled
those in — that human sign-off is the actual deliverable of issue #30.*
