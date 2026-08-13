# Local Sign-Flip / Permutation Audit

Exact sign and exhaustive sign-flip tests are computed from existing local
experimental contrasts. No model is retrained here.

## Unified Split Random-Minus-Protocol

| unit | n | + | - | mean delta | sign p | mean sign-flip p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| deepmask_gpr | 4 | 4 | 0 | +0.1156 | 0.0625 | 0.0625 |
| mojahid | 4 | 4 | 0 | +0.1233 | 0.0625 | 0.0625 |
| tigpr | 4 | 3 | 1 | +0.0174 | 0.3125 | 0.1250 |
| zenodo_14637589 | 4 | 4 | 0 | +0.1098 | 0.0625 | 0.0625 |
| all_assets | 16 | 15 | 1 | +0.0916 | 0.0003 | 0.0000 |

## 4TU Log-Clip Stress Deltas

| unit | n | + | - | mean delta | sign p | mean sign-flip p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fixed_split_seed_sweep | 20 | 0 | 10 | -0.0966 | 0.0010 | 0.0010 |
| group_aware_project_splits | 5 | 0 | 2 | -0.0169 | 0.2500 | 0.2500 |

## Boundary

These tests strengthen the local statistical audit layer. They do not
replace cluster bootstrap, deep model reruns or blind external validation.
