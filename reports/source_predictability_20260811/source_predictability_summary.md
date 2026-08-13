# Source Predictability Sweep

Runs per task: `5`

| task | samples | classes | balanced accuracy | chance BA | accuracy | majority acc | macro-F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mojahid_processing_role_is_augmented | 2524 | 2 | 0.6010 | 0.5000 | 0.6319 | 0.7112 | 0.5877 |
| mojahid_augmentation_lineage_source_group | 1126 | 80 | 0.6079 | 0.0125 | 0.6006 | 0.0187 | 0.5995 |
| ressam_environment_source_group | 1050 | 2 | 0.9926 | 0.5000 | 0.9930 | 0.5714 | 0.9929 |

Boundary: these are internal source-signal probes. They show whether
provenance or processing lineage is learnable from images, but they do
not measure blind external generalization.
