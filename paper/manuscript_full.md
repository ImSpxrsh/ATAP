# A computational susceptibility map for BAX/BAK-independent salvage in BH3-mimetic-resistant blood cancers

*Draft manuscript. Predict-and-map, public data only. **No efficacy is claimed** — every
susceptibility statement is predicted from mechanism, not measured (see GUARDRAILS §3).*

---

## Abstract
BH3-mimetics such as venetoclax kill cancer cells by neutralizing anti-apoptotic guardians
(BCL-2, MCL-1) to unleash the apoptotic executioners BAX and BAK. When a tumor loses BAX/BAK,
the entire BH3-mimetic class fails at the same executioner step, and no guardian-targeting drug
can restore killing. ATAP — an amphipathic tail-anchoring peptide from Bfl-1 (BCL2A1 residues
147–175) — permeabilizes mitochondria **independently of BAX/BAK**, making it a mechanistically
rational salvage for exactly this setting. Using only public data (DepMap, GDSC, Beat AML, TCGA,
and 10x Visium spatial transcriptomics) and **no ATAP response data**, we built — twice, in two
independent implementations — a pipeline that (i) defines executioner loss from genomics, (ii)
tests its association with venetoclax resistance, (iii) scores a mechanistic ATAP-susceptibility,
and (iv) maps it spatially. Both implementations converge on the same honest result: the
**guardian-dependence axis** robustly predicts venetoclax resistance (Beat AML n=367,
ρ=−0.275, permutation p=5×10⁻⁴; DepMap guardian-only ρ=0.50), whereas the **executioner-loss
axis is null** in cell lines and patients (M3 ΔR²≈0.001; pan-BH3-mimetic MCL1i crux test β=−0.04,
p=0.65; ablation ρ≈0), and the mechanistic composite is beaten by BCL-2 expression alone
(ρ=−0.567), with a monocytic-differentiation signature the dominant confounder (ρ=+0.721).
Because BAX/BAK loss is rare at diagnosis (~2–5%) but reaches ~17% at venetoclax relapse, and
because mRNA is a weak surrogate for executioner function, the executioner axis is **not
testable in these data by construction**. We therefore define the exact decisive data — functional
apoptotic priming (BH3 profiling) and engineered BAX/BAK-null lines — and pre-register a single
falsifiable bench test. The contribution is a mechanistic rationale, a target-population map, and
a novel spatial "routing" concept — not evidence of ATAP activity.

## 1. Introduction
Venetoclax has transformed treatment of CLL and AML, but resistance is common and mechanistically
diverse: guardian switching (MCL-1/BCL-xL upregulation), loss of TP53/priming, monocytic
differentiation, and — critically for this work — loss of the executioners themselves. Because
every BH3-mimetic ultimately depends on BAX/BAK to permeabilize the mitochondrion, executioner
loss is a **class-wide** liability: it cannot be rescued by switching to a different guardian
inhibitor. A pore-former that does not require BAX/BAK would, in principle, address precisely this
population. ATAP (and its optimized, tumor-penetrating form ATAP-iRGD-M8) is such an agent, but it
has only been studied in solid tumors. We ask, computationally: *which blood cancers are
executioner-deficient and guardian-dependent, and where within a tumor is that state localized?*

## 2. Methods (summary; full detail in `docs/methods.md` and `ARCHITECTURE.md`)
**Data.** DepMap (expression, CN, mutation, CRISPR, Model metadata); GDSC (ex-vivo dose-response
for venetoclax, navitoclax, ABT-737, MCL-1 inhibitors, pan-guardian agents); Beat AML 2.0 (RNA,
mutations, ex-vivo venetoclax AUC on 671 patients); TCGA-LAML/DLBC; 10x Human Lymph Node Visium.
**Executioner loss (M1).** Damaging BAX/BAK1 mutation OR deep deletion OR bottom-decile expression
of both, computed with no reference to drug data (non-circular). **Backbone (M2).** OLS of
z-scored resistance on executioner loss, lineage-adjusted, with permutation null. **Confounders
(M3).** Nested OLS adding MCL-1, BCL-2:BCL-xL ratio, BCL-2 hotspot. **Multiverse (M4).** 360-spec
specification curve, FDR, stability score. **Stratifier (M5/M6).** Susceptibility =
√(guardian_dependence × executioner_deficiency), validated against observed venetoclax resistance.
**Spatial (M7).** Per-spot routing (bypass-required vs venetoclax-sufficient) with per-spot
multiverse stability, on real Visium. **Validation (M8).** Synthetic ground-truth recovery, power
curves, permutation nulls — labelled method validation, never biology. **Prior-art (M9).** Dated
search log. Two independent implementations (an OO `atap` library + a flat module pipeline) run
the same logic against the same config for internal replication.

## 3. Results
**3.1 The resistance mechanism is real but guardian-driven.** In the Beat AML primary cohort
(n=367), the mechanistic score identifies venetoclax-resistant patients (ρ=−0.275, permutation
p=5×10⁻⁴); DepMap replicates the direction. Ablation shows the signal is carried **entirely by
guardian dependence** (guardian-only ρ=0.50 DepMap / 0.27 Beat AML) and **not** by executioner
deficiency (ρ≈0).

