# TIGPR Duplicate-Aware Sweep

Samples: `7169`
Labels: `{'Crack': 1224, 'Interlayer_bonding_deficiency': 2020, 'Loose': 2100, 'No_damage': 1520, 'Void': 305}`
Seeds: `[20260811, 20260812, 20260813, 20260814, 20260815]`

## Duplicate Audit

- Exact duplicate groups: `243`
- Exact duplicate images: `486`
- Cross-label exact duplicate groups: `2`

## Split Summary

| split | HOG BA | metadata BA | shared hash groups | shared test samples |
| --- | ---: | ---: | ---: | ---: |
| hash_group_stratified_80_20 | 0.6777 | 0.8892 | 0.0 | 0.0 |
| random_stratified_80_20 | 0.7314 | 0.8847 | 76.6 | 76.6 |

## Random Minus Group-Aware

| metric | mean delta | std | min | max |
| --- | ---: | ---: | ---: | ---: |
| random_minus_group_hog_accuracy | 0.0176 | 0.0177 | 0.0006 | 0.0448 |
| random_minus_group_hog_balanced_accuracy | 0.0537 | 0.0162 | 0.0403 | 0.0797 |
| random_minus_group_hog_macro_f1 | 0.0523 | 0.0120 | 0.0376 | 0.0690 |
| random_minus_group_metadata_accuracy | 0.0002 | 0.0049 | -0.0055 | 0.0050 |
| random_minus_group_metadata_balanced_accuracy | -0.0045 | 0.0419 | -0.0497 | 0.0471 |
| random_minus_group_metadata_macro_f1 | -0.0002 | 0.0344 | -0.0359 | 0.0410 |

Boundary: this closes a restored-local TIGPR duplicate-aware baseline,
but it does not close blind external validation because labels and media
are visible before model development.
