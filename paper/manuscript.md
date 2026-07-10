# ATAP-M8 as BAX-independent salvage for BH3-mimetic-resistant blood cancers
### Computational susceptibility map (predict-and-map). Manuscript skeleton + claim map.

> **Honesty boundary (GUARDRAILS §3):** This project predicts *susceptibility from
> mechanism*. It uses **zero ATAP response data**. Every susceptibility statement is
> *predicted, not measured*. No efficacy is claimed or shown.

---

## Pre-registration — M2 backbone hypothesis (locked before M4 multiverse)

*Registered 2026-07-10, before running the specification curve (M4), so the multiverse
cannot be read as p-hacking (spec §7).*

- **Hypothesis (H1):** In heme-lineage cancer cell lines, greater executioner loss
  (BAX/BAK1 deficiency, `executioner_loss_score`) is associated with **reduced venetoclax
  sensitivity** (resistance), because the BH3-mimetic class kills through BAX/BAK.
- **Primary dataset:** DepMap heme cell lines joined to GDSC2 venetoclax dose-response.
- **Primary drug / metric:** venetoclax, `LN_IC50` (higher = more resistant).
- **Pre-registered direction:** **positive** coefficient on `executioner_loss_score`
  (executioner loss → higher LN_IC50 → resistance).
- **Primary model:** OLS `LN_IC50 ~ executioner_loss_score + C(lineage)`; effect size =
  standardized β with 95% CI; p secondary.
- **Secondary:** AUC metric; navitoclax; binary executioner-loss call; the continuous
  score's expression component alone.
- **Falsification:** a null or negative (protective) coefficient is a valid, reportable
  outcome and will be reported as such (spec M2 acceptance). We do **not** require H1 to
  be true for the project to succeed — the executioner-loss construct and the map stand
  regardless.

**A-priori caveat:** executioner loss is rare (M1: ~4.6% of heme lines), so binary-call
power is limited; the continuous score is the primary predictor.

---

## Claim map (claim → figure → data → guardrail) — filled as modules complete

| # | Claim | Figure | Data | Guardrail bound |
|---|-------|--------|------|-----------------|
| 1 | BH3-mimetics kill via BAX/BAK; executioner loss fails the whole class; ATAP bypasses it | F1 | established biology (schematic) | §3 no efficacy — established mechanism only |
| 2 | Executioner loss + high guardian dependence is present and quantifiable across heme lineages | F3 | DepMap/TCGA/BeatAML | prevalence = addressable population, not benefit |
| 3 | Executioner loss tracks venetoclax resistance (backbone) | F4 | DepMap+GDSC | correlation ≠ ATAP efficacy |
| 4 | Signal survives known confounders (MCL1, BCL2/BCL-xL ratio, BCL2 hotspots) | F5 | M3 | report increment even if small |
| 5 | Association is robust to analytic choice | F6 | M4 multiverse | figure exists to bound overclaiming |
| 6 | Susceptibility score stratifies subtypes | F7 | M5/M6 | score = mechanistic rationale, not kill rate |
| 7 | Executioner-loss patients sit in the ex vivo venetoclax-resistant tail | F8 | BeatAML | target population, not ATAP sensitivity |
| 8 | Intratumoral routing: where venetoclax is predicted sufficient vs bypass-required | F9–F10 | M7 spatial | predicted routing map, not treatment map |
| 9 | Methods recover known ground truth; structure beats chance | F11–F12 | M8 synthetic | labeled method validation only |
| 10 | Heme indication novelty + IP gate | (M9 log) | priorart_log.md | novelty is an output of M9, not asserted a priori |

*(figure/data cells updated as each module writes its results)*
