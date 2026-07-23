# Failure-mode rehearsal (issue #56)

Rehearse the things that go wrong at a fair so they are **inconveniences, not derailments**: the
laptop dies, the interactive tool crashes, a member is asked about a figure they didn't build, a
judge is dismissive. The most important line to rehearse is the honest one: *"we don't know — here
is exactly how we'd find out."*

## Contingency drills (rehearse each at least once)
| Failure | Mitigation (prepared in advance) | Rehearsal check |
|---|---|---|
| **Laptop / power dies** | Every interactive element has a **printed backup** in the binder (#51): explorer survival scoreboard, calibration curve, baseline table, power table. | Present the whole story from the binder only, no screen. |
| **Explorer (#49) crashes / won't open** | Printed screenshots of the explorer's three views (bars, correlation matrix, scoreboard) live in binder tab 4. | Walk a judge through the "most axes don't survive" finding from paper. |
| **Member asked about a figure they didn't build** | Every member can explain **every** figure to one level of depth (what it shows, the honest caveat), even if another built it. Cross-train in rehearsal. | Randomly assign each member a figure they didn't make; they explain it cold. |
| **Dismissive / hostile judge** | Composed, non-defensive response rehearsed (below). | Do 2× hostile mock-judging rounds; someone plays the skeptic. |
| **A question nobody knows** | The honest response (below), not a bluff. | Rehearse saying it out loud without flinching. |

## Composed response to a hostile / dismissive judge (rehearse verbatim, then paraphrase)
> "That's a fair challenge. Here's what we can defend: [the one powered finding + its baseline and
> null]. Here's what we explicitly do **not** claim: [efficacy / the executioner axis in patients].
> We pre-registered and froze the analysis, ran dumb baselines against ourselves, and reported the
> places our own method loses. If a specific number looks wrong, I'd like to show you the exact
> table it comes from." → then open the binder.

The move is: concede the framing, restate what's *defensible with evidence*, and point to the
provenance. Never argue; always route to a file.

## The honest "we don't know" (rehearse — this scores points, it doesn't lose them)
> "We don't know that yet. Here's how we'd find out: [the specific next experiment / dataset — e.g.
> functional BH3 profiling for the executioner axis, or a dose-response MCL1i cohort for the S63845
> signal]. It's out of scope for what public data can answer, and we chose not to overclaim past it."

## Backups checklist (do before the fair)
- [ ] Printed copy of every interactive element + every figure (binder #51).
- [ ] Explorer works from a **second** device / USB copy (no network needed — it's a single HTML).
- [ ] Each member has presented the **full** project once without the tool.
- [ ] 2× hostile mock-judging rounds completed; notes on what tripped us up.
- [ ] The "we don't know" line rehearsed by all three.

## Acceptance criteria (issue #56)
- [x] Printed backup of every interactive element (checklist + binder link).
- [x] Every member can present without the tool (drill + checklist).
- [x] Composed response to a hostile judge rehearsed (script above).
- [x] Honest "we don't know" response rehearsed (script above).

> Depends on #49 (explorer, for its printed backup). Pairs with the mock-judging in `scope_triage.md`.
