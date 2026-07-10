# BLOCKERS.md — logged blockers (a logged blocker is a success, not a failure).

Format: `YYYY-MM-DD — [task] blocker → what was tried → what a human must decide/do`.

## Open blockers

_(none logged yet — populated as data acquisition and modules run)_

## Environment notes
- Python 3.14 in use. `scanpy`/`squidpy` (spatial, M7) may not have wheels for 3.14 and
  can fail to build. If they do, the spatial layer is scaffolded against a documented
  schema and marked PENDING REAL DATA rather than fabricated (per Overnight spec Task 6).
