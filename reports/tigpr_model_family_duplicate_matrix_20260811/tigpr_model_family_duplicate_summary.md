# TIGPR Model-Family Duplicate Matrix

Samples: `7169`
Seeds: `[20260811, 20260812, 20260813, 20260814, 20260815]`
Material-support threshold: `0.05` balanced accuracy.

## Model-Family Summary

| model_family | random BA | group BA | random-minus-group BA | material support |
| --- | ---: | ---: | ---: | --- |
| hog_logistic_sgd | 0.7314 | 0.6777 | 0.0537 | True |
| pixel_logistic_sgd | 0.4752 | 0.4009 | 0.0743 | True |
| metadata_logistic_sgd | 0.6175 | 0.6417 | -0.0241 | False |
| hog_metadata_logistic_sgd | 0.7749 | 0.7192 | 0.0558 | True |
| hog_extra_trees | 0.7860 | 0.7037 | 0.0823 | True |

## Claim Summary

- Directional support: `4/5`
- Material support: `4/5`
- Mean delta across model families: `0.0484`
- Claim status: `supported`

Boundary: TIGPR is restored local evidence. This matrix tests duplicate
isolation and model-family dependence; it does not satisfy blind external
validation because the asset and labels are visible locally.
