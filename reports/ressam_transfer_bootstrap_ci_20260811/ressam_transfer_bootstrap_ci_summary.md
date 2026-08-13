# Res-SAM Transfer Delta Bootstrap CI

Bootstrap draws per contrast: `10000`
Bootstrap unit: model family delta rows from the five-model synthesis.

| contrast | models | mean delta | 95% CI | positive fraction | material fraction >=0.05 |
| --- | ---: | ---: | ---: | ---: | ---: |
| within_minus_transfer_synthetic_to_real_world | 5 | 0.3743 | [0.1721, 0.5470] | 0.9997 | 0.9997 |
| within_minus_transfer_real_world_to_synthetic | 5 | 0.4239 | [0.2963, 0.5516] | 1.0000 | 1.0000 |

Boundary: this is a cross-model-family uncertainty check over the
current five local model-family deltas. It is not a sample-level
external validation interval.
