# Reverse-engineered deadline calendar (issue #61)

Work backward from the fair date. **Approvals and forms — not analysis — are what most often
disqualify strong projects**, so they are treated as the earliest immovable deadlines. Every
externally-dependent item carries a **two-week buffer**.

> **Fill in `[FAIR DATE]` and the dated cells from the official current-year TNJSF + ISEF
> calendars before relying on this.** Offsets below are planning defaults ("T‑minus" = weeks
> before the fair); replace each with the real published date. Do not treat an offset as a
> confirmed deadline.

## Anchor
- **`[FAIR DATE]`** = TNJSF fair day (confirm on the official site).
- **`[ISEF DATE]`** = ISEF week (only relevant if the project advances).
- Buffer rule: the *internal* target for any externally-dependent item is **its real deadline
  minus 14 days**.

## Backward schedule (replace T‑minus with real dates)
| When (target) | Item | Type | Buffer applied | Owner |
|---|---|---|---|---|
| **T‑minus 12–16 wk** | ISEF/SRC/IRB forms identified; which apply (human subjects? hazardous? — likely N/A here, confirm) | approval | — start earliest | `[M?]` |
| **T‑minus 10–14 wk** | Required approvals **submitted** (SRC/IRB/IBC if any) | approval | +2 wk before any bench work | `[M?]` |
| **T‑minus 10 wk** | Fair **registration** opens/closes — confirm exact date | registration | +2 wk internal target | `[M?]` |
| **T‑minus 8 wk** | **Preprint go/no-go date** (see below) | decision | hard gate | `[M?]` |
| **T‑minus 6 wk** | Abstract drafted + calibrated-language audit | writing | +2 wk before fair abstract deadline | `[M?]` |
| **T‑minus 4–6 wk** | Fair **abstract deadline** — confirm exact date | submission | internal target 2 wk earlier | `[M?]` |
| **T‑minus 4 wk** | Master figure + poster to print-ready | design | +1 wk print buffer | `[M?]` |
| **T‑minus 3 wk** | Poster **sent to print** | production | print turnaround buffer | `[M?]` |
| **T‑minus 2 wk** | Provenance ledger fully signed (issue #30); binder assembled (#51) | rigor | hard gate | `[M?]` |
| **T‑minus 1–2 wk** | Hostile mock judging ×2 (#56); nested pitches rehearsed | rehearsal | — | all |
| **`[FAIR DATE]`** | Fair | — | — | all |

## Preprint go/no-go (explicit, per the issue)
- The preprint needs **[mentor] review + server screening lead time** — estimate **≥ N weeks** end
  to end (fill N from the mentor's real turnaround + the server's typical screening window).
- **Go/no-go date = `[FAIR DATE]` − (N weeks + 2-week buffer).** If the manuscript is not
  submission-ready by that date, the preprint is **cut** (it's already out of the core in
  `scope_triage.md`) — do not let it jeopardize the fair deliverables.

## Immovable-first principle
Forms/approvals are scheduled **first and earliest**, because they depend on other people and
cannot be compressed. Analysis and figures flex around them, never the reverse.

## Weekly review
- All three members review this calendar **every week** (put it on the same agenda as
  `scope_triage.md` and `ownership_map.md`).
- Any externally-dependent item without a confirmed real date is a **red flag** until the date is
  pinned from the official source.

## Acceptance criteria (issue #61)
- [x] Every hard deadline slotted: registration, forms, approvals, abstract, fair date (structure; real dates to fill).
- [x] Two-week buffer on every externally-dependent item (buffer rule + column).
- [x] Preprint go/no-go date included (formula above).
- [x] Reviewed weekly by all three members (process above).

> Depends on #17 (fair conflict/eligibility) and the confirmed dates from #60 — pin those first.
