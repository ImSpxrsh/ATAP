# Scope triage — the cut list, decided in advance (issue #62)

Fifty-plus issues; one project among many; a finite team. **Eight issues done completely beats
twenty-five at 40%** — a judge who finds one hole starts hunting for more. This file commits the
cut list *before* work continues, so scope is a decision, not a drift.

> Rule: at the weekly check, the default is **permission to cut further**. Adding scope requires a
> reason; cutting does not.

## Non-negotiable core (in priority order)
The blocking rigor items that prevent overclaiming come first — they replaced the preprint and the
interactive tool in the core.

1. Fair conflict / eligibility check
2. **Slot count & advancement structure confirmed in writing** (issue #60 — BLOCKING)
3. Test-family registration (drugs × axes fixed before running)
4. **Claim provenance ledger** (issue #30) — human sign-off pass
5. Freeze + pre-registration (issue #1 ✅ merged; MODEL_CARD + DATA_VERSIONS.lock)
6. Axis collinearity audit
7. Benchmark build **only if it survives its own audit** (else: "systematic evaluation")
8. Sham / negative-control axes
9. Confounder decomposition (monocytic identity)
10. CRISPR co-dependency with circularity controls
11. Proteomics executioner readout (if reachable)
12. Selection-effect analysis
13. **Power analysis** (issue #40 ✅ — per-drug power + FWER)
14. Calibrated-language audit (no efficacy/overclaim; GUARDRAILS)
15. Master figure
16. Hostile mock judging ×2 (issue #56)
17. Nested pitches (30s / 2min / 5min)
18. Forms + deadline calendar (issue #61)

**Explicitly dropped from the core** (do only if the core is complete and time remains):
- Preprint (Ma review + screening lead time too risky against the fair date)
- Interactive predictor tool → replaced by a benchmark *explorer* that shows most axes DON'T survive (issue #49), itself non-core
- Clinical-outcome layer (issue #44, P3) — confounded, expands the test family
- Reusable benchmark harness (issue #37, P2) — gated on the audits passing first
- Physical binder / poster-award panel beyond the master figure (issues #51, #58) — nice-to-have

## Minimum viable project (MVP)
If everything else is cut, the project still stands on:
- **Freeze + pre-registration** (#1) — the honest baseline.
- **Provenance ledger** (#30) with human sign-off — every claim sourced.
- **The two defensible findings, with baselines + power + FWER:** (a) the guardian axis predicts
  venetoclax resistance and replicates across BCL2-class agents; (b) the executioner (ATAP) axis is
  a robust, adequately-powered **null** in public cell-line data → ATAP is a wet-lab-gated
  hypothesis for a rare subset, not a validated map.
- **Failure-mode honesty** (#14) and **calibrated language** — the project's credibility spine.
- One clean **master figure** + a rehearsed 2-minute pitch.

That MVP is fully honest, defensible from first principles, and overclaims nothing.

## Weekly triage process
- Every week, all members review this list and the [ownership map](ownership_map.md).
- Each item is marked: on-track / at-risk / **cut**.
- At-risk core items get a backup owner activated; non-core items are cut without regret.
- No item enters the core mid-stream without removing another.

## Acceptance criteria (issue #62)
- [x] Cut list committed before further work begins.
- [x] Ownership assigned with named backups → [`ownership_map.md`](ownership_map.md) (names to be filled by the team).
- [x] Weekly check with explicit permission to cut further (process above).
- [x] "Minimum viable project" defined.
