# Reporting Summary draft 2026-08-10

Draft boundary: this is a pre-submission draft based on current checkpoint artifacts. It is not a final Nature Reporting Summary because blind external validation, rendered figures, repository identifiers, licence, rights and final source-data mapping remain open.

## Draft answers

### Study design

The current checkpoint is a provenance-aware benchmark workflow for GPR recognition. It separates executable local asset evidence from unresolved confirmation gates and reports split, environment-transfer and counterfactual stress-test contrasts.

Evidence anchor: M1; M2; M6; manuscript assembly skeleton.

Status: `draft_answer_ready_not_final`. Risk: `medium`.

Missing before submission: Final article framing and final figure/table set.

### Sample size and exclusions

Local executable rows are Mojahid 2524, 4TU 99 and Res-SAM 1050. TIGPR has 0 local executable rows and is supporting-only at this checkpoint.

Evidence anchor: M1; Table 1; unified manifests.

Status: `draft_answer_ready_not_final`. Risk: `medium`.

Missing before submission: Final inclusion/exclusion criteria and third-party licence boundaries for each asset.

### Randomization and split strategy

The benchmark distinguishes random stratified, grouped and environment-transfer protocols. Mojahid compares random and grouped splits; Res-SAM compares within-environment and cross-environment transfer; 4TU stress tests include fixed-split and project-level repeated-split layers.

Evidence anchor: M2; M4; Figure 2; Figure 3; Figure 4.

Status: `draft_answer_ready_not_final`. Risk: `medium`.

Missing before submission: Frozen split manifests and exact seed table for every final figure.

### Blinding

No completed blind external validation exists. A protocol, analyst-facing manifest template, label-holdout template, one-shot submission template, intake validator and locked evaluator are available, but no real external asset has passed strict intake.

Evidence anchor: M6; external validation readiness; blind external acquisition package.

Status: `protocol_only_not_final`. Risk: `high`.

Missing before submission: Real external asset, strict-SHA manifest, label holdout, frozen prediction submission, label unlock and one-shot locked evaluation.

### Statistical analysis

Current analyses report balanced accuracy, delta balanced accuracy, directional support, material support counts, feasibility states and stress-test sensitivity summaries. The material-support threshold is 0.05 delta balanced accuracy in the five-model synthesis.

Evidence anchor: M3; M4; M5; Figure 2-5 source data.

Status: `draft_answer_ready_not_final`. Risk: `medium`.

Missing before submission: Final uncertainty interval policy, final statistical test plan and multiple-comparison policy if inferential tests are added.

### Software and code availability

Current scripts regenerate checkpoint artifacts through run_m0_m2_checks.ps1 using the local Python environment. Public code repository URL, release tag, archive DOI and software licence are not yet available.

Evidence anchor: M7; repository metadata package; code availability draft.

Status: `local_only_not_final`. Risk: `high`.

Missing before submission: Public repository URL, release tag, archive DOI, software licence and final figure-generation backend.

### Data availability

Derived manifests, source-data tables, protocol files and audit artifacts exist locally and in sanitized staging preview. Data repository DOI/accession, final Source Data, licence decision and third-party rights review are not yet complete.

Evidence anchor: source-data deposit package; repository metadata package; release readiness audit.

Status: `local_only_not_final`. Risk: `high`.

Missing before submission: Repository DOI/accession, dataset README, licence, final source-data mapping and third-party data source citations.

### External validation

External validation readiness remains NO-GO. Existing external-blind scripts and templates validate structure only and do not constitute a real blind external result.

Evidence anchor: external validation readiness; Figure 6 source data; blind external acquisition package.

Status: `not_ready`. Risk: `high`.

Missing before submission: Acquire or restore a separate blind external asset and run the locked evaluation after label unlock.

## Chinese check

这份 Reporting Summary 只能作为预填草案。不能把 protocol_only、local_only 或 not_ready 项写成 final ready。尤其是 blinding/external validation、Data Availability、Code Availability 仍是高风险未闭合项。
