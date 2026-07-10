# Poster — ATAP-M8 as BAX-independent salvage for BH3-mimetic-resistant blood cancers

> Predict-and-map. **Zero ATAP response data.** Predicted susceptibility, not efficacy.
> Built **twice independently** — both implementations reach the same conclusion (replication).

## Narrative arc (§8)
1. **The class-wide vulnerability [F1].** BH3-mimetics (venetoclax, MCL-1i) all kill through
   BAX/BAK. Lose the executioners → the whole class fails at the executioner step. ATAP-M8
   forms the pore directly, bypassing them (established biology).
2. **The target population is real and concentrated at relapse.** Executioner (BAX/BAK) loss is
   rare at diagnosis (~2–5%) but **acquired inactivating BAX mutations reach ~17% at venetoclax
   relapse** (Moujalled, *Blood* 2023) — exactly the setting that needs a salvage. [F3, F_M1]
2b. **Honest self-critique (this earns trust).** Our mechanistic composite is **beaten by BCL-2
   expression alone** (ρ=−0.567), and a **monocytic-differentiation signature dominates**
   (ρ=+0.721) — independently rediscovering known resistance biology. We report it. [F4–F5]
3. **It's robust-to-analytic-choice… in its weakness [F6].** 360-spec curve: 77%
   directionally consistent, 0% significant after FDR. The figure bounds the claim.
4. **Here's the target population [F7–F8].** A BCL-2-family susceptibility composite tracks
   *observed* ex vivo venetoclax resistance in real Beat AML patients (ρ=0.23, p=6e-6) and
   DepMap (ρ=0.34) — the addressable population, not an ATAP kill rate.
5. **Here's where inside a tumor it matters [F9–F10].** Real lymph-node Visium: 16% of spots
   are "bypass-required" (dependent yet executioner-low), 60% venetoclax-sufficient, with
   per-spot confidence. Executioner availability as a spatial routing question — novel.
6. **Methods are validated and honest about scope [F11–F12].** Synthetic recovery ROC=1.0;
   structure beats permutation nulls; power curves.
7. **Prior-art / IP gate.** Heme indication appears literature-open (prior ATAP work is
   solid-tumor); patent scope flagged for IP counsel.
8. **One testable prediction for the bench [F13].** Pre-registered single-prediction
   validation on a BAX-deficient, venetoclax-resistant line (if access lands).

## Claim map (claim → figure → guardrail)
| claim | figure(s) | guardrail bound |
|-------|-----------|-----------------|
| Class-wide executioner-step vulnerability; ATAP bypass | F1 | established biology, no efficacy |
| Executioner loss is present and quantifiable | F3, F_M1 | prevalence = addressable upper bound |
| Executioner loss → venetoclax resistance (weak) | F4 | correlation ≠ ATAP efficacy |
| Adds ~0 beyond confounders | F5 | reported, not hidden |
| Directionally consistent, not robust | F6 | anti-overclaiming device |
| Susceptibility tracks observed resistance | F7, F8 | target population, not kill rate |
| Intratumoral routing map | F9, F10 | predicted routing, not treatment |
| Methods recover truth; beat chance | F11, F12 | synthetic = validation only |
| Heme indication novelty + IP | priorart_log.md | novelty is M9 output, patent flagged |
| One bench-testable prediction | F13 | validates one prediction, not efficacy |

## Honest bottom line
The mechanism is sound and the *target-population* and *spatial-routing* layers are real and
novel. Three independent tests (confounders, pan-BH3-mimetic, ablation) agree the
executioner-loss axis is **orthogonal to measurable venetoclax resistance** — because BAX/BAK
loss is rare and concentrated at relapse, and mRNA is a weak proxy for executioner function.
That is a *signpost*, not a dead end: it names the decisive data (functional BH3 profiling +
engineered BAX/BAK-null lines) and the one falsifiable bench test. A rationale-and-map that
knows exactly what would prove it — not a demonstration of ATAP activity.
