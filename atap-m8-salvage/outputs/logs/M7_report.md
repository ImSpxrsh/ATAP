# M7 report — spatial priming + routing (REAL 10x Human Lymph Node Visium)

> Expression-based inference. A PREDICTED routing map, not a treatment map (GUARDRAILS §3). Lymph node = lymphoid tissue of origin for lymphomas.

- Spots after QC: 4032 / 4035 (min counts 200, min genes 100).
- Panel genes mapped: ['BAX', 'BAK1', 'BCL2', 'MCL1', 'BCL2A1', 'BCL2L1']

## Routing distribution (per spot)

| category | spots | % |
|----------|-------|---|
| venetoclax-sufficient | 2420 | 60.0 |
| low-signal | 963 | 23.9 |
| bypass-required | 649 | 16.1 |

- Mean per-spot stability (S³): 0.67 (across 81 spatial analytic choices).
- Bypass-required spots mean stability 0.47.

**Interpretation:** intratumoral/inter-niche heterogeneity in executioner-vs-guardian state is quantifiable in real lymphoid tissue. 'Bypass-required' spots (guardian-dependent yet executioner-low) are where a BAX-independent agent is *mechanistically rational*; 'venetoclax-sufficient' spots retain executioners. This poses executioner availability as a spatial routing question — an expression-based hypothesis, not evidence of efficacy.
