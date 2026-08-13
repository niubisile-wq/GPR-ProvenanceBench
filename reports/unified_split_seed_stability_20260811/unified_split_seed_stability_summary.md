# Unified Split Seed Stability

Five SGD-logistic seeds are evaluated for every unified split.

| dataset | protocol | BA mean | BA std | random - protocol BA mean | delta min | delta max |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| mojahid | random_stratified_70_15_15 | 0.8373 | 0.0106 | +0.0000 | +0.0000 | +0.0000 |
| mojahid | existing_fold_p2 | 0.7607 | 0.0140 | +0.0766 | +0.0612 | +0.0896 |
| mojahid | source_group_holdout_70_15_15 | 0.7283 | 0.0177 | +0.1091 | +0.0808 | +0.1321 |
| mojahid | provenance_size_holdout_p4 | 0.6902 | 0.0137 | +0.1472 | +0.1116 | +0.1670 |
| mojahid | datasail_like_group_balance | 0.7283 | 0.0177 | +0.1091 | +0.0808 | +0.1321 |
| tigpr | random_stratified_70_15_15 | 0.7135 | 0.0096 | +0.0000 | +0.0000 | +0.0000 |
| tigpr | existing_fold_p2 | 0.7174 | 0.0016 | -0.0039 | -0.0124 | +0.0110 |
| tigpr | source_group_holdout_70_15_15 | 0.7003 | 0.0082 | +0.0132 | +0.0084 | +0.0190 |
| tigpr | provenance_size_holdout_p4 | 0.6483 | 0.0075 | +0.0652 | +0.0516 | +0.0768 |
| tigpr | datasail_like_group_balance | 0.7003 | 0.0082 | +0.0132 | +0.0084 | +0.0190 |
| zenodo_14637589 | random_stratified_70_15_15 | 0.8941 | 0.0053 | +0.0000 | +0.0000 | +0.0000 |
| zenodo_14637589 | existing_fold_p2 | 0.8687 | 0.0092 | +0.0254 | +0.0163 | +0.0333 |
| zenodo_14637589 | source_group_holdout_70_15_15 | 0.8375 | 0.0151 | +0.0566 | +0.0279 | +0.0783 |
| zenodo_14637589 | provenance_size_holdout_p4 | 0.6145 | 0.0189 | +0.2796 | +0.2585 | +0.3055 |
| zenodo_14637589 | datasail_like_group_balance | 0.8375 | 0.0151 | +0.0566 | +0.0279 | +0.0783 |
| deepmask_gpr | random_stratified_70_15_15 | 0.8825 | 0.0069 | +0.0000 | +0.0000 | +0.0000 |
| deepmask_gpr | existing_fold_p2 | 0.7661 | 0.0026 | +0.1163 | +0.1116 | +0.1265 |
| deepmask_gpr | source_group_holdout_70_15_15 | 0.7601 | 0.0061 | +0.1224 | +0.1137 | +0.1306 |
| deepmask_gpr | provenance_size_holdout_p4 | 0.7661 | 0.0026 | +0.1163 | +0.1116 | +0.1265 |
| deepmask_gpr | datasail_like_group_balance | 0.7601 | 0.0061 | +0.1224 | +0.1137 | +0.1306 |

## Boundary

This is local seed stability for a lightweight baseline. It does not
replace full deep-model seed sweeps or blind external validation.
