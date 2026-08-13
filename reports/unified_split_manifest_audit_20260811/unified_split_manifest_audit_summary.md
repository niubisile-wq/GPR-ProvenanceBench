# Unified Split Manifest Audit

This report creates local executable split manifests for current usable assets.
DataSAIL is represented only by a deterministic source-group balancing proxy, not the external solver.

| dataset | protocol | rows | train | val | test | shared train-test groups | missing test labels |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| mojahid | random_stratified_70_15_15 | 2524 | 1761 | 383 | 380 | 157 | [] |
| mojahid | existing_fold_p2 | 2524 | 1512 | 426 | 586 | 0 | [] |
| mojahid | source_group_holdout_70_15_15 | 2524 | 1738 | 394 | 392 | 0 | [] |
| mojahid | provenance_size_holdout_p4 | 2524 | 1705 | 285 | 534 | 0 | [] |
| mojahid | datasail_like_group_balance | 2524 | 1738 | 394 | 392 | 0 | [] |
| tigpr | random_stratified_70_15_15 | 7169 | 5017 | 1076 | 1076 | 44 | [] |
| tigpr | existing_fold_p2 | 7169 | 4301 | 1434 | 1434 | 49 | [] |
| tigpr | source_group_holdout_70_15_15 | 7169 | 5019 | 1075 | 1075 | 0 | [] |
| tigpr | provenance_size_holdout_p4 | 7169 | 5016 | 717 | 1436 | 0 | [] |
| tigpr | datasail_like_group_balance | 7169 | 5019 | 1075 | 1075 | 0 | [] |
| zenodo_14637589 | random_stratified_70_15_15 | 914 | 638 | 138 | 138 | 16 | [] |
| zenodo_14637589 | existing_fold_p2 | 914 | 444 | 260 | 210 | 0 | [] |
| zenodo_14637589 | source_group_holdout_70_15_15 | 914 | 433 | 271 | 210 | 0 | [] |
| zenodo_14637589 | provenance_size_holdout_p4 | 914 | 236 | 147 | 531 | 0 | [] |
| zenodo_14637589 | datasail_like_group_balance | 914 | 433 | 271 | 210 | 0 | [] |
| deepmask_gpr | random_stratified_70_15_15 | 2524 | 1766 | 379 | 379 | 216 | [] |
| deepmask_gpr | existing_fold_p2 | 2524 | 1746 | 266 | 512 | 0 | [] |
| deepmask_gpr | source_group_holdout_70_15_15 | 2524 | 1740 | 392 | 392 | 0 | [] |
| deepmask_gpr | provenance_size_holdout_p4 | 2524 | 1746 | 266 | 512 | 0 | [] |
| deepmask_gpr | datasail_like_group_balance | 2524 | 1740 | 392 | 392 | 0 | [] |

## Boundary

These split manifests strengthen local reproducibility and leakage auditing.
They do not create blind external validation and do not replace a true DataSAIL run.
