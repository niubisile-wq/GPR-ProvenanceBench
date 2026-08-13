# Reporting Summary finalization prelock 2026-08-10

This package turns the Reporting Summary draft into a finalization-control artifact. It does not make the Reporting Summary final.

## Use

1. Use `reporting_summary_final_lock_matrix.csv` to decide which fields can be finalized after evidence arrives.
2. Use `reporting_summary_author_confirmation_checklist.csv` for author/external confirmations.
3. Use `reporting_summary_forbidden_final_wording.csv` to prevent protocol-only or local-only evidence from becoming final submission claims.

## Stop rules

1. Do not mark blinding complete before a real external asset, label holdout and frozen prediction submission exist.
2. Do not mark data/code availability complete before DOI/accession, licence and rights clearance exist.
3. Do not mark figure/source-data fields complete before final rendered figures and panel-level Source Data exist.
4. Do not mark Reporting Summary final while any high-risk field remains blocked.
