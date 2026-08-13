# Target-Source Association Audit

Permutation draws per complete task: `1000`

| task | samples | target classes | source classes | NMI | Cramer's V | MI permutation p | mean source purity | pure source groups |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mojahid_label_vs_source_group | 2524 | 3 | 692 | 0.2514 | 0.8724 | 0.0010 | 0.9796 | 0.9465 |
| mojahid_label_vs_processing_role | 2524 | 3 | 2 | 0.1079 | 0.4265 | 0.0010 | 0.5749 | 0.0000 |
| ressam_label_vs_environment | 1050 | 6 | 2 | 0.1699 | 0.5477 | 0.0010 | 0.2500 | 0.0000 |
| four_tu_label_vs_project | 0 | 0 | 0 | NA | NA | NA | NA | NA |

Boundary: this is a manifest-level target-source coupling audit. It
quantifies label/source association but does not prove external
generalization or causal mechanism by itself.
