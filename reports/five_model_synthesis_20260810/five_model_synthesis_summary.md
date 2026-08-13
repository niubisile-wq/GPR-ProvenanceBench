# Five-Model Cross-Model Synthesis 2026-08-10

Scope: Mojahid and Res-SAM only. This synthesis does not include a full 4TU five-model matrix or external blind validation.

Material-support threshold: delta_mean >= 0.05 balanced accuracy.

## Claim-Level Summary

| dataset | contrast | directional support | material support | mean delta | min delta | max delta | status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| mojahid | random_minus_grouped_balanced_accuracy | 5/5 | 1/5 | 0.0406 | 0.0098 | 0.0976 | directional_only |
| res_sam | within_minus_transfer_real_world_to_synthetic | 5/5 | 5/5 | 0.4239 | 0.2356 | 0.6089 | supported |
| res_sam | within_minus_transfer_synthetic_to_real_world | 4/5 | 4/5 | 0.3743 | -0.0103 | 0.5833 | supported |

## Model-Level Evidence

| model | dataset | contrast | delta_mean | directional | material |
| --- | --- | --- | ---: | --- | --- |
| hog_rbf_svm | mojahid | random_minus_grouped_balanced_accuracy | 0.0976 | True | True |
| hog_rbf_svm | res_sam | within_minus_transfer_synthetic_to_real_world | 0.4117 | True | True |
| hog_rbf_svm | res_sam | within_minus_transfer_real_world_to_synthetic | 0.5556 | True | True |
| lbp_linear_svm | mojahid | random_minus_grouped_balanced_accuracy | 0.0365 | True | False |
| lbp_linear_svm | res_sam | within_minus_transfer_synthetic_to_real_world | 0.3083 | True | True |
| lbp_linear_svm | res_sam | within_minus_transfer_real_world_to_synthetic | 0.2356 | True | True |
| tinycnn | mojahid | random_minus_grouped_balanced_accuracy | 0.0098 | True | False |
| tinycnn | res_sam | within_minus_transfer_synthetic_to_real_world | -0.0103 | False | False |
| tinycnn | res_sam | within_minus_transfer_real_world_to_synthetic | 0.2907 | True | True |
| resnet18_embedding_linear_svm | mojahid | random_minus_grouped_balanced_accuracy | 0.0250 | True | False |
| resnet18_embedding_linear_svm | res_sam | within_minus_transfer_synthetic_to_real_world | 0.5783 | True | True |
| resnet18_embedding_linear_svm | res_sam | within_minus_transfer_real_world_to_synthetic | 0.4289 | True | True |
| efficientnet_b0_embedding_linear_svm | mojahid | random_minus_grouped_balanced_accuracy | 0.0340 | True | False |
| efficientnet_b0_embedding_linear_svm | res_sam | within_minus_transfer_synthetic_to_real_world | 0.5833 | True | True |
| efficientnet_b0_embedding_linear_svm | res_sam | within_minus_transfer_real_world_to_synthetic | 0.6089 | True | True |

## Interpretation

1. Res-SAM environment transfer is the strongest current cross-model claim: both transfer directions reach material support in at least 4/5 model families.
2. Mojahid random-minus-grouped inflation is directionally consistent across 5/5 model families, but only HOG+RBF-SVM reaches the 0.05 material threshold. This should be framed as a modest, model-dependent split effect rather than a strong universal inflation claim.
3. TinyCNN weakens the synthetic-to-real Res-SAM direction and nearly removes the Mojahid gap, so the manuscript must explicitly report model-family dependence.

## Boundary

This synthesis closes the first five-model matrix for Mojahid and Res-SAM only. It does not close G0/G1 for Nature Communications because 4TU group-aware evidence remains weak, TIGPR is local NO-GO, and blind external validation is still absent.
