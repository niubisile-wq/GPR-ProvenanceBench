# Planned Five-Model Cross-Model Synthesis 2026-08-11

This matrix uses the five families explicitly named in the frozen plan: HOG+RBF-SVM, lightweight CNN, ResNet18, EfficientNetB0 and DeiT-Tiny.

Material-support threshold: delta_mean >= 0.05 balanced accuracy.

## Claim-Level Summary

| dataset | contrast | directional support | material support | mean delta | min delta | max delta | status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| mojahid | random_minus_grouped_balanced_accuracy | 5/5 | 1/5 | 0.0371 | 0.0098 | 0.0976 | directional_only |
| res_sam | within_minus_transfer_real_world_to_synthetic | 5/5 | 5/5 | 0.4888 | 0.2907 | 0.6089 | supported |
| res_sam | within_minus_transfer_synthetic_to_real_world | 4/5 | 4/5 | 0.4139 | -0.0103 | 0.5833 | supported |

## Model-Level Evidence

| model | dataset | contrast | delta_mean | directional | material |
| --- | --- | --- | ---: | --- | --- |
| hog_rbf_svm | mojahid | random_minus_grouped_balanced_accuracy | 0.0976 | True | True |
| hog_rbf_svm | res_sam | within_minus_transfer_synthetic_to_real_world | 0.4117 | True | True |
| hog_rbf_svm | res_sam | within_minus_transfer_real_world_to_synthetic | 0.5556 | True | True |
| lightweight_cnn | mojahid | random_minus_grouped_balanced_accuracy | 0.0098 | True | False |
| lightweight_cnn | res_sam | within_minus_transfer_synthetic_to_real_world | -0.0103 | False | False |
| lightweight_cnn | res_sam | within_minus_transfer_real_world_to_synthetic | 0.2907 | True | True |
| resnet18_embedding_linear_svm | mojahid | random_minus_grouped_balanced_accuracy | 0.0250 | True | False |
| resnet18_embedding_linear_svm | res_sam | within_minus_transfer_synthetic_to_real_world | 0.5783 | True | True |
| resnet18_embedding_linear_svm | res_sam | within_minus_transfer_real_world_to_synthetic | 0.4289 | True | True |
| efficientnet_b0_embedding_linear_svm | mojahid | random_minus_grouped_balanced_accuracy | 0.0340 | True | False |
| efficientnet_b0_embedding_linear_svm | res_sam | within_minus_transfer_synthetic_to_real_world | 0.5833 | True | True |
| efficientnet_b0_embedding_linear_svm | res_sam | within_minus_transfer_real_world_to_synthetic | 0.6089 | True | True |
| deit_tiny_embedding_linear_svm | mojahid | random_minus_grouped_balanced_accuracy | 0.0191 | True | False |
| deit_tiny_embedding_linear_svm | res_sam | within_minus_transfer_synthetic_to_real_world | 0.5067 | True | True |
| deit_tiny_embedding_linear_svm | res_sam | within_minus_transfer_real_world_to_synthetic | 0.5600 | True | True |

## Boundary

The architecture slot is now complete for the planned Mojahid/Res-SAM directional matrix. ResNet18, EfficientNetB0 and DeiT-Tiny use frozen ImageNet embeddings rather than end-to-end fine-tuning. This matrix does not include a real blind external asset and does not establish external repair benefit.
