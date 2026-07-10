# Meeting brief — talking points for the NJIT cancer researcher

Read-off-able. Lead with honesty; the null results are a feature, not a weakness. Everything
below is defensible from a saved figure/table.

---

## 0. The 30-second pitch (say this first)
> "We built a computational map that predicts *which* blood cancers should be vulnerable to a
> BAX/BAK-independent way of killing cancer cells — for patients where the standard drug
> venetoclax fails. We used only public data, we make no efficacy claims, and importantly our
> headline result is an honest one: the resistance signal we can measure is driven by a
> different axis than we hypothesized, which tells us exactly what experiment to do next."

If you say nothing else, say that. It signals you understand your own result.

---

## 1. The biology (so you can talk fluently)
- **Apoptosis via the mitochondria (MOMP):** cells die when the mitochondrial outer membrane
  gets permeabilized, releasing cytochrome c → caspases → death.
- **The BCL-2 family controls this**, in three roles:
  - **Guardians** (anti-apoptotic): **BCL-2, MCL-1, BCL-xL, Bfl-1** — keep the cell alive.
  - **Executioners** (pore-formers): **BAX, BAK** — the proteins that actually punch the hole.
  - **Sensitizers/activators** (BH3-only): BIM, PUMA, NOXA, BAD — tip the balance to death.
- **Venetoclax** (and the whole "BH3-mimetic" class) works by **blocking a guardian** (BCL-2),
  freeing the executioners to act. It's FDA-approved in CLL and AML.
- **The problem we target:** if a tumor **loses BAX/BAK** (the executioners), then blocking the
  guardian does nothing — there's no one left to punch the hole. The **entire drug class fails
  at the same step.**
- **ATAP** ("amphipathic tail-anchoring peptide") is a fragment of the guardian **Bfl-1**
  (gene BCL2A1, residues 147–175) that **forms mitochondrial pores by itself — without needing
  BAX/BAK.** So in principle it's a *salvage* for exactly the patients where venetoclax fails.
  That's the whole thesis: **executioner loss = class-wide vulnerability = rational ATAP niche.**

---

## 2. What we actually built
- A reproducible computational pipeline (Python), built **twice, independently**, that both
  reach the same conclusion (built-in replication).
- **Public data only:** DepMap (cancer cell lines), GDSC (drug screens), **Beat AML** (671 AML
  patients with real *ex-vivo* venetoclax response), TCGA (patient tumors), and **10x Visium
  spatial transcriptomics** (where in a tissue each cell state sits).
- Four things the pipeline does:
  1. **Define executioner loss** from genetics (mutations, deletions, low expression of BAX/BAK).
  2. **Test** whether that predicts venetoclax resistance.
  3. **Score** a "susceptibility" (guardian-dependent AND executioner-deficient = ATAP-rational).
  4. **Map** it spatially — where inside a tumor the bypass is needed.
- **Zero ATAP lab data is used** (none exists for blood cancer) — we predict from mechanism.

---

## 3. What we found (the honest headline — practice saying this cleanly)
- ✅ **The guardian axis is real.** Our mechanistic score identifies the venetoclax-**resistant**
  patients in Beat AML (Spearman ρ = −0.275, permutation p = 0.0005; n=367). Replicated in DepMap.
- ❌ **The executioner-loss axis is null in the data we have.** Once you account for guardian
  dependence, executioner loss adds essentially nothing (ΔR² ≈ 0.001). We confirmed this **three
  independent ways** (confounder model, pan-drug test, ablation).
- 🔍 **We stress-tested our own model and it partly failed** (this earns credibility): our
  composite score is **beaten by BCL-2 expression alone** (ρ = −0.567), and a **monocytic-
  differentiation signature is the strongest predictor of all** (ρ = +0.721). We report this,
  not hide it.
- 🧠 **Why that's not a dead end:** executioner (BAX/BAK) loss is **rare** (~2–5% of cases) and
  expression is a **weak proxy** for whether the protein actually works. So the data *can't*
  validate the executioner axis by construction — you'd need a **functional** readout. That's a
  finding, not a failure: it tells us the exact next experiment.
- 🗺️ **Spatial proof-of-concept:** on a real lymph-node section, ~16% of spots are
  "bypass-required" (guardian-dependent but executioner-low) — showing the idea can be *localized*.

---

## 4. What inspired us / prior work we built on (cite these if asked "where did this come from?")
- **BCL-2 family apoptosis biology** — the whole guardian/executioner framework (Green, Letai labs).
- **BH3 profiling & "dynamic BH3 profiling"** (Anthony Letai, Dana-Farber) — the idea that you can
  *functionally* measure how "primed" a cell is to die. This is the method we say we *need* next.
- **Venetoclax-resistance literature** — especially **monocytic AML resistance** (Pollyea,
  Jordan, DiNardo at CU Anschutz) and **TP53/priming loss** (Nechiporuk). Our monocytic finding
  independently rediscovers theirs — good sign our pipeline is real.
- **ATAP peptide** — **Jianjie Ma's lab** (Ohio State / Rutgers) + TRIM-edicine; the optimized
  **ATAP-iRGD-M8** was tested in prostate cancer (De et al., *Oncotarget* 2014). All prior ATAP
  work is **solid tumors** — the blood-cancer indication appears open.
