# Unified Split Model-Ranking Audit

Two lightweight model families are evaluated on every unified split.

| dataset | protocol | top model | random top | flip vs random | SGD BA | ExtraTrees BA |
| --- | --- | --- | --- | --- | ---: | ---: |
| mojahid | random_stratified_70_15_15 | sgd_logistic | sgd_logistic | False | 0.8530 | 0.8356 |
| mojahid | existing_fold_p2 | sgd_logistic | sgd_logistic | False | 0.7704 | 0.7603 |
| mojahid | source_group_holdout_70_15_15 | extra_trees | sgd_logistic | True | 0.7311 | 0.7543 |
| mojahid | provenance_size_holdout_p4 | extra_trees | sgd_logistic | True | 0.6860 | 0.7070 |
| mojahid | datasail_like_group_balance | extra_trees | sgd_logistic | True | 0.7311 | 0.7543 |
| tigpr | random_stratified_70_15_15 | extra_trees | extra_trees | False | 0.7087 | 0.7791 |
| tigpr | existing_fold_p2 | extra_trees | extra_trees | False | 0.7160 | 0.7592 |
| tigpr | source_group_holdout_70_15_15 | extra_trees | extra_trees | False | 0.6959 | 0.7122 |
| tigpr | provenance_size_holdout_p4 | extra_trees | extra_trees | False | 0.6571 | 0.7095 |
| tigpr | datasail_like_group_balance | extra_trees | extra_trees | False | 0.6959 | 0.7122 |
| zenodo_14637589 | random_stratified_70_15_15 | extra_trees | extra_trees | False | 0.8961 | 0.9385 |
| zenodo_14637589 | existing_fold_p2 | sgd_logistic | extra_trees | True | 0.8678 | 0.8624 |
| zenodo_14637589 | source_group_holdout_70_15_15 | extra_trees | extra_trees | False | 0.8434 | 0.8896 |
| zenodo_14637589 | provenance_size_holdout_p4 | extra_trees | extra_trees | False | 0.5907 | 0.6528 |
| zenodo_14637589 | datasail_like_group_balance | extra_trees | extra_trees | False | 0.8434 | 0.8896 |
| deepmask_gpr | random_stratified_70_15_15 | sgd_logistic | sgd_logistic | False | 0.8767 | 0.8763 |
| deepmask_gpr | existing_fold_p2 | sgd_logistic | sgd_logistic | False | 0.7642 | 0.7422 |
| deepmask_gpr | source_group_holdout_70_15_15 | sgd_logistic | sgd_logistic | False | 0.7579 | 0.7409 |
| deepmask_gpr | provenance_size_holdout_p4 | sgd_logistic | sgd_logistic | False | 0.7642 | 0.7422 |
| deepmask_gpr | datasail_like_group_balance | sgd_logistic | sgd_logistic | False | 0.7579 | 0.7409 |

## Boundary

This is a local model-ranking sensitivity audit. It does not replace the
larger five-model synthesis or blind external validation.
