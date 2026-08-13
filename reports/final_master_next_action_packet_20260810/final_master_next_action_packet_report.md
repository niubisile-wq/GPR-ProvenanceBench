# NatComms 19.48 Final Next Actions

Source of truth: `reports/final_submission_master_dependency_bridge_validator_20260810/`.

Current state: final submission is blocked. Do not upload portal files or mark the manuscript submission-ready.

## Allowed Human Actions

### 1. Send the author decision closure packet and capture send evidence.

- Owner: corresponding_author
- Required input: Email/message sent to coauthors or advisor with decision packet attached or pasted.
- Acceptance test: email_sent=true, immutable send log recorded, and sent packet checksum retained.
- Recheck: `py scripts/build_natcomms_author_response_log_validator.py`

### 2. Return four required decisions: figure backend, external asset availability, licence direction and Track B fallback.

- Owner: author_and_advisor
- Required input: Nonblank accepted values for all four decision rows.
- Acceptance test: decision_rows=0 unresolved and blank_author_reply_fields=0 after intake.
- Recheck: `py scripts/build_manual_evidence_final_intake_validator.py`

### 3. Place real returned evidence files into the canonical return/RB-001 inbox routes.

- Owner: author_or_data_holder
- Required input: Returned files with source identity, timestamps and SHA256 provenance.
- Acceptance test: candidate_return_files > 0 and scanner/hash manifest reconciliation passes.
- Recheck: `py scripts/build_final_return_evidence_intake_scanner.py`

### 4. Collect Figure 1-Figure 6 approve/revise/drop decisions before final candidate generation.

- Owner: figure_owner_and_author_team
- Required input: Six figure review rows with accepted decision values and comments for revisions.
- Acceptance test: approved_rows covers required figures and final_candidate_generation_allowed=true.
- Recheck: `py scripts/build_python_figure_author_review_intake_validator.py`

### 5. Resolve repository DOI, code DOI, licence and third-party rights direction.

- Owner: repository_or_rights_owner
- Required input: Repository/accession identifiers, release licence and rights-clearance decisions.
- Acceptance test: final_availability_ready=true and portal files are no longer skeleton-only.
- Recheck: `py scripts/build_availability_repository_finalization_validator.py`

### 6. After decisions and evidence return, rerun only the guarded validation sequence, not portal upload.

- Owner: manuscript_operator
- Required input: Completed actions 1-5 plus accepted manual evidence receipts.
- Acceptance test: 19.47 changes only after upstream validators report zero open gates.
- Recheck: `powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1`

## Forbidden Until 19.47 Passes

- Upload any file to the Nature Communications portal. Reason: portal_upload_ready=false and portal_file_upload_allowed_rows=0.
- Mark the manuscript submission-ready. Reason: final_submission_master_allowed=false and submission_ready=false.
- Close master gates or residual blockers manually. Reason: open_master_gates=8 and ready_to_close_rows=0.
- Run route/writeback/transition commands as if evidence were present. Reason: candidate_return_files=0 and writeback/transition remain blocked.
- Replace open-gate language with final external-validation claims. Reason: real blind external validation remains NO-GO.

## Final Recheck

After real evidence and replies are present, rerun:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_m0_m2_checks.ps1
```

Submission is still false unless 19.47 reports `final_submission_master_allowed=true` and `submission_ready=true`.
