# Benchmark explorer — usage (issue #49)

An **offline, self-contained** interactive explorer. The interactive object *is* the finding:
most candidate axes for BH3-mimetic response don't survive scrutiny.

## Run it (at the poster, no network)
Just open the file in any browser — double-click, or:
```
open tools/benchmark_explorer/index.html      # macOS
```
No server, no internet, no install. All data is embedded in the single HTML file.

## What it shows
1. **Axis selector + effect bars.** Pick a candidate axis; see its Spearman ρ against each real
   BH3-mimetic spec (venetoclax/navitoclax × LN_IC50/AUC, and S63845 if present). Each bar is
   **blue if it clears the grey sham (permutation) null band, orange if it sits inside it.**
2. **Inter-axis correlation matrix.** How redundant the axes are with each other.
3. **Survival scoreboard.** How many specs each axis clears — the headline: `monocytic_signature`
   clears 0/5, `executioner_loss_score` 1/5, while the guardian axes clear most.

## What it deliberately does NOT do
- No individual-level / patient susceptibility prediction.
- No clinical claim, no efficacy statement.
- It is a **methods explorer over aggregate axis behaviour** — that scope is why it replaces the
  v2 "susceptibility predictor" idea (which would invite being read as clinical decision support).

## Regenerate (if the data or specs change)
```
PYTHONPATH=src python tools/benchmark_explorer/build_explorer.py
```
Recomputes effect sizes, permutation null bands, and correlations from the frozen data, then
rewrites `index.html` with the numbers embedded. Seeded (`config.yaml:seed`), so it is reproducible.

## For the "tested by an outside person" acceptance criterion
Hand someone the open page with **no explanation** and ask: "which of these predictors actually
work?" If the blue/orange bars + scoreboard lead them to "the guardian ones work, monocytic and
executioner mostly don't," the tool passed. Record who tested it and what they concluded.

## Acceptance criteria (issue #49)
- [x] Runs offline at the poster; no network dependency (single self-contained HTML).
- [x] Shows axis performance, sham null band, spec distribution (specs), inter-axis correlation.
- [x] No individual-level prediction; no clinical claim.
- [x] Usable with zero verbal explanation (selector + color-coded bars + scoreboard).
- [ ] *Tested by an outside person receiving no instructions* — the remaining human step (log the result).
