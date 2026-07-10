# PROGRESS — ATAP-M8 salvage project

Maps the master build spec (modules M0–M9, figures F1–F13, backlog P0–P4) to current status.
Rigor contract: [`GUARDRAILS.md`](GUARDRAILS.md). Honest run log: [`NOTES.md`](NOTES.md).

## Status by module

| Mod | What | Status |
|-----|------|--------|
| M0 | Data acquisition + MANIFEST | **partial** — cBioPortal API (BeatAML expr+mut) and BeatAML2 drug-response (venetoclax AUC) both wired & fetching live; DepMap/GDSC/TCGA/spatial still to add |
| M1 | BCL-2 panel + executioner-loss (LOF) logic | **partial** — panel + priors in `biology.py`; formal continuous `executioner_loss_score` (0–1) + binary call per spec still to add |
| M2 | Backbone association (executioner state → venetoclax resistance) | **DONE (real, primary cohort)** — BeatAML n=367: venetoclax_score vs ex-vivo AUC rho=−0.275, perm p=0.0005, 95% CI [−0.362,−0.183]; salvage_index rho=+0.278. Model not fit to drug data. `scripts/04_validate_beataml.py`, fig `beataml_backbone.png` |
| M3 | Confounder decomposition (MCL1, BCL2:BCL-XL ratio, BCL2 gatekeeper muts) | **DONE — honest NULL.** On BeatAML n=367, executioner state adds ~nothing beyond confounders (ΔR²=+0.001, ΔAIC=+1.6, perm p=0.53, partial Spearman=+0.04). M2's signal is carried by the guardian/MCL1 axis; executioner loss is rare (1 LoF/671) so not a population-level driver. Refines thesis: ATAP niche = rare executioner-loss *subset*, not general resistance. `scripts/05_confounders_m3.py` |
| M4 | Multiverse / specification curve + stability score | not started — sweep LOF defs × cutoffs × metric (IC50/AUC) × drug × lineage × covariates |
| M5 | ATAP-susceptibility stratifier (mechanistic composite, NOT trained on ATAP) | **partial** — two-axis scorer + quadrants in `scoring.py`; validated against real venetoclax resistance in M2 |
| M6 | Subtype stratification (TCGA/BeatAML prevalence) | not started |
| M7 | Spatial priming + routing map + per-spot stability | **partial** — `spatial.py` has spot scoring + Moran's I / Getis-Ord; needs a QC'd real heme spatial section + routing index |
| M8 | Method validation (synthetic ground truth, power, nulls) | **partial** — simulator + recovery tests exist; formal power curves + labeled synthetic-validation figures to add |
| M9 | Prior-art + IP gate (run EARLY per spec) | **not started — should run soon** (novelty is an output, not an input) |

## Figures (spec F1–F13)
Done/available: F8-equivalent (`beataml_backbone.png`), the two-axis map, spatial need map.
Not yet: F1 mechanism schematic, F3 prevalence, F4 forest, F5 confounder, F6 spec-curve, F7 ridgeline,
F9/F10 spatial, F11/F12 synthetic-validation, F2/F13 schematics.

## Key results so far (all real data, honestly scoped)
- **M2 backbone holds on real patients** (see table). Validates the venetoclax-RESISTANT *target
  population*; per GUARDRAILS #3 this does NOT show ATAP-M8 efficacy — no ATAP-response data exists.
- Real BeatAML prevalence (671 pts): predicted salvage_target 20.7% (threshold-shaped; the
  meaningful finding is the internal-consistency + the M2 drug-response validation, not the fraction).

## Next (backlog order)
1. **M9 prior-art gate** — run early; dated, logged search (`outputs/logs/priorart_log.md`).
2. **M1 formal executioner_loss_score** — now higher priority: cleanly isolate the *rare*
   executioner-loss subset (mutation OR deep deletion OR bottom-decile BAX+BAK), then a SUBGROUP
   analysis — is that subset enriched in the venetoclax-resistant tail? (M3 showed executioner state
   is not a general predictor, so the value is in the specific subset, not the population trend.)
3. **M4 specification curve** (the signature robustness panel) once M1 score exists.
4. Foundation: `config.yaml` (panels/thresholds/seeds), `environment.yml` (pinned deps), MANIFEST.
5. DepMap heme route — genetic BAX/BAK loss + CRISPR dependency may represent executioner loss
   better than primary AML does, giving M3 a fairer test in a cohort where the phenotype exists.

## Open coordination note
The other instance (ImSpxrsh) mis-pushed MOSAIC artifacts here in commit `1ed0c4e`
(`poster/mosaic_isef_poster.*`, `results/glioblastoma/*`). Wrong-repo contamination — left in place
(don't delete another instance's push), flag for cleanup. Two instances on this repo: pull before
work, keep changes additive/complementary, never force-push.
