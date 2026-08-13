# Unified Split Five-Family Matrix

Five lightweight model/feature families are evaluated for every unified split.

| dataset | protocol | top model | random top | flip vs random |
| --- | --- | --- | --- | --- |
| mojahid | random_stratified_70_15_15 | image_metadata_extra_trees | image_metadata_extra_trees | False |
| mojahid | existing_fold_p2 | image_metadata_extra_trees | image_metadata_extra_trees | False |
| mojahid | source_group_holdout_70_15_15 | image_metadata_extra_trees | image_metadata_extra_trees | False |
| mojahid | provenance_size_holdout_p4 | image_metadata_extra_trees | image_metadata_extra_trees | False |
| mojahid | datasail_like_group_balance | image_metadata_extra_trees | image_metadata_extra_trees | False |
| tigpr | random_stratified_70_15_15 | pixel32_extra_trees | pixel32_extra_trees | False |
| tigpr | existing_fold_p2 | pixel32_extra_trees | pixel32_extra_trees | False |
| tigpr | source_group_holdout_70_15_15 | pixel32_extra_trees | pixel32_extra_trees | False |
| tigpr | provenance_size_holdout_p4 | pixel32_extra_trees | pixel32_extra_trees | False |
| tigpr | datasail_like_group_balance | pixel32_extra_trees | pixel32_extra_trees | False |
| zenodo_14637589 | random_stratified_70_15_15 | raw_file_metadata_extra_trees | raw_file_metadata_extra_trees | False |
| zenodo_14637589 | existing_fold_p2 | byte_signature_sgd_logistic | raw_file_metadata_extra_trees | True |
| zenodo_14637589 | source_group_holdout_70_15_15 | byte_signature_extra_trees | raw_file_metadata_extra_trees | True |
| zenodo_14637589 | provenance_size_holdout_p4 | byte_signature_extra_trees | raw_file_metadata_extra_trees | True |
| zenodo_14637589 | datasail_like_group_balance | byte_signature_extra_trees | raw_file_metadata_extra_trees | True |
| deepmask_gpr | random_stratified_70_15_15 | pixel32_extra_trees | pixel32_extra_trees | False |
| deepmask_gpr | existing_fold_p2 | image_metadata_extra_trees | pixel32_extra_trees | True |
| deepmask_gpr | source_group_holdout_70_15_15 | image_metadata_extra_trees | pixel32_extra_trees | True |
| deepmask_gpr | provenance_size_holdout_p4 | image_metadata_extra_trees | pixel32_extra_trees | True |
| deepmask_gpr | datasail_like_group_balance | image_metadata_extra_trees | pixel32_extra_trees | True |

## Boundary

This is a local lightweight five-family matrix. It strengthens split
and model-selection sensitivity evidence, but it is not a deep-backbone
replacement for ResNet/DeiT training and does not close blind external
validation.
