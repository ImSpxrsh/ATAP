# dbGaP Data Access Request — Beat AML (phs001657)

**Study:** phs001657 — *Functional Genomic Landscape of Acute Myeloid Leukemia* (Beat AML;
NCT01728402). Currently released as **phs001657.v3.p1**. Controlled access via a Data Use
Certification (DUC).
Verify current version at: https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs001657

**Why this and not the open data:** The open Beat AML 2.0 files (already in this repo)
give ex vivo inhibitor AUC + normalized RNA-seq. The controlled study adds the full
harmonized functional/proteomic layers and complete WES/variant calls needed to build a
**functional** executioner-loss readout and to link BAX/BAK status to ex vivo venetoclax
response at the individual-variant level.

## What you need
- A PI/institutional signing official (SO) with an eRA Commons / NIH account.
- Local IRB determination (usually "not human subjects research" for de-identified dbGaP
  secondary analysis — confirm with your IRB).
- A cloud or approved local environment meeting the NIH Security Best Practices.

## Research Use Statement (paste into the DAR)
> We request access to phs001657 (Beat AML) to perform a secondary computational analysis
> predicting which BH3-mimetic-resistant acute myeloid leukemia cases are mechanistically
> susceptible to BAX/BAK-independent mitochondrial pore-formation. Specifically, we will
> (1) classify apoptotic-executioner (BAX/BAK1) loss from somatic variants, copy number,
> and expression; (2) relate executioner loss and BCL-2-family guardian dependence to ex
> vivo venetoclax sensitivity; and (3) build and validate a mechanistic susceptibility
> score against observed drug response. This is a computational susceptibility-mapping and
> target-population study; it makes no therapeutic or efficacy claims and involves no
> patient contact or re-identification. Data will be analyzed only within an approved
> secure environment, not redistributed, and reported only in aggregate.

## Data Use Limitations to confirm you can meet
- General Research Use (GRU) or Disease-Specific (AML) — read the study's DUL and match it
  in the statement above.
- No attempt at re-identification; no combining with other data to re-identify.
- Aggregate reporting only; retain data within the approved environment.

## Where it plugs into this repo
Drop the harmonized variant/expression/drug tables into `data/raw/` and point
`src/data/harmonize.py::build_beataml` at them (it already keys on dbGaP RNA/DNA sample
IDs). The functional-priming hook is `src/functional.py`.
