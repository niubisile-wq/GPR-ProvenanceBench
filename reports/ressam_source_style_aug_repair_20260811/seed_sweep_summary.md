# Res-SAM Source-Side Style Augmentation Repair

Runs: `40`

| transfer | raw baseline | best aug test mode | best aug bal acc | best delta |
| --- | ---: | --- | ---: | ---: |
| synthetic_to_real_world | 0.4367 | source_style_aug_to_per_image_equalized_target | 0.4267 | -0.0100 |
| real_world_to_synthetic | 0.3511 | source_style_aug_to_raw_target | 0.3400 | -0.0111 |

Boundary: source-style augmentation only uses source-domain labels and
per-image deterministic transforms. It does not inspect target-domain
batch statistics, but it is still internal evidence because Res-SAM is
already part of local model development.
