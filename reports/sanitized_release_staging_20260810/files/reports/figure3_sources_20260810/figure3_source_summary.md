# Figure 3 Source Data 2026-08-10

Purpose: freeze the Mojahid split-inflation baseline source data before plotting.

Main claim: Mojahid random-minus-grouped split inflation is directionally consistent across model families but modest and model-dependent.

Boundary: Figure 3 is secondary support. It must not be framed as a universal leakage result because only 1/5 model families reaches material support.

## HOG + RBF-SVM Seed-Sweep Split Metrics

| split | metric | mean | std | min | max |
| --- | --- | ---: | ---: | ---: | ---: |
| random_stratified_80_20 | accuracy | 0.9580 | 0.0051 | 0.9525 | 0.9644 |
| random_stratified_80_20 | balanced_accuracy | 0.9543 | 0.0049 | 0.9489 | 0.9603 |
| random_stratified_80_20 | macro_f1 | 0.9546 | 0.0051 | 0.9492 | 0.9614 |
| grouped_fold_0_test_fold_1_val | accuracy | 0.8669 | 0.0000 | 0.8669 | 0.8669 |
| grouped_fold_0_test_fold_1_val | balanced_accuracy | 0.8566 | 0.0000 | 0.8566 | 0.8566 |
| grouped_fold_0_test_fold_1_val | macro_f1 | 0.8579 | 0.0000 | 0.8579 | 0.8579 |

## Five-Model Mojahid Delta

| model | delta BA | directional | material | interpretation |
| --- | ---: | --- | --- | --- |
| HOG + RBF-SVM | 0.0976 | yes | yes | material support |
| LBP + LinearSVM | 0.0365 | yes | no | directional only |
| TinyCNN | 0.0098 | yes | no | directional only |
| ResNet18 emb. + LinearSVM | 0.0250 | yes | no | directional only |
| EfficientNetB0 emb. + LinearSVM | 0.0340 | yes | no | directional only |

## Claim Boundary

- directional support: 5/5
- material support: 1/5
- mean delta BA: 0.0406
- delta range BA: 0.0098 to 0.0976
- claim status: directional_only
- boundary: Directional but modest/model-dependent split effect; do not frame as universal leakage.

## Plotting Notes

1. Show HOG random vs grouped as a concrete split-sensitivity example.
2. Show five-model deltas to prevent overgeneralizing the HOG result.
3. Visually mark the 0.05 material-support threshold.
4. Keep Figure 3 secondary to Figure 2.
