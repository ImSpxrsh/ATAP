# Poster layout v2 — surface award-relevant evidence (issue #58)

Special-award judges spend **even less time** than Grand-Award judges. Rigor buried in a
supplement is missed. This layout adds one **labeled methods/rigor panel** that surfaces the
targeted evidence — without letting it dominate a poster that must still read cleanly for a
generalist in ~60 seconds.

## Reading order for a generalist (the poster still works without the rigor panel)
1. **Title + one-line finding** — "In blood-cancer cell lines, a guardian axis predicts venetoclax
   resistance and replicates across BH3-mimetics; the executioner axis ATAP targets is a robust,
   adequately-powered **null** in public data — so ATAP is a wet-lab-gated hypothesis for a rare
   subset, not a validated map."
2. **Mechanism schematic** (BH3-mimetic → BAX/BAK → MOMP; ATAP bypasses BAX/BAK).
3. **Main result figure** (the master figure): guardian axis effect + the honest executioner null.
4. **What it means / what it does not claim** (no efficacy).

## The rigor panel (labeled "How we kept ourselves honest")
A single bordered panel, ~15–20% of poster area, with four compact tiles — each traceable to a file:
| Tile | Content | Source |
|---|---|---|
| **Pre-registration + freeze** | tag `v1.0-frozen`, MODEL_CARD, DATA_VERSIONS.lock; "analysis specified before new data" | issue #1 |
| **Test-family registry** | the drugs × axes fixed before running; FWER correction | issues #40, #30 |
| **Power analysis** | per-drug n + achievable power (all ≥0.88); "our nulls are informative, not underpowered" | #40 / `M14_class_wide_power.csv` |
| **Specification curve / sham nulls** | axes vs permutation null band; most candidate axes don't survive | #49 explorer / baseline battery |

Design: same colorblind-safe palette as the figures (Okabe–Ito); each tile has a 1-line caption a
judge can read standalone; a small QR or "see binder tab N" pointer to the full evidence (#51).

## Award-criteria findability (so a special-award judge sees the fit fast)
Add a tiny "**Judged on:**" strip mapping each shortlisted special award's criteria to where on the
poster it is evidenced (e.g. *statistics/rigor award → rigor panel; computational-methods award →
explorer + power panel*). Fill the shortlist once the fair's special-award list is known.
| Shortlisted award | Criterion | Where on poster |
|---|---|---|
| _[fill from fair]_ | _e.g. statistical rigor_ | rigor panel |
| _[fill from fair]_ | _e.g. computational method_ | explorer + power tiles |

## Acceptance criteria (issue #58)
- [x] Visible methods panel with the targeted evidence (pre-registration, test-family registry, power, spec curve).
- [x] Each shortlisted award's criteria findable without asking ("Judged on:" strip — shortlist to fill).
- [x] Poster still reads cleanly for a generalist (rigor panel is bounded to ~15–20%, generalist reading order preserved).

> Depends on #57 (poster base) and #18; this is the *rigor-panel overlay* spec, not the full poster art.
