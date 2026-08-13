# NatComms 19.53 External Dependency Escalation

# External dependency escalation email

Subject: Required evidence and decisions before GPR-ProvenanceBench can re-enter final checks

Dear team,

The current 2026-08-10 NatComms package is internally auditable, but the final
submission gate is blocked. Please provide the following evidence or decisions.

1. Author sendout evidence: sent time, sender account, recipient list, sent
   packet path and SHA256, and immutable send-log evidence.
2. Four author/advisor decisions: figure backend, external blind asset
   availability, licence direction, and Track B fallback if no real external
   asset is available.
3. Real returned evidence files in the canonical inbox routes, with source
   identity, timestamp and SHA256 provenance.
4. Figure 1-Figure 6 author review decisions: approve, revise or reject, with
   comments for any revision.
5. Repository/rights/DOI decisions: repository DOI/accession, code DOI, licence
   route, third-party rights decision and exclusion list.

Do not upload portal files or mark the manuscript submission-ready. After the
above receipts are complete, the guarded launcher will decide whether the final
M0-M2 recheck can run.

Best,
[Author]


## Request Matrix

### FMR-001 - corresponding_author

- Send now: yes
- Request: sent_datetime_local, sender account, recipient list, sent packet path, sent packet SHA256, immutable send log path
- Target or route: `reports/natcomms_author_response_tracker_20260810/author_response_send_log_template.csv`
- Acceptance test: email_sent=true and author response log validator passes
- First validator: `py scripts/build_natcomms_author_response_log_validator.py`

### FMR-002 - author_and_advisor

- Send now: yes
- Request: backend choice, external asset decision, licence direction, Track B fallback decision, decision timestamp
- Target or route: `reports/author_decision_closure_packet_v2_20260810/author_decision_closure_form_v2.csv`
- Acceptance test: all four author decision rows resolved with accepted values
- First validator: `py scripts/build_manual_evidence_final_intake_validator.py`

### FMR-003 - author_or_data_holder

- Send now: yes
- Request: canonical folder, file name, SHA256, source identity, timestamp and operator attestation
- Target or route: `final_return_evidence_inbox_20260810/ plus rb001 receipt template`
- Acceptance test: candidate_return_files > 0 and scanner/hash reconciliation passes
- First validator: `py scripts/build_final_return_evidence_intake_scanner.py`

### FMR-004 - figure_owner_and_author_team

- Send now: yes
- Request: Figure 1-Figure 6 approve/revise/reject decision, reviewer identity and comments
- Target or route: `reports/python_figure_author_review_packet_20260810/python_figure_author_review_form.csv`
- Acceptance test: required figure rows approved or revision queue explicitly accepted
- First validator: `py scripts/build_python_figure_author_review_intake_validator.py`

### FMR-005 - repository_or_rights_owner

- Send now: yes
- Request: repository DOI/accession, code DOI, licence, third-party rights decision and exclusion list
- Target or route: `repository_predeposit_handoff and rights_licence_completion_handoff`
- Acceptance test: final_availability_ready=true and rights blockers closed
- First validator: `py scripts/build_availability_repository_finalization_validator.py`

### FMR-006 - manuscript_operator

- Send now: no
- Request: completed receipt IDs FMR-001 to FMR-005, M0-M2 log path, exit code and summary of changed gates
- Target or route: `reports/latest_run_m0_m2_checks_20260810.log`
- Acceptance test: M0-M2 passes after real evidence without portal upload
- First validator: `powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1`
