# NatComms 19.90 Daily Execution Status Capsule

Current decision: do not run system validation, writeback, recheck, portal upload or submission.

Allowed now:
- MOF-001 / FMR-001 / external_sendout: Send the external dependency packages through the real human channel and capture complete send receipts.
- MOF-002 / FMR-002 / author_decisions: Collect backend, scope and rights/licence decisions from the author or responsible owner.
- MOF-003 / FMR-003 / returned_files: Place returned author reply files and external-blind payloads into the mapped return inbox.
- MOF-004 / FMR-004 / figure_approval: Complete figure author review decisions for Figure 1 through Figure 6.
- MOF-005 / FMR-005 / repository_rights_doi: Finalize repositories, DOI records, licence selection and third-party rights clearance.

Blocked commands:
- py scripts/validate_manual_only_execution_forms_20260810.py [MOF-001]: candidate_files=0; filled_cells=0/10
- py scripts/validate_manual_only_execution_forms_20260810.py [MOF-002]: candidate_files=0; filled_cells=0/10
- py scripts/validate_manual_only_execution_forms_20260810.py [MOF-003]: candidate_files=0; filled_cells=0/10
- py scripts/validate_manual_only_execution_forms_20260810.py [MOF-004]: candidate_files=0; filled_cells=0/10
- py scripts/validate_manual_only_execution_forms_20260810.py [MOF-005]: candidate_files=0; filled_cells=0/10
- any --execute-writeback [GLOBAL]: no downstream validation/preflight candidate is allowed
- guarded recheck, portal upload or submission [GLOBAL]: manual evidence incomplete and submission_ready=false

Status numbers:
- manual_action_queue_rows=5
- runnable_validation_rows=0
- blocked_command_rows=7
- complete_receipt_rows=0
- submission_ready=false
- goal_complete=false

Boundary: this capsule is read-only status packaging. It does not execute human actions, create evidence, run validators, execute writeback, run recheck, upload portal files or submit.
