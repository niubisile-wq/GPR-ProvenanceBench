# Data Availability Skeleton 2026-08-10

Ready-to-paste status: not ready. Persistent repository identifiers are missing.

## Draft Statement

The derived sample manifests, figure source data, table source data, external-validation templates and reproducibility metadata generated for this study will be deposited in [REPOSITORY] under [DOI/accession] before submission. The deposited record should include the unified sample manifests, figure/table source-data files, benchmark reports, protocol files, environment metadata and a README mapping each file to the corresponding manuscript figure, table or Methods module. Public or third-party GPR datasets reused in the analysis, including Mojahid, 4TU, Res-SAM and TIGPR-related records, should be accessed from their original providers under their respective licences and cited with verified dataset identifiers. The current external blind-validation asset is not yet available; no data supporting a completed blind external-validation claim exist at this checkpoint.

## Repository and Citation Actions

1. Create a durable repository record for derived benchmark artifacts and source data.
2. Add a dataset README with file descriptions, columns, units, checksums where relevant and figure/table mapping.
3. Verify original source identifiers, licences and redistribution rights for Mojahid, 4TU, Res-SAM and TIGPR before final wording.
4. Add formal DataCite-style dataset citations after repository records are created.
5. Do not use temporary cloud links or local Baidu/desktop paths as the only availability route.

## Inventory

| id | dataset | supports | route | identifier status | note |
| --- | --- | --- | --- | --- | --- |
| D1 | Unified sample manifests | Figure 1; Table 1; asset boundary | public repository planned | missing_persistent_identifier | Contains derived sample metadata and local paths; local absolute paths should be sanitized or replaced with relative/deposit paths before public release. |
| D2 | Figure and table source data | Figures 1-6; Tables 1-3 | public repository planned | missing_persistent_identifier | Ready as derived source data; final rendered figure source files still depend on plotting backend selection. |
| D3 | Reused public or third-party GPR datasets | Mojahid, 4TU, Res-SAM and TIGPR asset context | reused public source or third-party restricted | source_identifiers_need_verification | Dataset-specific licences, official URLs, versions and redistribution rights must be verified before submission. |
| D4 | External blind validation asset | Future Figure 6 or main external validation claim | not applicable yet | not_started | Current gate is NO-GO; no statement may claim completed blind external validation. |
| D5 | Environment and reproducibility metadata | Reproducibility checks; Methods M7 | public repository planned | missing_persistent_identifier | Current environment is CPU/Python 3.12 for M0-M2 checks; not a full final training environment. |

## Chinese Author Check

1. 不能写“数据可向通讯作者索取”作为主要方案，除非有明确限制原因和机构化申请流程。
2. 不能写“所有数据都在文中”，因为当前还需要 figure/table source data 和代码仓库记录。
3. 不能伪造 DOI、accession number、仓库名或 licence。
4. 当前只能写 derived artifacts will be deposited，不应写 have been deposited，除非真实仓库记录已经创建。
