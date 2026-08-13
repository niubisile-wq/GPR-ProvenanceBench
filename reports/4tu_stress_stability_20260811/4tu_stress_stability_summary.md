# 4TU Stress Stability Audit

Variant audited: `log_clip`
Bootstrap draws: `10000`

| layer | units | selected models | mean delta | 95% CI | negative units | mean flip |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| fixed_split_seed_sweep | 20 | dummy_majority, extra_trees, rbf_svm | -0.0966 | [-0.1596, -0.0429] | 0.5000 | 0.4417 |
| group_aware_project_splits | 5 | dummy_majority, extra_trees, rbf_svm | -0.0169 | [-0.0462, 0.0000] | 0.4000 | 0.1877 |

Fixed-minus-group-aware delta attenuation: `-0.0797`.

Boundary: this confirms that the 4TU fixed-split stress signal weakens
under group-aware project splits. It supports a stress-test boundary,
not a main confirmation or external validation claim.
