# 4TU Task-Source Association Audit

Permutation draws per complete pair: `1000`

| target | source | feasibility | samples | labels | source classes | NMI | Cramer's V | MI p | mean purity |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Land type | project_id | usable_with_caution | 93 | 4 | 9 | 0.2794 | 0.5141 | 0.0010 | 0.6881 |
| Land type | split_role | usable_with_caution | 93 | 4 | 3 | 0.0622 | 0.2262 | 0.0639 | 0.4599 |
| Land use | project_id | not_viable_for_group_holdout | 93 | 5 | 9 | 0.6461 | 0.9202 | 0.0010 | 0.9444 |
| Land use | split_role | not_viable_for_group_holdout | 93 | 5 | 3 | 0.5625 | 0.7362 | 0.0010 | 0.7623 |
| Land cover | project_id | weak_due_to_single_project_labels | 93 | 4 | 9 | 0.3368 | 0.5504 | 0.0010 | 0.7159 |
| Land cover | split_role | weak_due_to_single_project_labels | 93 | 4 | 3 | 0.0266 | 0.1521 | 0.5864 | 0.4256 |
| Utility crossing | project_id | usable_with_caution | 84 | 2 | 9 | 0.0334 | 0.2308 | 0.7942 | 0.9448 |
| Utility crossing | split_role | usable_with_caution | 84 | 2 | 3 | 0.0029 | 0.0585 | 0.8701 | 0.9341 |
| Construction workers | project_id | not_viable_for_group_holdout | 93 | 4 | 9 | 0.7095 | 1.0000 | 0.0010 | 1.0000 |
| Construction workers | split_role | not_viable_for_group_holdout | 93 | 4 | 3 | 0.4252 | 0.6875 | 0.0010 | 0.5574 |
| Relative groundwater level | project_id | weak_due_to_single_project_labels | 93 | 3 | 9 | 0.1841 | 0.4880 | 0.0010 | 0.8848 |
| Relative groundwater level | split_role | weak_due_to_single_project_labels | 93 | 3 | 3 | 0.1249 | 0.2704 | 0.0020 | 0.7679 |

Boundary: this uses 4TU task-level metadata labels, not pixel-level or
trace-level target annotations. It strengthens the feasibility-boundary
audit and should not be promoted to main confirmation evidence.
