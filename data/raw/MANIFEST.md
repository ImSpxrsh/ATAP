# data/raw/MANIFEST.md — provenance for every raw download.

Every file in `data/raw/` MUST have a row here BEFORE analysis is written on top of it
(GUARDRAILS §6, Overnight spec Task 1). Never edit raw files in place.

| file | dataset | source URL / accession | release / version | download date | n_rows | n_cols | notes |
|------|---------|------------------------|-------------------|---------------|--------|--------|-------|

_(populated by `src/data/fetch_data.py`; each successful download appends a row and
prints the row/col counts.)_
