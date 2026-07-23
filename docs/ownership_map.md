# Ownership map & team-redundancy plan (issues #62, #63)

Three people; one **will** get sick or pulled away in the final month. Every P0 needs a **backup
owner who has actually read the code/output**, not just been assigned on paper.

> **Fill in real names before relying on this.** Members are placeholders `[M1]`, `[M2]`, `[M3]`
> here so the structure is committed without guessing who is who. Replace at the first team meeting.
> A backup is only "real" once the ☑ *code-reviewed* box is checked — they have opened the files
> and can run/explain them.

## P0 / blocking items — primary + backup owner
| Item | Issue | Primary | Backup | Backup code-reviewed? |
|---|---|---|---|---|
| Freeze + pre-registration (MODEL_CARD, DATA_VERSIONS.lock) | #1 ✅merged | `[M1]` | `[M2]` | ☐ |
| One-command clean-room reproduction (Makefile/CI) | #2 | `[M2]` | `[M1]` | ☐ |
| Baseline battery (BCL2-alone etc.) | #10 | `[M1]` | `[M3]` | ☐ |
| Claim provenance ledger + human sign-off | #30 | `[M3]` | `[M1]` | ☐ |
| Class-wide + power accounting | #40 | `[M1]` | `[M2]` | ☐ |
| **TNJSF slot count confirmed in writing** | #60 | `[M3]` | `[M2]` | ☐ (email sent?) |
| Reverse-engineered deadline calendar | #61 | `[M2]` | `[M3]` | ☐ |
| Scope triage / cut list upkeep | #62 | `[M1]` | `[M3]` | ☐ |

## P1 items — primary + backup owner
| Item | Issue | Primary | Backup | Reviewed? |
|---|---|---|---|---|
| Calibration & uncertainty | #12 | `[M1]` | `[M3]` | ☐ |
| CLL external validation | #8 | `[M2]` | `[M1]` | ☐ |
| Clean figure regeneration pass | #19 | `[M3]` | `[M2]` | ☐ |
| Interactive benchmark explorer | #49 | `[M2]` | `[M1]` | ☐ |
| Team redundancy plan (this file) | #63 | `[M1]` | `[M2]` | ☐ |

## Contingency — a member becomes unavailable in the final month
1. **Immediate:** the backup owner takes over every item that member was **primary** on. Because the
   backup has already code-reviewed (the ☑ box), there is no cold-start.
2. **Re-triage:** invoke [`scope_triage.md`](scope_triage.md) — cut non-core items owned by the
   remaining two down to the MVP if load exceeds capacity.
3. **Presentation:** per issue #56, every member must be able to present the **whole** project
   (including figures they did not build) without the tool. This is the human redundancy for the
   live event, not just for the code.
4. **Single points of failure to eliminate NOW:** the provenance-ledger sign-off (#30) and the
   fair-structure email (#60) must not be sole-owned — both listed with backups above.

## Standing rule
No P0 ships with an unchecked backup ☐. "Backup has read the code" is a gate, verified at the
weekly triage, not a checkbox filled at assignment time.

## Acceptance criteria
**#63:** (a) primary + backup for every P0 ✅ (names pending); (b) backups have reviewed the code —
tracked by the ☑ column, filled as reviews happen; (c) contingency documented ✅.
**#62 (ownership portion):** ownership assigned with named backups ✅ (structure; names to fill).
