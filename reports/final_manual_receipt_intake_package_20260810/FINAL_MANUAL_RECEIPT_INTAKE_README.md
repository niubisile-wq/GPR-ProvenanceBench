# NatComms 19.49 Final Manual Receipt Intake

Purpose: collect real human receipts for the 19.48 manual-only actions.

Current state: no receipt is complete. Portal upload, system execution and submission-ready remain forbidden.

## Receipt Rows

### FMR-001 - author_sendout_evidence

- Owner: corresponding_author
- Required evidence: sent_datetime_local, sender account, recipient list, sent packet path, sent packet SHA256, immutable send log path
- Target or route: `reports/natcomms_author_response_tracker_20260810/author_response_send_log_template.csv`
- Acceptance test: email_sent=true and author response log validator passes
- First validator: `py scripts/build_natcomms_author_response_log_validator.py`
- Current status: missing

### FMR-002 - author_decision_values

- Owner: author_and_advisor
- Required evidence: backend choice, external asset decision, licence direction, Track B fallback decision, decision timestamp
- Target or route: `reports/author_decision_closure_packet_v2_20260810/author_decision_closure_form_v2.csv`
- Acceptance test: all four author decision rows resolved with accepted values
- First validator: `py scripts/build_manual_evidence_final_intake_validator.py`
- Current status: missing

### FMR-003 - real_returned_evidence_drop

- Owner: author_or_data_holder
- Required evidence: canonical folder, file name, SHA256, source identity, timestamp and operator attestation
- Target or route: `final_return_evidence_inbox_20260810/ plus rb001 receipt template`
- Acceptance test: candidate_return_files > 0 and scanner/hash reconciliation passes
- First validator: `py scripts/build_final_return_evidence_intake_scanner.py`
- Current status: missing

### FMR-004 - figure_author_review_decisions

- Owner: figure_owner_and_author_team
- Required evidence: Figure 1-Figure 6 approve/revise/reject decision, reviewer identity and comments
- Target or route: `reports/python_figure_author_review_packet_20260810/python_figure_author_review_form.csv`
- Acceptance test: required figure rows approved or revision queue explicitly accepted
- First validator: `py scripts/build_python_figure_author_review_intake_validator.py`
- Current status: missing

### FMR-005 - repository_rights_doi_decisions

- Owner: repository_or_rights_owner
- Required evidence: repository DOI/accession, code DOI, licence, third-party rights decision and exclusion list
- Target or route: `repository_predeposit_handoff and rights_licence_completion_handoff`
- Acceptance test: final_availability_ready=true and rights blockers closed
- First validator: `py scripts/build_availability_repository_finalization_validator.py`
- Current status: missing

### FMR-006 - guarded_recheck_receipt

- Owner: manuscript_operator
- Required evidence: completed receipt IDs FMR-001 to FMR-005, M0-M2 log path, exit code and summary of changed gates
- Target or route: `reports/latest_run_m0_m2_checks_20260810.log`
- Acceptance test: M0-M2 passes after real evidence without portal upload
- First validator: `powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1`
- Current status: waiting_for_FMR_001_to_FMR_005

## No-go Rules

- Do not replace placeholders unless the evidence exists on disk or in an inspectable send/decision record.
- Do not run writeback, transition, portal upload or submission commands from this template.
- Do not mark any receipt complete without SHA256/source/timestamp where required.
- Do not claim `submission_ready=true` unless 19.47 later reports it.
