# Unified Split Effect Statistics

Bootstrap uncertainty for random-minus-protocol balanced-accuracy gaps.

| dataset | contrast | delta BA | 95% CI | p(delta <= 0) | random shared groups | comparison shared groups |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| mojahid | random_minus_existing_fold_p2 | +0.0826 | [+0.0290, +0.1357] | 0.0030 | 157 | 0 |
| mojahid | random_minus_source_group_holdout_70_15_15 | +0.1219 | [+0.0532, +0.1863] | 0.0010 | 157 | 0 |
| mojahid | random_minus_provenance_size_holdout_p4 | +0.1670 | [+0.1064, +0.2280] | 0.0005 | 157 | 0 |
| mojahid | random_minus_datasail_like_group_balance | +0.1219 | [+0.0568, +0.1871] | 0.0005 | 157 | 0 |
| tigpr | random_minus_existing_fold_p2 | -0.0073 | [-0.0530, +0.0353] | 0.6387 | 44 | 49 |
| tigpr | random_minus_source_group_holdout_70_15_15 | +0.0128 | [-0.0371, +0.0594] | 0.3098 | 44 | 0 |
| tigpr | random_minus_provenance_size_holdout_p4 | +0.0516 | [+0.0065, +0.0956] | 0.0110 | 44 | 0 |
| tigpr | random_minus_datasail_like_group_balance | +0.0128 | [-0.0341, +0.0603] | 0.2914 | 44 | 0 |
| zenodo_14637589 | random_minus_existing_fold_p2 | +0.0283 | [-0.0522, +0.1017] | 0.2459 | 16 | 0 |
| zenodo_14637589 | random_minus_source_group_holdout_70_15_15 | +0.0527 | [-0.0273, +0.1290] | 0.0955 | 16 | 0 |
| zenodo_14637589 | random_minus_provenance_size_holdout_p4 | +0.3055 | [+0.2294, +0.3776] | 0.0005 | 16 | 0 |
| zenodo_14637589 | random_minus_datasail_like_group_balance | +0.0527 | [-0.0261, +0.1283] | 0.1024 | 16 | 0 |
| deepmask_gpr | random_minus_existing_fold_p2 | +0.1124 | [+0.0599, +0.1628] | 0.0005 | 216 | 0 |
| deepmask_gpr | random_minus_source_group_holdout_70_15_15 | +0.1188 | [+0.0658, +0.1747] | 0.0005 | 216 | 0 |
| deepmask_gpr | random_minus_provenance_size_holdout_p4 | +0.1124 | [+0.0615, +0.1637] | 0.0005 | 216 | 0 |
| deepmask_gpr | random_minus_datasail_like_group_balance | +0.1188 | [+0.0632, +0.1738] | 0.0005 | 216 | 0 |

## Boundary

This is local bootstrap uncertainty over fixed split baselines. It is not
a replacement for external validation or a full multi-seed training study.
