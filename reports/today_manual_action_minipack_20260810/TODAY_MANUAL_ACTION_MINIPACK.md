# NatComms 今日人工动作最小包 2026-08-10

当前状态：还不能投稿。这个文件只列出今天可以人工执行的最小动作，不代表已经发送或已经收回证据。

Master dispatch zip: `<LOCAL_DESKTOP>\\NatComms_manual_dispatch_master_packet_20260810.zip`

## 今天优先做

### 1. MD-001 - corresponding author / coauthors

- Can execute today: `yes`
- Action: Send NatComms author sendout bundle v2 and record real send evidence.
- Attachments: `attachments\author_sendout\NatComms_author_sendout_bundle_v2_20260810.zip; attachments\author_sendout\author_sendout_email_ready_draft_cn.md; attachments\author_sendout\manual_sendout_execution_checklist.csv`
- Acceptance evidence: send log completed with timestamp, sender and recipient route; returned forms tracked later.
- First validator after return: `validate_external_blind_intake.py --strict-sha and evaluate_external_blind_submission.py --main-claim after label unlock`

### 2. MD-002 - corresponding author / analysis lead

- Can execute today: `yes`
- Action: Choose exactly one figure backend and one figure scope in figure_backend_decision_ticket.csv.
- Attachments: `attachments\backend_scope\FIGURE_BACKEND_SCOPE_DECISION_HANDOFF.md; attachments\backend_scope\backend_option_recommendation_matrix.csv; attachments\backend_scope\figure_backend_decision_ticket.csv`
- Acceptance evidence: backend validator reports backend_selected=true, scope_confirmed=true and rendering_allowed=true.
- First validator after return: `figure backend validator, figure rendering workflow, visual QA, figure source-data lock, full M0-M2`

### 3. MD-003 - advisor / collaborator / third-party data holder

- Can execute today: `yes`
- Action: Send Track B external blind asset request and rights checklist.
- Attachments: `attachments\external_asset\external_asset_contact_packet_queue.csv; attachments\external_asset\external_blind_asset_request_letter.md; attachments\external_asset\external_asset_rights_checklist.csv`
- Acceptance evidence: real unlabeled asset, strict-SHA manifest, sealed labels and rights statement are returned.
- First validator after return: `repository DOI/code DOI landing-page checks plus release readiness and availability prelock rerun`

### 4. MD-004 - repository/rights lead

- Can execute today: `yes`
- Action: Resolve software licence, derived-data licence and raw third-party exclusion/permission decisions.
- Attachments: `attachments\rights_licence\rights_licence_decision_matrix.csv; attachments\rights_licence\rights_completion_command_queue.csv`
- Acceptance evidence: licence_selected=true, third_party_rights_cleared=true or raw-data exclusion finalized.
- First validator after return: `reporting_summary_finalization_prelock and reporting_summary_completion_handoff rerun`

### 5. MD-005 - corresponding author / statistics reviewer / rights lead

- Can execute today: `yes`
- Action: Answer Reporting Summary author confirmations.
- Attachments: `attachments\reporting_summary\reporting_summary_author_handoff_queue.csv; attachments\reporting_summary\reporting_summary_item_completion_matrix.csv`
- Acceptance evidence: four author confirmation rows completed and Reporting Summary completion handoff rerun.
- First validator after return: `rights_licence_completion_handoff and release readiness audit rerun`

### 6. MD-006 - writing lead

- Can execute today: `no`
- Action: Defer final reference replacement until final prose and figure/table calls are stable.
- Attachments: `attachments\references\reference_manual_verification_queue.csv; attachments\references\citation_marker_final_replacement_queue.csv`
- Acceptance evidence: manual verification complete, final marker replacement allowed, final RIS/ENW regenerated.
- First validator after return: `reference_completion_handoff rerun after final prose and marker replacement`

## 禁止

- TODAY-STOP-001: Do not mark email_sent=true until the message is actually sent outside this script.
- TODAY-STOP-002: Do not record backend/scope from recommendation; record only author/analysis-owner choice.
- TODAY-STOP-003: Do not place external labels in analyst-visible folders before prediction freeze.
- TODAY-STOP-004: Do not close rights/licence from silence or missing replies.
- TODAY-STOP-005: Do not replace references today unless final prose and figure/table calls are stable.