**3.2 The executioner-loss axis is null in these data — three independent ways.** (i) M3: once
guardian confounders are included, executioner loss adds ΔR²≈0.001 (partial p≈0.7). (ii)
Pan-BH3-mimetic test: executioner loss does not predict resistance across the drug class; the
MCL1-selective crux test (which would dissociate guardian-switching from executioner loss) is null
(β=−0.04, p=0.65). (iii) Multiverse: across 360 specifications the executioner effect is
directionally weak and 0% significant after FDR. A parallel implementation reaches the same null
via a 25-specification curve (executioner effect 100% robustly null).

**3.3 Honest model critique.** A discrimination battery shows the mechanistic composite is
**beaten by BCL-2 expression alone** (ρ=−0.567) and that a **monocytic-differentiation signature
dominates** (ρ=+0.721) — independently recovering a known biological axis of venetoclax resistance,
which validates the pipeline while bounding the composite's novelty.

**3.4 A calibrated decision boundary ("tipping point").** Rather than assert an (unsupportable)
physical threshold, we fit the logistic boundary that separates venetoclax responders from
non-responders in the two-axis (guardian × executioner) plane and bootstrap it. The boundary
predicts response (DepMap AUC=0.75, Beat AML AUC=0.64) and is **driven by the guardian axis**
(β_guardian=+0.97 [+0.58,+1.42] DepMap, +0.48 [+0.27,+0.70] Beat AML — CIs exclude 0), while the
**executioner axis coefficient is ~0** (CIs span 0). The response "tipping point" is thus a
guardian-dependence threshold (~0.47–0.54 rank, bootstrap CI reported), and the executioner axis —
the mechanistic ATAP modifier — is explicitly the part these data cannot resolve.

**3.5 The susceptibility map and spatial routing.** The composite tracks observed venetoclax
resistance (DepMap ρ=0.34; Beat AML ρ=0.23) and stratifies subtypes; on real lymphoid tissue,
~16% of spots are "bypass-required" (guardian-dependent yet executioner-low) with quantified
per-spot stability — reframing executioner availability as a spatial routing question.

**3.6 Single-cell resolution (van Galen AML atlas).** Across 3,434 malignant cells from 8 AML
patients, monocytic malignant cells occupy a distinct region of the guardian/executioner plane:
markedly higher MCL-1 (median 1.45 vs 0.0, p=8×10⁻⁶⁴) and guardian dependence (0.67 vs 0.25,
p=1×10⁻⁶⁹) than primitive (HSC/Prog/GMP-like) cells, with **identical** executioner availability
(p=0.84). This provides a single-cell mechanism for the monocytic venetoclax-resistance signature
identified in §3.3 — intratumoral heterogeneity concentrated on the guardian (MCL-1) axis — and
independently recovers established monocytic-resistance biology.

**3.7 Prognostic layer (Beat AML, n=649).** The mechanistic score is not an independent
prognostic marker: a crude executioner-availability survival association (HR 0.86, p=0.004) is
confounded by ELN2017 risk and age and is null after adjustment (HR 0.94, p=0.25) — confirming
the score indexes drug-response biology, not prognosis.

**3.8 Method validation and prior art.** Synthetic recovery reaches ROC-AUC=1.0 and recovered
spatial structure beats a permutation null (p=0.001). Prior-art search finds the hematologic ATAP
indication literature-open (all prior work solid-tumor); patent scope is flagged for IP counsel.

## 4. Discussion
The convergent, twice-replicated result is that guardian dependence — not executioner loss — drives
*measurable* venetoclax resistance in public cohorts. This is not evidence against the executioner
hypothesis; it is a direct consequence of two facts. First, **BAX/BAK loss is rare at diagnosis
(~2–5%) but is enriched at venetoclax relapse, where acquired inactivating BAX mutations reach ~17%**
(Moujalled et al., *Blood* 2023) — i.e., the target population is concentrated in exactly the
relapse setting our diagnosis-weighted public cohorts under-sample. Second, **mRNA is a weak proxy
for whether the executioner step actually works**; the functionally decisive quantity is apoptotic
priming, which expression cannot capture. The executioner axis is therefore **orthogonal to what
these data can measure**, and locating it precisely there — rather than forcing a spurious p<0.05 —
is the honest and useful outcome. It also dictates the next data: **functional dynamic BH3
profiling** and **engineered BAX/BAK-null lines**.

## 5. Limitations
Predicted, not validated; no ATAP data; the core executioner hypothesis is unproven and untestable
in expression data; strong confounding by differentiation state and BCL-2 level; the spatial layer
is normal lymphoid tissue, not bone-marrow niche; the composite is a hypothesis, not a validated
biomarker.

## 6. Conclusion and the one decisive experiment
This work delivers a mechanistic rationale, a documented (relapse-enriched) target population, and
a novel spatial-routing framework — while being explicit that ATAP efficacy is unproven. The
project is designed to converge on a single falsifiable test: **ATAP-iRGD-M8 kills a BAX/BAK-null,
venetoclax-resistant blood-cancer line at a dose where venetoclax fails, and spares a normal
control.** A "no" is as informative as a "yes." Everything upstream — the map, the score, the
routing — exists to aim that one experiment.

---
*Figures F1–F13 in `outputs/figures/` and `results/`; per-module reports in `outputs/logs/`;
data provenance in `data/raw/MANIFEST.md`; pre-registration and claim map in
[`manuscript.md`](manuscript.md).*
