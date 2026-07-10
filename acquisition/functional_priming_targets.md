# Functional apoptotic-priming data — the biggest scientific upgrade

**Why this matters most.** M3 showed the *expression-based* executioner-loss proxy adds
little beyond guardian dependence. A **functional** readout of whether a cell can execute
MOMP — BH3 profiling / dynamic BH3 profiling (DBP) — measures exactly the executioner-step
competence the thesis depends on. Replacing (or augmenting) the expression proxy with
functional priming is the single change most likely to make the association real.

## What BH3 profiling gives you
- **Overall priming** (% cytochrome c / depolarization to a promiscuous BH3 peptide) — how
  close to the apoptotic threshold the cell sits.
- **Guardian dependence** (response to BAD = BCL2/BCL-xL dependence; MS1/HRK = MCL1/BCL-xL)
  — which guardian the cell leans on (your would-be venetoclax target).
- **Executioner competence** — low priming despite dependence ≈ the "can't execute" state
  your routing calls "bypass-required."

## Targets to obtain (verify each before citing)
1. **Reduced Mitochondrial Apoptotic Priming Drives Resistance to BH3 Mimetics in AML**
   (Cancer Cell 2020). Supplemental tables carry per-sample priming/DBP values. Start here
   — likely the cleanest public priming-vs-venetoclax dataset.
   https://www.cell.com/cancer-cell/fulltext/S1535-6108(20)30541-9
2. **Beat AML controlled (phs001657)** — see `dbgap_beataml_DAR.md`; check whether the
   controlled release includes functional apoptosis assays beyond drug AUC.
3. **Letai-lab DBP cohorts** (multiple AML/CLL papers) — request per-sample priming
   matrices where not in supplements. Confirm accession/availability before relying on it.
4. **GEO/EGA search terms** to run: "dynamic BH3 profiling AML", "mitochondrial priming
   venetoclax", "BH3 profiling leukemia dataset". Log any hit in `data/raw/MANIFEST.md`.

> Do not assume any specific priming dataset is downloadable until you have opened it —
> same rule as the rest of this repo (no invented accessions). Items 1–4 are leads to
> verify, not confirmed files.

## How it plugs in (already scaffolded)
`src/functional.py` defines the expected schema: `sample_id, overall_priming,
bad_response, ms1_response, hrk_response, [venetoclax_auc]`. When a real priming table
lands, it computes a **functional executioner-competence** feature that feeds M1 (as a
4th executioner-loss component), M2/M3 (as a predictor with far more signal than
expression), and M5 (as the executioner-deficiency half of the susceptibility score).
Until then it is marked PENDING REAL DATA and emits no numbers.
