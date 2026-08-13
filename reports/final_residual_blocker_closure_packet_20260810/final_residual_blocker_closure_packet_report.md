# Final residual blocker closure packet 2026-08-10

Status: `final_residual_blocker_closure_packet_ready_waiting_for_external_evidence`

This packet converts the eight residual blockers into closure items. It does not provide the missing evidence, write protected targets, close gates, upload files or submit the manuscript.

## Closure Order

1. `RB-001` Collect real returned evidence: candidate_return_files > 0 and route scan has no invalid file rows.
2. `RB-002` Perform protected evidence writeback: writeback_allowed_rows > 0 after scanner acceptance; evidence_writeback_performed recorded only after manual writeback.
3. `RB-003` Fill and validate author replies: blank_author_reply_fields = 0 and evidence_rows_passed equals required evidence rows.
4. `RB-004` Ingest final figure approvals: approved_rows covers all required final figure rows and final_figures_ready=true.
5. `RB-005` Finalize repository DOI, licence and third-party rights: final_availability_ready=true with DOI/licence/rights all accepted.
6. `RB-007` Verify and lock final references: final_references_ready=true and no placeholder/candidate reference markers remain.
7. `RB-006` Lock the final Reporting Summary: final_reporting_summary_ready=true and no dependency row is open.
8. `RB-008` Run final submission gate and portal upload readiness: open_master_gates = 0, portal_upload_ready_rows > 0 and submission_ready=true.

## Current Hard Stops

1. candidate_return_files=0
2. writeback_allowed_rows=0
3. blank_author_reply_fields=12
4. commands_allowed_now=0
5. open_master_gates=8
6. submission_ready=False

Boundary: only RB-001 manual collection can start without returned evidence. All downstream closure rows remain blocked until accepted evidence exists.
