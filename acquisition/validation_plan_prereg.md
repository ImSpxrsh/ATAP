# Pre-registered validation — one map-derived prediction, one experiment

The breakthrough is not the prediction; it's the prediction **confirmed**. This is a
single, falsifiable test designed so a "no" is as informative as a "yes." Hand to your
wet-lab collaborator. (This corresponds to figure F13.)

## The prediction being tested (locked before the experiment)
> A blood-cancer line that is (i) **BAX/BAK-deficient** (executioner loss) and (ii)
> **venetoclax-resistant** will be killed by ATAP-iRGD-M8 at a dose where venetoclax fails,
> whereas an executioner-intact, venetoclax-sensitive line is killed by both.

This follows directly from the map: executioner-loss → BH3-mimetic class fails at the
executioner step → a BAX/BAK-independent pore-former should still induce MOMP.

## Minimal design (2×2, the smallest decisive experiment)
| line | executioner state | venetoclax | ATAP-M8 (predicted) |
|------|-------------------|-----------|----------------------|
| BAX/BAK-DKO (e.g. CRISPR-engineered from a sensitive parental) | lost | resistant | **sensitive** (key cell) |
| isogenic parental | intact | sensitive | sensitive |
| known venetoclax-resistant, executioner-intact | intact | resistant | may resist (specificity control) |
| non-malignant control (e.g. PBMC) | intact | — | toxicity check |

Isogenic BAX/BAK-DKO vs parental is the cleanest design — it isolates executioner state as
the only variable.

## Readouts
- Viability dose-response (CellTiter-Glo) → IC50 for venetoclax and ATAP-M8 per line.
- MOMP / apoptosis: cytochrome c release or Annexin V, ± caspase; confirm ATAP-M8 kills via
  MOMP even in the DKO.
- Primary endpoint: **ATAP-M8 IC50 in the DKO is not worse than in the parental**, while
  **venetoclax IC50 in the DKO is much worse** (resistant). That dissociation is the result.

## Controls & rigor
- Scrambled/inactive peptide control; vehicle.
- ≥3 biological replicates; pre-register the IC50 threshold and the "resistant" cutoff.
- Blind the analysis to line identity where feasible.

## What counts as falsification
If ATAP-M8 fails to kill the BAX/BAK-DKO line, the BAX-independent-salvage hypothesis is
wrong for that context — report it. The design is built so a negative is publishable and
honest, not a fishing expedition.

## Sourcing
- ATAP-iRGD-M8: `atap_outreach_email.md` (collaboration) or synthesize from the published
  sequence (De et al. 2014 + patent).
- Lines: a BAX/BAK-DKO of a venetoclax-sensitive AML line (e.g. engineered in-house), plus
  a documented venetoclax-resistant line. Pick the specific line from the map's
  highest-susceptibility, executioner-loss calls once functional priming data (#2) is in.
