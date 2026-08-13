# Sanitized Release Staging Preview 2026-08-10

This directory is a local preview of derived artifacts that passed the release-readiness audit's `candidate_after_licence` filter.

It is not a public release. It has no DOI, no selected licence and no verified third-party rights record.

## Scope

- Staged files: 37
- Categories: claim_evidence_plan, companion_artifact_skeleton, figure_table_source_data, methods_skeleton, reproducibility_script, results_skeleton, submission_skeleton
- Excluded by design: unified sample manifests, protocols, files containing local path markers, files containing repository/DOI placeholders and third-party raw data.

## Files

See `sanitized_release_manifest.csv` for staged paths, SHA256 checksums and marker scan results.

## Required Before Public Release

1. Choose and apply a licence after institutional review.
2. Create public repository metadata and DOI/accession.
3. Verify third-party data rights and official citations.
4. Add final rendered figures and panel-level source-data mapping.
5. Re-run `run_m0_m2_checks.ps1` after any source-data change.
