# NatComms 19.86 Manual Execution Brief

Current status: only real human evidence actions are allowed.

Allowed now:

001. FMR-001 / external_sendout
- Do now: Send the external dependency packages through the real human channel and capture complete send receipts.
- Put evidence here: `manual_evidence/external_dependency_sendout_20260810`
- Fill form: `reports/manual_only_execution_forms_20260810/forms/MOF-001_external_sendout.csv`
- Proof required: sender, recipient, timestamp, message subject/body hash and attachment SHA256 values
- After evidence: run 19.84 validation first; downstream validator remains blocked until the form passes

002. FMR-002 / author_decisions
- Do now: Collect backend, scope and rights/licence decisions from the author or responsible owner.
- Put evidence here: `manual_evidence_inbox_20260810`
- Fill form: `reports/manual_only_execution_forms_20260810/forms/MOF-002_author_decisions.csv`
- Proof required: signed or attributable decision record, date and selected options
- After evidence: run 19.84 validation first; downstream validator remains blocked until the form passes

003. FMR-003 / returned_files
- Do now: Place returned author reply files and external-blind payloads into the mapped return inbox.
- Put evidence here: `final_return_evidence_inbox_20260810`
- Fill form: `reports/manual_only_execution_forms_20260810/forms/MOF-003_returned_files.csv`
- Proof required: returned files, source route, checksum manifest and no sensitive label/answer leakage
- After evidence: run 19.84 validation first; downstream validator remains blocked until the form passes

004. FMR-004 / figure_approval
- Do now: Complete figure author review decisions for Figure 1 through Figure 6.
- Put evidence here: `reports/python_figure_author_review_return_inbox_20260810/returned_author_review_files`
- Fill form: `reports/manual_only_execution_forms_20260810/forms/MOF-004_figure_approval.csv`
- Proof required: figure-level approval/revision/rejection decision and attributable comments
- After evidence: run 19.84 validation first; downstream validator remains blocked until the form passes

005. FMR-005 / repository_rights_doi
- Do now: Finalize repositories, DOI records, licence selection and third-party rights clearance.
- Put evidence here: `final_return_evidence_inbox_20260810/04_repository_rights_doi`
- Fill form: `reports/manual_only_execution_forms_20260810/forms/MOF-005_repository_rights_doi.csv`
- Proof required: repository DOI, code DOI if applicable, licence, rights clearance and availability wording
- After evidence: run 19.84 validation first; downstream validator remains blocked until the form passes

Hard no-go commands:
- Do not run any --execute-writeback command. Reason: ready_for_writeback_rows=0.
- Do not run downstream validators from incomplete forms. Reason: ready_for_downstream_validator_rows=0.
- Do not run guarded recheck. Reason: complete_receipt_rows=0.
- Do not upload portal files or mark submitted. Reason: submission_ready=false.

Boundary: this brief does not send messages, create evidence, run validators, execute writeback, run recheck, upload portal files or submit.
