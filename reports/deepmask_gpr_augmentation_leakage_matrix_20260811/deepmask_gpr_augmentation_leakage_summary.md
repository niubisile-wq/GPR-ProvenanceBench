# DeepMask GPR Augmentation Leakage Matrix

Runs: 60
Best random minus best group-holdout BA: +0.0407
Best random minus train-augmented/test-original BA: -0.0346

| protocol | feature | model | runs | BA mean | BA std | shared base groups mean |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| base_source_group_holdout_80_20 | hog64 | hog64_sgd | 5 | 0.7934 | 0.0357 | 0.0 |
| base_source_group_holdout_80_20 | metadata | metadata_extra_trees | 5 | 0.8695 | 0.0125 | 0.0 |
| base_source_group_holdout_80_20 | pixel32 | pixel32_extra_trees | 5 | 0.9247 | 0.0075 | 0.0 |
| random_stratified_80_20 | hog64 | hog64_sgd | 5 | 0.8799 | 0.0098 | 238.0 |
| random_stratified_80_20 | metadata | metadata_extra_trees | 5 | 0.8749 | 0.0131 | 238.0 |
| random_stratified_80_20 | pixel32 | pixel32_extra_trees | 5 | 0.9654 | 0.0060 | 238.0 |
| train_augmented_test_original | hog64 | hog64_sgd | 5 | 0.9751 | 0.0050 | 285.0 |
| train_augmented_test_original | metadata | metadata_extra_trees | 5 | 0.5659 | 0.0061 | 285.0 |
| train_augmented_test_original | pixel32 | pixel32_extra_trees | 5 | 1.0000 | 0.0000 | 285.0 |
| train_original_test_augmented | hog64 | hog64_sgd | 5 | 0.8135 | 0.0072 | 285.0 |
| train_original_test_augmented | metadata | metadata_extra_trees | 5 | 0.3791 | 0.0073 | 285.0 |
| train_original_test_augmented | pixel32 | pixel32_extra_trees | 5 | 0.9059 | 0.0019 | 285.0 |

## Boundary

This matrix is a fourth local/public asset stress test. It does not close
the hard blind external validation gate.
