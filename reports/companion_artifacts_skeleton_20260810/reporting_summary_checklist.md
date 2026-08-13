# Reporting Summary Checklist Skeleton 2026-08-10

Purpose: identify Nature-style reporting fields that must be resolved before submission.

| item | current status | evidence | missing before submission | risk |
| --- | --- | --- | --- | --- |
| Study design | partial | Results/Methods skeletons define asset audit, split/transfer contrasts and gates. | Final manuscript framing and exact article type. | medium |
| Sample size and exclusions | partial | Unified manifests record executable rows: Mojahid 2524, 4TU 99, Res-SAM 1050, TIGPR 0. | Final inclusion/exclusion criteria and dataset licence constraints for each source. | medium |
| Randomization and split strategy | partial | Current Results skeleton distinguishes random, grouped and environment-transfer contrasts. | Frozen split manifests for every final figure and exact seed table. | medium |
| Blinding | protocol_only | Blind external validation protocol, templates and locked evaluator dry run exist. | Real external asset with label holdout, strict-SHA manifest and one-shot prediction submission. | high |
| Statistical analysis | partial | Current source packages report balanced accuracy deltas, support counts and feasibility status. | Final statistical test plan, uncertainty intervals and multiple-comparison policy where applicable. | medium |
| Software and code availability | local_only | Scripts and run_m0_m2_checks.ps1 regenerate current M0-M2 artifacts. | Public repository URL, release tag, archive DOI, licence and README. | high |
| Data availability | local_only | Derived manifests and figure/table source data exist locally. | Repository DOI/accession, dataset README, licence, source-data mapping and third-party data source citations. | high |
| External validation | not_ready | External validation readiness gate is NO-GO. | Acquire or restore external asset and run the locked evaluation after label unlock. | high |

## Blocking Items

1. Data Availability is not submission-ready because no persistent repository identifier exists.
2. Code Availability is not submission-ready because no public release DOI exists.
3. Blinding is protocol-ready only; no real blind external validation asset has passed strict-SHA intake.
4. Final figure files and source-data panel mapping are not complete.
