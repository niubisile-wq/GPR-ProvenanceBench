# Figure 2 and Table 2 Source Data 2026-08-10

Purpose: freeze the source data for the current strongest manuscript claim before plotting.

Main claim: Res-SAM environment-transfer fragility has stronger cross-model support than Mojahid random-minus-grouped split inflation.

Boundary: this source package excludes 4TU and true blind external validation. It must not be used to claim completed external blind validation.

## Figure 2 Source Data

| contrast | model | delta BA | directional | material |
| --- | --- | ---: | --- | --- |
| Mojahid: random - grouped | HOG + RBF-SVM | 0.0976 | yes | yes |
| Res-SAM: within synthetic - synthetic->real | HOG + RBF-SVM | 0.4117 | yes | yes |
| Res-SAM: within real - real->synthetic | HOG + RBF-SVM | 0.5556 | yes | yes |
| Mojahid: random - grouped | LBP + LinearSVM | 0.0365 | yes | no |
| Res-SAM: within synthetic - synthetic->real | LBP + LinearSVM | 0.3083 | yes | yes |
| Res-SAM: within real - real->synthetic | LBP + LinearSVM | 0.2356 | yes | yes |
| Mojahid: random - grouped | TinyCNN | 0.0098 | yes | no |
| Res-SAM: within synthetic - synthetic->real | TinyCNN | -0.0103 | no | no |
| Res-SAM: within real - real->synthetic | TinyCNN | 0.2907 | yes | yes |
| Mojahid: random - grouped | ResNet18 emb. + LinearSVM | 0.0250 | yes | no |
| Res-SAM: within synthetic - synthetic->real | ResNet18 emb. + LinearSVM | 0.5783 | yes | yes |
| Res-SAM: within real - real->synthetic | ResNet18 emb. + LinearSVM | 0.4289 | yes | yes |
| Mojahid: random - grouped | EfficientNetB0 emb. + LinearSVM | 0.0340 | yes | no |
| Res-SAM: within synthetic - synthetic->real | EfficientNetB0 emb. + LinearSVM | 0.5833 | yes | yes |
| Res-SAM: within real - real->synthetic | EfficientNetB0 emb. + LinearSVM | 0.6089 | yes | yes |

## Table 2 Manuscript Draft

| dataset | contrast | directional support | material support | mean delta BA | delta range BA | status | interpretation |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| Mojahid | Mojahid: random - grouped | 5/5 | 1/5 | 0.0406 | 0.0098 to 0.0976 | directional_only | Directional but modest/model-dependent split effect; do not frame as a universal inflation result. |
| Res-SAM | Res-SAM: within real - real->synthetic | 5/5 | 5/5 | 0.4239 | 0.2356 to 0.6089 | supported | Strong material support for real-to-synthetic environment-transfer fragility. |
| Res-SAM | Res-SAM: within synthetic - synthetic->real | 4/5 | 4/5 | 0.3743 | -0.0103 to 0.5833 | supported | Strong material support for synthetic-to-real environment-transfer fragility, with one model-family exception. |

## Plotting Notes

1. Lead panel: model-family delta balanced accuracy for the three contrasts.
2. Use a clear material-support threshold line at 0.05 balanced accuracy.
3. Encode unsupported or negative TinyCNN synthetic-to-real result distinctly.
4. Keep Mojahid visually secondary to avoid overstating the split gap.
