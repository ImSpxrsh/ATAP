# Data-request email drafts (for YOU to send — review & fill placeholders first)

> These are drafts. I am not sending anything. Replace [bracketed] fields, verify the current
> corresponding-author email from the paper before sending, and — where possible — have your
> PI/mentor (e.g. your NJIT contact) co-sign or be CC'd; author-held clinical data almost always
> requires a PI-level Data Transfer Agreement + IRB, which lands better coming from a lab.

---

## Email 1 — WEHI (BAX-at-relapse AML cohort)

**To:** Prof. Andrew H. Wei — wei.a@wehi.edu.au *(verify current address; he has moved between
WEHI / Peter MacCallum / The Alfred — check the paper's corresponding-author line)*
**Cc:** [your PI / mentor, if co-sponsoring]
**Subject:** Data request — BAX-mutant venetoclax-resistant AML cohort (Moujalled et al., Blood 2023)

Dear Professor Wei,

I'm [name], a [student/researcher] at [institution], working [with / under] [PI/mentor,
institution] on a computational analysis of the BCL-2-family apoptotic machinery in
BH3-mimetic-resistant blood cancers. Your 2023 *Blood* paper showing that ~17% of AML patients
acquire inactivating **BAX** mutations at venetoclax relapse is central to our hypothesis: that
apoptotic-**executioner** (BAX/BAK) loss defines a distinct, class-wide-resistant population for
which a BAX/BAK-independent strategy would be mechanistically rational.

We have built a mechanistic susceptibility model from public data (DepMap, GDSC, Beat AML, TCGA)
and consistently find that executioner loss is too rare at diagnosis to test in those cohorts.
Your relapse cohort is, to our knowledge, the clearest documentation of the population we care
about. I'm writing to ask whether you would consider sharing the associated data — the targeted
**BAX / BCL-2 / myeloid** sequencing and, if possible, the single-cell multiomic data — under
whatever data transfer agreement and ethics arrangements you require.

To be clear about scope and intent: this is a computational, secondary-analysis project that
makes **no efficacy claims** and involves no patient contact or re-identification. We would gladly
sign a DTA, provide our local IRB determination, restrict analysis to an approved environment,
acknowledge WEHI/your group, and share our analysis and code with you in advance. We're also
very open to doing this as a collaboration rather than a one-way data request.

Thank you for considering it — and for the paper, which sharpened how we think about this problem.

Kind regards,
[Name, title, institution]
[PI/mentor name + email, if applicable]

---

## Email 2 — Letai / Garcia lab, Dana-Farber (functional BH3-profiling data)

*One email covers BOTH functional-priming datasets: the 2025 dynamic-BH3-profiling database
(92 AML patients) and the 2020* Cancer Cell *"Reduced Mitochondrial Apoptotic Priming" cohort —
both from this lab.*

**To:** Dr. Anthony Letai — anthony_letai@dfci.harvard.edu · and/or Dr. Jacqueline Garcia —
jacqueline_garcia@dfci.harvard.edu *(verify from the papers' corresponding-author lines)*
**Cc:** Jeremy Ryan (DBP methods lead) if listed; [your PI/mentor]
**Subject:** Request — dynamic BH3-profiling AML data for a computational apoptotic-priming analysis

Dear Dr. Letai and Dr. Garcia,

I'm [name], a [student/researcher] at [institution], working [with] [PI/mentor] on a computational
map of BCL-2-family apoptotic dependence in BH3-mimetic-resistant blood cancers. A central finding
of our work — using public cohorts (Beat AML, DepMap) — is that **expression-based** measures of
apoptotic-executioner (BAX/BAK) status are a weak proxy: they predict venetoclax resistance only
through guardian dependence, not through executioner competence. The right readout is a
**functional** one, which is exactly what your dynamic BH3 profiling provides.

I'm writing to ask whether the per-sample **DBP / apoptotic-priming data** from your recent AML
work — the 2025 dynamic-BH3-profiling study (~92 patients) and, if available, the 2020
*Cancer Cell* priming cohort — could be shared for secondary analysis. Concretely, we would use
overall priming and peptide-specific (BAD / MS1 / HRK) responses and venetoclax delta-priming as a
functional executioner-competence feature, to test whether *functional* priming — unlike
expression — dissociates guardian dependence from executioner loss.

Scope and intent: this is a computational, secondary-analysis project that makes **no efficacy
claims** and involves no re-identification. We would sign any data-use agreement, provide our IRB
determination, keep the data in an approved environment, acknowledge your group, and share our
methods and results with you. We'd welcome doing this as a collaboration.

Thank you very much for considering it — your BH3-profiling work is the functional standard we're
trying to build toward computationally.

Kind regards,
[Name, title, institution]
[PI/mentor name + email, if applicable]

---

## Practical notes
- **Verify every email address** from the paper's corresponding-author line before sending;
  senior authors change institutions.
- **Lead with the honest framing** (no efficacy claims, secondary analysis, willing to
  collaborate) — clinical-data holders are far more responsive to a scoped, humble request.
- **A PI/mentor co-sign massively increases response + is usually required** for the DTA/IRB.
  If your NJIT meeting goes well, ask whether he'll be the sponsoring PI for these requests.
- Keep a log of who you contacted and when (add rows to `outputs/logs/priorart_log.md` or a new
  `acquisition/outreach_log.md`).
