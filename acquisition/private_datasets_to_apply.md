# Controlled/private datasets to apply for — ranked by what they unlock

Goal: get the data that can actually test the **executioner-loss axis** (BAX/BAK failure),
which public expression data cannot (rare event + weak proxy — see three converging nulls).
Each entry is verified against the source; "by request" vs "formal DAR" is noted honestly.

> Honesty carries over: none of these lets us claim ATAP efficacy. They let us (a) show the
> executioner-loss population is real and enriched at relapse, and (b) test it *functionally*.
> The efficacy proof is still the wet-lab experiment.

---

## TIER 1 — the executioner-loss population itself (highest value)

### 1. WEHI BAX-at-relapse AML cohort — Moujalled et al., *Blood* 2023
- **What:** 41 venetoclax-resistant + 34 chemo-resistant AML patients; **targeted BAX
  sequencing**, BCL-2/myeloid gene panels, and **single-cell multiomic (DNA + protein)**.
- **The headline that makes our thesis real:** **17% of AML patients relapsing after
  venetoclax acquire inactivating BAX mutations** (frameshift/nonsense/truncating +
  cytosol-retaining missense) — rare after chemo. This *is* the executioner-loss population,
  and it's **enriched at relapse**, exactly where a salvage is needed.
- **Why we need it:** turns "executioner loss is rare (~2–5%) at diagnosis" into "17% at
  venetoclax relapse" — moves the target population from hypothetical to documented.
- **Access:** **by request to the corresponding author, Andrew H. Wei (WEHI), wei.a@wehi.edu.au**
  (Data Availability: *"Data are available on request from the corresponding author"*). Expect
  a Data Transfer Agreement + your local IRB/ethics determination.
- **Refs:** paper PMC10651776 (Blood 141(6):634); commentary Blood 141(6):562.

---

## TIER 2 — functional apoptotic priming (the readout expression can't give)

### 2. Dynamic BH3 Profiling AML database — bioRxiv 2025 (92 patients)
- **What:** prospective **dynamic BH3 profiling (DBP)** on myeloblasts from **92 AML patients**
  with a fixed drug panel, plus a combined **genetic + functional annotation database**;
  venetoclax delta-priming, BAD/MS1/HRK peptide responses, CD123-subpopulation priming.
- **Why we need it (this is the #1 scientific upgrade):** DBP measures **whether the cell can
  execute MOMP** — the functional analogue of executioner competence. It replaces our weak
  expression proxy and drops straight into `src/functional.py`.
- **Access:** check the paper's Data Availability (bioRxiv **doi:10.1101/2025.10.14.682414**,
  **PMID 41278625**); if not deposited, request from the corresponding author. Newer preprint,
  so a polite early request is reasonable.

### 3. "Reduced Mitochondrial Apoptotic Priming" cohort — Vo/Ryan/Letai, *Cancer Cell* 2020
- **What:** BH3 profiling / DBP in AML **PDX models + clinical samples** with acquired
  resistance to venetoclax **and** the MCL-1 inhibitor S63845; priming decreases drive
  BH3-mimetic resistance.
- **Why we need it:** independent functional-priming cohort spanning **both** BCL-2 and MCL-1
  resistance — directly tests the "class-wide executioner-step failure" idea.
- **Access:** supplementary tables (PMC7988687) for per-sample priming; request raw from the
  Letai lab (Dana-Farber) if needed.

---

## TIER 3 — venetoclax response/failure cohorts (formal DAR, ready to submit now)

### 4. EGA — venetoclax response/failure RNA-seq (WEHI/Alfred)
- **Accession:** dataset **EGAD00001005949**, study **EGAS00001003820**.
- **What:** RNA-seq of **31 AML patients in three response classes** — Durable remission (10),
  **Relapsed (10), Refractory (11)** — after frontline venetoclax + HMA or LDAC. 39 BAM files.
- **Why we need it:** cleanly **labeled venetoclax response vs failure** — a real external test
  set for the guardian/susceptibility score, with the failing subset we care about.
- **Access (formal DAR — this is the one you can submit immediately):** EGA portal →
  https://ega-archive.org/access/request-data/how-to-request-data ; requires the **WEHI/Alfred
  Data Transfer Agreement** + evidence of local IRB/ethics. Data Access Committee
  **EGAC00001001461**.

### 5. Beat AML — full controlled release (dbGaP)
- **Accession:** **phs001657** ("Functional Genomic Landscape of AML"; currently v3.p1).
- **What:** the complete WES/RNA + **ex-vivo drug sensitivity (venetoclax)** + functional layers
  for ~562 patients — beyond the open portal we already used.
- **Why we need it:** the individual-variant BAX/BAK calls + full drug matrix for a properly
  powered executioner-vs-response test on the largest functional AML cohort.
- **Access (formal DAR):** dbGaP Authorized Access via a **Data Use Certification**, signed by
  your PI/institutional Signing Official (eRA Commons). Research-use statement already drafted in
  [`dbgap_beataml_DAR.md`](dbgap_beataml_DAR.md).

---

## TIER 4 — additional venetoclax-resistance cohorts (verify accession in each paper)
- **Transcriptional/phenotypic heterogeneity of VEN resistance in AML** (bioRxiv 2024,
  PMC10862759): 4 transcriptionally distinct VEN-resistant clusters, transcriptomic + ex-vivo
  drug response — check its Data Availability for the EGA/GEO accession.
- **rrAML single-cell pharmacoscopy** (21 relapsed/refractory AML): single-cell ex-vivo drug
  profiling + DNA/RNA/protein — a functional + multiomic relapse cohort; find accession in paper.
- **RNA-splicing / BCL2-inhibition leukemia** (*Cancer Cell* 2022): splicing modulation enhances
  BCL-2 inhibition — check for deposited data if the splicing angle becomes relevant.

---

## Suggested order to apply (given you can get a DAR sponsored)
1. **EGAD00001005949** (formal EGA DAR) — submit now; labeled venetoclax response/failure, ready.
2. **phs001657** (formal dbGaP DUC) — submit with your PI; biggest functional AML cohort.
3. **WEHI BAX cohort** (email Andrew Wei) — the actual executioner-loss population; highest thesis value.
4. **DBP 92-patient database** (email corresponding author) — the functional priming readout.

## What each does to our pipeline
| Dataset | Feeds | Turns which null into a testable claim |
|---------|-------|----------------------------------------|
| WEHI BAX cohort | M1 executioner-loss (real LOF calls), relapse prevalence | "executioner loss is rare" → "17% at relapse" |
| DBP 92-pt / Letai 2020 | `src/functional.py` → M1/M2/M3/M5 | "expression is a weak proxy" → functional competence |
| EGA EGAD00001005949 | external validation of susceptibility/guardian score | "single-cohort signal" → replicated response/failure |
| Beat AML phs001657 | powered executioner-vs-response test | "underpowered / rare event" → largest functional cohort |
