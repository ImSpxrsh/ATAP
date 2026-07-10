# Single-cell layer — guardian/executioner state across AML cell states
(van Galen 2019, GSE116256; pooled 8 diagnosis samples, 6,095 cells, 3,434 malignant).

## Cell-type profile (top by 'bypass' = guardian-high × executioner-low)
| CellType | n | MCL1 | BCL2 | guardian | exec avail | bypass |
|----------|---|------|------|----------|-----------|--------|
| Mono | 564 | 1.12 | 0.03 | 0.61 | 0.49 | 0.312 |
| Mono-like | 1133 | 1.24 | 0.01 | 0.62 | 0.51 | 0.304 |
| cDC | 157 | 0.93 | 0.16 | 0.52 | 0.51 | 0.259 |
| ProMono | 165 | 1.18 | 0.07 | 0.55 | 0.53 | 0.257 |
| ProMono-like | 226 | 1.05 | 0.07 | 0.52 | 0.51 | 0.257 |
| cDC-like | 353 | 0.90 | 0.07 | 0.53 | 0.52 | 0.255 |
| GMP | 193 | 0.86 | 0.12 | 0.49 | 0.47 | 0.253 |
| CTL | 86 | 0.61 | 0.22 | 0.48 | 0.48 | 0.247 |
| T | 536 | 0.45 | 0.40 | 0.46 | 0.47 | 0.241 |
| HSC | 130 | 0.69 | 0.13 | 0.45 | 0.47 | 0.239 |

## Crux test — monocytic vs primitive MALIGNANT cells (n_mono=1,359, n_prim=2,075)
| feature | monocytic median | primitive median | p |
|---------|------------------|------------------|---|
| MCL1 | 1.454 | 0.000 | 8.40e-64 |
| BCL2 | 0.000 | 0.000 | 9.69e-23 |
| guardian_dependence | 0.671 | 0.251 | 1.41e-69 |
| executioner_availability | 0.451 | 0.451 | 8.43e-01 |
| bypass_score | 0.337 | 0.138 | 6.81e-41 |

## Per-patient robustness (not driven by one sample)
- Monocytic > primitive guardian dependence in **4/5 patients** (direction), significant (p<0.05) in **4/5**.

| sample | n_mono | n_prim | Δ guardian (mono−prim) | p |
|--------|--------|--------|------------------------|---|
| AML1012-D0 | 310 | 546 | +0.098 | 3.97e-04 |
| AML210A-D0 | 233 | 231 | +0.394 | 1.10e-09 |
| AML328-D0 | 215 | 478 | +0.337 | 1.68e-14 |
| AML329-D0 | 18 | 235 | +0.000 | 2.56e-01 |
| AML419A-D0 | 581 | 487 | +0.219 | 4.79e-35 |

**Reading:** if monocytic malignant cells sit in a distinct region of the guardian/executioner plane (e.g., higher MCL-1 / lower BCL-2 dependence), that is a single-cell mechanism for the monocytic venetoclax-resistance signature our bulk discrimination battery flagged — intratumoral heterogeneity in the exact axis the framework scores. Expression-based cell-state map; no efficacy claim.
