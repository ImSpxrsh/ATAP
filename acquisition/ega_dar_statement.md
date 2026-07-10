# EGA Data Access Request — venetoclax response/failure RNA-seq (EGAD00001005949)

**Dataset:** EGAD00001005949 — *RNAseq data from "Molecular patterns of response and treatment
failure after frontline venetoclax combinations in older patients with AML."*
**Study:** EGAS00001003820 · **Data Access Committee:** EGAC00001001461 · 31 patients / 39 BAM
files (Durable remission 10, Relapsed 10, Refractory 11).
**Apply at:** https://ega-archive.org/access/request-data/how-to-request-data

## What you need before submitting
- A **PI / institutional lead** to sign the WEHI/Alfred **Data Transfer Agreement** (a student
  generally cannot be the sole signatory — this is a good ask for your NJIT contact if he'll
  co-sponsor).
- **Local IRB / ethics determination** (usually "not human subjects / secondary use of
  de-identified data" — confirm with the institution's IRB office).
- An institutional email and the signing official's details.

## Research Use Statement (paste into the EGA request form)
> We request access to EGAD00001005949 to perform a secondary computational analysis of
> BCL-2-family apoptotic biology in venetoclax-treated acute myeloid leukemia. Using the
> RNA-sequencing profiles, we will (1) compute a mechanistic, pre-specified susceptibility
> score from BCL-2-family guardian dependence and apoptotic-executioner (BAX/BAK) expression,
> not trained on drug response; and (2) test whether this score separates the durable-remission,
> relapsed, and refractory response groups, as an independent external validation of a model
> developed on public cohorts (DepMap, Beat AML). This is a computational target-population and
> biomarker-validation study. It makes no therapeutic or efficacy claims, involves no patient
> contact or re-identification, and will not attempt to re-identify individuals or link the data
> to any external identifiers. Data will be analyzed only within an approved secure environment,
> will not be redistributed, and results will be reported only in aggregate.

## Data Use conditions to confirm you can meet
- Named-user access only; no redistribution; retain data within the approved environment.
- No re-identification attempts; aggregate reporting only.
- Acknowledge the data producers (WEHI / The Alfred) in any output.

## Where it plugs into the pipeline
RNA-seq BAMs → panel-gene expression matrix → `src/panels.py` (executioner-loss) +
`src/stratify.py` (susceptibility) → test score vs the three response classes. A clean external
replication of the guardian/susceptibility signal on labeled venetoclax response/failure.
