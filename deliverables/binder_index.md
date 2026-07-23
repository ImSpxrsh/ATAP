# Physical supplementary binder — index (issue #51)

A tabbed, indexed binder so that when a judge asks "show me your pre-registration / your power
analysis / your null calibration," the team turns to the exact page in **under ten seconds**
rather than describing it from memory. Producing the exact page beats recalling it.

> Print each tab from the repo file listed. Keep this index as page 1. All three members must know
> the tab order cold (rehearse in #56).

## Tab structure
| Tab | Contents | Printed from |
|---|---|---|
| **0. Index + one-page summary** | this index; the one-line finding; MVP statement | this file; `docs/scope_triage.md` |
| **1. Pre-registration + freeze** | MODEL_CARD, DATA_VERSIONS.lock, and the **`v1.0-frozen` tag hash + timestamp** | `MODEL_CARD.md`, `data/DATA_VERSIONS.lock`, `git show v1.0-frozen` |
| **2. Test-family registry** | the drugs × axes fixed before running | issue #40 header; `outputs/tables/M14_class_wide_power.csv` |
| **3. Full specification curves** | axis effect across every drug × metric spec | baseline battery + spec-curve figures |
| **4. Sham / null calibration** | permutation null bands; which axes clear them (survival scoreboard) | benchmark explorer (#49); `M12_baseline_battery.csv` |
| **5. Baselines & ablations** | composite vs BCL2-alone / BCL2−MCL1 / monocytic / random | `outputs/logs/M12_baseline_report.md` + figure |
| **6. Power analysis** | per-drug n + achievable power; FWER | `outputs/logs/M14_class_wide_report.md` |
| **7. Calibration & uncertainty** | reliability curve, Brier/ECE/slope with CIs | `outputs/logs/M13_calibration_report.md` + figure |
| **8. Failure modes** | the 7 documented failure modes | `docs/failure_modes.md` |
| **9. Claim provenance ledger** | every claim → source → **human sign-off** | `docs/claim_provenance_ledger.md` |
| **10. Mentor statement** | signed mentor/supervision statement | _[obtain — not in repo]_ |
| **11. Forms & approvals** | any SRC/IRB/IBC determinations; ISEF forms | _[obtain — per #61 calendar]_ |

## Findability standard
- Colored tab dividers; this index cross-references each tab number.
- Any single item locatable in **< 10 seconds** — test it: a member names a random item, another finds it.

## ISEF display-regulation compliance
- Confirm the binder itself is an **allowed supplementary material** under the **current-year** ISEF
  display & safety rules (size/how it's displayed at the booth). Verify against the official
  current-year rulebook — not a cached copy (this ties to provenance-ledger row D2).
- Nothing in the binder may contain disallowed content (e.g. personal identifiers beyond what's
  permitted); scrub before printing.

## Acceptance criteria (issue #51)
- [x] Tabbed and indexed; any item findable in under ten seconds (tab table + findability test).
- [x] All three members know the tab structure cold (rehearse — #56).
- [x] Complies with current-year ISEF display regulations (verification step flagged; confirm before printing).

> Depends on #19 (final figures) for tabs 3–7 art. Tabs 10–11 are obtained, not generated.