- **Specification-curve / multiverse analysis** (Simonsohn; Steegen) — a method from
  psychology/economics for testing whether a result survives *every reasonable* analysis choice.
  We used it as an anti-overclaiming device (we ran 360 model specifications).
- **DepMap / dependency mapping** (Broad Institute) — the public cell-line genomics backbone.

---

## 5. Limitations (own them before he raises them)
1. **Predicted, not validated.** No ATAP data exists for blood cancer; we can't and don't show
   ATAP kills anything.
2. **The executioner axis — our core hypothesis — is unproven in this data** and can't be proven
   with cell-line expression (rare event + weak proxy).
3. **Expression ≠ function.** Low BAX/BAK mRNA doesn't guarantee the executioner step is broken.
4. **Confounding is strong.** Differentiation state (monocytic) and BCL-2 level explain most of
   the measurable signal.
5. **Spatial layer is normal lymphoid tissue, not bone marrow** (couldn't verify a downloadable
   marrow-niche dataset) — so it's a proof-of-concept, not a marrow claim.
6. **The composite score is a hypothesis, not a validated biomarker** — beaten by BCL-2 alone.

---

## 6. Likely tough questions + your answers (rehearse these)

**Q: "Isn't this just rediscovering that BCL-2-dependent cells respond to a BCL-2 inhibitor?"**
A: "Yes — and we say so explicitly. The guardian axis is confirmatory, not novel. Our *novel*
piece is the executioner-loss/ATAP-salvage angle and the spatial routing idea. We're honest that
the confirmatory part is strong and the novel part is an unvalidated hypothesis."

**Q: "Why would ATAP be selective for cancer? Wouldn't a pore-former kill everything?"**
A: "That's the key risk and why the optimized version is **ATAP-iRGD-M8** — the iRGD peptide is a
tumor-penetrating targeting moiety. Selectivity is exactly the thing that has to be shown at the
bench; we don't claim it."

**Q: "BAX/BAK loss is rare — is this even a real clinical population?"**
A: "It's rare at diagnosis (~2–5%), but it's enriched at **relapse after venetoclax**, which is
the population that actually needs a salvage. That's where we'd look, and it's an open question we
flag as needing relapse-cohort data."

**Q: "How do you know your executioner-loss call is right if expression is a weak proxy?"**
A: "We don't — that's our stated limitation. The right readout is **functional BH3 profiling** or
**engineered BAX/BAK-knockout lines**. That's our #1 ask."

**Q: "What's your evidence the model isn't overfit / p-hacked?"**
A: "We pre-registered the hypothesis, ran a 360-specification multiverse, used permutation nulls
and FDR correction, and built it twice independently. The executioner result is *robustly null* —
you can't p-hack your way to a null you didn't want."

**Q: "What would convince you you're right?"**
A: "One clean experiment: ATAP-M8 kills a **BAX/BAK-knockout, venetoclax-resistant** blood-cancer
line at a dose where venetoclax fails, and spares a normal control. We've written the
pre-registered plan for exactly that."

**Q: "What's genuinely new here versus the ATAP literature?"**
A: "The heme (blood-cancer) indication, the computational target-population map, and posing
'executioner availability' as a *spatial routing* question. Prior ATAP work is all solid-tumor."

---

## 7. What we want from him (the asks — pick based on his expertise)
1. **Sanity-check the biology** — is the executioner-loss → class-failure logic sound? Any obvious
   confounder we missed?
2. **Functional data** — does he (or a colleague) have or know of **BH3-profiling / apoptotic-
   priming** datasets, or access to Beat AML controlled data (dbGaP phs001657)?
3. **A relapse cohort** — post-venetoclax AML samples with BAX/BAK status.
4. **Wet-lab feasibility** — could a BAX/BAK-knockout venetoclax-resistant line + ATAP-M8 viability
   assay be run? We have the pre-registered design.
5. **Mentorship / a reality check** on whether this is worth pushing toward publication or a
   competition, and how to frame it honestly.

---

## 8. Cheat-sheet: numbers & terms to have on the tip of your tongue
| Term | Say this |
|------|----------|
| MOMP | mitochondrial outer-membrane permeabilization = the commit-to-death step |
| BH3-mimetic | drug that blocks a guardian (venetoclax = BCL-2) |
| Executioners | BAX, BAK — the pore-formers the drug class depends on |
| ATAP / ATAP-iRGD-M8 | Bfl-1 peptide that pores mitochondria *without* BAX/BAK; iRGD = tumor targeting |
| Beat AML | 671-patient AML dataset with real ex-vivo drug response (our primary cohort) |
| Guardian axis result | ρ = −0.275, p = 0.0005 (real) |
| BCL-2 alone | ρ = −0.567 (beats our composite — we admit it) |
| Monocytic signature | ρ = +0.721 (dominant confounder) |
| Executioner axis | null (ΔR² ≈ 0.001) across 3 independent tests |
| Prevalence of executioner loss | ~2–5% (rare; enriched at relapse) |
| Our honest one-liner | "Guardian axis real and confirmatory; executioner/ATAP axis is a hypothesis the data can't yet test — here's the experiment that would." |

---

### Final tone advice
You're a student bringing an honest, well-engineered analysis to an expert. Don't oversell. The
sentence that will impress a cancer researcher most is: *"Our main hypothesis is currently a null
in the data we can access, and we can tell you precisely why and what would test it."* That's how
real science sounds.
