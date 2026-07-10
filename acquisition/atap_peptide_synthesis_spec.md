# ATAP-iRGD-M8 — peptide sequence & synthesis spec

> Source: De et al., *Amphipathic tail-anchoring peptide is a promising therapeutic agent for
> prostate cancer treatment*, **Oncotarget 2014** (PMC4202157), Table 2 + sequence text.
> **Verify the exact sequence against the paper's Table 2 and the Rutgers patent before ordering
> synthesis** — this was transcribed from the paper, and one wrong residue makes a dead peptide.

## Sequences
| Construct | Sequence | Notes |
|-----------|----------|-------|
| **ATAP core** (Bfl-1/BCL2A1 aa 147–175) | `KFEPKSGWMTFLEVTGKIAEMLSLLKQYC` | 29 aa; the mitochondrial pore-forming tail anchor |
| **iRGD** | `CRGDKGPDC` | tumor-penetrating, cyclic (internal disulfide); binds αvβ3/αvβ5 + neuropilin-1 |
| **ATAP-iRGD (parental)** | `KFEPKSGWMTFLEVTGKIAEMLSLLKQYCRGDKGPDC` | disulfide bridge Cys29–Cys37 |
| **ATAP-iRGD-M8** | `Ac-KKFEPKSGWMTFLEVTGKIAEMLSLLKQYCRGDKGPDC-amide` | the optimized construct we'd test |

## M8 modifications (vs parental ATAP-iRGD)
1. **N-terminal acetylation** (`Ac-`) — blocks exopeptidase degradation → longer half-life.
2. **C-terminal amidation** (`-amide`) — same, and removes a terminal charge.
3. **One extra N-terminal lysine** (the `KK…` instead of `K…`) — improves aqueous solubility.
- Reported activity: cytotoxicity comparable to parental, **IC50 = 2.1 ± 0.5 µM** in cultured
  cancer cells; improved stability/solubility; longer blood half-life.

## Synthesis notes (for a vendor order — GenScript / Peptide2.0 / CPC Scientific)
- **Length 38 aa** with a **disulfide** (Cys29–Cys37) → specify **oxidized/cyclized** form.
- **Modifications:** N-term acetyl, C-term amide, as above.
- **Purity:** ≥95% HPLC for cell assays; provide **MS + HPLC QC**.
- **Two Cys but one intended bridge** — confirm the vendor forms the Cys29–Cys37 bond and
  doesn't scramble; ATAP's own Cys (position 29 in the core numbering) is part of the designed
  bridge to the iRGD Cys.
- **Controls to order alongside** (for the F13 experiment): a **scrambled-sequence** peptide of
  identical composition, and optionally **ATAP-iRGD parental** (no M8 mods) as a comparator.
- Solubility: formulate per the paper (physiological saline; M8 was optimized for this).

## Freedom-to-operate (do not skip)
Rutgers–RWJMS holds ATAP composition/use patents. **Synthesis for internal research use** vs any
**commercial/clinical** use are different legal questions — clear with your institution's
tech-transfer office before ordering (this is the IP blocker in [`../docs/BLOCKERS.md`](../docs/BLOCKERS.md)).

## Where it's used
This peptide is the agent in the pre-registered validation ([`validation_plan_prereg.md`](validation_plan_prereg.md)):
ATAP-iRGD-M8 vs venetoclax on a BAX/BAK-null, venetoclax-resistant blood-cancer line.
