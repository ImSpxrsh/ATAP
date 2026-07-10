# BLOCKERS.md — logged blockers (a logged blocker is a success, not a failure).

Format: `[task] blocker → what was tried → what a human must decide/do`.

## Open blockers / human-must-decide (ranked)

1. **[M9 / IP] Patent scope of the ATAP / ATAP-iRGD-M8 composition is unresolved.**
   → Located: Rutgers–RWJMS holds ATAP composition/use patents (secondary sources). Could
   NOT determine from literature whether claims cover hematologic malignancies or "any
   cancer." → **A mentor / IP professional must pull the actual patent family (Google
   Patents / USPTO / Espacenet) and read claim scope** before any novelty or
   freedom-to-operate assertion. This is a search to inform the gate, not legal advice.

2. **[M7 / spatial] No verified bone-marrow niche (endosteal vs vascular) spatial dataset
   was found.** → Searched 10x demos / GEO / HCA-style sources; did NOT confirm a
   downloadable marrow-niche Visium/Xenium that resolves endosteal vs vascular niches. The
   "Bone Marrow Biogeography Atlas" was NOT assumed real (never opened one). → Fell back to
   the real 10x **Human Lymph Node** Visium (lymphoid, all BCL-2-family genes expressed),
   which makes the spatial layer a heme-relevant proof-of-concept but **not** a marrow-niche
   claim. **A human should confirm/point to a real marrow spatial dataset** (dbGaP/EGA/HCA)
   if the endosteal-vs-vascular routing claim is wanted.

3. **[M2/M3] Backbone signal is weak; construct is mechanistic, not a strong predictor.**
   → Not a data-access blocker but a scientific one to flag: executioner loss adds ~no
   signal beyond guardian dependence for venetoclax in cell lines. → **A human should
   decide** whether the poster leads with the mechanism/rationale + spatial-routing novelty
   (recommended) rather than the cell-line association, and whether to seek a cohort with
   more executioner-loss events (functional BH3 profiling / paired resistance samples).

4. **[data] BeatAML BCL-2-family LOF mutations are near-absent; mutation arm is thin.**
   → Real biology (rare), not an error. → If a functional-loss readout is desired, a human
   could add BH3-profiling / dynamic priming data (not public at scale).

5. **[gene panel] Confirm the ATAP-susceptibility gene panel with a mentor.** → The
   mito-import (TIMM/TOMM) and cardiolipin (CRLS1) genes were specified but are NOT yet used
   in the scored composite (they are candidate modulators of ATAP pore insertion, mechanism
   unproven). → **A human should confirm whether/how to weight them** before they enter a
   results claim.

## Resolved during the run
- **SSL cert failures in urllib** → switched network layer to `requests` (certifi).
- **DepMap CN scale** → OmicsCNGene is linear relative CN, not log2; cutoff corrected to
  ≤0.25 (DECISIONS.md).
- **BeatAML DNA↔RNA sample IDs** → crosswalk built from the probit file.
- **scanpy/squidpy on Python 3.14** → installed successfully (1.12.2 / 1.8.3); spatial
  layer runs on real data (no blocker).

## Environment notes
- Python 3.14; system venv (not conda). Versions locked in
  `outputs/logs/environment_lock.txt`.
