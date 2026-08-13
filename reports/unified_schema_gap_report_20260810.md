# Unified Schema Gap Report 2026-08-10

This report checks current sample indexes against the frozen unified schema.

## mojahid

Source: `manifest\mojahid_sample_index_v1.csv`

Current field count: 15
Unified schema field count: 32
Missing field count: 23
Extra field count: 6

Missing fields:

- `asset_role`
- `label_source`
- `file_sha256`
- `raw_trace_id`
- `project_id`
- `activity_id`
- `site_id`
- `survey_line_id`
- `device_id`
- `antenna_frequency_mhz`
- `acquisition_date`
- `operator_id`
- `processing_chain_id`
- `export_format`
- `augmentation_ancestor_id`
- `exact_duplicate_group`
- `near_duplicate_group`
- `source_group`
- `split_protocol`
- `split_role`
- `created_by`
- `created_date`
- `notes`

Extra fields:

- `path_verified`
- `split_group`
- `source_role`
- `mode`
- `size_bytes`
- `sha256`

## tigpr

Source: `manifest\tigpr_sample_index_v1.csv`

Current field count: 15
Unified schema field count: 32
Missing field count: 23
Extra field count: 6

Missing fields:

- `asset_role`
- `label_source`
- `file_sha256`
- `raw_trace_id`
- `project_id`
- `activity_id`
- `site_id`
- `survey_line_id`
- `device_id`
- `antenna_frequency_mhz`
- `acquisition_date`
- `operator_id`
- `processing_chain_id`
- `export_format`
- `augmentation_ancestor_id`
- `exact_duplicate_group`
- `near_duplicate_group`
- `source_group`
- `split_protocol`
- `split_role`
- `created_by`
- `created_date`
- `notes`

Extra fields:

- `path_verified`
- `split_group`
- `source_role`
- `mode`
- `size_bytes`
- `sha256`
