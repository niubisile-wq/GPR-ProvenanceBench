# Unified Split Baseline

One lightweight baseline is evaluated over every generated split manifest.

| dataset | protocol | model | test n | shared groups | balanced accuracy | random - protocol BA |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| mojahid | random_stratified_70_15_15 | hog_sgd_logistic | 380 | 157 | 0.8530 | +0.0000 |
| mojahid | existing_fold_p2 | hog_sgd_logistic | 586 | 0 | 0.7704 | +0.0826 |
| mojahid | source_group_holdout_70_15_15 | hog_sgd_logistic | 392 | 0 | 0.7311 | +0.1219 |
| mojahid | provenance_size_holdout_p4 | hog_sgd_logistic | 534 | 0 | 0.6860 | +0.1670 |
| mojahid | datasail_like_group_balance | hog_sgd_logistic | 392 | 0 | 0.7311 | +0.1219 |
| tigpr | random_stratified_70_15_15 | hog_sgd_logistic | 1076 | 44 | 0.7087 | +0.0000 |
| tigpr | existing_fold_p2 | hog_sgd_logistic | 1434 | 49 | 0.7160 | -0.0073 |
| tigpr | source_group_holdout_70_15_15 | hog_sgd_logistic | 1075 | 0 | 0.6959 | +0.0128 |
| tigpr | provenance_size_holdout_p4 | hog_sgd_logistic | 1436 | 0 | 0.6571 | +0.0516 |
| tigpr | datasail_like_group_balance | hog_sgd_logistic | 1075 | 0 | 0.6959 | +0.0128 |
| zenodo_14637589 | random_stratified_70_15_15 | byte_signature_sgd_logistic | 138 | 16 | 0.8961 | +0.0000 |
| zenodo_14637589 | existing_fold_p2 | byte_signature_sgd_logistic | 210 | 0 | 0.8678 | +0.0283 |
| zenodo_14637589 | source_group_holdout_70_15_15 | byte_signature_sgd_logistic | 210 | 0 | 0.8434 | +0.0527 |
| zenodo_14637589 | provenance_size_holdout_p4 | byte_signature_sgd_logistic | 531 | 0 | 0.5907 | +0.3055 |
| zenodo_14637589 | datasail_like_group_balance | byte_signature_sgd_logistic | 210 | 0 | 0.8434 | +0.0527 |
| deepmask_gpr | random_stratified_70_15_15 | hog_sgd_logistic | 379 | 216 | 0.8767 | +0.0000 |
| deepmask_gpr | existing_fold_p2 | hog_sgd_logistic | 512 | 0 | 0.7642 | +0.1124 |
| deepmask_gpr | source_group_holdout_70_15_15 | hog_sgd_logistic | 392 | 0 | 0.7579 | +0.1188 |
| deepmask_gpr | provenance_size_holdout_p4 | hog_sgd_logistic | 512 | 0 | 0.7642 | +0.1124 |
| deepmask_gpr | datasail_like_group_balance | hog_sgd_logistic | 392 | 0 | 0.7579 | +0.1188 |

## Boundary

These are local split-protocol baselines. They quantify split sensitivity
but do not create blind external validation.
