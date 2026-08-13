$ErrorActionPreference = "Stop"

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)]
        [string] $FilePath,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]] $Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

$Bench = Split-Path -Parent $PSScriptRoot
$Root = Split-Path -Parent $Bench
Set-Location -LiteralPath $Root

Write-Host "Checking Python launcher"
Invoke-Native py --version

Write-Host "Checking core imports"
Invoke-Native py -c "import yaml, numpy, PIL, sklearn, skimage; print('core-ok')"

Write-Host "Checking torch imports"
Invoke-Native py -c "import torch, torchvision; print('torch=' + torch.__version__); print('torchvision=' + torchvision.__version__)"

Write-Host "Validating Mojahid/TIGPR manifests"
Invoke-Native py (Join-Path $Root "scripts\validate_manifest_consistency.py")

Write-Host "Auditing unified schema gaps"
Invoke-Native py (Join-Path $Bench "scripts\audit_unified_schema.py")

Write-Host "Building unified sample manifests"
Invoke-Native py (Join-Path $Bench "scripts\build_unified_sample_manifests.py")

Write-Host "Auditing TIGPR local asset status"
Invoke-Native py (Join-Path $Bench "scripts\audit_tigpr_local_assets.py")

Write-Host "Auditing 4TU group-aware feasibility"
Invoke-Native py (Join-Path $Bench "scripts\audit_4tu_group_feasibility.py")

Write-Host "Building 4TU model-family extension audit"
Invoke-Native py (Join-Path $Bench "scripts\build_4tu_model_family_extension_audit.py")

Write-Host "Building external validation readiness checklist"
Invoke-Native py (Join-Path $Bench "scripts\build_external_validation_readiness.py")

Write-Host "Validating blind external intake templates"
Invoke-Native py (Join-Path $Bench "scripts\validate_external_blind_intake.py")

Write-Host "Running blind external locked-evaluation dry run"
Invoke-Native py (Join-Path $Bench "scripts\evaluate_external_blind_submission.py")

Write-Host "Building manuscript figure/table plan"
Invoke-Native py (Join-Path $Bench "scripts\build_manuscript_figure_table_plan.py")

Write-Host "Building Figure 2 and Table 2 source package"
Invoke-Native py (Join-Path $Bench "scripts\build_figure2_table2_sources.py")

Write-Host "Building Figure 3 source package"
Invoke-Native py (Join-Path $Bench "scripts\build_figure3_sources.py")

Write-Host "Building Figure 4 source package"
Invoke-Native py (Join-Path $Bench "scripts\build_figure4_sources.py")

Write-Host "Building Figure 1 and Table 1 source package"
Invoke-Native py (Join-Path $Bench "scripts\build_figure1_table1_sources.py")

Write-Host "Building Figure 5 and Figure 6 source package"
Invoke-Native py (Join-Path $Bench "scripts\build_figure5_figure6_sources.py")

Write-Host "Building Results section skeleton"
Invoke-Native py (Join-Path $Bench "scripts\build_results_section_skeleton.py")

Write-Host "Building Methods section skeleton"
Invoke-Native py (Join-Path $Bench "scripts\build_methods_section_skeleton.py")

Write-Host "Building submission package skeleton"
Invoke-Native py (Join-Path $Bench "scripts\build_submission_package_skeleton.py")

Write-Host "Building companion artifact skeletons"
Invoke-Native py (Join-Path $Bench "scripts\build_companion_artifacts_skeleton.py")

Write-Host "Building source-data deposit package"
Invoke-Native py (Join-Path $Bench "scripts\build_source_data_deposit_package.py")

Write-Host "Building release readiness audit"
Invoke-Native py (Join-Path $Bench "scripts\build_release_readiness_audit.py")

Write-Host "Building sanitized release staging preview"
Invoke-Native py (Join-Path $Bench "scripts\build_sanitized_release_staging.py")

Write-Host "Building manuscript assembly skeleton"
Invoke-Native py (Join-Path $Bench "scripts\build_manuscript_assembly_skeleton.py")

Write-Host "Building narrative section skeleton"
Invoke-Native py (Join-Path $Bench "scripts\build_narrative_section_skeleton.py")

Write-Host "Building narrative section drafts"
Invoke-Native py (Join-Path $Bench "scripts\build_narrative_section_drafts.py")

Write-Host "Building narrative citation pass"
Invoke-Native py (Join-Path $Bench "scripts\build_narrative_citation_pass.py")

Write-Host "Building citation-tagged narrative drafts v1"
Invoke-Native py (Join-Path $Bench "scripts\build_narrative_cited_drafts.py")

Write-Host "Building figure/table/source-data anchor lock"
Invoke-Native py (Join-Path $Bench "scripts\build_figure_table_anchor_lock.py")

Write-Host "Building manuscript table drafts"
Invoke-Native py (Join-Path $Bench "scripts\build_manuscript_table_drafts.py")

Write-Host "Building submission readiness dashboard"
Invoke-Native py (Join-Path $Bench "scripts\build_submission_readiness_dashboard.py")

Write-Host "Building figure rendering specification"
Invoke-Native py (Join-Path $Bench "scripts\build_figure_rendering_spec.py")

Write-Host "Building blind external acquisition package"
Invoke-Native py (Join-Path $Bench "scripts\build_blind_external_acquisition_package.py")

Write-Host "Building external asset triage register"
Invoke-Native py (Join-Path $Bench "scripts\build_external_asset_triage_register.py")

Write-Host "Building repository metadata package"
Invoke-Native py (Join-Path $Bench "scripts\build_repository_metadata_package.py")

Write-Host "Building repository release manifest lock"
Invoke-Native py (Join-Path $Bench "scripts\build_repository_release_manifest_lock.py")

Write-Host "Building Reporting Summary draft"
Invoke-Native py (Join-Path $Bench "scripts\build_reporting_summary_draft.py")

Write-Host "Building author decision intake package"
Invoke-Native py (Join-Path $Bench "scripts\build_author_decision_intake_package.py")

Write-Host "Building author action packet"
Invoke-Native py (Join-Path $Bench "scripts\build_author_action_packet.py")

Write-Host "Building submission gap-closure matrix"
Invoke-Native py (Join-Path $Bench "scripts\build_submission_gap_closure_matrix.py")

Write-Host "Building manuscript claim readiness audit"
Invoke-Native py (Join-Path $Bench "scripts\build_manuscript_claim_readiness_audit.py")

Write-Host "Building conservative manuscript draft"
Invoke-Native py (Join-Path $Bench "scripts\build_conservative_manuscript_draft.py")

Write-Host "Building conservative Methods draft"
Invoke-Native py (Join-Path $Bench "scripts\build_conservative_methods_draft.py")

Write-Host "Building author-review manuscript package"
Invoke-Native py (Join-Path $Bench "scripts\build_author_review_manuscript_package.py")

Write-Host "Building pre-submission reviewer-risk audit"
Invoke-Native py (Join-Path $Bench "scripts\build_pre_submission_reviewer_risk_audit.py")

Write-Host "Building reviewer-risk revision action packet"
Invoke-Native py (Join-Path $Bench "scripts\build_reviewer_risk_revision_action_packet.py")

Write-Host "Building broad-interest framing revision"
Invoke-Native py (Join-Path $Bench "scripts\build_broad_interest_framing_revision.py")

Write-Host "Building reference numbering prelock package"
Invoke-Native py (Join-Path $Bench "scripts\build_reference_numbering_prelock_package.py")

Write-Host "Building reference public verification package"
Invoke-Native py (Join-Path $Bench "scripts\build_reference_public_verification_package.py")

Write-Host "Building sentence citation support lock"
Invoke-Native py (Join-Path $Bench "scripts\build_sentence_citation_support_lock.py")

Write-Host "Building reference completion handoff"
Invoke-Native py (Join-Path $Bench "scripts\build_reference_completion_handoff.py")

Write-Host "Building reference final lock validator"
Invoke-Native py (Join-Path $Bench "scripts\build_reference_final_lock_validator.py")

Write-Host "Building availability statement prelock package"
Invoke-Native py (Join-Path $Bench "scripts\build_availability_statement_prelock_package.py")

Write-Host "Building availability/repository finalization validator"
Invoke-Native py (Join-Path $Bench "scripts\build_availability_repository_finalization_validator.py")

Write-Host "Building Reporting Summary finalization prelock"
Invoke-Native py (Join-Path $Bench "scripts\build_reporting_summary_finalization_prelock.py")

Write-Host "Building Reporting Summary final lock validator"
Invoke-Native py (Join-Path $Bench "scripts\build_reporting_summary_final_lock_validator.py")

Write-Host "Building external validation contingency framing"
Invoke-Native py (Join-Path $Bench "scripts\build_external_validation_contingency_framing.py")

Write-Host "Building Track B manuscript branch prelock"
Invoke-Native py (Join-Path $Bench "scripts\build_track_b_manuscript_branch_prelock.py")

Write-Host "Building submission command dashboard v2"
Invoke-Native py (Join-Path $Bench "scripts\build_submission_command_dashboard_v2.py")

Write-Host "Building Nat Comms submission assembly preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_submission_assembly_preflight.py")

Write-Host "Building Nat Comms cover letter prelock"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_cover_letter_prelock.py")

Write-Host "Building Nat Comms initial-submission text preassembly"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_initial_submission_text_preassembly.py")

Write-Host "Building Nat Comms Supplementary Information preassembly"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_supplementary_info_preassembly.py")

Write-Host "Building R4 manuscript boundary synchronization audit"
Invoke-Native py (Join-Path $Bench "scripts\build_r4_manuscript_boundary_sync_audit.py")

Write-Host "Building release delta synchronization audit"
Invoke-Native py (Join-Path $Bench "scripts\build_release_delta_sync_audit.py")

Write-Host "Building repository predeposit handoff"
Invoke-Native py (Join-Path $Bench "scripts\build_repository_predeposit_handoff.py")

Write-Host "Building rights/licence completion handoff"
Invoke-Native py (Join-Path $Bench "scripts\build_rights_licence_completion_handoff.py")

Write-Host "Building Nat Comms administrative declarations prelock"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_admin_declarations_prelock.py")

Write-Host "Building Nat Comms portal upload manifest prelock"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_portal_upload_manifest_prelock.py")

Write-Host "Building Nat Comms finalization master checklist"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_finalization_master_checklist.py")

Write-Host "Building Nat Comms author finalization reply packet"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_author_finalization_reply_packet.py")

Write-Host "Building Nat Comms author reply ingestion validator"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_author_reply_ingestion_validator.py")

Write-Host "Building Nat Comms gate closure evidence binder"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_gate_closure_evidence_binder.py")

Write-Host "Building Nat Comms finalization command dashboard v3"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_finalization_command_dashboard_v3.py")

Write-Host "Building Nat Comms submission final lock validator"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_submission_final_lock_validator.py")

Write-Host "Building manual evidence final intake validator"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_evidence_final_intake_validator.py")

Write-Host "Building final human execution closeout board"
Invoke-Native py (Join-Path $Bench "scripts\build_final_human_execution_closeout_board.py")

Write-Host "Building final human execution handoff packet"
Invoke-Native py (Join-Path $Bench "scripts\build_final_human_execution_handoff_packet.py")

Write-Host "Building final return evidence inbox scaffold"
Invoke-Native py (Join-Path $Bench "scripts\build_final_return_evidence_inbox_scaffold.py")

Write-Host "Building final return evidence intake scanner"
Invoke-Native py (Join-Path $Bench "scripts\build_final_return_evidence_intake_scanner.py")

Write-Host "Building final return evidence writeback preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_final_return_evidence_writeback_preflight.py")

Write-Host "Building post-writeback gate transition validator"
Invoke-Native py (Join-Path $Bench "scripts\build_post_writeback_gate_transition_validator.py")

Write-Host "Building post-return guarded execution runner"
Invoke-Native py (Join-Path $Bench "scripts\build_post_return_guarded_execution_runner.py")

Write-Host "Building final operator execution bundle v2"
Invoke-Native py (Join-Path $Bench "scripts\build_final_operator_execution_bundle_v2.py")

Write-Host "Building final operator bundle v2 acceptance validator"
Invoke-Native py (Join-Path $Bench "scripts\build_final_operator_bundle_v2_acceptance_validator.py")

Write-Host "Building final completion residual blocker audit"
Invoke-Native py (Join-Path $Bench "scripts\build_final_completion_residual_blocker_audit.py")

Write-Host "Building final residual blocker closure packet"
Invoke-Native py (Join-Path $Bench "scripts\build_final_residual_blocker_closure_packet.py")

Write-Host "Building RB-001 return evidence drop kit"
Invoke-Native py (Join-Path $Bench "scripts\build_rb001_return_evidence_drop_kit.py")

Write-Host "Building RB-001 return evidence hash reconciliation"
Invoke-Native py (Join-Path $Bench "scripts\build_rb001_return_evidence_hash_reconciliation.py")

Write-Host "Building RB-001 post-drop dry-run gate"
Invoke-Native py (Join-Path $Bench "scripts\build_rb001_post_drop_dry_run_gate.py")

Write-Host "Building RB-001 diagnostic-only runner"
Invoke-Native py (Join-Path $Bench "scripts\build_rb001_diagnostic_only_runner.py")

Write-Host "Building RB-001 manual execution receipt"
Invoke-Native py (Join-Path $Bench "scripts\build_rb001_manual_execution_receipt.py")

Write-Host "Building RB-001 receipt completion validator"
Invoke-Native py (Join-Path $Bench "scripts\build_rb001_receipt_completion_validator.py")

Write-Host "Building RB-001 closeout dashboard"
Invoke-Native py (Join-Path $Bench "scripts\build_rb001_closeout_dashboard.py")

Write-Host "Building RB-002 writeback readiness dashboard"
Invoke-Native py (Join-Path $Bench "scripts\build_rb002_writeback_readiness_dashboard.py")

Write-Host "Building RB-002 protected writeback receipt"
Invoke-Native py (Join-Path $Bench "scripts\build_rb002_protected_writeback_receipt.py")

Write-Host "Building RB-002 writeback receipt completion validator"
Invoke-Native py (Join-Path $Bench "scripts\build_rb002_writeback_receipt_completion_validator.py")

Write-Host "Building Nat Comms next execution packet"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_next_execution_packet.py")

Write-Host "Building Nat Comms author sendout preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_author_sendout_preflight.py")

Write-Host "Building Nat Comms author sendout bundle"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_author_sendout_bundle.py")

Write-Host "Building Nat Comms author response tracker"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_author_response_tracker.py")

Write-Host "Building Nat Comms author response log validator"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_author_response_log_validator.py")

Write-Host "Building manual field preservation audit"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_field_preservation_audit.py")

Write-Host "Building author fill guide packet"
Invoke-Native py (Join-Path $Bench "scripts\build_author_fill_guide_packet.py")

Write-Host "Building Nat Comms author sendout bundle v2"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_author_sendout_bundle_v2.py")

Write-Host "Building Nat Comms sendout v2 lifecycle consistency audit"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_sendout_v2_lifecycle_consistency_audit.py")

Write-Host "Building Nat Comms canonical send log v2 overlay"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_canonical_send_log_v2_overlay.py")

Write-Host "Rebuilding Nat Comms author response log validator after v2 overlay"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_author_response_log_validator.py")

Write-Host "Building Nat Comms manual sendout execution guard"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_manual_sendout_execution_guard.py")

Write-Host "Building Nat Comms sendout evidence receipt completion validator"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_sendout_evidence_receipt_completion_validator.py")

Write-Host "Building Nat Comms canonical tracker v2 consistency validator"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_canonical_tracker_v2_consistency_validator.py")

Write-Host "Building Nat Comms return tracker to RB-001 crosswalk validator"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_return_tracker_to_rb001_crosswalk_validator.py")

Write-Host "Building RB-001 hash manifest readiness validator"
Invoke-Native py (Join-Path $Bench "scripts\build_rb001_hash_manifest_readiness_validator.py")

Write-Host "Building RB-001 closeout dependency bridge validator"
Invoke-Native py (Join-Path $Bench "scripts\build_rb001_closeout_dependency_bridge_validator.py")

Write-Host "Building RB-002 entry dependency bridge validator"
Invoke-Native py (Join-Path $Bench "scripts\build_rb002_entry_dependency_bridge_validator.py")

Write-Host "Building post-writeback transition dependency bridge validator"
Invoke-Native py (Join-Path $Bench "scripts\build_post_writeback_transition_dependency_bridge_validator.py")

Write-Host "Building Nat Comms author sendout dispatch preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_natcomms_author_sendout_dispatch_preflight.py")

Write-Host "Building figure rendering preflight package"
Invoke-Native py (Join-Path $Bench "scripts\build_figure_rendering_preflight_package.py")

Write-Host "Building figure backend decision validator"
Invoke-Native py (Join-Path $Bench "scripts\build_figure_backend_decision_validator.py")

Write-Host "Building figure backend/scope decision handoff"
Invoke-Native py (Join-Path $Bench "scripts\build_figure_backend_scope_decision_handoff.py")

Write-Host "Building Reporting Summary completion handoff"
Invoke-Native py (Join-Path $Bench "scripts\build_reporting_summary_completion_handoff.py")

Write-Host "Building manual dispatch master packet"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_dispatch_master_packet.py")

Write-Host "Building today manual action minipack"
Invoke-Native py (Join-Path $Bench "scripts\build_today_manual_action_minipack.py")

Write-Host "Building manual evidence inbox scaffold"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_evidence_inbox_scaffold.py")

Write-Host "Building manual evidence inbox audit"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_evidence_inbox_audit.py")

Write-Host "Building inbox-to-tracker writeback queue"
Invoke-Native py (Join-Path $Bench "scripts\build_inbox_to_tracker_writeback_queue.py")

Write-Host "Building manual evidence lifecycle dashboard"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_evidence_lifecycle_dashboard.py")

Write-Host "Building next human execution handoff bundle"
Invoke-Native py (Join-Path $Bench "scripts\build_next_human_execution_handoff_bundle.py")

Write-Host "Building human execution handoff acceptance checklist"
Invoke-Native py (Join-Path $Bench "scripts\build_human_execution_handoff_acceptance_checklist.py")

Write-Host "Building manual post-handoff recheck runner"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_post_handoff_recheck_runner.py")

Write-Host "Building submission completion ledger"
Invoke-Native py (Join-Path $Bench "scripts\build_submission_completion_ledger.py")

Write-Host "Building portal submission file preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_portal_submission_file_preflight.py")

Write-Host "Building final manuscript preassembly guard"
Invoke-Native py (Join-Path $Bench "scripts\build_final_manuscript_preassembly_guard.py")

Write-Host "Building gate closure execution board"
Invoke-Native py (Join-Path $Bench "scripts\build_gate_closure_execution_board.py")

Write-Host "Building gate closure dependency bridge validator"
Invoke-Native py (Join-Path $Bench "scripts\build_gate_closure_dependency_bridge_validator.py")

Write-Host "Building post-dispatch evidence intake validator"
Invoke-Native py (Join-Path $Bench "scripts\build_post_dispatch_evidence_intake_validator.py")

Write-Host "Building manual evidence intake worksheet"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_evidence_intake_worksheet.py")

Write-Host "Building post-evidence safe rerun guard"
Invoke-Native py (Join-Path $Bench "scripts\build_post_evidence_safe_rerun_guard.py")

Write-Host "Building manual evidence entry preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_evidence_entry_preflight.py")

Write-Host "Building operator runbook after manual dispatch"
Invoke-Native py (Join-Path $Bench "scripts\build_operator_runbook_after_manual_dispatch.py")

Write-Host "Building post-gate manual evidence dependency bridge validator"
Invoke-Native py (Join-Path $Bench "scripts\build_post_gate_manual_evidence_dependency_bridge_validator.py")

Write-Host "Building figure source-data lock package"
Invoke-Native py (Join-Path $Bench "scripts\build_figure_source_data_lock_package.py")

Write-Host "Building Python figure preview package"
Invoke-Native py (Join-Path $Bench "scripts\build_python_figure_preview_package.py")

Write-Host "Building Python figure preview visual QA"
Invoke-Native py (Join-Path $Bench "scripts\build_python_figure_preview_visual_qa.py")

Write-Host "Building Python figure author review packet"
Invoke-Native py (Join-Path $Bench "scripts\build_python_figure_author_review_packet.py")

Write-Host "Building Python figure author review intake validator"
Invoke-Native py (Join-Path $Bench "scripts\build_python_figure_author_review_intake_validator.py")

Write-Host "Building Python figure author review return inbox"
Invoke-Native py (Join-Path $Bench "scripts\build_python_figure_author_review_return_inbox.py")

Write-Host "Building Python figure author review writeback queue"
Invoke-Native py (Join-Path $Bench "scripts\build_python_figure_author_review_writeback_queue.py")

Write-Host "Building Python figure final candidate preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_python_figure_final_candidate_preflight.py")

Write-Host "Building Python figure final export QA template"
Invoke-Native py (Join-Path $Bench "scripts\build_python_figure_final_export_qa_template.py")

Write-Host "Building Python figure portal upload blocker"
Invoke-Native py (Join-Path $Bench "scripts\build_python_figure_portal_upload_blocker.py")

Write-Host "Building Python figure Source Data panel-map preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_python_figure_source_data_panel_map_preflight.py")

Write-Host "Building figure/portal final dependency bridge validator"
Invoke-Native py (Join-Path $Bench "scripts\build_figure_portal_final_dependency_bridge_validator.py")

Write-Host "Building author decision closure packet v2"
Invoke-Native py (Join-Path $Bench "scripts\build_author_decision_closure_packet_v2.py")

Write-Host "Building author/final closeout dependency bridge validator"
Invoke-Native py (Join-Path $Bench "scripts\build_author_final_closeout_dependency_bridge_validator.py")

Write-Host "Building final submission master dependency bridge validator"
Invoke-Native py (Join-Path $Bench "scripts\build_final_submission_master_dependency_bridge_validator.py")

Write-Host "Building final master next-action packet"
Invoke-Native py (Join-Path $Bench "scripts\build_final_master_next_action_packet.py")

Write-Host "Building final manual receipt intake package"
Invoke-Native py (Join-Path $Bench "scripts\build_final_manual_receipt_intake_package.py")

Write-Host "Building final manual receipt completion validator"
Invoke-Native py (Join-Path $Bench "scripts\build_final_manual_receipt_completion_validator.py")

Write-Host "Building final guarded recheck launcher"
Invoke-Native py (Join-Path $Bench "scripts\build_final_guarded_recheck_launcher.py")

Write-Host "Building final guarded recheck execution audit"
Invoke-Native py (Join-Path $Bench "scripts\build_final_guarded_recheck_execution_audit.py")

Write-Host "Building external dependency escalation packet"
Invoke-Native py (Join-Path $Bench "scripts\build_external_dependency_escalation_packet.py")

Write-Host "Building external dependency escalation sendout receipt validator"
Invoke-Native py (Join-Path $Bench "scripts\build_external_dependency_escalation_sendout_receipt_validator.py")

Write-Host "Building external dependency safe-send execution packet"
Invoke-Native py (Join-Path $Bench "scripts\build_external_dependency_safe_send_execution_packet.py")

Write-Host "Building external dependency sendout receipt preservation regression"
Invoke-Native py (Join-Path $Bench "scripts\build_external_dependency_sendout_receipt_preservation_regression.py")

Write-Host "Building external dependency sendout evidence intake preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_external_dependency_sendout_evidence_intake_preflight.py")

Write-Host "Building external dependency EDS guarded writeback applier"
Invoke-Native py (Join-Path $Bench "scripts\build_external_dependency_eds_guarded_writeback_applier.py")

Write-Host "Building external dependency post-writeback revalidation orchestrator"
Invoke-Native py (Join-Path $Bench "scripts\build_external_dependency_post_writeback_revalidation_orchestrator.py")

Write-Host "Building FMR-001 sendout completion writeback preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr001_sendout_completion_writeback_preflight.py")

Write-Host "Building FMR-001 guarded writeback applier"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr001_guarded_writeback_applier.py")

Write-Host "Building FMR-001 guarded writeback regression"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr001_guarded_writeback_regression.py")

Write-Host "Building FMR-002 author decision writeback preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr002_author_decision_writeback_preflight.py")

Write-Host "Building FMR-002 guarded writeback applier"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr002_guarded_writeback_applier.py")

Write-Host "Building FMR-002 guarded writeback regression"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr002_guarded_writeback_regression.py")

Write-Host "Building FMR-003 returned evidence writeback preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr003_returned_evidence_writeback_preflight.py")

Write-Host "Building FMR-003 guarded writeback applier"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr003_guarded_writeback_applier.py")

Write-Host "Building FMR-003 guarded writeback regression"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr003_guarded_writeback_regression.py")

Write-Host "Building FMR-004 figure review writeback preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr004_figure_review_writeback_preflight.py")

Write-Host "Building FMR-004 guarded writeback applier"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr004_guarded_writeback_applier.py")

Write-Host "Building FMR-004 guarded writeback regression"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr004_guarded_writeback_regression.py")

Write-Host "Building FMR-005 repository rights DOI writeback preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr005_repository_rights_doi_writeback_preflight.py")

Write-Host "Building FMR-005 guarded writeback applier"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr005_guarded_writeback_applier.py")

Write-Host "Building FMR-005 guarded writeback regression"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr005_guarded_writeback_regression.py")

Write-Host "Building FMR-006 guarded recheck receipt writeback preflight"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr006_guarded_recheck_receipt_writeback_preflight.py")

Write-Host "Building FMR-006 guarded writeback applier"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr006_guarded_writeback_applier.py")

Write-Host "Building FMR-006 guarded writeback regression"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr006_guarded_writeback_regression.py")

Write-Host "Building FMR guarded writeback coverage audit"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr_guarded_writeback_coverage_audit.py")

Write-Host "Building FMR evidence-to-writeback execution order audit"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr_evidence_to_writeback_execution_order_audit.py")

Write-Host "Building FMR manual evidence inbox integrity audit"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr_manual_evidence_inbox_integrity_audit.py")

Write-Host "Building FMR manual evidence operator packet"
Invoke-Native py (Join-Path $Bench "scripts\build_fmr_manual_evidence_operator_packet.py")

Write-Host "Building final execution board"
Invoke-Native py (Join-Path $Bench "scripts\build_final_execution_board_20260810.py")

Write-Host "Building manual-only execution forms"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_only_execution_forms_20260810.py")

Write-Host "Validating manual-only execution forms"
Invoke-Native py (Join-Path $Bench "scripts\validate_manual_only_execution_forms_20260810.py")

Write-Host "Building manual evidence readiness monitor"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_evidence_readiness_monitor_20260810.py")

Write-Host "Building manual execution brief"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_execution_brief_20260810.py")

Write-Host "Validating manual execution brief acceptance"
Invoke-Native py (Join-Path $Bench "scripts\validate_manual_execution_brief_acceptance_20260810.py")

Write-Host "Watching manual evidence arrival"
Invoke-Native py (Join-Path $Bench "scripts\watch_manual_evidence_arrival_20260810.py")

Write-Host "Building manual evidence route snapshot"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_evidence_route_snapshot_20260810.py")

Write-Host "Building daily execution status capsule"
Invoke-Native py (Join-Path $Bench "scripts\build_daily_execution_status_capsule_20260810.py")

Write-Host "Validating daily execution capsule re-entry"
Invoke-Native py (Join-Path $Bench "scripts\validate_daily_execution_capsule_reentry_20260810.py")

Write-Host "Building manual action backfill template audit"
Invoke-Native py (Join-Path $Bench "scripts\build_manual_action_backfill_template_audit_20260810.py")

Write-Host "Guarding manual form validation launcher"
Invoke-Native py (Join-Path $Bench "scripts\guard_manual_form_validation_launcher_20260810.py")

Write-Host "Building external manual evidence blocker certificate"
Invoke-Native py (Join-Path $Bench "scripts\build_external_manual_evidence_blocker_certificate_20260810.py")

Write-Host "Building local-only pre-review package"
Invoke-Native py (Join-Path $Bench "scripts\build_local_only_prereview_package_20260811.py")

Write-Host "Building figure preview completion bridge"
Invoke-Native py (Join-Path $Bench "scripts\build_figure_preview_completion_bridge_20260811.py")

Write-Host "Building figure final-candidate review packet"
Invoke-Native py (Join-Path $Bench "scripts\build_figure_final_candidate_review_packet_20260811.py")

Write-Host "Building Source Data panel-map review packet"
Invoke-Native py (Join-Path $Bench "scripts\build_source_data_panel_map_review_packet_20260811.py")

Write-Host "Building Results figure/source alignment packet"
Invoke-Native py (Join-Path $Bench "scripts\build_results_figure_source_alignment_packet_20260811.py")

Write-Host "Building availability/repository consistency review"
Invoke-Native py (Join-Path $Bench "scripts\build_availability_repository_consistency_review_20260811.py")

Write-Host "Building experiment completion audit"
Invoke-Native py (Join-Path $Bench "scripts\build_experiment_completion_audit_20260811.py")

Write-Host "Checking manuscript-facing text encoding"
Invoke-Native py (Join-Path $Bench "scripts\check_manuscript_text_encoding.py")

if (Test-Path -LiteralPath (Join-Path $Root "external_assets\res_sam_repo\gpr_data.zip")) {
    Write-Host "Building Res-SAM unified sample manifest"
    Invoke-Native py `
        (Join-Path $Bench "scripts\build_ressam_unified_manifest.py") `
        --zip-path (Join-Path $Root "external_assets\res_sam_repo\gpr_data.zip") `
        --extract-dir (Join-Path $Root "external_assets\res_sam_data") `
        --output-csv (Join-Path $Bench "data_manifests\res_sam_unified_samples_20260810.csv") `
        --summary-md (Join-Path $Bench "data_manifests\res_sam_unified_samples_20260810.md")
}

$RequiredArtifacts = @(
    "reports\4tu_counterfactual_hog_seed_sweep_20260810\hog_seed_sweep_summary.json",
    "reports\4tu_counterfactual_hog_seed_sweep_20260810\hog_seed_sweep_summary.md",
    "reports\4tu_counterfactual_hog_seed_sweep_20260810\hog_seed_sweep_metrics.csv",
    "reports\4tu_counterfactual_cnn_20260810\cnn_reliance_summary.json",
    "reports\4tu_counterfactual_cnn_20260810\cnn_reliance_summary.md",
    "reports\4tu_counterfactual_cnn_20260810\cnn_reliance_metrics.csv",
    "reports\4tu_counterfactual_cnn_seed_sweep_20260810\cnn_seed_sweep_summary.json",
    "reports\4tu_counterfactual_cnn_seed_sweep_20260810\cnn_seed_sweep_summary.md",
    "reports\4tu_counterfactual_cnn_seed_sweep_20260810\cnn_seed_sweep_metrics.csv",
    "reports\4tu_counterfactual_hog_group_splits_20260810\hog_group_split_summary.json",
    "reports\4tu_counterfactual_hog_group_splits_20260810\hog_group_split_summary.md",
    "reports\4tu_counterfactual_hog_group_splits_20260810\hog_group_split_metrics.csv",
    "reports\tigpr_local_asset_audit_20260810.json",
    "reports\tigpr_local_asset_audit_20260810.md",
    "reports\lbp_linear_svm_matrix_20260810\lbp_linear_svm_summary.json",
    "reports\lbp_linear_svm_matrix_20260810\lbp_linear_svm_summary.md",
    "reports\lbp_linear_svm_matrix_20260810\lbp_linear_svm_metrics.csv",
    "reports\tinycnn_matrix_20260810\tinycnn_summary.json",
    "reports\tinycnn_matrix_20260810\tinycnn_summary.md",
    "reports\tinycnn_matrix_20260810\tinycnn_metrics.csv",
    "reports\resnet18_embedding_svm_matrix_20260810\resnet18_embedding_svm_summary.json",
    "reports\resnet18_embedding_svm_matrix_20260810\resnet18_embedding_svm_summary.md",
    "reports\resnet18_embedding_svm_matrix_20260810\resnet18_embedding_svm_metrics.csv",
    "reports\efficientnet_b0_embedding_svm_matrix_20260810\efficientnet_b0_embedding_svm_summary.json",
    "reports\efficientnet_b0_embedding_svm_matrix_20260810\efficientnet_b0_embedding_svm_summary.md",
    "reports\efficientnet_b0_embedding_svm_matrix_20260810\efficientnet_b0_embedding_svm_metrics.csv",
    "reports\five_model_synthesis_20260810\five_model_synthesis_summary.json",
    "reports\five_model_synthesis_20260810\five_model_synthesis_summary.md",
    "reports\five_model_synthesis_20260810\five_model_synthesis_model_rows.csv",
    "reports\five_model_synthesis_20260810\five_model_synthesis_claim_summary.csv",
    "reports\4tu_group_feasibility_20260810\4tu_group_feasibility_summary.json",
    "reports\4tu_group_feasibility_20260810\4tu_group_feasibility_summary.md",
    "reports\4tu_group_feasibility_20260810\4tu_group_feasibility_targets.csv",
    "reports\4tu_group_feasibility_20260810\4tu_group_feasibility_project_labels.csv",
    "reports\4tu_model_family_extension_audit_20260810\4tu_model_family_extension_matrix.csv",
    "reports\4tu_model_family_extension_audit_20260810\4tu_evidence_layer_upgrade_decisions.csv",
    "reports\4tu_model_family_extension_audit_20260810\4tu_claim_upgrade_decision.csv",
    "reports\4tu_model_family_extension_audit_20260810\4tu_model_family_extension_audit_qa.csv",
    "reports\4tu_model_family_extension_audit_20260810\4tu_model_family_extension_audit.md",
    "reports\4tu_model_family_extension_audit_20260810\4tu_model_family_extension_audit_summary.json",
    "reports\external_validation_readiness_20260810\external_validation_readiness_summary.json",
    "reports\external_validation_readiness_20260810\external_validation_readiness_summary.md",
    "reports\external_validation_readiness_20260810\external_validation_readiness_tracks.csv",
    "protocols\blind_external_validation_protocol_20260810.md",
    "scripts\build_external_blind_manifest.py",
    "scripts\validate_external_blind_intake.py",
    "scripts\evaluate_external_blind_submission.py",
    "scripts\build_manuscript_figure_table_plan.py",
    "scripts\build_figure2_table2_sources.py",
    "scripts\build_figure3_sources.py",
    "scripts\build_figure4_sources.py",
    "scripts\build_figure1_table1_sources.py",
    "scripts\build_figure5_figure6_sources.py",
    "scripts\build_results_section_skeleton.py",
    "scripts\build_methods_section_skeleton.py",
    "scripts\build_submission_package_skeleton.py",
    "scripts\build_companion_artifacts_skeleton.py",
    "scripts\build_source_data_deposit_package.py",
    "scripts\build_release_readiness_audit.py",
    "scripts\build_sanitized_release_staging.py",
    "scripts\build_manuscript_assembly_skeleton.py",
    "scripts\build_narrative_section_skeleton.py",
    "scripts\build_narrative_section_drafts.py",
    "scripts\build_narrative_citation_pass.py",
    "scripts\build_narrative_cited_drafts.py",
    "scripts\build_figure_table_anchor_lock.py",
    "scripts\build_manuscript_table_drafts.py",
    "scripts\build_submission_readiness_dashboard.py",
    "scripts\build_figure_rendering_spec.py",
    "scripts\build_blind_external_acquisition_package.py",
    "scripts\build_external_asset_triage_register.py",
    "scripts\build_repository_metadata_package.py",
    "scripts\build_repository_release_manifest_lock.py",
    "scripts\build_release_delta_sync_audit.py",
    "scripts\build_repository_predeposit_handoff.py",
    "scripts\build_rights_licence_completion_handoff.py",
    "scripts\build_reporting_summary_draft.py",
    "scripts\build_author_decision_intake_package.py",
    "scripts\build_author_action_packet.py",
    "scripts\build_submission_gap_closure_matrix.py",
    "scripts\build_manuscript_claim_readiness_audit.py",
    "scripts\build_conservative_manuscript_draft.py",
    "scripts\build_conservative_methods_draft.py",
    "scripts\build_author_review_manuscript_package.py",
    "scripts\build_pre_submission_reviewer_risk_audit.py",
    "scripts\build_reviewer_risk_revision_action_packet.py",
    "scripts\build_broad_interest_framing_revision.py",
    "scripts\build_reference_numbering_prelock_package.py",
    "scripts\build_reference_public_verification_package.py",
    "scripts\build_sentence_citation_support_lock.py",
    "scripts\build_reference_completion_handoff.py",
    "scripts\build_reference_final_lock_validator.py",
    "scripts\build_availability_statement_prelock_package.py",
    "scripts\build_availability_repository_finalization_validator.py",
    "scripts\build_reporting_summary_finalization_prelock.py",
    "scripts\build_reporting_summary_final_lock_validator.py",
    "scripts\build_external_validation_contingency_framing.py",
    "scripts\build_track_b_manuscript_branch_prelock.py",
    "scripts\build_submission_command_dashboard_v2.py",
    "scripts\build_natcomms_submission_assembly_preflight.py",
    "scripts\build_natcomms_cover_letter_prelock.py",
    "scripts\build_natcomms_initial_submission_text_preassembly.py",
    "scripts\build_natcomms_supplementary_info_preassembly.py",
    "scripts\build_r4_manuscript_boundary_sync_audit.py",
    "scripts\build_natcomms_admin_declarations_prelock.py",
    "scripts\build_natcomms_portal_upload_manifest_prelock.py",
    "scripts\build_natcomms_finalization_master_checklist.py",
    "scripts\build_natcomms_author_finalization_reply_packet.py",
    "scripts\build_natcomms_author_reply_ingestion_validator.py",
    "scripts\build_natcomms_gate_closure_evidence_binder.py",
    "scripts\build_natcomms_finalization_command_dashboard_v3.py",
    "scripts\build_natcomms_submission_final_lock_validator.py",
    "scripts\build_manual_evidence_final_intake_validator.py",
    "scripts\build_final_human_execution_closeout_board.py",
    "scripts\build_final_human_execution_handoff_packet.py",
    "scripts\build_final_return_evidence_inbox_scaffold.py",
    "scripts\build_final_return_evidence_intake_scanner.py",
    "scripts\build_final_return_evidence_writeback_preflight.py",
    "scripts\build_post_writeback_gate_transition_validator.py",
    "scripts\build_post_return_guarded_execution_runner.py",
    "scripts\build_final_operator_execution_bundle_v2.py",
    "scripts\build_final_operator_bundle_v2_acceptance_validator.py",
    "scripts\build_final_completion_residual_blocker_audit.py",
    "scripts\build_final_residual_blocker_closure_packet.py",
    "scripts\build_rb001_return_evidence_drop_kit.py",
    "scripts\build_rb001_return_evidence_hash_reconciliation.py",
    "scripts\build_rb001_post_drop_dry_run_gate.py",
    "scripts\build_rb001_diagnostic_only_runner.py",
    "scripts\build_rb001_manual_execution_receipt.py",
    "scripts\build_rb001_receipt_completion_validator.py",
    "scripts\build_rb001_closeout_dashboard.py",
    "scripts\build_rb002_writeback_readiness_dashboard.py",
    "scripts\build_rb002_protected_writeback_receipt.py",
    "scripts\build_rb002_writeback_receipt_completion_validator.py",
    "scripts\build_natcomms_next_execution_packet.py",
    "scripts\build_natcomms_author_sendout_preflight.py",
    "scripts\build_natcomms_author_sendout_bundle.py",
    "scripts\build_natcomms_author_response_tracker.py",
    "scripts\build_natcomms_author_response_log_validator.py",
    "scripts\build_manual_field_preservation_audit.py",
    "scripts\build_author_fill_guide_packet.py",
    "scripts\build_natcomms_author_sendout_bundle_v2.py",
    "scripts\build_natcomms_sendout_v2_lifecycle_consistency_audit.py",
    "scripts\build_natcomms_canonical_send_log_v2_overlay.py",
    "scripts\build_natcomms_manual_sendout_execution_guard.py",
    "scripts\build_natcomms_sendout_evidence_receipt_completion_validator.py",
    "scripts\build_natcomms_canonical_tracker_v2_consistency_validator.py",
    "scripts\build_natcomms_return_tracker_to_rb001_crosswalk_validator.py",
    "scripts\build_rb001_hash_manifest_readiness_validator.py",
    "scripts\build_rb001_closeout_dependency_bridge_validator.py",
    "scripts\build_rb002_entry_dependency_bridge_validator.py",
    "scripts\build_post_writeback_transition_dependency_bridge_validator.py",
    "scripts\build_natcomms_author_sendout_dispatch_preflight.py",
    "scripts\build_4tu_model_family_extension_audit.py",
    "scripts\build_figure_rendering_preflight_package.py",
    "scripts\build_figure_backend_decision_validator.py",
    "scripts\build_figure_backend_scope_decision_handoff.py",
    "scripts\build_reporting_summary_completion_handoff.py",
    "scripts\build_manual_dispatch_master_packet.py",
    "scripts\build_today_manual_action_minipack.py",
    "scripts\build_manual_evidence_inbox_scaffold.py",
    "scripts\build_manual_evidence_inbox_audit.py",
    "scripts\build_inbox_to_tracker_writeback_queue.py",
    "scripts\build_manual_evidence_lifecycle_dashboard.py",
    "scripts\build_next_human_execution_handoff_bundle.py",
    "scripts\build_human_execution_handoff_acceptance_checklist.py",
    "scripts\build_manual_post_handoff_recheck_runner.py",
    "scripts\build_submission_completion_ledger.py",
    "scripts\build_portal_submission_file_preflight.py",
    "scripts\build_final_manuscript_preassembly_guard.py",
    "scripts\build_gate_closure_execution_board.py",
    "scripts\build_gate_closure_dependency_bridge_validator.py",
    "scripts\build_post_dispatch_evidence_intake_validator.py",
    "scripts\build_manual_evidence_intake_worksheet.py",
    "scripts\build_manual_evidence_entry_preflight.py",
    "scripts\build_post_evidence_safe_rerun_guard.py",
    "scripts\build_operator_runbook_after_manual_dispatch.py",
    "scripts\build_post_gate_manual_evidence_dependency_bridge_validator.py",
    "scripts\build_python_figure_preview_package.py",
    "scripts\build_python_figure_preview_visual_qa.py",
    "scripts\build_python_figure_author_review_packet.py",
    "scripts\build_python_figure_author_review_intake_validator.py",
    "scripts\build_python_figure_author_review_return_inbox.py",
    "scripts\build_python_figure_author_review_writeback_queue.py",
    "scripts\build_python_figure_final_candidate_preflight.py",
    "scripts\build_python_figure_final_export_qa_template.py",
    "scripts\build_python_figure_portal_upload_blocker.py",
    "scripts\build_python_figure_source_data_panel_map_preflight.py",
    "scripts\build_figure_portal_final_dependency_bridge_validator.py",
    "scripts\build_author_decision_closure_packet_v2.py",
    "scripts\build_author_final_closeout_dependency_bridge_validator.py",
    "scripts\build_final_submission_master_dependency_bridge_validator.py",
    "scripts\build_final_master_next_action_packet.py",
    "scripts\build_final_manual_receipt_intake_package.py",
    "scripts\build_final_manual_receipt_completion_validator.py",
    "scripts\build_final_guarded_recheck_launcher.py",
    "scripts\build_final_guarded_recheck_execution_audit.py",
    "scripts\build_external_dependency_escalation_packet.py",
    "scripts\build_external_dependency_escalation_sendout_receipt_validator.py",
    "scripts\build_external_dependency_safe_send_execution_packet.py",
    "scripts\build_external_dependency_sendout_receipt_preservation_regression.py",
    "scripts\build_external_dependency_sendout_evidence_intake_preflight.py",
    "scripts\build_external_dependency_eds_guarded_writeback_applier.py",
    "scripts\build_external_dependency_post_writeback_revalidation_orchestrator.py",
    "scripts\build_fmr001_sendout_completion_writeback_preflight.py",
    "scripts\build_fmr001_guarded_writeback_applier.py",
    "scripts\build_fmr001_guarded_writeback_regression.py",
    "scripts\build_fmr002_author_decision_writeback_preflight.py",
    "scripts\build_fmr002_guarded_writeback_applier.py",
    "scripts\build_fmr002_guarded_writeback_regression.py",
    "scripts\build_fmr003_returned_evidence_writeback_preflight.py",
    "scripts\build_fmr003_guarded_writeback_applier.py",
    "scripts\build_fmr003_guarded_writeback_regression.py",
    "scripts\build_fmr004_figure_review_writeback_preflight.py",
    "scripts\build_fmr004_guarded_writeback_applier.py",
    "scripts\build_fmr004_guarded_writeback_regression.py",
    "scripts\build_fmr005_repository_rights_doi_writeback_preflight.py",
    "scripts\build_fmr005_guarded_writeback_applier.py",
    "scripts\build_fmr005_guarded_writeback_regression.py",
    "scripts\build_fmr006_guarded_recheck_receipt_writeback_preflight.py",
    "scripts\build_fmr006_guarded_writeback_applier.py",
    "scripts\build_fmr006_guarded_writeback_regression.py",
    "scripts\build_fmr_guarded_writeback_coverage_audit.py",
    "scripts\build_fmr_evidence_to_writeback_execution_order_audit.py",
    "scripts\build_fmr_manual_evidence_inbox_integrity_audit.py",
    "scripts\build_fmr_manual_evidence_operator_packet.py",
    "scripts\build_final_execution_board_20260810.py",
    "scripts\build_manual_only_execution_forms_20260810.py",
    "scripts\validate_manual_only_execution_forms_20260810.py",
    "scripts\build_manual_evidence_readiness_monitor_20260810.py",
    "scripts\build_manual_execution_brief_20260810.py",
    "scripts\validate_manual_execution_brief_acceptance_20260810.py",
    "scripts\watch_manual_evidence_arrival_20260810.py",
    "scripts\build_manual_evidence_route_snapshot_20260810.py",
    "scripts\build_daily_execution_status_capsule_20260810.py",
    "scripts\validate_daily_execution_capsule_reentry_20260810.py",
    "scripts\build_manual_action_backfill_template_audit_20260810.py",
    "scripts\guard_manual_form_validation_launcher_20260810.py",
    "scripts\build_external_manual_evidence_blocker_certificate_20260810.py",
    "scripts\check_manuscript_text_encoding.py",
    "external_blind\README_20260810.md",
    "data_manifests\external_blind_manifest_template_20260810.csv",
    "data_manifests\external_blind_label_holdout_template_20260810.csv",
    "data_manifests\external_blind_prediction_submission_template_20260810.csv",
    "reports\external_blind_intake_20260810\external_blind_intake_validation_summary.json",
    "reports\external_blind_intake_20260810\external_blind_intake_validation_summary.md",
    "reports\external_blind_locked_evaluation_20260810\external_blind_locked_evaluation_summary.json",
    "reports\external_blind_locked_evaluation_20260810\external_blind_locked_evaluation_summary.md",
    "reports\external_blind_locked_evaluation_20260810\external_blind_locked_evaluation_by_group.csv",
    "reports\manuscript_figure_table_plan_20260810\figure_table_plan_summary.json",
    "reports\manuscript_figure_table_plan_20260810\figure_table_plan_summary.md",
    "reports\manuscript_figure_table_plan_20260810\figure_table_claim_evidence_map.csv",
    "reports\figure2_table2_sources_20260810\figure2_source_data.csv",
    "reports\figure2_table2_sources_20260810\table2_model_family_support.csv",
    "reports\figure2_table2_sources_20260810\figure2_table2_source_summary.md",
    "reports\figure2_table2_sources_20260810\figure2_table2_source_summary.json",
    "reports\figure3_sources_20260810\figure3_hog_split_source_data.csv",
    "reports\figure3_sources_20260810\figure3_model_delta_source_data.csv",
    "reports\figure3_sources_20260810\figure3_claim_boundary.csv",
    "reports\figure3_sources_20260810\figure3_source_summary.md",
    "reports\figure3_sources_20260810\figure3_source_summary.json",
    "reports\figure4_sources_20260810\figure4_counterfactual_source_data.csv",
    "reports\figure4_sources_20260810\figure4_evidence_layer_boundary.csv",
    "reports\figure4_sources_20260810\figure4_source_summary.md",
    "reports\figure4_sources_20260810\figure4_source_summary.json",
    "reports\figure1_table1_sources_20260810\table1_asset_audit.csv",
    "reports\figure1_table1_sources_20260810\figure1_flow_source.csv",
    "reports\figure1_table1_sources_20260810\figure1_table1_source_summary.md",
    "reports\figure1_table1_sources_20260810\figure1_table1_source_summary.json",
    "reports\figure5_figure6_sources_20260810\figure5_4tu_feasibility_source_data.csv",
    "reports\figure5_figure6_sources_20260810\figure6_external_gate_source_data.csv",
    "reports\figure5_figure6_sources_20260810\figure5_figure6_source_summary.md",
    "reports\figure5_figure6_sources_20260810\figure5_figure6_source_summary.json",
    "reports\results_section_skeleton_20260810\results_paragraph_claim_evidence_map.csv",
    "reports\results_section_skeleton_20260810\results_section_skeleton.md",
    "reports\results_section_skeleton_20260810\results_section_skeleton.json",
    "reports\methods_section_skeleton_20260810\methods_module_map.csv",
    "reports\methods_section_skeleton_20260810\methods_section_skeleton.md",
    "reports\methods_section_skeleton_20260810\methods_section_skeleton.json",
    "reports\submission_package_skeleton_20260810\title_candidates.csv",
    "reports\submission_package_skeleton_20260810\submission_claim_evidence_map.csv",
    "reports\submission_package_skeleton_20260810\terminology_ledger.csv",
    "reports\submission_package_skeleton_20260810\title_abstract_significance.md",
    "reports\submission_package_skeleton_20260810\cover_letter_skeleton.md",
    "reports\submission_package_skeleton_20260810\submission_package_summary.json",
    "reports\companion_artifacts_skeleton_20260810\data_repository_plan.csv",
    "reports\companion_artifacts_skeleton_20260810\data_availability_skeleton.md",
    "reports\companion_artifacts_skeleton_20260810\code_availability_skeleton.md",
    "reports\companion_artifacts_skeleton_20260810\reporting_summary_checklist.csv",
    "reports\companion_artifacts_skeleton_20260810\reporting_summary_checklist.md",
    "reports\companion_artifacts_skeleton_20260810\companion_artifacts_summary.json",
    "reports\source_data_deposit_package_20260810\source_data_file_manifest.csv",
    "reports\source_data_deposit_package_20260810\figure_table_source_mapping.csv",
    "reports\source_data_deposit_package_20260810\SOURCE_DATA_README.md",
    "reports\source_data_deposit_package_20260810\source_data_deposit_summary.json",
    "reports\release_readiness_audit_20260810\release_file_audit.csv",
    "reports\release_readiness_audit_20260810\licence_and_rights_checklist.csv",
    "reports\release_readiness_audit_20260810\RELEASE_READINESS_README.md",
    "reports\release_readiness_audit_20260810\PUBLIC_RELEASE_README_SKELETON.md",
    "reports\release_readiness_audit_20260810\release_readiness_summary.json",
    "reports\sanitized_release_staging_20260810\sanitized_release_manifest.csv",
    "reports\sanitized_release_staging_20260810\SANITIZED_RELEASE_README.md",
    "reports\sanitized_release_staging_20260810\PUBLIC_RELEASE_README_SKELETON.md",
    "reports\sanitized_release_staging_20260810\sanitized_release_summary.json",
    "reports\manuscript_assembly_skeleton_20260810\manuscript_section_plan.csv",
    "reports\manuscript_assembly_skeleton_20260810\claim_section_traceability.csv",
    "reports\manuscript_assembly_skeleton_20260810\manuscript_blocker_checklist.csv",
    "reports\manuscript_assembly_skeleton_20260810\manuscript_assembly_skeleton.md",
    "reports\manuscript_assembly_skeleton_20260810\manuscript_assembly_summary.json",
    "reports\narrative_section_skeleton_20260810\introduction_paragraph_contracts.csv",
    "reports\narrative_section_skeleton_20260810\discussion_paragraph_contracts.csv",
    "reports\narrative_section_skeleton_20260810\conclusion_paragraph_contracts.csv",
    "reports\narrative_section_skeleton_20260810\narrative_claim_evidence_risk_map.csv",
    "reports\narrative_section_skeleton_20260810\narrative_section_skeleton.md",
    "reports\narrative_section_skeleton_20260810\narrative_section_summary.json",
    "reports\narrative_section_drafts_20260810\introduction_draft_v0.md",
    "reports\narrative_section_drafts_20260810\discussion_draft_v0.md",
    "reports\narrative_section_drafts_20260810\conclusion_draft_v0.md",
    "reports\narrative_section_drafts_20260810\narrative_section_drafts_v0.md",
    "reports\narrative_section_drafts_20260810\narrative_section_draft_paragraphs.csv",
    "reports\narrative_section_drafts_20260810\narrative_overclaim_scan.csv",
    "reports\narrative_section_drafts_20260810\narrative_section_drafts_summary.json",
    "reports\narrative_citation_pass_20260810\citation_need_segments.csv",
    "reports\narrative_citation_pass_20260810\citation_candidate_library.csv",
    "reports\narrative_citation_pass_20260810\narrative_citation_mapping.csv",
    "reports\narrative_citation_pass_20260810\references_narrative_citation_pass.ris",
    "reports\narrative_citation_pass_20260810\citation_pass_browser.html",
    "reports\narrative_citation_pass_20260810\citation_pass_report.md",
    "reports\narrative_citation_pass_20260810\citation_pass_summary.json",
    "reports\narrative_cited_drafts_20260810\introduction_draft_v1_cited.md",
    "reports\narrative_cited_drafts_20260810\discussion_draft_v1_cited.md",
    "reports\narrative_cited_drafts_20260810\conclusion_draft_v1_cited.md",
    "reports\narrative_cited_drafts_20260810\narrative_section_drafts_v1_cited.md",
    "reports\narrative_cited_drafts_20260810\citation_insertion_audit.csv",
    "reports\narrative_cited_drafts_20260810\unresolved_citation_and_pointer_items.csv",
    "reports\narrative_cited_drafts_20260810\narrative_cited_drafts_report.md",
    "reports\narrative_cited_drafts_20260810\narrative_cited_drafts_summary.json",
    "reports\figure_table_anchor_lock_20260810\figure_table_numbering_lock.csv",
    "reports\figure_table_anchor_lock_20260810\source_data_anchor_map.csv",
    "reports\figure_table_anchor_lock_20260810\narrative_pointer_resolution.csv",
    "reports\figure_table_anchor_lock_20260810\internal_metric_citation_map.csv",
    "reports\figure_table_anchor_lock_20260810\narrative_section_drafts_v1_anchored.md",
    "reports\figure_table_anchor_lock_20260810\figure_table_anchor_lock_report.md",
    "reports\figure_table_anchor_lock_20260810\figure_table_anchor_lock_summary.json",
    "reports\manuscript_table_drafts_20260810\table1_dataset_asset_audit_draft.csv",
    "reports\manuscript_table_drafts_20260810\table1_dataset_asset_audit_draft.md",
    "reports\manuscript_table_drafts_20260810\table2_model_family_support_draft.csv",
    "reports\manuscript_table_drafts_20260810\table2_model_family_support_draft.md",
    "reports\manuscript_table_drafts_20260810\table3_open_gates_draft.csv",
    "reports\manuscript_table_drafts_20260810\table3_open_gates_draft.md",
    "reports\manuscript_table_drafts_20260810\manuscript_table_drafts.md",
    "reports\manuscript_table_drafts_20260810\table_caption_and_boundary_audit.csv",
    "reports\manuscript_table_drafts_20260810\manuscript_table_drafts_report.md",
    "reports\manuscript_table_drafts_20260810\manuscript_table_drafts_summary.json",
    "reports\submission_readiness_dashboard_20260810\submission_readiness_dashboard.csv",
    "reports\submission_readiness_dashboard_20260810\open_gate_priority_queue.csv",
    "reports\submission_readiness_dashboard_20260810\milestone_completion_matrix.csv",
    "reports\submission_readiness_dashboard_20260810\submission_readiness_dashboard.md",
    "reports\submission_readiness_dashboard_20260810\submission_readiness_dashboard_summary.json",
    "reports\figure_rendering_spec_20260810\figure_rendering_spec.csv",
    "reports\figure_rendering_spec_20260810\figure_rendering_qa_checklist.csv",
    "reports\figure_rendering_spec_20260810\figure_rendering_priority_queue.csv",
    "reports\figure_rendering_spec_20260810\figure_rendering_spec.md",
    "reports\figure_rendering_spec_20260810\figure_rendering_spec_summary.json",
    "reports\blind_external_acquisition_package_20260810\external_blind_asset_request_letter.md",
    "reports\blind_external_acquisition_package_20260810\label_holder_sop.md",
    "reports\blind_external_acquisition_package_20260810\external_asset_request_items.csv",
    "reports\blind_external_acquisition_package_20260810\blind_handoff_checklist.csv",
    "reports\blind_external_acquisition_package_20260810\external_asset_rights_checklist.csv",
    "reports\blind_external_acquisition_package_20260810\BLIND_EXTERNAL_ACQUISITION_README.md",
    "reports\blind_external_acquisition_package_20260810\blind_external_acquisition_package_summary.json",
    "reports\external_asset_triage_register_20260810\external_asset_route_triage.csv",
    "reports\external_asset_triage_register_20260810\external_asset_acceptance_gates.csv",
    "reports\external_asset_triage_register_20260810\external_asset_contact_packet_queue.csv",
    "reports\external_asset_triage_register_20260810\external_asset_no_go_shortcuts.csv",
    "reports\external_asset_triage_register_20260810\external_asset_triage_register_qa.csv",
    "reports\external_asset_triage_register_20260810\EXTERNAL_ASSET_TRIAGE_REGISTER_README.md",
    "reports\external_asset_triage_register_20260810\external_asset_triage_register_report.md",
    "reports\external_asset_triage_register_20260810\external_asset_triage_register_summary.json",
    "reports\repository_metadata_package_20260810\repository_metadata_fields.csv",
    "reports\repository_metadata_package_20260810\release_inclusion_plan.csv",
    "reports\repository_metadata_package_20260810\release_exclusion_plan.csv",
    "reports\repository_metadata_package_20260810\licence_decision_matrix.csv",
    "reports\repository_metadata_package_20260810\CITATION.cff.draft",
    "reports\repository_metadata_package_20260810\zenodo_metadata_draft.json",
    "reports\repository_metadata_package_20260810\data_availability_update_draft.md",
    "reports\repository_metadata_package_20260810\code_availability_update_draft.md",
    "reports\repository_metadata_package_20260810\REPOSITORY_METADATA_README.md",
    "reports\repository_metadata_package_20260810\repository_metadata_package_summary.json",
    "reports\repository_release_manifest_lock_20260810\repository_release_manifest_lock.csv",
    "reports\repository_release_manifest_lock_20260810\release_category_lock_summary.csv",
    "reports\repository_release_manifest_lock_20260810\release_exclusion_lock.csv",
    "reports\repository_release_manifest_lock_20260810\doi_metadata_predeposit_lock.csv",
    "reports\repository_release_manifest_lock_20260810\rights_and_licence_release_blockers.csv",
    "reports\repository_release_manifest_lock_20260810\availability_release_crosswalk.csv",
    "reports\repository_release_manifest_lock_20260810\repository_release_manifest_lock_qa.csv",
    "reports\repository_release_manifest_lock_20260810\REPOSITORY_RELEASE_MANIFEST_LOCK_README.md",
    "reports\repository_release_manifest_lock_20260810\repository_release_manifest_lock_report.md",
    "reports\repository_release_manifest_lock_20260810\repository_release_manifest_lock_summary.json",
    "reports\release_delta_sync_audit_20260810\release_delta_sync_matrix.csv",
    "reports\release_delta_sync_audit_20260810\release_delta_inclusion_decisions.csv",
    "reports\release_delta_sync_audit_20260810\release_delta_sync_qa.csv",
    "reports\release_delta_sync_audit_20260810\release_delta_sync_report.md",
    "reports\release_delta_sync_audit_20260810\release_delta_sync_summary.json",
    "reports\repository_predeposit_handoff_20260810\repository_platform_metadata_prefill.csv",
    "reports\repository_predeposit_handoff_20260810\repository_file_upload_queue.csv",
    "reports\repository_predeposit_handoff_20260810\repository_rights_licence_action_register.csv",
    "reports\repository_predeposit_handoff_20260810\repository_availability_deposit_crosswalk.csv",
    "reports\repository_predeposit_handoff_20260810\repository_predeposit_handoff_qa.csv",
    "reports\repository_predeposit_handoff_20260810\REPOSITORY_PREDEPOSIT_HANDOFF_README.md",
    "reports\repository_predeposit_handoff_20260810\repository_predeposit_handoff_report.md",
    "reports\repository_predeposit_handoff_20260810\repository_predeposit_handoff_summary.json",
    "reports\rights_licence_completion_handoff_20260810\rights_licence_decision_matrix.csv",
    "reports\rights_licence_completion_handoff_20260810\rights_availability_dependency_map.csv",
    "reports\rights_licence_completion_handoff_20260810\rights_release_action_queue.csv",
    "reports\rights_licence_completion_handoff_20260810\rights_no_go_shortcuts.csv",
    "reports\rights_licence_completion_handoff_20260810\rights_completion_command_queue.csv",
    "reports\rights_licence_completion_handoff_20260810\rights_licence_completion_handoff_qa.csv",
    "reports\rights_licence_completion_handoff_20260810\RIGHTS_LICENCE_COMPLETION_HANDOFF_README.md",
    "reports\rights_licence_completion_handoff_20260810\rights_licence_completion_handoff_report.md",
    "reports\rights_licence_completion_handoff_20260810\rights_licence_completion_handoff_summary.json",
    "reports\reporting_summary_draft_20260810\reporting_summary_draft_answers.csv",
    "reports\reporting_summary_draft_20260810\reporting_summary_unresolved_items.csv",
    "reports\reporting_summary_draft_20260810\reporting_summary_method_trace.csv",
    "reports\reporting_summary_draft_20260810\reporting_summary_draft.md",
    "reports\reporting_summary_draft_20260810\reporting_summary_draft_report.md",
    "reports\reporting_summary_draft_20260810\reporting_summary_draft_summary.json",
    "reports\author_decision_intake_package_20260810\author_decision_register.csv",
    "reports\author_decision_intake_package_20260810\decision_dependency_map.csv",
    "reports\author_decision_intake_package_20260810\next_author_actions.csv",
    "reports\author_decision_intake_package_20260810\author_decision_intake.md",
    "reports\author_decision_intake_package_20260810\author_decision_intake_report.md",
    "reports\author_decision_intake_package_20260810\author_decision_intake_summary.json",
    "reports\author_action_packet_20260810\author_decision_form_cn.csv",
    "reports\author_action_packet_20260810\next_72h_author_actions.csv",
    "reports\author_action_packet_20260810\external_blind_request_email_draft.md",
    "reports\author_action_packet_20260810\coauthor_decision_checklist.md",
    "reports\author_action_packet_20260810\author_action_one_page_cn.md",
    "reports\author_action_packet_20260810\author_action_packet_report.md",
    "reports\author_action_packet_20260810\author_action_packet_summary.json",
    "reports\submission_gap_closure_matrix_20260810\submission_gap_closure_matrix.csv",
    "reports\submission_gap_closure_matrix_20260810\minimum_evidence_requirements.csv",
    "reports\submission_gap_closure_matrix_20260810\next_execution_order.csv",
    "reports\submission_gap_closure_matrix_20260810\submission_no_go_statement.md",
    "reports\submission_gap_closure_matrix_20260810\submission_gap_closure_matrix.md",
    "reports\submission_gap_closure_matrix_20260810\submission_gap_closure_report.md",
    "reports\submission_gap_closure_matrix_20260810\submission_gap_closure_summary.json",
    "reports\manuscript_claim_readiness_audit_20260810\manuscript_claim_readiness_audit.csv",
    "reports\manuscript_claim_readiness_audit_20260810\forbidden_claims_ledger.csv",
    "reports\manuscript_claim_readiness_audit_20260810\abstract_claim_guardrails.csv",
    "reports\manuscript_claim_readiness_audit_20260810\allowed_manuscript_claims.md",
    "reports\manuscript_claim_readiness_audit_20260810\manuscript_claim_readiness_report.md",
    "reports\manuscript_claim_readiness_audit_20260810\manuscript_claim_readiness_summary.json",
    "reports\conservative_manuscript_draft_20260810\conservative_manuscript_draft_v0_1.md",
    "reports\conservative_manuscript_draft_20260810\title_candidates_v0_1.csv",
    "reports\conservative_manuscript_draft_20260810\terminology_ledger_v0_1.csv",
    "reports\conservative_manuscript_draft_20260810\paragraph_map_v0_1.csv",
    "reports\conservative_manuscript_draft_20260810\draft_claim_trace_v0_1.csv",
    "reports\conservative_manuscript_draft_20260810\draft_boundary_qa_v0_1.csv",
    "reports\conservative_manuscript_draft_20260810\conservative_manuscript_draft_report.md",
    "reports\conservative_manuscript_draft_20260810\conservative_manuscript_draft_summary.json",
    "reports\conservative_methods_draft_20260810\methods_draft_v0_1.md",
    "reports\conservative_methods_draft_20260810\methods_module_trace_v0_1.csv",
    "reports\conservative_methods_draft_20260810\methods_word_budget_v0_1.csv",
    "reports\conservative_methods_draft_20260810\methods_boundary_qa_v0_1.csv",
    "reports\conservative_methods_draft_20260810\methods_draft_report.md",
    "reports\conservative_methods_draft_20260810\methods_draft_summary.json",
    "reports\author_review_manuscript_package_20260810\author_review_manuscript_v0_1.md",
    "reports\author_review_manuscript_package_20260810\author_review_section_word_budget.csv",
    "reports\author_review_manuscript_package_20260810\author_review_manuscript_qa.csv",
    "reports\author_review_manuscript_package_20260810\author_review_open_gate_impact.csv",
    "reports\author_review_manuscript_package_20260810\author_review_manuscript_report.md",
    "reports\author_review_manuscript_package_20260810\author_review_manuscript_summary.json",
    "reports\pre_submission_reviewer_risk_audit_20260810\review_fact_base.json",
    "reports\pre_submission_reviewer_risk_audit_20260810\pre_submission_reviewer_reports.md",
    "reports\pre_submission_reviewer_risk_audit_20260810\reviewer_risk_priority_queue.csv",
    "reports\pre_submission_reviewer_risk_audit_20260810\review_axis_assessment.csv",
    "reports\pre_submission_reviewer_risk_audit_20260810\reviewer_audit_qa.csv",
    "reports\pre_submission_reviewer_risk_audit_20260810\reviewer_risk_audit_report.md",
    "reports\pre_submission_reviewer_risk_audit_20260810\reviewer_risk_audit_summary.json",
    "reports\reviewer_risk_revision_action_packet_20260810\reviewer_risk_to_action_matrix.csv",
    "reports\reviewer_risk_revision_action_packet_20260810\next_14_day_revision_sprint.csv",
    "reports\reviewer_risk_revision_action_packet_20260810\manuscript_revision_instructions.md",
    "reports\reviewer_risk_revision_action_packet_20260810\evidence_closure_acceptance_tests.csv",
    "reports\reviewer_risk_revision_action_packet_20260810\decision_escalation_sheet.csv",
    "reports\reviewer_risk_revision_action_packet_20260810\reviewer_risk_revision_action_packet_report.md",
    "reports\reviewer_risk_revision_action_packet_20260810\reviewer_risk_revision_action_packet_summary.json",
    "reports\broad_interest_framing_revision_20260810\broad_interest_title_candidates.csv",
    "reports\broad_interest_framing_revision_20260810\broad_interest_abstract_revision.md",
    "reports\broad_interest_framing_revision_20260810\broad_interest_intro_opening_revision.md",
    "reports\broad_interest_framing_revision_20260810\workflow_schematic_caption_draft.md",
    "reports\broad_interest_framing_revision_20260810\framing_claim_evidence_boundary.csv",
    "reports\broad_interest_framing_revision_20260810\broad_interest_framing_qa.csv",
    "reports\broad_interest_framing_revision_20260810\broad_interest_framing_revision_report.md",
    "reports\broad_interest_framing_revision_20260810\broad_interest_framing_revision_summary.json",
    "reports\reference_numbering_prelock_20260810\manuscript_candidate_marker_inventory.csv",
    "reports\reference_numbering_prelock_20260810\reference_numbering_prelock.csv",
    "reports\reference_numbering_prelock_20260810\reference_candidate_verification_table.csv",
    "reports\reference_numbering_prelock_20260810\unresolved_reference_lock_actions.csv",
    "reports\reference_numbering_prelock_20260810\reference_prelock_qa.csv",
    "reports\reference_numbering_prelock_20260810\REFERENCE_PRELOCK_README.md",
    "reports\reference_numbering_prelock_20260810\reference_numbering_prelock_report.md",
    "reports\reference_numbering_prelock_20260810\reference_numbering_prelock_summary.json",
    "reports\reference_public_verification_20260810\public_reference_metadata_verification.csv",
    "reports\reference_public_verification_20260810\current_manuscript_reference_order_verified_prelock.csv",
    "reports\reference_public_verification_20260810\reference_support_boundary_audit.csv",
    "reports\reference_public_verification_20260810\reference_final_lock_remaining_actions.csv",
    "reports\reference_public_verification_20260810\candidate_references_prelock.ris",
    "reports\reference_public_verification_20260810\candidate_references_prelock.enw",
    "reports\reference_public_verification_20260810\REFERENCE_PUBLIC_VERIFICATION_README.md",
    "reports\reference_public_verification_20260810\reference_public_verification_report.md",
    "reports\reference_public_verification_20260810\reference_public_verification_summary.json",
    "reports\sentence_citation_support_lock_20260810\sentence_citation_support_lock.csv",
    "reports\sentence_citation_support_lock_20260810\citation_marker_replacement_plan.csv",
    "reports\sentence_citation_support_lock_20260810\citation_overclaim_guardrails.csv",
    "reports\sentence_citation_support_lock_20260810\sentence_citation_support_lock_qa.csv",
    "reports\sentence_citation_support_lock_20260810\SENTENCE_CITATION_SUPPORT_LOCK_README.md",
    "reports\sentence_citation_support_lock_20260810\sentence_citation_support_lock_report.md",
    "reports\sentence_citation_support_lock_20260810\sentence_citation_support_lock_summary.json",
    "reports\reference_completion_handoff_20260810\reference_completion_matrix.csv",
    "reports\reference_completion_handoff_20260810\citation_marker_final_replacement_queue.csv",
    "reports\reference_completion_handoff_20260810\reference_manual_verification_queue.csv",
    "reports\reference_completion_handoff_20260810\reference_export_finalization_queue.csv",
    "reports\reference_completion_handoff_20260810\reference_no_go_shortcuts.csv",
    "reports\reference_completion_handoff_20260810\reference_completion_handoff_qa.csv",
    "reports\reference_completion_handoff_20260810\REFERENCE_COMPLETION_HANDOFF_README.md",
    "reports\reference_completion_handoff_20260810\reference_completion_handoff_report.md",
    "reports\reference_completion_handoff_20260810\reference_completion_handoff_summary.json",
    "reports\reference_final_lock_validator_20260810\reference_final_lock_gate_matrix.csv",
    "reports\reference_final_lock_validator_20260810\reference_final_lock_blockers.csv",
    "reports\reference_final_lock_validator_20260810\reference_final_lock_command_queue.csv",
    "reports\reference_final_lock_validator_20260810\reference_final_lock_no_go_rules.csv",
    "reports\reference_final_lock_validator_20260810\reference_final_lock_validator_qa.csv",
    "reports\reference_final_lock_validator_20260810\REFERENCE_FINAL_LOCK_VALIDATOR_README.md",
    "reports\reference_final_lock_validator_20260810\reference_final_lock_validator_report.md",
    "reports\reference_final_lock_validator_20260810\reference_final_lock_validator_summary.json",
    "reports\availability_statement_prelock_20260810\availability_access_route_matrix.csv",
    "reports\availability_statement_prelock_20260810\data_availability_statement_variants.csv",
    "reports\availability_statement_prelock_20260810\code_availability_statement_variants.csv",
    "reports\availability_statement_prelock_20260810\availability_statement_gate_requirements.csv",
    "reports\availability_statement_prelock_20260810\fair_metadata_prelock_checklist.csv",
    "reports\availability_statement_prelock_20260810\availability_statement_prelock_qa.csv",
    "reports\availability_statement_prelock_20260810\AVAILABILITY_PRELOCK_README.md",
    "reports\availability_statement_prelock_20260810\availability_statement_prelock_report.md",
    "reports\availability_statement_prelock_20260810\availability_statement_prelock_summary.json",
    "reports\availability_repository_finalization_validator_20260810\availability_repository_final_gate_matrix.csv",
    "reports\availability_repository_finalization_validator_20260810\availability_repository_blockers.csv",
    "reports\availability_repository_finalization_validator_20260810\availability_statement_usable_variant_matrix.csv",
    "reports\availability_repository_finalization_validator_20260810\availability_repository_command_queue.csv",
    "reports\availability_repository_finalization_validator_20260810\availability_repository_finalization_validator_qa.csv",
    "reports\availability_repository_finalization_validator_20260810\AVAILABILITY_REPOSITORY_FINALIZATION_VALIDATOR_README.md",
    "reports\availability_repository_finalization_validator_20260810\availability_repository_finalization_validator_report.md",
    "reports\availability_repository_finalization_validator_20260810\availability_repository_finalization_validator_summary.json",
    "reports\reporting_summary_finalization_prelock_20260810\reporting_summary_final_lock_matrix.csv",
    "reports\reporting_summary_finalization_prelock_20260810\reporting_summary_author_confirmation_checklist.csv",
    "reports\reporting_summary_finalization_prelock_20260810\reporting_summary_forbidden_final_wording.csv",
    "reports\reporting_summary_finalization_prelock_20260810\reporting_summary_availability_gate_crosswalk.csv",
    "reports\reporting_summary_finalization_prelock_20260810\reporting_summary_prelock_qa.csv",
    "reports\reporting_summary_finalization_prelock_20260810\REPORTING_SUMMARY_PRELOCK_README.md",
    "reports\reporting_summary_finalization_prelock_20260810\reporting_summary_finalization_prelock_report.md",
    "reports\reporting_summary_finalization_prelock_20260810\reporting_summary_finalization_prelock_summary.json",
    "reports\reporting_summary_final_lock_validator_20260810\reporting_summary_final_lock_gate_matrix.csv",
    "reports\reporting_summary_final_lock_validator_20260810\reporting_summary_item_final_lock_status.csv",
    "reports\reporting_summary_final_lock_validator_20260810\reporting_summary_final_lock_blockers.csv",
    "reports\reporting_summary_final_lock_validator_20260810\reporting_summary_final_lock_command_queue.csv",
    "reports\reporting_summary_final_lock_validator_20260810\reporting_summary_final_lock_validator_qa.csv",
    "reports\reporting_summary_final_lock_validator_20260810\reporting_summary_forbidden_final_wording_import.csv",
    "reports\reporting_summary_final_lock_validator_20260810\REPORTING_SUMMARY_FINAL_LOCK_VALIDATOR_README.md",
    "reports\reporting_summary_final_lock_validator_20260810\reporting_summary_final_lock_validator_report.md",
    "reports\reporting_summary_final_lock_validator_20260810\reporting_summary_final_lock_validator_summary.json",
    "reports\external_validation_contingency_framing_20260810\external_validation_branch_decision_matrix.csv",
    "reports\external_validation_contingency_framing_20260810\contingency_title_set.csv",
    "reports\external_validation_contingency_framing_20260810\track_a_external_validated_abstract_scaffold.md",
    "reports\external_validation_contingency_framing_20260810\track_b_no_external_validation_abstract.md",
    "reports\external_validation_contingency_framing_20260810\discussion_boundary_insertions.csv",
    "reports\external_validation_contingency_framing_20260810\external_validation_no_go_wording.csv",
    "reports\external_validation_contingency_framing_20260810\external_validation_contingency_qa.csv",
    "reports\external_validation_contingency_framing_20260810\EXTERNAL_VALIDATION_CONTINGENCY_README.md",
    "reports\external_validation_contingency_framing_20260810\external_validation_contingency_framing_report.md",
    "reports\external_validation_contingency_framing_20260810\external_validation_contingency_framing_summary.json",
    "reports\track_b_manuscript_branch_prelock_20260810\track_b_one_sentence_argument.md",
    "reports\track_b_manuscript_branch_prelock_20260810\track_b_title_candidates.csv",
    "reports\track_b_manuscript_branch_prelock_20260810\track_b_abstract_prelock.md",
    "reports\track_b_manuscript_branch_prelock_20260810\track_b_branch_lock_matrix.csv",
    "reports\track_b_manuscript_branch_prelock_20260810\track_b_section_prelock_actions.csv",
    "reports\track_b_manuscript_branch_prelock_20260810\track_b_claim_role_lock.csv",
    "reports\track_b_manuscript_branch_prelock_20260810\track_b_forbidden_upgrade_ledger.csv",
    "reports\track_b_manuscript_branch_prelock_20260810\track_b_manuscript_branch_prelock.md",
    "reports\track_b_manuscript_branch_prelock_20260810\track_b_branch_prelock_qa.csv",
    "reports\track_b_manuscript_branch_prelock_20260810\TRACK_B_MANUSCRIPT_BRANCH_PRELOCK_README.md",
    "reports\track_b_manuscript_branch_prelock_20260810\track_b_manuscript_branch_prelock_report.md",
    "reports\track_b_manuscript_branch_prelock_20260810\track_b_manuscript_branch_prelock_summary.json",
    "reports\submission_command_dashboard_v2_20260810\submission_command_dashboard_v2.csv",
    "reports\submission_command_dashboard_v2_20260810\current_branch_and_decision_register.csv",
    "reports\submission_command_dashboard_v2_20260810\global_forbidden_claims_dashboard.csv",
    "reports\submission_command_dashboard_v2_20260810\prelock_artifact_status_register.csv",
    "reports\submission_command_dashboard_v2_20260810\submission_command_dashboard_v2.md",
    "reports\submission_command_dashboard_v2_20260810\submission_command_dashboard_v2_qa.csv",
    "reports\submission_command_dashboard_v2_20260810\submission_command_dashboard_v2_report.md",
    "reports\submission_command_dashboard_v2_20260810\submission_command_dashboard_v2_summary.json",
    "reports\natcomms_submission_assembly_preflight_20260810\natcomms_submission_item_preflight.csv",
    "reports\natcomms_submission_assembly_preflight_20260810\submission_hard_blocker_register.csv",
    "reports\natcomms_submission_assembly_preflight_20260810\submission_assembly_execution_order.csv",
    "reports\natcomms_submission_assembly_preflight_20260810\natcomms_format_budget_preflight.csv",
    "reports\natcomms_submission_assembly_preflight_20260810\natcomms_submission_assembly_preflight_qa.csv",
    "reports\natcomms_submission_assembly_preflight_20260810\NATCOMMS_SUBMISSION_ASSEMBLY_PREFLIGHT_README.md",
    "reports\natcomms_submission_assembly_preflight_20260810\natcomms_submission_assembly_preflight_report.md",
    "reports\natcomms_submission_assembly_preflight_20260810\natcomms_submission_assembly_preflight_summary.json",
    "reports\natcomms_cover_letter_prelock_20260810\natcomms_cover_letter_prelock.md",
    "reports\natcomms_cover_letter_prelock_20260810\editor_pitch_sentence_map.csv",
    "reports\natcomms_cover_letter_prelock_20260810\cover_letter_finalization_checklist.csv",
    "reports\natcomms_cover_letter_prelock_20260810\cover_letter_forbidden_language.csv",
    "reports\natcomms_cover_letter_prelock_20260810\natcomms_cover_letter_prelock_qa.csv",
    "reports\natcomms_cover_letter_prelock_20260810\NATCOMMS_COVER_LETTER_PRELOCK_README.md",
    "reports\natcomms_cover_letter_prelock_20260810\natcomms_cover_letter_prelock_report.md",
    "reports\natcomms_cover_letter_prelock_20260810\natcomms_cover_letter_prelock_summary.json",
    "reports\natcomms_initial_submission_text_preassembly_20260810\natcomms_initial_submission_text_preassembly.md",
    "reports\natcomms_initial_submission_text_preassembly_20260810\natcomms_text_word_budget.csv",
    "reports\natcomms_initial_submission_text_preassembly_20260810\natcomms_display_item_preassembly.csv",
    "reports\natcomms_initial_submission_text_preassembly_20260810\natcomms_text_open_gate_matrix.csv",
    "reports\natcomms_initial_submission_text_preassembly_20260810\natcomms_companion_statement_queue.csv",
    "reports\natcomms_initial_submission_text_preassembly_20260810\natcomms_text_preassembly_qa.csv",
    "reports\natcomms_initial_submission_text_preassembly_20260810\NATCOMMS_TEXT_PREASSEMBLY_README.md",
    "reports\natcomms_initial_submission_text_preassembly_20260810\natcomms_text_preassembly_report.md",
    "reports\natcomms_initial_submission_text_preassembly_20260810\natcomms_text_preassembly_summary.json",
    "reports\natcomms_supplementary_info_preassembly_20260810\supplementary_information_preassembly.md",
    "reports\natcomms_supplementary_info_preassembly_20260810\supplementary_information_toc.csv",
    "reports\natcomms_supplementary_info_preassembly_20260810\supplementary_methods_module_map.csv",
    "reports\natcomms_supplementary_info_preassembly_20260810\main_text_to_supplement_crosswalk.csv",
    "reports\natcomms_supplementary_info_preassembly_20260810\figure_to_supplement_role_map.csv",
    "reports\natcomms_supplementary_info_preassembly_20260810\supplementary_source_data_boundary_map.csv",
    "reports\natcomms_supplementary_info_preassembly_20260810\supplementary_open_gate_ledger.csv",
    "reports\natcomms_supplementary_info_preassembly_20260810\supplementary_info_preassembly_qa.csv",
    "reports\natcomms_supplementary_info_preassembly_20260810\NATCOMMS_SUPPLEMENTARY_INFO_PREASSEMBLY_README.md",
    "reports\natcomms_supplementary_info_preassembly_20260810\supplementary_info_preassembly_report.md",
    "reports\natcomms_supplementary_info_preassembly_20260810\supplementary_info_preassembly_summary.json",
    "reports\r4_manuscript_boundary_sync_audit_20260810\r4_manuscript_boundary_sync_audit.csv",
    "reports\r4_manuscript_boundary_sync_audit_20260810\r4_boundary_sync_qa.csv",
    "reports\r4_manuscript_boundary_sync_audit_20260810\r4_manuscript_boundary_sync_report.md",
    "reports\r4_manuscript_boundary_sync_audit_20260810\r4_manuscript_boundary_sync_summary.json",
    "reports\natcomms_admin_declarations_prelock_20260810\official_submission_admin_source_check.csv",
    "reports\natcomms_admin_declarations_prelock_20260810\title_page_field_prelock.csv",
    "reports\natcomms_admin_declarations_prelock_20260810\title_page_prelock.md",
    "reports\natcomms_admin_declarations_prelock_20260810\author_contribution_intake_matrix.csv",
    "reports\natcomms_admin_declarations_prelock_20260810\admin_declarations_prelock.csv",
    "reports\natcomms_admin_declarations_prelock_20260810\admin_declarations_prelock.md",
    "reports\natcomms_admin_declarations_prelock_20260810\cover_letter_admin_crosscheck.csv",
    "reports\natcomms_admin_declarations_prelock_20260810\reviewer_suggestion_intake.csv",
    "reports\natcomms_admin_declarations_prelock_20260810\editorial_policy_decision_prelock.csv",
    "reports\natcomms_admin_declarations_prelock_20260810\admin_declarations_prelock_qa.csv",
    "reports\natcomms_admin_declarations_prelock_20260810\NATCOMMS_ADMIN_DECLARATIONS_PRELOCK_README.md",
    "reports\natcomms_admin_declarations_prelock_20260810\admin_declarations_prelock_report.md",
    "reports\natcomms_admin_declarations_prelock_20260810\admin_declarations_prelock_summary.json",
    "reports\natcomms_portal_upload_manifest_prelock_20260810\portal_upload_item_manifest.csv",
    "reports\natcomms_portal_upload_manifest_prelock_20260810\portal_stage_upload_strategy.csv",
    "reports\natcomms_portal_upload_manifest_prelock_20260810\portal_blocker_crosswalk.csv",
    "reports\natcomms_portal_upload_manifest_prelock_20260810\portal_upload_finalization_order.csv",
    "reports\natcomms_portal_upload_manifest_prelock_20260810\portal_upload_official_rule_sources.csv",
    "reports\natcomms_portal_upload_manifest_prelock_20260810\portal_upload_manifest_qa.csv",
    "reports\natcomms_portal_upload_manifest_prelock_20260810\portal_upload_manifest_prelock.md",
    "reports\natcomms_portal_upload_manifest_prelock_20260810\NATCOMMS_PORTAL_UPLOAD_MANIFEST_PRELOCK_README.md",
    "reports\natcomms_portal_upload_manifest_prelock_20260810\portal_upload_manifest_report.md",
    "reports\natcomms_portal_upload_manifest_prelock_20260810\portal_upload_manifest_summary.json",
    "reports\natcomms_finalization_master_checklist_20260810\finalization_master_checklist.csv",
    "reports\natcomms_finalization_master_checklist_20260810\owner_action_master_queue.csv",
    "reports\natcomms_finalization_master_checklist_20260810\finalization_dependency_graph.csv",
    "reports\natcomms_finalization_master_checklist_20260810\finalization_forbidden_claims_master.csv",
    "reports\natcomms_finalization_master_checklist_20260810\finalization_master_checklist_qa.csv",
    "reports\natcomms_finalization_master_checklist_20260810\finalization_master_checklist.md",
    "reports\natcomms_finalization_master_checklist_20260810\NATCOMMS_FINALIZATION_MASTER_CHECKLIST_README.md",
    "reports\natcomms_finalization_master_checklist_20260810\finalization_master_checklist_report.md",
    "reports\natcomms_finalization_master_checklist_20260810\finalization_master_checklist_summary.json",
    "reports\natcomms_author_finalization_reply_packet_20260810\author_finalization_reply_form_cn.csv",
    "reports\natcomms_author_finalization_reply_packet_20260810\corresponding_author_metadata_form.csv",
    "reports\natcomms_author_finalization_reply_packet_20260810\figure_backend_decision_ticket.csv",
    "reports\natcomms_author_finalization_reply_packet_20260810\track_branch_and_external_validation_reply.csv",
    "reports\natcomms_author_finalization_reply_packet_20260810\licence_rights_reply_sheet.csv",
    "reports\natcomms_author_finalization_reply_packet_20260810\reviewer_and_policy_reply_sheet.csv",
    "reports\natcomms_author_finalization_reply_packet_20260810\reporting_summary_author_reply_sheet.csv",
    "reports\natcomms_author_finalization_reply_packet_20260810\coauthor_finalization_email_cn.md",
    "reports\natcomms_author_finalization_reply_packet_20260810\author_reply_packet_qa.csv",
    "reports\natcomms_author_finalization_reply_packet_20260810\NATCOMMS_AUTHOR_FINALIZATION_REPLY_PACKET_README.md",
    "reports\natcomms_author_finalization_reply_packet_20260810\author_finalization_reply_packet_report.md",
    "reports\natcomms_author_finalization_reply_packet_20260810\author_finalization_reply_packet_summary.json",
    "reports\natcomms_author_reply_ingestion_validator_20260810\author_reply_ingestion_validation.csv",
    "reports\natcomms_author_reply_ingestion_validator_20260810\gate_closure_from_author_replies.csv",
    "reports\natcomms_author_reply_ingestion_validator_20260810\ancillary_reply_sheet_ingestion_status.csv",
    "reports\natcomms_author_reply_ingestion_validator_20260810\author_reply_evidence_rules.csv",
    "reports\natcomms_author_reply_ingestion_validator_20260810\author_reply_ingestion_validator_qa.csv",
    "reports\natcomms_author_reply_ingestion_validator_20260810\NATCOMMS_AUTHOR_REPLY_INGESTION_VALIDATOR_README.md",
    "reports\natcomms_author_reply_ingestion_validator_20260810\author_reply_ingestion_validator_report.md",
    "reports\natcomms_author_reply_ingestion_validator_20260810\author_reply_ingestion_validator_summary.json",
    "reports\natcomms_gate_closure_evidence_binder_20260810\gate_artifact_evidence_requirements.csv",
    "reports\natcomms_gate_closure_evidence_binder_20260810\gate_closure_evidence_binder.csv",
    "reports\natcomms_gate_closure_evidence_binder_20260810\gate_closure_execution_order.csv",
    "reports\natcomms_gate_closure_evidence_binder_20260810\gate_closure_forbidden_shortcuts.csv",
    "reports\natcomms_gate_closure_evidence_binder_20260810\gate_closure_evidence_binder_qa.csv",
    "reports\natcomms_gate_closure_evidence_binder_20260810\NATCOMMS_GATE_CLOSURE_EVIDENCE_BINDER_README.md",
    "reports\natcomms_gate_closure_evidence_binder_20260810\gate_closure_evidence_binder_report.md",
    "reports\natcomms_gate_closure_evidence_binder_20260810\gate_closure_evidence_binder_summary.json",
    "reports\natcomms_finalization_command_dashboard_v3_20260810\finalization_command_dashboard_v3.csv",
    "reports\natcomms_finalization_command_dashboard_v3_20260810\portal_upload_command_overlay.csv",
    "reports\natcomms_finalization_command_dashboard_v3_20260810\critical_path_command_queue.csv",
    "reports\natcomms_finalization_command_dashboard_v3_20260810\finalization_no_go_register_v3.csv",
    "reports\natcomms_finalization_command_dashboard_v3_20260810\finalization_command_dashboard_v3.md",
    "reports\natcomms_finalization_command_dashboard_v3_20260810\finalization_command_dashboard_v3_qa.csv",
    "reports\natcomms_finalization_command_dashboard_v3_20260810\NATCOMMS_FINALIZATION_COMMAND_DASHBOARD_V3_README.md",
    "reports\natcomms_finalization_command_dashboard_v3_20260810\finalization_command_dashboard_v3_report.md",
    "reports\natcomms_finalization_command_dashboard_v3_20260810\finalization_command_dashboard_v3_summary.json",
    "reports\natcomms_submission_final_lock_validator_20260810\natcomms_submission_final_lock_gate_matrix.csv",
    "reports\natcomms_submission_final_lock_validator_20260810\natcomms_submission_final_lock_blockers.csv",
    "reports\natcomms_submission_final_lock_validator_20260810\natcomms_submission_final_lock_command_queue.csv",
    "reports\natcomms_submission_final_lock_validator_20260810\natcomms_submission_final_lock_portal_overlay.csv",
    "reports\natcomms_submission_final_lock_validator_20260810\natcomms_submission_final_lock_qa.csv",
    "reports\natcomms_submission_final_lock_validator_20260810\NATCOMMS_SUBMISSION_FINAL_LOCK_VALIDATOR_README.md",
    "reports\natcomms_submission_final_lock_validator_20260810\natcomms_submission_final_lock_validator_report.md",
    "reports\natcomms_submission_final_lock_validator_20260810\natcomms_submission_final_lock_validator_summary.json",
    "reports\manual_evidence_final_intake_validator_20260810\manual_evidence_final_intake_gate_matrix.csv",
    "reports\manual_evidence_final_intake_validator_20260810\manual_evidence_final_intake_status.csv",
    "reports\manual_evidence_final_intake_validator_20260810\manual_evidence_safe_edit_matrix.csv",
    "reports\manual_evidence_final_intake_validator_20260810\manual_evidence_final_intake_blockers.csv",
    "reports\manual_evidence_final_intake_validator_20260810\manual_evidence_final_intake_qa.csv",
    "reports\manual_evidence_final_intake_validator_20260810\MANUAL_EVIDENCE_FINAL_INTAKE_VALIDATOR_README.md",
    "reports\manual_evidence_final_intake_validator_20260810\manual_evidence_final_intake_validator_report.md",
    "reports\manual_evidence_final_intake_validator_20260810\manual_evidence_final_intake_validator_summary.json",
    "reports\final_human_execution_closeout_board_20260810\final_human_execution_action_queue.csv",
    "reports\final_human_execution_closeout_board_20260810\final_human_execution_evidence_matrix.csv",
    "reports\final_human_execution_closeout_board_20260810\final_human_execution_no_go_rules.csv",
    "reports\final_human_execution_closeout_board_20260810\final_human_execution_dependency_order.csv",
    "reports\final_human_execution_closeout_board_20260810\final_human_execution_closeout_qa.csv",
    "reports\final_human_execution_closeout_board_20260810\FINAL_HUMAN_EXECUTION_CLOSEOUT_BOARD_README.md",
    "reports\final_human_execution_closeout_board_20260810\final_human_execution_closeout_board_report.md",
    "reports\final_human_execution_closeout_board_20260810\final_human_execution_closeout_board_summary.json",
    "reports\final_human_execution_handoff_packet_20260810\final_human_execution_handoff_manifest.csv",
    "reports\final_human_execution_handoff_packet_20260810\final_human_execution_return_routing.csv",
    "reports\final_human_execution_handoff_packet_20260810\final_human_execution_operator_checklist.csv",
    "reports\final_human_execution_handoff_packet_20260810\final_human_execution_validation_commands.csv",
    "reports\final_human_execution_handoff_packet_20260810\final_human_execution_packet_no_go_rules.csv",
    "reports\final_human_execution_handoff_packet_20260810\final_human_execution_handoff_packet_qa.csv",
    "reports\final_human_execution_handoff_packet_20260810\FINAL_HUMAN_EXECUTION_HANDOFF_PACKET_README.md",
    "reports\final_human_execution_handoff_packet_20260810\final_human_execution_handoff_packet_report.md",
    "reports\final_human_execution_handoff_packet_20260810\final_human_execution_handoff_packet_summary.json",
    "reports\final_human_execution_handoff_packet_20260810\NatComms_final_human_execution_handoff_packet_20260810.zip",
    "reports\final_return_evidence_inbox_scaffold_20260810\final_return_evidence_canonical_routes.csv",
    "reports\final_return_evidence_inbox_scaffold_20260810\final_return_evidence_folder_manifest.csv",
    "reports\final_return_evidence_inbox_scaffold_20260810\final_return_evidence_route_migration_map.csv",
    "reports\final_return_evidence_inbox_scaffold_20260810\final_return_evidence_inbox_qa.csv",
    "reports\final_return_evidence_inbox_scaffold_20260810\FINAL_RETURN_EVIDENCE_INBOX_SCAFFOLD_README.md",
    "reports\final_return_evidence_inbox_scaffold_20260810\final_return_evidence_inbox_scaffold_report.md",
    "reports\final_return_evidence_inbox_scaffold_20260810\final_return_evidence_inbox_scaffold_summary.json",
    "reports\final_return_evidence_intake_scanner_20260810\final_return_evidence_route_scan.csv",
    "reports\final_return_evidence_intake_scanner_20260810\final_return_evidence_file_manifest.csv",
    "reports\final_return_evidence_intake_scanner_20260810\final_return_evidence_invalid_files.csv",
    "reports\final_return_evidence_intake_scanner_20260810\final_return_evidence_next_validation_commands.csv",
    "reports\final_return_evidence_intake_scanner_20260810\final_return_evidence_intake_scanner_qa.csv",
    "reports\final_return_evidence_intake_scanner_20260810\FINAL_RETURN_EVIDENCE_INTAKE_SCANNER_README.md",
    "reports\final_return_evidence_intake_scanner_20260810\final_return_evidence_intake_scanner_report.md",
    "reports\final_return_evidence_intake_scanner_20260810\final_return_evidence_intake_scanner_summary.json",
    "reports\final_return_evidence_writeback_preflight_20260810\final_return_writeback_route_matrix.csv",
    "reports\final_return_evidence_writeback_preflight_20260810\final_return_writeback_protected_targets.csv",
    "reports\final_return_evidence_writeback_preflight_20260810\final_return_writeback_validation_commands.csv",
    "reports\final_return_evidence_writeback_preflight_20260810\final_return_writeback_no_go_rules.csv",
    "reports\final_return_evidence_writeback_preflight_20260810\final_return_writeback_preflight_qa.csv",
    "reports\final_return_evidence_writeback_preflight_20260810\FINAL_RETURN_EVIDENCE_WRITEBACK_PREFLIGHT_README.md",
    "reports\final_return_evidence_writeback_preflight_20260810\final_return_evidence_writeback_preflight_report.md",
    "reports\final_return_evidence_writeback_preflight_20260810\final_return_evidence_writeback_preflight_summary.json",
    "reports\post_writeback_gate_transition_validator_20260810\post_writeback_route_transition_matrix.csv",
    "reports\post_writeback_gate_transition_validator_20260810\post_writeback_gate_transition_status.csv",
    "reports\post_writeback_gate_transition_validator_20260810\post_writeback_final_sequence.csv",
    "reports\post_writeback_gate_transition_validator_20260810\post_writeback_transition_no_go_rules.csv",
    "reports\post_writeback_gate_transition_validator_20260810\post_writeback_gate_transition_qa.csv",
    "reports\post_writeback_gate_transition_validator_20260810\POST_WRITEBACK_GATE_TRANSITION_VALIDATOR_README.md",
    "reports\post_writeback_gate_transition_validator_20260810\post_writeback_gate_transition_validator_report.md",
    "reports\post_writeback_gate_transition_validator_20260810\post_writeback_gate_transition_validator_summary.json",
    "reports\post_return_guarded_execution_runner_20260810\post_return_guarded_command_plan.csv",
    "reports\post_return_guarded_execution_runner_20260810\post_return_global_guard_state.csv",
    "reports\post_return_guarded_execution_runner_20260810\post_return_guarded_final_sequence.csv",
    "reports\post_return_guarded_execution_runner_20260810\post_return_guarded_execution_qa.csv",
    "reports\post_return_guarded_execution_runner_20260810\run_post_return_guarded_execution.ps1",
    "reports\post_return_guarded_execution_runner_20260810\POST_RETURN_GUARDED_EXECUTION_RUNNER_README.md",
    "reports\post_return_guarded_execution_runner_20260810\post_return_guarded_execution_runner_report.md",
    "reports\post_return_guarded_execution_runner_20260810\post_return_guarded_execution_runner_summary.json",
    "reports\final_operator_execution_bundle_v2_20260810\final_operator_execution_bundle_v2_manifest.csv",
    "reports\final_operator_execution_bundle_v2_20260810\final_operator_execution_bundle_v2_sequence.csv",
    "reports\final_operator_execution_bundle_v2_20260810\final_operator_execution_bundle_v2_qa.csv",
    "reports\final_operator_execution_bundle_v2_20260810\FINAL_OPERATOR_EXECUTION_BUNDLE_V2_README.md",
    "reports\final_operator_execution_bundle_v2_20260810\final_operator_execution_bundle_v2_report.md",
    "reports\final_operator_execution_bundle_v2_20260810\final_operator_execution_bundle_v2_summary.json",
    "reports\final_operator_execution_bundle_v2_20260810\NatComms_final_operator_execution_bundle_v2_20260810.zip",
    "reports\final_operator_bundle_v2_acceptance_validator_20260810\final_operator_bundle_v2_required_members.csv",
    "reports\final_operator_bundle_v2_acceptance_validator_20260810\final_operator_bundle_v2_category_coverage.csv",
    "reports\final_operator_bundle_v2_acceptance_validator_20260810\final_operator_bundle_v2_acceptance_qa.csv",
    "reports\final_operator_bundle_v2_acceptance_validator_20260810\guard_runner_acceptance_stdout.txt",
    "reports\final_operator_bundle_v2_acceptance_validator_20260810\guard_runner_acceptance_stderr.txt",
    "reports\final_operator_bundle_v2_acceptance_validator_20260810\FINAL_OPERATOR_BUNDLE_V2_ACCEPTANCE_VALIDATOR_README.md",
    "reports\final_operator_bundle_v2_acceptance_validator_20260810\final_operator_bundle_v2_acceptance_validator_report.md",
    "reports\final_operator_bundle_v2_acceptance_validator_20260810\final_operator_bundle_v2_acceptance_validator_summary.json",
    "reports\final_completion_residual_blocker_audit_20260810\final_completion_completed_artifacts.csv",
    "reports\final_completion_residual_blocker_audit_20260810\final_completion_residual_blockers.csv",
    "reports\final_completion_residual_blocker_audit_20260810\final_completion_readiness_matrix.csv",
    "reports\final_completion_residual_blocker_audit_20260810\final_completion_residual_blocker_audit_qa.csv",
    "reports\final_completion_residual_blocker_audit_20260810\FINAL_COMPLETION_RESIDUAL_BLOCKER_AUDIT_README.md",
    "reports\final_completion_residual_blocker_audit_20260810\final_completion_residual_blocker_audit_report.md",
    "reports\final_completion_residual_blocker_audit_20260810\final_completion_residual_blocker_audit_summary.json",
    "reports\final_residual_blocker_closure_packet_20260810\final_residual_blocker_closure_packet.csv",
    "reports\final_residual_blocker_closure_packet_20260810\final_residual_blocker_dependency_order.csv",
    "reports\final_residual_blocker_closure_packet_20260810\final_residual_blocker_validation_commands.csv",
    "reports\final_residual_blocker_closure_packet_20260810\final_residual_blocker_closure_packet_qa.csv",
    "reports\final_residual_blocker_closure_packet_20260810\FINAL_RESIDUAL_BLOCKER_CLOSURE_PACKET_README.md",
    "reports\final_residual_blocker_closure_packet_20260810\final_residual_blocker_closure_packet_report.md",
    "reports\final_residual_blocker_closure_packet_20260810\final_residual_blocker_closure_packet_summary.json",
    "reports\rb001_return_evidence_drop_kit_20260810\rb001_return_evidence_drop_locations.csv",
    "reports\rb001_return_evidence_drop_kit_20260810\rb001_return_evidence_hash_manifest_template.csv",
    "reports\rb001_return_evidence_drop_kit_20260810\rb001_return_evidence_after_drop_commands.csv",
    "reports\rb001_return_evidence_drop_kit_20260810\RB001_RETURN_EVIDENCE_DROP_KIT_README.md",
    "reports\rb001_return_evidence_drop_kit_20260810\rb001_return_evidence_drop_kit_report.md",
    "reports\rb001_return_evidence_drop_kit_20260810\rb001_return_evidence_drop_kit_manifest.csv",
    "reports\rb001_return_evidence_drop_kit_20260810\rb001_return_evidence_drop_kit_summary.json",
    "reports\rb001_return_evidence_hash_reconciliation_20260810\rb001_return_evidence_hash_reconciliation.csv",
    "reports\rb001_return_evidence_hash_reconciliation_20260810\rb001_return_evidence_missing_source_register.csv",
    "reports\rb001_return_evidence_hash_reconciliation_20260810\rb001_return_evidence_hash_mismatch.csv",
    "reports\rb001_return_evidence_hash_reconciliation_20260810\rb001_return_evidence_hash_reconciliation_commands.csv",
    "reports\rb001_return_evidence_hash_reconciliation_20260810\rb001_return_evidence_hash_reconciliation_qa.csv",
    "reports\rb001_return_evidence_hash_reconciliation_20260810\RB001_RETURN_EVIDENCE_HASH_RECONCILIATION_README.md",
    "reports\rb001_return_evidence_hash_reconciliation_20260810\rb001_return_evidence_hash_reconciliation_summary.json",
    "reports\rb001_post_drop_dry_run_gate_20260810\rb001_post_drop_command_sequence.csv",
    "reports\rb001_post_drop_dry_run_gate_20260810\rb001_post_drop_guard_matrix.csv",
    "reports\rb001_post_drop_dry_run_gate_20260810\rb001_post_drop_dry_run_qa.csv",
    "reports\rb001_post_drop_dry_run_gate_20260810\RB001_POST_DROP_DRY_RUN_GATE_README.md",
    "reports\rb001_post_drop_dry_run_gate_20260810\rb001_post_drop_dry_run_gate_report.md",
    "reports\rb001_post_drop_dry_run_gate_20260810\rb001_post_drop_dry_run_gate_summary.json",
    "reports\rb001_diagnostic_only_runner_20260810\run_rb001_diagnostic_only.ps1",
    "reports\rb001_diagnostic_only_runner_20260810\rb001_diagnostic_only_runner_commands.csv",
    "reports\rb001_diagnostic_only_runner_20260810\rb001_diagnostic_only_runner_qa.csv",
    "reports\rb001_diagnostic_only_runner_20260810\rb001_diagnostic_runner_stdout.txt",
    "reports\rb001_diagnostic_only_runner_20260810\rb001_diagnostic_runner_stderr.txt",
    "reports\rb001_diagnostic_only_runner_20260810\RB001_DIAGNOSTIC_ONLY_RUNNER_README.md",
    "reports\rb001_diagnostic_only_runner_20260810\rb001_diagnostic_only_runner_summary.json",
    "reports\rb001_manual_execution_receipt_20260810\rb001_manual_execution_receipt_template.csv",
    "reports\rb001_manual_execution_receipt_20260810\rb001_manual_execution_receipt_incomplete_rows.csv",
    "reports\rb001_manual_execution_receipt_20260810\rb001_manual_execution_receipt_acceptance_criteria.csv",
    "reports\rb001_manual_execution_receipt_20260810\rb001_manual_execution_receipt_qa.csv",
    "reports\rb001_manual_execution_receipt_20260810\RB001_MANUAL_EXECUTION_RECEIPT_GUIDE.md",
    "reports\rb001_manual_execution_receipt_20260810\rb001_manual_execution_receipt_summary.json",
    "reports\rb001_receipt_completion_validator_20260810\rb001_receipt_completion_validation.csv",
    "reports\rb001_receipt_completion_validator_20260810\rb001_receipt_completion_gate_matrix.csv",
    "reports\rb001_receipt_completion_validator_20260810\rb001_receipt_completion_validator_qa.csv",
    "reports\rb001_receipt_completion_validator_20260810\RB001_RECEIPT_COMPLETION_VALIDATOR_README.md",
    "reports\rb001_receipt_completion_validator_20260810\rb001_receipt_completion_validator_report.md",
    "reports\rb001_receipt_completion_validator_20260810\rb001_receipt_completion_validator_summary.json",
    "reports\rb001_closeout_dashboard_20260810\rb001_closeout_prepared_layers.csv",
    "reports\rb001_closeout_dashboard_20260810\rb001_closeout_blockers.csv",
    "reports\rb001_closeout_dashboard_20260810\rb001_closeout_next_actions.csv",
    "reports\rb001_closeout_dashboard_20260810\rb001_closeout_dashboard_qa.csv",
    "reports\rb001_closeout_dashboard_20260810\RB001_CLOSEOUT_DASHBOARD_README.md",
    "reports\rb001_closeout_dashboard_20260810\rb001_closeout_dashboard_report.md",
    "reports\rb001_closeout_dashboard_20260810\rb001_closeout_dashboard_summary.json",
    "reports\rb002_writeback_readiness_dashboard_20260810\rb002_writeback_route_readiness.csv",
    "reports\rb002_writeback_readiness_dashboard_20260810\rb002_writeback_blockers.csv",
    "reports\rb002_writeback_readiness_dashboard_20260810\rb002_writeback_next_actions.csv",
    "reports\rb002_writeback_readiness_dashboard_20260810\rb002_writeback_readiness_dashboard_qa.csv",
    "reports\rb002_writeback_readiness_dashboard_20260810\RB002_WRITEBACK_READINESS_DASHBOARD_README.md",
    "reports\rb002_writeback_readiness_dashboard_20260810\rb002_writeback_readiness_dashboard_report.md",
    "reports\rb002_writeback_readiness_dashboard_20260810\rb002_writeback_readiness_dashboard_summary.json",
    "reports\rb002_protected_writeback_receipt_20260810\rb002_protected_writeback_receipt_template.csv",
    "reports\rb002_protected_writeback_receipt_20260810\rb002_protected_writeback_targets.csv",
    "reports\rb002_protected_writeback_receipt_20260810\rb002_protected_writeback_incomplete_rows.csv",
    "reports\rb002_protected_writeback_receipt_20260810\rb002_protected_writeback_acceptance_criteria.csv",
    "reports\rb002_protected_writeback_receipt_20260810\rb002_protected_writeback_receipt_qa.csv",
    "reports\rb002_protected_writeback_receipt_20260810\RB002_PROTECTED_WRITEBACK_RECEIPT_GUIDE.md",
    "reports\rb002_protected_writeback_receipt_20260810\rb002_protected_writeback_receipt_summary.json",
    "reports\rb002_writeback_receipt_completion_validator_20260810\rb002_writeback_receipt_completion_validation.csv",
    "reports\rb002_writeback_receipt_completion_validator_20260810\rb002_writeback_receipt_completion_gate_matrix.csv",
    "reports\rb002_writeback_receipt_completion_validator_20260810\rb002_writeback_receipt_completion_validator_qa.csv",
    "reports\rb002_writeback_receipt_completion_validator_20260810\RB002_WRITEBACK_RECEIPT_COMPLETION_VALIDATOR_README.md",
    "reports\rb002_writeback_receipt_completion_validator_20260810\rb002_writeback_receipt_completion_validator_report.md",
    "reports\rb002_writeback_receipt_completion_validator_20260810\rb002_writeback_receipt_completion_validator_summary.json",
    "reports\natcomms_next_execution_packet_20260810\next_execution_task_queue.csv",
    "reports\natcomms_next_execution_packet_20260810\owner_packet_distribution_matrix.csv",
    "reports\natcomms_next_execution_packet_20260810\next_execution_acceptance_tests.csv",
    "reports\natcomms_next_execution_packet_20260810\next_execution_handoff.md",
    "reports\natcomms_next_execution_packet_20260810\next_execution_stop_rules.csv",
    "reports\natcomms_next_execution_packet_20260810\next_execution_packet_qa.csv",
    "reports\natcomms_next_execution_packet_20260810\NATCOMMS_NEXT_EXECUTION_PACKET_README.md",
    "reports\natcomms_next_execution_packet_20260810\next_execution_packet_report.md",
    "reports\natcomms_next_execution_packet_20260810\next_execution_packet_summary.json",
    "reports\natcomms_author_sendout_preflight_20260810\author_sendout_attachment_manifest.csv",
    "reports\natcomms_author_sendout_preflight_20260810\author_sendout_blank_field_audit.csv",
    "reports\natcomms_author_sendout_preflight_20260810\author_sendout_email_consistency_check.csv",
    "reports\natcomms_author_sendout_preflight_20260810\author_sendout_pre_send_checklist.csv",
    "reports\natcomms_author_sendout_preflight_20260810\author_sendout_email_ready_draft_cn.md",
    "reports\natcomms_author_sendout_preflight_20260810\author_sendout_preflight_qa.csv",
    "reports\natcomms_author_sendout_preflight_20260810\NATCOMMS_AUTHOR_SENDOUT_PREFLIGHT_README.md",
    "reports\natcomms_author_sendout_preflight_20260810\author_sendout_preflight_report.md",
    "reports\natcomms_author_sendout_preflight_20260810\author_sendout_preflight_summary.json",
    "reports\natcomms_author_sendout_bundle_20260810\author_sendout_bundle_manifest.csv",
    "reports\natcomms_author_sendout_bundle_20260810\author_sendout_recipient_route.csv",
    "reports\natcomms_author_sendout_bundle_20260810\AUTHOR_SENDOUT_BUNDLE_INSTRUCTIONS.md",
    "reports\natcomms_author_sendout_bundle_20260810\author_sendout_email_ready_draft_cn.md",
    "reports\natcomms_author_sendout_bundle_20260810\NatComms_author_sendout_bundle_20260810.zip",
    "reports\natcomms_author_sendout_bundle_20260810\author_sendout_bundle_qa.csv",
    "reports\natcomms_author_sendout_bundle_20260810\NATCOMMS_AUTHOR_SENDOUT_BUNDLE_README.md",
    "reports\natcomms_author_sendout_bundle_20260810\author_sendout_bundle_report.md",
    "reports\natcomms_author_sendout_bundle_20260810\author_sendout_bundle_summary.json",
    "reports\natcomms_author_response_tracker_20260810\author_response_send_log_template.csv",
    "reports\natcomms_author_response_tracker_20260810\author_response_return_tracker.csv",
    "reports\natcomms_author_response_tracker_20260810\returned_attachment_validation_plan.csv",
    "reports\natcomms_author_response_tracker_20260810\post_reply_rerun_command_queue.csv",
    "reports\natcomms_author_response_tracker_20260810\author_response_tracker_stop_rules.csv",
    "reports\natcomms_author_response_tracker_20260810\AUTHOR_RESPONSE_TRACKER_README.md",
    "reports\natcomms_author_response_tracker_20260810\author_response_tracker_qa.csv",
    "reports\natcomms_author_response_tracker_20260810\author_response_tracker_report.md",
    "reports\natcomms_author_response_tracker_20260810\author_response_tracker_summary.json",
    "reports\natcomms_author_response_log_validator_20260810\author_response_send_log_validation.csv",
    "reports\natcomms_author_response_log_validator_20260810\author_response_return_log_validation.csv",
    "reports\natcomms_author_response_log_validator_20260810\author_response_lifecycle_gate_decision.csv",
    "reports\natcomms_author_response_log_validator_20260810\author_response_log_validator_qa.csv",
    "reports\natcomms_author_response_log_validator_20260810\AUTHOR_RESPONSE_LOG_VALIDATOR_README.md",
    "reports\natcomms_author_response_log_validator_20260810\author_response_log_validator_report.md",
    "reports\natcomms_author_response_log_validator_20260810\author_response_log_validator_summary.json",
    "reports\manual_field_preservation_audit_20260810\manual_field_preservation_targets.csv",
    "reports\manual_field_preservation_audit_20260810\manual_field_overwrite_risk_register.csv",
    "reports\manual_field_preservation_audit_20260810\sendout_manual_field_stage_audit.csv",
    "reports\manual_field_preservation_audit_20260810\manual_field_safe_rerun_order.csv",
    "reports\manual_field_preservation_audit_20260810\manual_field_preservation_audit_qa.csv",
    "reports\manual_field_preservation_audit_20260810\MANUAL_FIELD_PRESERVATION_AUDIT_README.md",
    "reports\manual_field_preservation_audit_20260810\manual_field_preservation_audit_report.md",
    "reports\manual_field_preservation_audit_20260810\manual_field_preservation_audit_summary.json",
    "reports\author_fill_guide_packet_20260810\author_core_reply_fill_guide.csv",
    "reports\author_fill_guide_packet_20260810\backend_and_scope_fill_guide.csv",
    "reports\author_fill_guide_packet_20260810\ancillary_reply_sheet_fill_guide.csv",
    "reports\author_fill_guide_packet_20260810\send_return_log_fill_guide.csv",
    "reports\author_fill_guide_packet_20260810\owner_specific_fill_assignments.csv",
    "reports\author_fill_guide_packet_20260810\prohibited_short_replies.csv",
    "reports\author_fill_guide_packet_20260810\author_fill_guide_packet_qa.csv",
    "reports\author_fill_guide_packet_20260810\AUTHOR_FILL_GUIDE_CN.md",
    "reports\author_fill_guide_packet_20260810\AUTHOR_FILL_GUIDE_PACKET_README.md",
    "reports\author_fill_guide_packet_20260810\author_fill_guide_packet_report.md",
    "reports\author_fill_guide_packet_20260810\author_fill_guide_packet_summary.json",
    "reports\natcomms_author_sendout_bundle_v2_20260810\author_sendout_bundle_v2_manifest.csv",
    "reports\natcomms_author_sendout_bundle_v2_20260810\author_sendout_bundle_v2_recipient_route.csv",
    "reports\natcomms_author_sendout_bundle_v2_20260810\author_sendout_bundle_v2_inventory.csv",
    "reports\natcomms_author_sendout_bundle_v2_20260810\AUTHOR_SENDOUT_BUNDLE_V2_INSTRUCTIONS.md",
    "reports\natcomms_author_sendout_bundle_v2_20260810\author_sendout_email_ready_draft_cn.md",
    "reports\natcomms_author_sendout_bundle_v2_20260810\NatComms_author_sendout_bundle_v2_20260810.zip",
    "reports\natcomms_author_sendout_bundle_v2_20260810\author_sendout_bundle_v2_qa.csv",
    "reports\natcomms_author_sendout_bundle_v2_20260810\NATCOMMS_AUTHOR_SENDOUT_BUNDLE_V2_README.md",
    "reports\natcomms_author_sendout_bundle_v2_20260810\author_sendout_bundle_v2_report.md",
    "reports\natcomms_author_sendout_bundle_v2_20260810\author_sendout_bundle_v2_summary.json",
    "reports\natcomms_author_sendout_bundle_v2_20260810\author_sendout_bundle_v2_zip_fingerprint.csv",
    "reports\natcomms_sendout_v2_lifecycle_consistency_audit_20260810\sendout_v2_lifecycle_send_log_audit.csv",
    "reports\natcomms_sendout_v2_lifecycle_consistency_audit_20260810\sendout_v2_zip_fingerprint_audit.csv",
    "reports\natcomms_sendout_v2_lifecycle_consistency_audit_20260810\sendout_v2_lifecycle_gate_matrix.csv",
    "reports\natcomms_sendout_v2_lifecycle_consistency_audit_20260810\sendout_v2_lifecycle_consistency_audit_qa.csv",
    "reports\natcomms_sendout_v2_lifecycle_consistency_audit_20260810\NATCOMMS_SENDOUT_V2_LIFECYCLE_CONSISTENCY_AUDIT_README.md",
    "reports\natcomms_sendout_v2_lifecycle_consistency_audit_20260810\sendout_v2_lifecycle_consistency_audit_report.md",
    "reports\natcomms_sendout_v2_lifecycle_consistency_audit_20260810\sendout_v2_lifecycle_consistency_audit_summary.json",
    "reports\natcomms_canonical_send_log_v2_overlay_20260810\canonical_send_log_v2_overlay_before_after.csv",
    "reports\natcomms_canonical_send_log_v2_overlay_20260810\canonical_send_log_v2_overlay_gate_matrix.csv",
    "reports\natcomms_canonical_send_log_v2_overlay_20260810\canonical_send_log_v2_overlay_qa.csv",
    "reports\natcomms_canonical_send_log_v2_overlay_20260810\NATCOMMS_CANONICAL_SEND_LOG_V2_OVERLAY_README.md",
    "reports\natcomms_canonical_send_log_v2_overlay_20260810\canonical_send_log_v2_overlay_report.md",
    "reports\natcomms_canonical_send_log_v2_overlay_20260810\canonical_send_log_v2_overlay_summary.json",
    "reports\natcomms_manual_sendout_execution_guard_20260810\manual_sendout_execution_checklist.csv",
    "reports\natcomms_manual_sendout_execution_guard_20260810\sendout_evidence_capture_template.csv",
    "reports\natcomms_manual_sendout_execution_guard_20260810\return_file_integrity_checklist.csv",
    "reports\natcomms_manual_sendout_execution_guard_20260810\post_send_validation_command_queue.csv",
    "reports\natcomms_manual_sendout_execution_guard_20260810\manual_sendout_execution_guard_qa.csv",
    "reports\natcomms_manual_sendout_execution_guard_20260810\NATCOMMS_MANUAL_SENDOUT_EXECUTION_GUARD_README.md",
    "reports\natcomms_manual_sendout_execution_guard_20260810\manual_sendout_execution_guard_report.md",
    "reports\natcomms_manual_sendout_execution_guard_20260810\manual_sendout_execution_guard_summary.json",
    "reports\natcomms_sendout_evidence_receipt_completion_validator_20260810\sendout_evidence_receipt_completion_validation.csv",
    "reports\natcomms_sendout_evidence_receipt_completion_validator_20260810\sendout_evidence_receipt_gate_matrix.csv",
    "reports\natcomms_sendout_evidence_receipt_completion_validator_20260810\sendout_to_rb001_intake_next_actions.csv",
    "reports\natcomms_sendout_evidence_receipt_completion_validator_20260810\sendout_evidence_receipt_completion_validator_qa.csv",
    "reports\natcomms_sendout_evidence_receipt_completion_validator_20260810\NATCOMMS_SENDOUT_EVIDENCE_RECEIPT_COMPLETION_VALIDATOR_README.md",
    "reports\natcomms_sendout_evidence_receipt_completion_validator_20260810\sendout_evidence_receipt_completion_validator_report.md",
    "reports\natcomms_sendout_evidence_receipt_completion_validator_20260810\sendout_evidence_receipt_completion_validator_summary.json",
    "reports\natcomms_canonical_tracker_v2_consistency_validator_20260810\canonical_tracker_v2_send_log_audit.csv",
    "reports\natcomms_canonical_tracker_v2_consistency_validator_20260810\canonical_tracker_v2_crosscheck_matrix.csv",
    "reports\natcomms_canonical_tracker_v2_consistency_validator_20260810\canonical_tracker_v2_consistency_validator_qa.csv",
    "reports\natcomms_canonical_tracker_v2_consistency_validator_20260810\NATCOMMS_CANONICAL_TRACKER_V2_CONSISTENCY_VALIDATOR_README.md",
    "reports\natcomms_canonical_tracker_v2_consistency_validator_20260810\canonical_tracker_v2_consistency_validator_report.md",
    "reports\natcomms_canonical_tracker_v2_consistency_validator_20260810\canonical_tracker_v2_consistency_validator_summary.json",
    "reports\natcomms_return_tracker_to_rb001_crosswalk_validator_20260810\return_tracker_to_rb001_crosswalk.csv",
    "reports\natcomms_return_tracker_to_rb001_crosswalk_validator_20260810\return_tracker_to_rb001_gate_matrix.csv",
    "reports\natcomms_return_tracker_to_rb001_crosswalk_validator_20260810\return_tracker_to_rb001_next_actions.csv",
    "reports\natcomms_return_tracker_to_rb001_crosswalk_validator_20260810\return_tracker_to_rb001_crosswalk_validator_qa.csv",
    "reports\natcomms_return_tracker_to_rb001_crosswalk_validator_20260810\NATCOMMS_RETURN_TRACKER_TO_RB001_CROSSWALK_VALIDATOR_README.md",
    "reports\natcomms_return_tracker_to_rb001_crosswalk_validator_20260810\return_tracker_to_rb001_crosswalk_validator_report.md",
    "reports\natcomms_return_tracker_to_rb001_crosswalk_validator_20260810\return_tracker_to_rb001_crosswalk_validator_summary.json",
    "reports\rb001_hash_manifest_readiness_validator_20260810\rb001_hash_manifest_row_readiness.csv",
    "reports\rb001_hash_manifest_readiness_validator_20260810\rb001_hash_manifest_gate_matrix.csv",
    "reports\rb001_hash_manifest_readiness_validator_20260810\rb001_hash_manifest_next_actions.csv",
    "reports\rb001_hash_manifest_readiness_validator_20260810\rb001_hash_manifest_readiness_validator_qa.csv",
    "reports\rb001_hash_manifest_readiness_validator_20260810\RB001_HASH_MANIFEST_READINESS_VALIDATOR_README.md",
    "reports\rb001_hash_manifest_readiness_validator_20260810\rb001_hash_manifest_readiness_validator_report.md",
    "reports\rb001_hash_manifest_readiness_validator_20260810\rb001_hash_manifest_readiness_validator_summary.json",
    "reports\rb001_closeout_dependency_bridge_validator_20260810\rb001_closeout_dependency_bridge_matrix.csv",
    "reports\rb001_closeout_dependency_bridge_validator_20260810\rb001_closeout_dependency_bridge_blockers.csv",
    "reports\rb001_closeout_dependency_bridge_validator_20260810\rb001_closeout_dependency_bridge_qa.csv",
    "reports\rb001_closeout_dependency_bridge_validator_20260810\RB001_CLOSEOUT_DEPENDENCY_BRIDGE_VALIDATOR_README.md",
    "reports\rb001_closeout_dependency_bridge_validator_20260810\rb001_closeout_dependency_bridge_validator_report.md",
    "reports\rb001_closeout_dependency_bridge_validator_20260810\rb001_closeout_dependency_bridge_validator_summary.json",
    "reports\rb002_entry_dependency_bridge_validator_20260810\rb002_entry_dependency_bridge_matrix.csv",
    "reports\rb002_entry_dependency_bridge_validator_20260810\rb002_entry_dependency_bridge_blockers.csv",
    "reports\rb002_entry_dependency_bridge_validator_20260810\rb002_entry_dependency_bridge_qa.csv",
    "reports\rb002_entry_dependency_bridge_validator_20260810\RB002_ENTRY_DEPENDENCY_BRIDGE_VALIDATOR_README.md",
    "reports\rb002_entry_dependency_bridge_validator_20260810\rb002_entry_dependency_bridge_validator_report.md",
    "reports\rb002_entry_dependency_bridge_validator_20260810\rb002_entry_dependency_bridge_validator_summary.json",
    "reports\post_writeback_transition_dependency_bridge_validator_20260810\post_writeback_transition_dependency_bridge_matrix.csv",
    "reports\post_writeback_transition_dependency_bridge_validator_20260810\post_writeback_transition_route_execution_bridge.csv",
    "reports\post_writeback_transition_dependency_bridge_validator_20260810\post_writeback_transition_dependency_bridge_blockers.csv",
    "reports\post_writeback_transition_dependency_bridge_validator_20260810\post_writeback_transition_dependency_bridge_qa.csv",
    "reports\post_writeback_transition_dependency_bridge_validator_20260810\POST_WRITEBACK_TRANSITION_DEPENDENCY_BRIDGE_VALIDATOR_README.md",
    "reports\post_writeback_transition_dependency_bridge_validator_20260810\post_writeback_transition_dependency_bridge_validator_report.md",
    "reports\post_writeback_transition_dependency_bridge_validator_20260810\post_writeback_transition_dependency_bridge_validator_summary.json",
    "reports\natcomms_author_sendout_dispatch_preflight_20260810\author_sendout_dispatch_preflight_matrix.csv",
    "reports\natcomms_author_sendout_dispatch_preflight_20260810\author_sendout_recipient_dispatch_sheet.csv",
    "reports\natcomms_author_sendout_dispatch_preflight_20260810\author_sendout_evidence_record_template.csv",
    "reports\natcomms_author_sendout_dispatch_preflight_20260810\author_sendout_dispatch_no_go_rules.csv",
    "reports\natcomms_author_sendout_dispatch_preflight_20260810\author_sendout_dispatch_preflight_qa.csv",
    "reports\natcomms_author_sendout_dispatch_preflight_20260810\AUTHOR_SENDOUT_DISPATCH_PREFLIGHT_README.md",
    "reports\natcomms_author_sendout_dispatch_preflight_20260810\author_sendout_dispatch_preflight_report.md",
    "reports\natcomms_author_sendout_dispatch_preflight_20260810\author_sendout_dispatch_preflight_summary.json",
    "reports\figure_rendering_preflight_20260810\figure_source_file_preflight.csv",
    "reports\figure_rendering_preflight_20260810\figure_rendering_kickoff_queue.csv",
    "reports\figure_rendering_preflight_20260810\figure_backend_decision_sheet.csv",
    "reports\figure_rendering_preflight_20260810\figure_visual_qa_import.csv",
    "reports\figure_rendering_preflight_20260810\figure_rendering_stop_rules.csv",
    "reports\figure_rendering_preflight_20260810\FIGURE_RENDERING_PREFLIGHT_README.md",
    "reports\figure_rendering_preflight_20260810\figure_rendering_preflight_report.md",
    "reports\figure_rendering_preflight_20260810\figure_rendering_preflight_summary.json",
    "reports\figure_backend_decision_validator_20260810\figure_backend_decision_validation.csv",
    "reports\figure_backend_decision_validator_20260810\figure_rendering_gate_decision.csv",
    "reports\figure_backend_decision_validator_20260810\figure_backend_decision_validator_qa.csv",
    "reports\figure_backend_decision_validator_20260810\figure_backend_choice_handoff.md",
    "reports\figure_backend_decision_validator_20260810\FIGURE_BACKEND_DECISION_VALIDATOR_README.md",
    "reports\figure_backend_decision_validator_20260810\figure_backend_decision_validator_report.md",
    "reports\figure_backend_decision_validator_20260810\figure_backend_decision_validator_summary.json",
    "reports\figure_backend_scope_decision_handoff_20260810\backend_option_recommendation_matrix.csv",
    "reports\figure_backend_scope_decision_handoff_20260810\figure_scope_impact_matrix.csv",
    "reports\figure_backend_scope_decision_handoff_20260810\post_backend_decision_execution_queue.csv",
    "reports\figure_backend_scope_decision_handoff_20260810\figure_backend_scope_decision_handoff_qa.csv",
    "reports\figure_backend_scope_decision_handoff_20260810\FIGURE_BACKEND_SCOPE_DECISION_HANDOFF.md",
    "reports\figure_backend_scope_decision_handoff_20260810\figure_backend_scope_decision_handoff_report.md",
    "reports\figure_backend_scope_decision_handoff_20260810\figure_backend_scope_decision_handoff_summary.json",
    "reports\reporting_summary_completion_handoff_20260810\reporting_summary_item_completion_matrix.csv",
    "reports\reporting_summary_completion_handoff_20260810\reporting_summary_author_handoff_queue.csv",
    "reports\reporting_summary_completion_handoff_20260810\reporting_summary_gate_dependency_map.csv",
    "reports\reporting_summary_completion_handoff_20260810\reporting_summary_completion_command_queue.csv",
    "reports\reporting_summary_completion_handoff_20260810\reporting_summary_completion_handoff_qa.csv",
    "reports\reporting_summary_completion_handoff_20260810\REPORTING_SUMMARY_COMPLETION_HANDOFF_README.md",
    "reports\reporting_summary_completion_handoff_20260810\reporting_summary_completion_handoff_report.md",
    "reports\reporting_summary_completion_handoff_20260810\reporting_summary_completion_handoff_summary.json",
    "reports\manual_dispatch_master_packet_20260810\manual_dispatch_master_queue.csv",
    "reports\manual_dispatch_master_packet_20260810\manual_dispatch_packet_inventory.csv",
    "reports\manual_dispatch_master_packet_20260810\manual_dispatch_stop_rules.csv",
    "reports\manual_dispatch_master_packet_20260810\manual_dispatch_master_packet_qa.csv",
    "reports\manual_dispatch_master_packet_20260810\MANUAL_DISPATCH_MASTER_PACKET_README.md",
    "reports\manual_dispatch_master_packet_20260810\manual_dispatch_master_packet_report.md",
    "reports\manual_dispatch_master_packet_20260810\manual_dispatch_master_packet_summary.json",
    "reports\today_manual_action_minipack_20260810\today_manual_action_minipack.csv",
    "reports\today_manual_action_minipack_20260810\today_evidence_capture_targets.csv",
    "reports\today_manual_action_minipack_20260810\today_manual_action_stop_rules.csv",
    "reports\today_manual_action_minipack_20260810\TODAY_MANUAL_ACTION_MINIPACK.md",
    "reports\today_manual_action_minipack_20260810\today_manual_action_minipack_qa.csv",
    "reports\today_manual_action_minipack_20260810\today_manual_action_minipack_report.md",
    "reports\today_manual_action_minipack_20260810\today_manual_action_minipack_summary.json",
    "reports\manual_evidence_inbox_scaffold_20260810\manual_evidence_inbox_manifest.csv",
    "reports\manual_evidence_inbox_scaffold_20260810\manual_evidence_inbox_operator_steps.csv",
    "reports\manual_evidence_inbox_scaffold_20260810\manual_evidence_inbox_stop_rules.csv",
    "reports\manual_evidence_inbox_scaffold_20260810\MANUAL_EVIDENCE_INBOX_README.md",
    "reports\manual_evidence_inbox_scaffold_20260810\manual_evidence_inbox_scaffold_qa.csv",
    "reports\manual_evidence_inbox_scaffold_20260810\manual_evidence_inbox_scaffold_report.md",
    "reports\manual_evidence_inbox_scaffold_20260810\manual_evidence_inbox_scaffold_summary.json",
    "reports\manual_evidence_inbox_audit_20260810\manual_evidence_inbox_folder_audit.csv",
    "reports\manual_evidence_inbox_audit_20260810\manual_evidence_inbox_file_checksums.csv",
    "reports\manual_evidence_inbox_audit_20260810\manual_evidence_inbox_sensitive_name_scan.csv",
    "reports\manual_evidence_inbox_audit_20260810\manual_evidence_inbox_audit_qa.csv",
    "reports\manual_evidence_inbox_audit_20260810\MANUAL_EVIDENCE_INBOX_AUDIT_README.md",
    "reports\manual_evidence_inbox_audit_20260810\manual_evidence_inbox_audit_report.md",
    "reports\manual_evidence_inbox_audit_20260810\manual_evidence_inbox_audit_summary.json",
    "reports\inbox_to_tracker_writeback_queue_20260810\inbox_to_tracker_writeback_queue.csv",
    "reports\inbox_to_tracker_writeback_queue_20260810\inbox_to_tracker_writeback_risks.csv",
    "reports\inbox_to_tracker_writeback_queue_20260810\inbox_to_tracker_command_sequence.csv",
    "reports\inbox_to_tracker_writeback_queue_20260810\inbox_to_tracker_writeback_queue_qa.csv",
    "reports\inbox_to_tracker_writeback_queue_20260810\INBOX_TO_TRACKER_WRITEBACK_QUEUE_README.md",
    "reports\inbox_to_tracker_writeback_queue_20260810\inbox_to_tracker_writeback_queue_report.md",
    "reports\inbox_to_tracker_writeback_queue_20260810\inbox_to_tracker_writeback_queue_summary.json",
    "reports\manual_evidence_lifecycle_dashboard_20260810\manual_evidence_lifecycle_dashboard.csv",
    "reports\manual_evidence_lifecycle_dashboard_20260810\manual_evidence_lifecycle_blockers.csv",
    "reports\manual_evidence_lifecycle_dashboard_20260810\manual_evidence_lifecycle_next_actions.csv",
    "reports\manual_evidence_lifecycle_dashboard_20260810\manual_evidence_lifecycle_dashboard_qa.csv",
    "reports\manual_evidence_lifecycle_dashboard_20260810\MANUAL_EVIDENCE_LIFECYCLE_DASHBOARD_README.md",
    "reports\manual_evidence_lifecycle_dashboard_20260810\manual_evidence_lifecycle_dashboard_report.md",
    "reports\manual_evidence_lifecycle_dashboard_20260810\manual_evidence_lifecycle_dashboard_summary.json",
    "reports\next_human_execution_handoff_bundle_20260810\next_human_execution_handoff_manifest.csv",
    "reports\next_human_execution_handoff_bundle_20260810\NEXT_HUMAN_EXECUTION_HANDOFF_README.md",
    "reports\next_human_execution_handoff_bundle_20260810\next_human_execution_handoff_bundle_qa.csv",
    "reports\next_human_execution_handoff_bundle_20260810\next_human_execution_handoff_bundle_report.md",
    "reports\next_human_execution_handoff_bundle_20260810\next_human_execution_handoff_bundle_summary.json",
    "reports\next_human_execution_handoff_bundle_20260810\NatComms_next_human_execution_handoff_20260810.zip",
    "reports\human_execution_handoff_acceptance_checklist_20260810\human_execution_handoff_acceptance_checklist.csv",
    "reports\human_execution_handoff_acceptance_checklist_20260810\human_execution_action_acceptance_evidence.csv",
    "reports\human_execution_handoff_acceptance_checklist_20260810\human_execution_handoff_acceptance_stop_rules.csv",
    "reports\human_execution_handoff_acceptance_checklist_20260810\human_execution_handoff_acceptance_qa.csv",
    "reports\human_execution_handoff_acceptance_checklist_20260810\HUMAN_EXECUTION_HANDOFF_ACCEPTANCE_README.md",
    "reports\human_execution_handoff_acceptance_checklist_20260810\human_execution_handoff_acceptance_report.md",
    "reports\human_execution_handoff_acceptance_checklist_20260810\human_execution_handoff_acceptance_summary.json",
    "reports\manual_post_handoff_recheck_runner_20260810\safe_recheck_command_sequence.csv",
    "reports\manual_post_handoff_recheck_runner_20260810\safe_recheck_inputs.csv",
    "reports\manual_post_handoff_recheck_runner_20260810\safe_recheck_stop_rules.csv",
    "reports\manual_post_handoff_recheck_runner_20260810\run_after_manual_evidence_recheck.ps1",
    "reports\manual_post_handoff_recheck_runner_20260810\manual_post_handoff_recheck_runner_qa.csv",
    "reports\manual_post_handoff_recheck_runner_20260810\MANUAL_POST_HANDOFF_RECHECK_RUNNER_README.md",
    "reports\manual_post_handoff_recheck_runner_20260810\manual_post_handoff_recheck_runner_report.md",
    "reports\manual_post_handoff_recheck_runner_20260810\manual_post_handoff_recheck_runner_summary.json",
    "reports\submission_completion_ledger_20260810\submission_completion_gate_ledger.csv",
    "reports\submission_completion_ledger_20260810\submission_dispatch_to_gate_crosswalk.csv",
    "reports\submission_completion_ledger_20260810\submission_final_verification_queue.csv",
    "reports\submission_completion_ledger_20260810\submission_handoff_status_register.csv",
    "reports\submission_completion_ledger_20260810\submission_no_go_shortcuts.csv",
    "reports\submission_completion_ledger_20260810\submission_completion_ledger_qa.csv",
    "reports\submission_completion_ledger_20260810\SUBMISSION_COMPLETION_LEDGER_README.md",
    "reports\submission_completion_ledger_20260810\submission_completion_ledger_report.md",
    "reports\submission_completion_ledger_20260810\submission_completion_ledger_summary.json",
    "reports\portal_submission_file_preflight_20260810\portal_submission_file_inventory.csv",
    "reports\portal_submission_file_preflight_20260810\portal_gate_to_file_gap_matrix.csv",
    "reports\portal_submission_file_preflight_20260810\portal_no_upload_rules.csv",
    "reports\portal_submission_file_preflight_20260810\portal_final_verification_order.csv",
    "reports\portal_submission_file_preflight_20260810\portal_submission_file_preflight_qa.csv",
    "reports\portal_submission_file_preflight_20260810\PORTAL_SUBMISSION_FILE_PREFLIGHT_README.md",
    "reports\portal_submission_file_preflight_20260810\portal_submission_file_preflight_report.md",
    "reports\portal_submission_file_preflight_20260810\portal_submission_file_preflight_summary.json",
    "reports\final_manuscript_preassembly_guard_20260810\final_manuscript_file_guard.csv",
    "reports\final_manuscript_preassembly_guard_20260810\final_manuscript_marker_scan.csv",
    "reports\final_manuscript_preassembly_guard_20260810\final_manuscript_no_finalization_rules.csv",
    "reports\final_manuscript_preassembly_guard_20260810\final_manuscript_preassembly_guard_qa.csv",
    "reports\final_manuscript_preassembly_guard_20260810\FINAL_MANUSCRIPT_PREASSEMBLY_GUARD_README.md",
    "reports\final_manuscript_preassembly_guard_20260810\final_manuscript_preassembly_guard_report.md",
    "reports\final_manuscript_preassembly_guard_20260810\final_manuscript_preassembly_guard_summary.json",
    "reports\gate_closure_execution_board_20260810\gate_closure_execution_board.csv",
    "reports\gate_closure_execution_board_20260810\gate_closure_command_order.csv",
    "reports\gate_closure_execution_board_20260810\gate_closure_stop_rules.csv",
    "reports\gate_closure_execution_board_20260810\gate_closure_execution_board_qa.csv",
    "reports\gate_closure_execution_board_20260810\GATE_CLOSURE_EXECUTION_BOARD_README.md",
    "reports\gate_closure_execution_board_20260810\gate_closure_execution_board_report.md",
    "reports\gate_closure_execution_board_20260810\gate_closure_execution_board_summary.json",
    "reports\gate_closure_dependency_bridge_validator_20260810\gate_closure_dependency_bridge_matrix.csv",
    "reports\gate_closure_dependency_bridge_validator_20260810\gate_closure_command_bridge.csv",
    "reports\gate_closure_dependency_bridge_validator_20260810\gate_closure_dependency_bridge_blockers.csv",
    "reports\gate_closure_dependency_bridge_validator_20260810\gate_closure_dependency_bridge_qa.csv",
    "reports\gate_closure_dependency_bridge_validator_20260810\GATE_CLOSURE_DEPENDENCY_BRIDGE_VALIDATOR_README.md",
    "reports\gate_closure_dependency_bridge_validator_20260810\gate_closure_dependency_bridge_validator_report.md",
    "reports\gate_closure_dependency_bridge_validator_20260810\gate_closure_dependency_bridge_validator_summary.json",
    "reports\post_dispatch_evidence_intake_validator_20260810\post_dispatch_evidence_intake_matrix.csv",
    "reports\post_dispatch_evidence_intake_validator_20260810\post_dispatch_next_validation_commands.csv",
    "reports\post_dispatch_evidence_intake_validator_20260810\post_dispatch_evidence_intake_validator_qa.csv",
    "reports\post_dispatch_evidence_intake_validator_20260810\POST_DISPATCH_EVIDENCE_INTAKE_VALIDATOR_README.md",
    "reports\post_dispatch_evidence_intake_validator_20260810\post_dispatch_evidence_intake_validator_report.md",
    "reports\post_dispatch_evidence_intake_validator_20260810\post_dispatch_evidence_intake_validator_summary.json",
    "reports\manual_evidence_intake_worksheet_20260810\manual_evidence_intake_worksheet.csv",
    "reports\manual_evidence_intake_worksheet_20260810\manual_evidence_field_dictionary.csv",
    "reports\manual_evidence_intake_worksheet_20260810\manual_evidence_dispatch_writeback_map.csv",
    "reports\manual_evidence_intake_worksheet_20260810\manual_evidence_intake_worksheet_qa.csv",
    "reports\manual_evidence_intake_worksheet_20260810\MANUAL_EVIDENCE_INTAKE_WORKSHEET_README.md",
    "reports\manual_evidence_intake_worksheet_20260810\manual_evidence_intake_worksheet_report.md",
    "reports\manual_evidence_intake_worksheet_20260810\manual_evidence_intake_worksheet_summary.json",
    "reports\manual_evidence_entry_preflight_20260810\manual_evidence_target_preflight.csv",
    "reports\manual_evidence_entry_preflight_20260810\manual_evidence_field_constraint_matrix.csv",
    "reports\manual_evidence_entry_preflight_20260810\manual_evidence_preflight_blockers.csv",
    "reports\manual_evidence_entry_preflight_20260810\manual_evidence_entry_preflight_qa.csv",
    "reports\manual_evidence_entry_preflight_20260810\MANUAL_EVIDENCE_ENTRY_PREFLIGHT_README.md",
    "reports\manual_evidence_entry_preflight_20260810\manual_evidence_entry_preflight_report.md",
    "reports\manual_evidence_entry_preflight_20260810\manual_evidence_entry_preflight_summary.json",
    "reports\post_evidence_safe_rerun_guard_20260810\post_evidence_stage_gate_matrix.csv",
    "reports\post_evidence_safe_rerun_guard_20260810\post_evidence_branch_rerun_matrix.csv",
    "reports\post_evidence_safe_rerun_guard_20260810\post_evidence_global_rerun_order.csv",
    "reports\post_evidence_safe_rerun_guard_20260810\post_evidence_safe_rerun_guard_qa.csv",
    "reports\post_evidence_safe_rerun_guard_20260810\POST_EVIDENCE_SAFE_RERUN_GUARD_README.md",
    "reports\post_evidence_safe_rerun_guard_20260810\post_evidence_safe_rerun_guard_report.md",
    "reports\post_evidence_safe_rerun_guard_20260810\post_evidence_safe_rerun_guard_summary.json",
    "reports\operator_runbook_after_manual_dispatch_20260810\operator_runbook_quickstart.csv",
    "reports\operator_runbook_after_manual_dispatch_20260810\OPERATOR_RUNBOOK_AFTER_MANUAL_DISPATCH.md",
    "reports\operator_runbook_after_manual_dispatch_20260810\operator_runbook_after_manual_dispatch_qa.csv",
    "reports\operator_runbook_after_manual_dispatch_20260810\operator_runbook_after_manual_dispatch_report.md",
    "reports\operator_runbook_after_manual_dispatch_20260810\operator_runbook_after_manual_dispatch_summary.json",
    "reports\post_gate_manual_evidence_dependency_bridge_validator_20260810\post_gate_manual_evidence_dependency_bridge_matrix.csv",
    "reports\post_gate_manual_evidence_dependency_bridge_validator_20260810\post_gate_manual_evidence_action_bridge.csv",
    "reports\post_gate_manual_evidence_dependency_bridge_validator_20260810\post_gate_manual_evidence_dependency_bridge_blockers.csv",
    "reports\post_gate_manual_evidence_dependency_bridge_validator_20260810\post_gate_manual_evidence_dependency_bridge_qa.csv",
    "reports\post_gate_manual_evidence_dependency_bridge_validator_20260810\POST_GATE_MANUAL_EVIDENCE_DEPENDENCY_BRIDGE_VALIDATOR_README.md",
    "reports\post_gate_manual_evidence_dependency_bridge_validator_20260810\post_gate_manual_evidence_dependency_bridge_validator_report.md",
    "reports\post_gate_manual_evidence_dependency_bridge_validator_20260810\post_gate_manual_evidence_dependency_bridge_validator_summary.json",
    "reports\figure_source_data_lock_20260810\figure_panel_claim_lock.csv",
    "reports\figure_source_data_lock_20260810\figure_source_data_manifest.csv",
    "reports\figure_source_data_lock_20260810\figure_caption_boundary_drafts.csv",
    "reports\figure_source_data_lock_20260810\figure_lock_qa.csv",
    "reports\figure_source_data_lock_20260810\FIGURE_SOURCE_DATA_LOCK_README.md",
    "reports\figure_source_data_lock_20260810\figure_source_data_lock_report.md",
    "reports\figure_source_data_lock_20260810\figure_source_data_lock_summary.json",
    "reports\python_figure_preview_package_20260810\figures\figure1_protocol_asset_boundary_preview.png",
    "reports\python_figure_preview_package_20260810\figures\figure1_protocol_asset_boundary_preview.svg",
    "reports\python_figure_preview_package_20260810\figures\figure1_protocol_asset_boundary_preview.pdf",
    "reports\python_figure_preview_package_20260810\figures\figure2_res_sam_transfer_signal_preview.png",
    "reports\python_figure_preview_package_20260810\figures\figure2_res_sam_transfer_signal_preview.svg",
    "reports\python_figure_preview_package_20260810\figures\figure2_res_sam_transfer_signal_preview.pdf",
    "reports\python_figure_preview_package_20260810\figures\figure3_mojahid_directional_boundary_preview.png",
    "reports\python_figure_preview_package_20260810\figures\figure3_mojahid_directional_boundary_preview.svg",
    "reports\python_figure_preview_package_20260810\figures\figure3_mojahid_directional_boundary_preview.pdf",
    "reports\python_figure_preview_package_20260810\figures\figure4_4tu_stress_boundary_preview.png",
    "reports\python_figure_preview_package_20260810\figures\figure4_4tu_stress_boundary_preview.svg",
    "reports\python_figure_preview_package_20260810\figures\figure4_4tu_stress_boundary_preview.pdf",
    "reports\python_figure_preview_package_20260810\figures\figure5_4tu_feasibility_gate_preview.png",
    "reports\python_figure_preview_package_20260810\figures\figure5_4tu_feasibility_gate_preview.svg",
    "reports\python_figure_preview_package_20260810\figures\figure5_4tu_feasibility_gate_preview.pdf",
    "reports\python_figure_preview_package_20260810\figures\figure6_external_validation_open_gate_preview.png",
    "reports\python_figure_preview_package_20260810\figures\figure6_external_validation_open_gate_preview.svg",
    "reports\python_figure_preview_package_20260810\figures\figure6_external_validation_open_gate_preview.pdf",
    "reports\python_figure_preview_package_20260810\python_figure_preview_manifest.csv",
    "reports\python_figure_preview_package_20260810\python_figure_preview_contract.csv",
    "reports\python_figure_preview_package_20260810\python_figure_preview_qa.csv",
    "reports\python_figure_preview_package_20260810\PYTHON_FIGURE_PREVIEW_README.md",
    "reports\python_figure_preview_package_20260810\python_figure_preview_report.md",
    "reports\python_figure_preview_package_20260810\python_figure_preview_summary.json",
    "reports\python_figure_preview_visual_qa_20260810\python_figure_preview_visual_qa.csv",
    "reports\python_figure_preview_visual_qa_20260810\python_figure_caption_boundary_qa.csv",
    "reports\python_figure_preview_visual_qa_20260810\python_figure_finalization_queue.csv",
    "reports\python_figure_preview_visual_qa_20260810\python_figure_preview_visual_qa_summary.csv",
    "reports\python_figure_preview_visual_qa_20260810\PYTHON_FIGURE_PREVIEW_VISUAL_QA_README.md",
    "reports\python_figure_preview_visual_qa_20260810\python_figure_preview_visual_qa_report.md",
    "reports\python_figure_preview_visual_qa_20260810\python_figure_preview_visual_qa_summary.json",
    "reports\python_figure_author_review_packet_20260810\figures_for_author_review\figure_1_author_review.png",
    "reports\python_figure_author_review_packet_20260810\figures_for_author_review\figure_1_author_review.pdf",
    "reports\python_figure_author_review_packet_20260810\figures_for_author_review\figure_2_author_review.png",
    "reports\python_figure_author_review_packet_20260810\figures_for_author_review\figure_2_author_review.pdf",
    "reports\python_figure_author_review_packet_20260810\figures_for_author_review\figure_3_author_review.png",
    "reports\python_figure_author_review_packet_20260810\figures_for_author_review\figure_3_author_review.pdf",
    "reports\python_figure_author_review_packet_20260810\figures_for_author_review\figure_4_author_review.png",
    "reports\python_figure_author_review_packet_20260810\figures_for_author_review\figure_4_author_review.pdf",
    "reports\python_figure_author_review_packet_20260810\figures_for_author_review\figure_5_author_review.png",
    "reports\python_figure_author_review_packet_20260810\figures_for_author_review\figure_5_author_review.pdf",
    "reports\python_figure_author_review_packet_20260810\figures_for_author_review\figure_6_author_review.png",
    "reports\python_figure_author_review_packet_20260810\figures_for_author_review\figure_6_author_review.pdf",
    "reports\python_figure_author_review_packet_20260810\python_figure_author_review_packet_manifest.csv",
    "reports\python_figure_author_review_packet_20260810\python_figure_author_review_form.csv",
    "reports\python_figure_author_review_packet_20260810\python_figure_author_review_stop_rules.csv",
    "reports\python_figure_author_review_packet_20260810\PYTHON_FIGURE_AUTHOR_REVIEW_INSTRUCTIONS.md",
    "reports\python_figure_author_review_packet_20260810\python_figure_author_review_packet_qa.csv",
    "reports\python_figure_author_review_packet_20260810\python_figure_author_review_packet_report.md",
    "reports\python_figure_author_review_packet_20260810\python_figure_author_review_packet_summary.json",
    "reports\python_figure_author_review_packet_20260810\NatComms_python_figure_author_review_packet_20260810.zip",
    "reports\python_figure_author_review_intake_validator_20260810\python_figure_author_review_intake_status.csv",
    "reports\python_figure_author_review_intake_validator_20260810\python_figure_author_review_next_commands.csv",
    "reports\python_figure_author_review_intake_validator_20260810\python_figure_author_review_intake_stop_rules.csv",
    "reports\python_figure_author_review_intake_validator_20260810\python_figure_author_review_intake_qa.csv",
    "reports\python_figure_author_review_intake_validator_20260810\PYTHON_FIGURE_AUTHOR_REVIEW_INTAKE_README.md",
    "reports\python_figure_author_review_intake_validator_20260810\python_figure_author_review_intake_report.md",
    "reports\python_figure_author_review_intake_validator_20260810\python_figure_author_review_intake_summary.json",
    "reports\python_figure_author_review_return_inbox_20260810\returned_author_review_files\README_DO_NOT_EDIT_TRACKERS_HERE.md",
    "reports\python_figure_author_review_return_inbox_20260810\python_figure_author_review_return_inbox_manifest.csv",
    "reports\python_figure_author_review_return_inbox_20260810\python_figure_author_review_return_file_audit.csv",
    "reports\python_figure_author_review_return_inbox_20260810\python_figure_author_review_return_stop_rules.csv",
    "reports\python_figure_author_review_return_inbox_20260810\python_figure_author_review_return_inbox_qa.csv",
    "reports\python_figure_author_review_return_inbox_20260810\PYTHON_FIGURE_AUTHOR_REVIEW_RETURN_INBOX_README.md",
    "reports\python_figure_author_review_return_inbox_20260810\python_figure_author_review_return_inbox_report.md",
    "reports\python_figure_author_review_return_inbox_20260810\python_figure_author_review_return_inbox_summary.json",
    "reports\python_figure_author_review_writeback_queue_20260810\python_figure_author_review_writeback_queue.csv",
    "reports\python_figure_author_review_writeback_queue_20260810\python_figure_author_review_protected_fields.csv",
    "reports\python_figure_author_review_writeback_queue_20260810\python_figure_author_review_writeback_commands.csv",
    "reports\python_figure_author_review_writeback_queue_20260810\python_figure_author_review_writeback_qa.csv",
    "reports\python_figure_author_review_writeback_queue_20260810\PYTHON_FIGURE_AUTHOR_REVIEW_WRITEBACK_README.md",
    "reports\python_figure_author_review_writeback_queue_20260810\python_figure_author_review_writeback_report.md",
    "reports\python_figure_author_review_writeback_queue_20260810\python_figure_author_review_writeback_summary.json",
    "reports\python_figure_final_candidate_preflight_20260810\python_figure_final_candidate_gate_matrix.csv",
    "reports\python_figure_final_candidate_preflight_20260810\python_figure_final_candidate_queue.csv",
    "reports\python_figure_final_candidate_preflight_20260810\python_figure_final_candidate_commands.csv",
    "reports\python_figure_final_candidate_preflight_20260810\python_figure_final_candidate_stop_rules.csv",
    "reports\python_figure_final_candidate_preflight_20260810\python_figure_final_candidate_preflight_qa.csv",
    "reports\python_figure_final_candidate_preflight_20260810\PYTHON_FIGURE_FINAL_CANDIDATE_PREFLIGHT_README.md",
    "reports\python_figure_final_candidate_preflight_20260810\python_figure_final_candidate_preflight_report.md",
    "reports\python_figure_final_candidate_preflight_20260810\python_figure_final_candidate_preflight_summary.json",
    "reports\python_figure_final_export_qa_template_20260810\python_figure_final_export_qa_checklist.csv",
    "reports\python_figure_final_export_qa_template_20260810\python_figure_source_data_panel_map_lock_queue.csv",
    "reports\python_figure_final_export_qa_template_20260810\python_figure_caption_lock_queue.csv",
    "reports\python_figure_final_export_qa_template_20260810\python_figure_final_export_stop_rules.csv",
    "reports\python_figure_final_export_qa_template_20260810\python_figure_final_export_qa_template_qa.csv",
    "reports\python_figure_final_export_qa_template_20260810\PYTHON_FIGURE_FINAL_EXPORT_QA_TEMPLATE_README.md",
    "reports\python_figure_final_export_qa_template_20260810\python_figure_final_export_qa_template_report.md",
    "reports\python_figure_final_export_qa_template_20260810\python_figure_final_export_qa_template_summary.json",
    "reports\python_figure_portal_upload_blocker_20260810\python_figure_portal_upload_blocker_overlay.csv",
    "reports\python_figure_portal_upload_blocker_20260810\python_figure_portal_no_upload_rules.csv",
    "reports\python_figure_portal_upload_blocker_20260810\python_figure_portal_upload_blocker_qa.csv",
    "reports\python_figure_portal_upload_blocker_20260810\PYTHON_FIGURE_PORTAL_UPLOAD_BLOCKER_README.md",
    "reports\python_figure_portal_upload_blocker_20260810\python_figure_portal_upload_blocker_report.md",
    "reports\python_figure_portal_upload_blocker_20260810\python_figure_portal_upload_blocker_summary.json",
    "reports\python_figure_source_data_panel_map_preflight_20260810\python_figure_source_data_panel_map_preflight.csv",
    "reports\python_figure_source_data_panel_map_preflight_20260810\python_figure_source_data_missing_sources.csv",
    "reports\python_figure_source_data_panel_map_preflight_20260810\python_figure_source_data_lock_requirements.csv",
    "reports\python_figure_source_data_panel_map_preflight_20260810\python_figure_source_data_panel_map_commands.csv",
    "reports\python_figure_source_data_panel_map_preflight_20260810\python_figure_source_data_panel_map_stop_rules.csv",
    "reports\python_figure_source_data_panel_map_preflight_20260810\python_figure_source_data_panel_map_preflight_qa.csv",
    "reports\python_figure_source_data_panel_map_preflight_20260810\PYTHON_FIGURE_SOURCE_DATA_PANEL_MAP_PREFLIGHT_README.md",
    "reports\python_figure_source_data_panel_map_preflight_20260810\python_figure_source_data_panel_map_preflight_report.md",
    "reports\python_figure_source_data_panel_map_preflight_20260810\python_figure_source_data_panel_map_preflight_summary.json",
    "reports\figure_portal_final_dependency_bridge_validator_20260810\figure_portal_final_dependency_bridge_matrix.csv",
    "reports\figure_portal_final_dependency_bridge_validator_20260810\figure_portal_final_asset_bridge.csv",
    "reports\figure_portal_final_dependency_bridge_validator_20260810\figure_portal_final_dependency_bridge_blockers.csv",
    "reports\figure_portal_final_dependency_bridge_validator_20260810\figure_portal_final_dependency_bridge_qa.csv",
    "reports\figure_portal_final_dependency_bridge_validator_20260810\FIGURE_PORTAL_FINAL_DEPENDENCY_BRIDGE_VALIDATOR_README.md",
    "reports\figure_portal_final_dependency_bridge_validator_20260810\figure_portal_final_dependency_bridge_validator_report.md",
    "reports\figure_portal_final_dependency_bridge_validator_20260810\figure_portal_final_dependency_bridge_validator_summary.json",
    "reports\author_decision_closure_packet_v2_20260810\author_decision_closure_form_v2.csv",
    "reports\author_decision_closure_packet_v2_20260810\next_24h_decision_closure_queue.csv",
    "reports\author_decision_closure_packet_v2_20260810\coauthor_decision_closure_email.md",
    "reports\author_decision_closure_packet_v2_20260810\external_data_holder_feasibility_note.md",
    "reports\author_decision_closure_packet_v2_20260810\author_decision_closure_packet_v2_qa.csv",
    "reports\author_decision_closure_packet_v2_20260810\author_decision_closure_packet_v2_report.md",
    "reports\author_decision_closure_packet_v2_20260810\author_decision_closure_packet_v2_summary.json",
    "reports\author_final_closeout_dependency_bridge_validator_20260810\author_final_closeout_dependency_bridge_matrix.csv",
    "reports\author_final_closeout_dependency_bridge_validator_20260810\author_final_closeout_action_bridge.csv",
    "reports\author_final_closeout_dependency_bridge_validator_20260810\author_final_closeout_dependency_bridge_blockers.csv",
    "reports\author_final_closeout_dependency_bridge_validator_20260810\author_final_closeout_dependency_bridge_qa.csv",
    "reports\author_final_closeout_dependency_bridge_validator_20260810\AUTHOR_FINAL_CLOSEOUT_DEPENDENCY_BRIDGE_VALIDATOR_README.md",
    "reports\author_final_closeout_dependency_bridge_validator_20260810\author_final_closeout_dependency_bridge_validator_report.md",
    "reports\author_final_closeout_dependency_bridge_validator_20260810\author_final_closeout_dependency_bridge_validator_summary.json",
    "reports\final_submission_master_dependency_bridge_validator_20260810\final_submission_master_dependency_bridge_matrix.csv",
    "reports\final_submission_master_dependency_bridge_validator_20260810\final_submission_master_item_bridge.csv",
    "reports\final_submission_master_dependency_bridge_validator_20260810\final_submission_master_dependency_bridge_blockers.csv",
    "reports\final_submission_master_dependency_bridge_validator_20260810\final_submission_master_dependency_bridge_qa.csv",
    "reports\final_submission_master_dependency_bridge_validator_20260810\FINAL_SUBMISSION_MASTER_DEPENDENCY_BRIDGE_VALIDATOR_README.md",
    "reports\final_submission_master_dependency_bridge_validator_20260810\final_submission_master_dependency_bridge_validator_report.md",
    "reports\final_submission_master_dependency_bridge_validator_20260810\final_submission_master_dependency_bridge_validator_summary.json",
    "reports\final_master_next_action_packet_20260810\final_master_next_manual_actions.csv",
    "reports\final_master_next_action_packet_20260810\final_master_forbidden_submission_actions.csv",
    "reports\final_master_next_action_packet_20260810\final_master_next_action_acceptance_tests.csv",
    "reports\final_master_next_action_packet_20260810\FINAL_MASTER_NEXT_ACTION_PACKET_README.md",
    "reports\final_master_next_action_packet_20260810\final_master_next_action_packet_report.md",
    "reports\final_master_next_action_packet_20260810\final_master_next_action_packet_summary.json",
    "reports\final_manual_receipt_intake_package_20260810\final_manual_receipt_intake_template.csv",
    "reports\final_manual_receipt_intake_package_20260810\final_manual_receipt_field_dictionary.csv",
    "reports\final_manual_receipt_intake_package_20260810\final_manual_receipt_acceptance_tests.csv",
    "reports\final_manual_receipt_intake_package_20260810\FINAL_MANUAL_RECEIPT_INTAKE_README.md",
    "reports\final_manual_receipt_intake_package_20260810\final_manual_receipt_intake_package_report.md",
    "reports\final_manual_receipt_intake_package_20260810\final_manual_receipt_intake_package_summary.json",
    "reports\final_manual_receipt_completion_validator_20260810\final_manual_receipt_completion_status.csv",
    "reports\final_manual_receipt_completion_validator_20260810\final_manual_receipt_completion_gate_matrix.csv",
    "reports\final_manual_receipt_completion_validator_20260810\final_manual_receipt_completion_blockers.csv",
    "reports\final_manual_receipt_completion_validator_20260810\final_manual_receipt_completion_validator_qa.csv",
    "reports\final_manual_receipt_completion_validator_20260810\FINAL_MANUAL_RECEIPT_COMPLETION_VALIDATOR_README.md",
    "reports\final_manual_receipt_completion_validator_20260810\final_manual_receipt_completion_validator_report.md",
    "reports\final_manual_receipt_completion_validator_20260810\final_manual_receipt_completion_validator_summary.json",
    "reports\final_guarded_recheck_launcher_20260810\final_guarded_recheck_command_gate.csv",
    "reports\final_guarded_recheck_launcher_20260810\final_guarded_recheck_blockers.csv",
    "reports\final_guarded_recheck_launcher_20260810\final_guarded_recheck_launcher_qa.csv",
    "reports\final_guarded_recheck_launcher_20260810\run_final_guarded_recheck_after_receipts.ps1",
    "reports\final_guarded_recheck_launcher_20260810\FINAL_GUARDED_RECHECK_LAUNCHER_README.md",
    "reports\final_guarded_recheck_launcher_20260810\final_guarded_recheck_launcher_report.md",
    "reports\final_guarded_recheck_launcher_20260810\final_guarded_recheck_launcher_summary.json",
    "reports\final_guarded_recheck_execution_audit_20260810\final_guarded_recheck_execution_audit.csv",
    "reports\final_guarded_recheck_execution_audit_20260810\final_guarded_recheck_run_log_template.csv",
    "reports\final_guarded_recheck_execution_audit_20260810\final_guarded_recheck_execution_no_go_rules.csv",
    "reports\final_guarded_recheck_execution_audit_20260810\final_guarded_recheck_execution_audit_qa.csv",
    "reports\final_guarded_recheck_execution_audit_20260810\FINAL_GUARDED_RECHECK_EXECUTION_AUDIT_README.md",
    "reports\final_guarded_recheck_execution_audit_20260810\final_guarded_recheck_execution_audit_report.md",
    "reports\final_guarded_recheck_execution_audit_20260810\final_guarded_recheck_execution_audit_summary.json",
    "reports\external_dependency_escalation_packet_20260810\external_dependency_escalation_request_matrix.csv",
    "reports\external_dependency_escalation_packet_20260810\external_dependency_evidence_contract.csv",
    "reports\external_dependency_escalation_packet_20260810\external_dependency_escalation_qa.csv",
    "reports\external_dependency_escalation_packet_20260810\external_dependency_escalation_email.md",
    "reports\external_dependency_escalation_packet_20260810\EXTERNAL_DEPENDENCY_ESCALATION_README.md",
    "reports\external_dependency_escalation_packet_20260810\external_dependency_escalation_report.md",
    "reports\external_dependency_escalation_packet_20260810\external_dependency_escalation_summary.json",
    "reports\external_dependency_escalation_sendout_receipt_validator_20260810\external_dependency_escalation_sendout_receipt_template.csv",
    "reports\external_dependency_escalation_sendout_receipt_validator_20260810\external_dependency_escalation_sendout_receipt_validation.csv",
    "reports\external_dependency_escalation_sendout_receipt_validator_20260810\external_dependency_escalation_sendout_receipt_qa.csv",
    "reports\external_dependency_escalation_sendout_receipt_validator_20260810\EXTERNAL_DEPENDENCY_ESCALATION_SENDOUT_RECEIPT_VALIDATOR_README.md",
    "reports\external_dependency_escalation_sendout_receipt_validator_20260810\external_dependency_escalation_sendout_receipt_validator_report.md",
    "reports\external_dependency_escalation_sendout_receipt_validator_20260810\external_dependency_escalation_sendout_receipt_validator_summary.json",
    "reports\external_dependency_safe_send_execution_packet_20260810\external_dependency_safe_send_task_list.csv",
    "reports\external_dependency_safe_send_execution_packet_20260810\external_dependency_safe_send_preflight.csv",
    "reports\external_dependency_safe_send_execution_packet_20260810\external_dependency_safe_send_forbidden_actions.csv",
    "reports\external_dependency_safe_send_execution_packet_20260810\external_dependency_safe_send_execution_qa.csv",
    "reports\external_dependency_safe_send_execution_packet_20260810\EXTERNAL_DEPENDENCY_SAFE_SEND_EXECUTION_README.md",
    "reports\external_dependency_safe_send_execution_packet_20260810\external_dependency_safe_send_execution_report.md",
    "reports\external_dependency_safe_send_execution_packet_20260810\external_dependency_safe_send_execution_summary.json",
    "reports\external_dependency_sendout_receipt_preservation_regression_20260810\external_dependency_sendout_receipt_preservation_regression_cases.csv",
    "reports\external_dependency_sendout_receipt_preservation_regression_20260810\external_dependency_sendout_receipt_preservation_regression_qa.csv",
    "reports\external_dependency_sendout_receipt_preservation_regression_20260810\EXTERNAL_DEPENDENCY_SENDOUT_RECEIPT_PRESERVATION_REGRESSION_README.md",
    "reports\external_dependency_sendout_receipt_preservation_regression_20260810\external_dependency_sendout_receipt_preservation_regression_report.md",
    "reports\external_dependency_sendout_receipt_preservation_regression_20260810\external_dependency_sendout_receipt_preservation_regression_summary.json",
    "reports\external_dependency_sendout_evidence_intake_preflight_20260810\external_dependency_sendout_evidence_metadata_template.csv",
    "reports\external_dependency_sendout_evidence_intake_preflight_20260810\external_dependency_sendout_evidence_intake_status.csv",
    "reports\external_dependency_sendout_evidence_intake_preflight_20260810\external_dependency_sendout_evidence_writeback_candidates.csv",
    "reports\external_dependency_sendout_evidence_intake_preflight_20260810\external_dependency_sendout_evidence_intake_qa.csv",
    "reports\external_dependency_sendout_evidence_intake_preflight_20260810\EXTERNAL_DEPENDENCY_SENDOUT_EVIDENCE_INTAKE_PREFLIGHT_README.md",
    "reports\external_dependency_sendout_evidence_intake_preflight_20260810\external_dependency_sendout_evidence_intake_preflight_report.md",
    "reports\external_dependency_sendout_evidence_intake_preflight_20260810\external_dependency_sendout_evidence_intake_preflight_summary.json",
    "reports\external_dependency_eds_guarded_writeback_applier_20260810\external_dependency_eds_guarded_writeback_preflight.csv",
    "reports\external_dependency_eds_guarded_writeback_applier_20260810\external_dependency_eds_guarded_writeback_candidate_audit.csv",
    "reports\external_dependency_eds_guarded_writeback_applier_20260810\external_dependency_eds_guarded_writeback_qa.csv",
    "reports\external_dependency_eds_guarded_writeback_applier_20260810\EXTERNAL_DEPENDENCY_EDS_GUARDED_WRITEBACK_APPLIER_README.md",
    "reports\external_dependency_eds_guarded_writeback_applier_20260810\external_dependency_eds_guarded_writeback_applier_report.md",
    "reports\external_dependency_eds_guarded_writeback_applier_20260810\external_dependency_eds_guarded_writeback_applier_summary.json",
    "reports\external_dependency_post_writeback_revalidation_orchestrator_20260810\external_dependency_post_writeback_revalidation_sequence.csv",
    "reports\external_dependency_post_writeback_revalidation_orchestrator_20260810\external_dependency_post_writeback_revalidation_command_manifest.csv",
    "reports\external_dependency_post_writeback_revalidation_orchestrator_20260810\external_dependency_post_writeback_revalidation_blockers.csv",
    "reports\external_dependency_post_writeback_revalidation_orchestrator_20260810\external_dependency_post_writeback_revalidation_qa.csv",
    "reports\external_dependency_post_writeback_revalidation_orchestrator_20260810\EXTERNAL_DEPENDENCY_POST_WRITEBACK_REVALIDATION_ORCHESTRATOR_README.md",
    "reports\external_dependency_post_writeback_revalidation_orchestrator_20260810\external_dependency_post_writeback_revalidation_orchestrator_report.md",
    "reports\external_dependency_post_writeback_revalidation_orchestrator_20260810\external_dependency_post_writeback_revalidation_orchestrator_summary.json",
    "reports\fmr001_sendout_completion_writeback_preflight_20260810\fmr001_sendout_completion_writeback_guard_matrix.csv",
    "reports\fmr001_sendout_completion_writeback_preflight_20260810\fmr001_sendout_completion_writeback_candidates.csv",
    "reports\fmr001_sendout_completion_writeback_preflight_20260810\fmr001_sendout_completion_writeback_blockers.csv",
    "reports\fmr001_sendout_completion_writeback_preflight_20260810\fmr001_sendout_completion_writeback_qa.csv",
    "reports\fmr001_sendout_completion_writeback_preflight_20260810\FMR001_SENDOUT_COMPLETION_WRITEBACK_PREFLIGHT_README.md",
    "reports\fmr001_sendout_completion_writeback_preflight_20260810\fmr001_sendout_completion_writeback_preflight_report.md",
    "reports\fmr001_sendout_completion_writeback_preflight_20260810\fmr001_sendout_completion_writeback_preflight_summary.json",
    "reports\fmr001_guarded_writeback_applier_20260810\fmr001_guarded_writeback_preflight.csv",
    "reports\fmr001_guarded_writeback_applier_20260810\fmr001_guarded_writeback_candidate_audit.csv",
    "reports\fmr001_guarded_writeback_applier_20260810\fmr001_guarded_writeback_qa.csv",
    "reports\fmr001_guarded_writeback_applier_20260810\FMR001_GUARDED_WRITEBACK_APPLIER_README.md",
    "reports\fmr001_guarded_writeback_applier_20260810\fmr001_guarded_writeback_applier_report.md",
    "reports\fmr001_guarded_writeback_applier_20260810\fmr001_guarded_writeback_applier_summary.json",
    "reports\fmr001_guarded_writeback_regression_20260810\fmr001_guarded_writeback_regression_cases.csv",
    "reports\fmr001_guarded_writeback_regression_20260810\fmr001_guarded_writeback_regression_qa.csv",
    "reports\fmr001_guarded_writeback_regression_20260810\FMR001_GUARDED_WRITEBACK_REGRESSION_README.md",
    "reports\fmr001_guarded_writeback_regression_20260810\fmr001_guarded_writeback_regression_report.md",
    "reports\fmr001_guarded_writeback_regression_20260810\fmr001_guarded_writeback_regression_summary.json",
    "reports\fmr002_author_decision_writeback_preflight_20260810\fmr002_author_decision_status.csv",
    "reports\fmr002_author_decision_writeback_preflight_20260810\fmr002_author_decision_writeback_guard_matrix.csv",
    "reports\fmr002_author_decision_writeback_preflight_20260810\fmr002_author_decision_writeback_candidates.csv",
    "reports\fmr002_author_decision_writeback_preflight_20260810\fmr002_author_decision_writeback_blockers.csv",
    "reports\fmr002_author_decision_writeback_preflight_20260810\fmr002_author_decision_writeback_qa.csv",
    "reports\fmr002_author_decision_writeback_preflight_20260810\FMR002_AUTHOR_DECISION_WRITEBACK_PREFLIGHT_README.md",
    "reports\fmr002_author_decision_writeback_preflight_20260810\fmr002_author_decision_writeback_preflight_report.md",
    "reports\fmr002_author_decision_writeback_preflight_20260810\fmr002_author_decision_writeback_preflight_summary.json",
    "reports\fmr002_guarded_writeback_applier_20260810\fmr002_guarded_writeback_preflight.csv",
    "reports\fmr002_guarded_writeback_applier_20260810\fmr002_guarded_writeback_candidate_audit.csv",
    "reports\fmr002_guarded_writeback_applier_20260810\fmr002_guarded_writeback_qa.csv",
    "reports\fmr002_guarded_writeback_applier_20260810\FMR002_GUARDED_WRITEBACK_APPLIER_README.md",
    "reports\fmr002_guarded_writeback_applier_20260810\fmr002_guarded_writeback_applier_report.md",
    "reports\fmr002_guarded_writeback_applier_20260810\fmr002_guarded_writeback_applier_summary.json",
    "reports\fmr002_guarded_writeback_regression_20260810\fmr002_guarded_writeback_regression_cases.csv",
    "reports\fmr002_guarded_writeback_regression_20260810\fmr002_guarded_writeback_regression_qa.csv",
    "reports\fmr002_guarded_writeback_regression_20260810\FMR002_GUARDED_WRITEBACK_REGRESSION_README.md",
    "reports\fmr002_guarded_writeback_regression_20260810\fmr002_guarded_writeback_regression_report.md",
    "reports\fmr002_guarded_writeback_regression_20260810\fmr002_guarded_writeback_regression_summary.json",
    "reports\fmr003_returned_evidence_writeback_preflight_20260810\fmr003_returned_evidence_writeback_guard_matrix.csv",
    "reports\fmr003_returned_evidence_writeback_preflight_20260810\fmr003_returned_evidence_writeback_candidates.csv",
    "reports\fmr003_returned_evidence_writeback_preflight_20260810\fmr003_returned_evidence_writeback_blockers.csv",
    "reports\fmr003_returned_evidence_writeback_preflight_20260810\fmr003_returned_evidence_writeback_qa.csv",
    "reports\fmr003_returned_evidence_writeback_preflight_20260810\FMR003_RETURNED_EVIDENCE_WRITEBACK_PREFLIGHT_README.md",
    "reports\fmr003_returned_evidence_writeback_preflight_20260810\fmr003_returned_evidence_writeback_preflight_report.md",
    "reports\fmr003_returned_evidence_writeback_preflight_20260810\fmr003_returned_evidence_writeback_preflight_summary.json",
    "reports\fmr003_guarded_writeback_applier_20260810\fmr003_guarded_writeback_preflight.csv",
    "reports\fmr003_guarded_writeback_applier_20260810\fmr003_guarded_writeback_candidate_audit.csv",
    "reports\fmr003_guarded_writeback_applier_20260810\fmr003_guarded_writeback_qa.csv",
    "reports\fmr003_guarded_writeback_applier_20260810\FMR003_GUARDED_WRITEBACK_APPLIER_README.md",
    "reports\fmr003_guarded_writeback_applier_20260810\fmr003_guarded_writeback_applier_report.md",
    "reports\fmr003_guarded_writeback_applier_20260810\fmr003_guarded_writeback_applier_summary.json",
    "reports\fmr003_guarded_writeback_regression_20260810\fmr003_guarded_writeback_regression_cases.csv",
    "reports\fmr003_guarded_writeback_regression_20260810\fmr003_guarded_writeback_regression_qa.csv",
    "reports\fmr003_guarded_writeback_regression_20260810\FMR003_GUARDED_WRITEBACK_REGRESSION_README.md",
    "reports\fmr003_guarded_writeback_regression_20260810\fmr003_guarded_writeback_regression_report.md",
    "reports\fmr003_guarded_writeback_regression_20260810\fmr003_guarded_writeback_regression_summary.json",
    "reports\fmr004_figure_review_writeback_preflight_20260810\fmr004_figure_review_status.csv",
    "reports\fmr004_figure_review_writeback_preflight_20260810\fmr004_figure_review_writeback_guard_matrix.csv",
    "reports\fmr004_figure_review_writeback_preflight_20260810\fmr004_figure_review_writeback_candidates.csv",
    "reports\fmr004_figure_review_writeback_preflight_20260810\fmr004_figure_review_writeback_blockers.csv",
    "reports\fmr004_figure_review_writeback_preflight_20260810\fmr004_figure_review_writeback_qa.csv",
    "reports\fmr004_figure_review_writeback_preflight_20260810\FMR004_FIGURE_REVIEW_WRITEBACK_PREFLIGHT_README.md",
    "reports\fmr004_figure_review_writeback_preflight_20260810\fmr004_figure_review_writeback_preflight_report.md",
    "reports\fmr004_figure_review_writeback_preflight_20260810\fmr004_figure_review_writeback_preflight_summary.json",
    "reports\fmr004_guarded_writeback_applier_20260810\fmr004_guarded_writeback_preflight.csv",
    "reports\fmr004_guarded_writeback_applier_20260810\fmr004_guarded_writeback_candidate_audit.csv",
    "reports\fmr004_guarded_writeback_applier_20260810\fmr004_guarded_writeback_qa.csv",
    "reports\fmr004_guarded_writeback_applier_20260810\FMR004_GUARDED_WRITEBACK_APPLIER_README.md",
    "reports\fmr004_guarded_writeback_applier_20260810\fmr004_guarded_writeback_applier_report.md",
    "reports\fmr004_guarded_writeback_applier_20260810\fmr004_guarded_writeback_applier_summary.json",
    "reports\fmr004_guarded_writeback_regression_20260810\fmr004_guarded_writeback_regression_cases.csv",
    "reports\fmr004_guarded_writeback_regression_20260810\fmr004_guarded_writeback_regression_qa.csv",
    "reports\fmr004_guarded_writeback_regression_20260810\FMR004_GUARDED_WRITEBACK_REGRESSION_README.md",
    "reports\fmr004_guarded_writeback_regression_20260810\fmr004_guarded_writeback_regression_report.md",
    "reports\fmr004_guarded_writeback_regression_20260810\fmr004_guarded_writeback_regression_summary.json",
    "reports\fmr005_repository_rights_doi_writeback_preflight_20260810\fmr005_repository_metadata_status.csv",
    "reports\fmr005_repository_rights_doi_writeback_preflight_20260810\fmr005_rights_licence_status.csv",
    "reports\fmr005_repository_rights_doi_writeback_preflight_20260810\fmr005_repository_rights_doi_guard_matrix.csv",
    "reports\fmr005_repository_rights_doi_writeback_preflight_20260810\fmr005_repository_rights_doi_candidates.csv",
    "reports\fmr005_repository_rights_doi_writeback_preflight_20260810\fmr005_repository_rights_doi_blockers.csv",
    "reports\fmr005_repository_rights_doi_writeback_preflight_20260810\fmr005_repository_rights_doi_qa.csv",
    "reports\fmr005_repository_rights_doi_writeback_preflight_20260810\FMR005_REPOSITORY_RIGHTS_DOI_WRITEBACK_PREFLIGHT_README.md",
    "reports\fmr005_repository_rights_doi_writeback_preflight_20260810\fmr005_repository_rights_doi_writeback_preflight_report.md",
    "reports\fmr005_repository_rights_doi_writeback_preflight_20260810\fmr005_repository_rights_doi_writeback_preflight_summary.json",
    "reports\fmr005_guarded_writeback_applier_20260810\fmr005_guarded_writeback_preflight.csv",
    "reports\fmr005_guarded_writeback_applier_20260810\fmr005_guarded_writeback_candidate_audit.csv",
    "reports\fmr005_guarded_writeback_applier_20260810\fmr005_guarded_writeback_qa.csv",
    "reports\fmr005_guarded_writeback_applier_20260810\FMR005_GUARDED_WRITEBACK_APPLIER_README.md",
    "reports\fmr005_guarded_writeback_applier_20260810\fmr005_guarded_writeback_applier_report.md",
    "reports\fmr005_guarded_writeback_applier_20260810\fmr005_guarded_writeback_applier_summary.json",
    "reports\fmr005_guarded_writeback_regression_20260810\fmr005_guarded_writeback_regression_cases.csv",
    "reports\fmr005_guarded_writeback_regression_20260810\fmr005_guarded_writeback_regression_qa.csv",
    "reports\fmr005_guarded_writeback_regression_20260810\FMR005_GUARDED_WRITEBACK_REGRESSION_README.md",
    "reports\fmr005_guarded_writeback_regression_20260810\fmr005_guarded_writeback_regression_report.md",
    "reports\fmr005_guarded_writeback_regression_20260810\fmr005_guarded_writeback_regression_summary.json",
    "reports\fmr006_guarded_recheck_receipt_writeback_preflight_20260810\fmr006_prerequisite_receipt_status.csv",
    "reports\fmr006_guarded_recheck_receipt_writeback_preflight_20260810\fmr006_guarded_recheck_receipt_guard_matrix.csv",
    "reports\fmr006_guarded_recheck_receipt_writeback_preflight_20260810\fmr006_guarded_recheck_receipt_candidates.csv",
    "reports\fmr006_guarded_recheck_receipt_writeback_preflight_20260810\fmr006_guarded_recheck_receipt_blockers.csv",
    "reports\fmr006_guarded_recheck_receipt_writeback_preflight_20260810\fmr006_guarded_recheck_receipt_qa.csv",
    "reports\fmr006_guarded_recheck_receipt_writeback_preflight_20260810\FMR006_GUARDED_RECHECK_RECEIPT_WRITEBACK_PREFLIGHT_README.md",
    "reports\fmr006_guarded_recheck_receipt_writeback_preflight_20260810\fmr006_guarded_recheck_receipt_writeback_preflight_report.md",
    "reports\fmr006_guarded_recheck_receipt_writeback_preflight_20260810\fmr006_guarded_recheck_receipt_writeback_preflight_summary.json",
    "reports\fmr006_guarded_writeback_applier_20260810\fmr006_guarded_writeback_preflight.csv",
    "reports\fmr006_guarded_writeback_applier_20260810\fmr006_guarded_writeback_candidate_audit.csv",
    "reports\fmr006_guarded_writeback_applier_20260810\fmr006_guarded_writeback_qa.csv",
    "reports\fmr006_guarded_writeback_applier_20260810\FMR006_GUARDED_WRITEBACK_APPLIER_README.md",
    "reports\fmr006_guarded_writeback_applier_20260810\fmr006_guarded_writeback_applier_report.md",
    "reports\fmr006_guarded_writeback_applier_20260810\fmr006_guarded_writeback_applier_summary.json",
    "reports\fmr006_guarded_writeback_regression_20260810\fmr006_guarded_writeback_regression_cases.csv",
    "reports\fmr006_guarded_writeback_regression_20260810\fmr006_guarded_writeback_regression_qa.csv",
    "reports\fmr006_guarded_writeback_regression_20260810\FMR006_GUARDED_WRITEBACK_REGRESSION_README.md",
    "reports\fmr006_guarded_writeback_regression_20260810\fmr006_guarded_writeback_regression_report.md",
    "reports\fmr006_guarded_writeback_regression_20260810\fmr006_guarded_writeback_regression_summary.json",
    "reports\fmr_guarded_writeback_coverage_audit_20260810\fmr_guarded_writeback_coverage_matrix.csv",
    "reports\fmr_guarded_writeback_coverage_audit_20260810\fmr_guarded_writeback_coverage_blockers.csv",
    "reports\fmr_guarded_writeback_coverage_audit_20260810\fmr_guarded_writeback_coverage_qa.csv",
    "reports\fmr_guarded_writeback_coverage_audit_20260810\FMR_GUARDED_WRITEBACK_COVERAGE_AUDIT_README.md",
    "reports\fmr_guarded_writeback_coverage_audit_20260810\fmr_guarded_writeback_coverage_audit_report.md",
    "reports\fmr_guarded_writeback_coverage_audit_20260810\fmr_guarded_writeback_coverage_audit_summary.json",
    "reports\fmr_evidence_to_writeback_execution_order_audit_20260810\fmr_evidence_to_writeback_execution_order.csv",
    "reports\fmr_evidence_to_writeback_execution_order_audit_20260810\fmr_guarded_writeback_command_manifest.csv",
    "reports\fmr_evidence_to_writeback_execution_order_audit_20260810\fmr_execution_order_global_gates.csv",
    "reports\fmr_evidence_to_writeback_execution_order_audit_20260810\fmr_execution_order_blockers.csv",
    "reports\fmr_evidence_to_writeback_execution_order_audit_20260810\fmr_execution_order_qa.csv",
    "reports\fmr_evidence_to_writeback_execution_order_audit_20260810\FMR_EVIDENCE_TO_WRITEBACK_EXECUTION_ORDER_AUDIT_README.md",
    "reports\fmr_evidence_to_writeback_execution_order_audit_20260810\fmr_evidence_to_writeback_execution_order_audit_report.md",
    "reports\fmr_evidence_to_writeback_execution_order_audit_20260810\fmr_evidence_to_writeback_execution_order_audit_summary.json",
    "reports\fmr_manual_evidence_inbox_integrity_audit_20260810\fmr_manual_evidence_inbox_integrity_matrix.csv",
    "reports\fmr_manual_evidence_inbox_integrity_audit_20260810\fmr_manual_evidence_candidate_file_audit.csv",
    "reports\fmr_manual_evidence_inbox_integrity_audit_20260810\fmr_manual_evidence_inbox_blockers.csv",
    "reports\fmr_manual_evidence_inbox_integrity_audit_20260810\fmr_manual_evidence_inbox_qa.csv",
    "reports\fmr_manual_evidence_inbox_integrity_audit_20260810\FMR_MANUAL_EVIDENCE_INBOX_INTEGRITY_AUDIT_README.md",
    "reports\fmr_manual_evidence_inbox_integrity_audit_20260810\fmr_manual_evidence_inbox_integrity_audit_report.md",
    "reports\fmr_manual_evidence_inbox_integrity_audit_20260810\fmr_manual_evidence_inbox_integrity_audit_summary.json",
    "reports\fmr_manual_evidence_operator_packet_20260810\fmr_manual_evidence_operator_packet.csv",
    "reports\fmr_manual_evidence_operator_packet_20260810\fmr_manual_evidence_operator_stop_rules.csv",
    "reports\fmr_manual_evidence_operator_packet_20260810\fmr_manual_evidence_operator_qa.csv",
    "reports\fmr_manual_evidence_operator_packet_20260810\FMR_MANUAL_EVIDENCE_OPERATOR_PACKET_README.md",
    "reports\fmr_manual_evidence_operator_packet_20260810\fmr_manual_evidence_operator_packet_report.md",
    "reports\fmr_manual_evidence_operator_packet_20260810\fmr_manual_evidence_operator_packet_summary.json",
    "reports\final_execution_board_20260810\final_execution_board.csv",
    "reports\final_execution_board_20260810\final_execution_unlock_sequence.csv",
    "reports\final_execution_board_20260810\final_execution_no_go_rules.csv",
    "reports\final_execution_board_20260810\final_execution_board_qa.csv",
    "reports\final_execution_board_20260810\FINAL_EXECUTION_BOARD_README.md",
    "reports\final_execution_board_20260810\final_execution_board_report.md",
    "reports\final_execution_board_20260810\final_execution_board_summary.json",
    "reports\manual_only_execution_forms_20260810\manual_only_execution_forms_index.csv",
    "reports\manual_only_execution_forms_20260810\manual_only_execution_evidence_manifest.csv",
    "reports\manual_only_execution_forms_20260810\manual_only_execution_stop_rules.csv",
    "reports\manual_only_execution_forms_20260810\manual_only_execution_forms_qa.csv",
    "reports\manual_only_execution_forms_20260810\MANUAL_ONLY_EXECUTION_FORMS_README.md",
    "reports\manual_only_execution_forms_20260810\manual_only_execution_forms_report.md",
    "reports\manual_only_execution_forms_20260810\manual_only_execution_forms_summary.json",
    "reports\manual_only_execution_forms_20260810\forms\MOF-001_external_sendout.csv",
    "reports\manual_only_execution_forms_20260810\forms\MOF-002_author_decisions.csv",
    "reports\manual_only_execution_forms_20260810\forms\MOF-003_returned_files.csv",
    "reports\manual_only_execution_forms_20260810\forms\MOF-004_figure_approval.csv",
    "reports\manual_only_execution_forms_20260810\forms\MOF-005_repository_rights_doi.csv",
    "reports\manual_only_execution_forms_validation_20260810\manual_only_execution_form_validation_status.csv",
    "reports\manual_only_execution_forms_validation_20260810\manual_only_execution_form_blockers.csv",
    "reports\manual_only_execution_forms_validation_20260810\manual_only_execution_form_to_validator_routes.csv",
    "reports\manual_only_execution_forms_validation_20260810\manual_only_execution_form_validation_qa.csv",
    "reports\manual_only_execution_forms_validation_20260810\MANUAL_ONLY_EXECUTION_FORMS_VALIDATION_README.md",
    "reports\manual_only_execution_forms_validation_20260810\manual_only_execution_forms_validation_report.md",
    "reports\manual_only_execution_forms_validation_20260810\manual_only_execution_forms_validation_summary.json",
    "reports\manual_evidence_readiness_monitor_20260810\manual_evidence_readiness_monitor.csv",
    "reports\manual_evidence_readiness_monitor_20260810\manual_evidence_next_allowed_actions.csv",
    "reports\manual_evidence_readiness_monitor_20260810\manual_evidence_readiness_monitor_qa.csv",
    "reports\manual_evidence_readiness_monitor_20260810\MANUAL_EVIDENCE_READINESS_MONITOR_README.md",
    "reports\manual_evidence_readiness_monitor_20260810\manual_evidence_readiness_monitor_report.md",
    "reports\manual_evidence_readiness_monitor_20260810\manual_evidence_readiness_monitor_summary.json",
    "reports\manual_execution_brief_20260810\manual_execution_brief_actions.csv",
    "reports\manual_execution_brief_20260810\manual_execution_brief_no_go.csv",
    "reports\manual_execution_brief_20260810\manual_execution_brief_qa.csv",
    "reports\manual_execution_brief_20260810\MANUAL_EXECUTION_BRIEF_README.md",
    "reports\manual_execution_brief_20260810\manual_execution_brief_report.md",
    "reports\manual_execution_brief_20260810\manual_execution_brief_summary.json",
    "reports\manual_execution_brief_acceptance_20260810\manual_execution_brief_acceptance_checks.csv",
    "reports\manual_execution_brief_acceptance_20260810\manual_execution_brief_handoff_manifest.csv",
    "reports\manual_execution_brief_acceptance_20260810\manual_execution_brief_acceptance_qa.csv",
    "reports\manual_execution_brief_acceptance_20260810\MANUAL_EXECUTION_BRIEF_ACCEPTANCE_README.md",
    "reports\manual_execution_brief_acceptance_20260810\manual_execution_brief_acceptance_report.md",
    "reports\manual_execution_brief_acceptance_20260810\manual_execution_brief_acceptance_summary.json",
    "reports\manual_evidence_arrival_watcher_20260810\manual_evidence_watched_locations.csv",
    "reports\manual_evidence_arrival_watcher_20260810\manual_evidence_detected_candidates.csv",
    "reports\manual_evidence_arrival_watcher_20260810\manual_evidence_form_fill_status.csv",
    "reports\manual_evidence_arrival_watcher_20260810\manual_evidence_arrival_next_routes.csv",
    "reports\manual_evidence_arrival_watcher_20260810\manual_evidence_arrival_watcher_qa.csv",
    "reports\manual_evidence_arrival_watcher_20260810\MANUAL_EVIDENCE_ARRIVAL_WATCHER_README.md",
    "reports\manual_evidence_arrival_watcher_20260810\manual_evidence_arrival_watcher_report.md",
    "reports\manual_evidence_arrival_watcher_20260810\manual_evidence_arrival_watcher_summary.json",
    "reports\manual_evidence_route_snapshot_20260810\manual_evidence_route_snapshot.csv",
    "reports\manual_evidence_route_snapshot_20260810\manual_evidence_runnable_validation_queue.csv",
    "reports\manual_evidence_route_snapshot_20260810\manual_evidence_blocked_command_queue.csv",
    "reports\manual_evidence_route_snapshot_20260810\manual_evidence_route_snapshot_qa.csv",
    "reports\manual_evidence_route_snapshot_20260810\MANUAL_EVIDENCE_ROUTE_SNAPSHOT_README.md",
    "reports\manual_evidence_route_snapshot_20260810\manual_evidence_route_snapshot_report.md",
    "reports\manual_evidence_route_snapshot_20260810\manual_evidence_route_snapshot_summary.json",
    "reports\daily_execution_status_capsule_20260810\daily_execution_status_capsule.csv",
    "reports\daily_execution_status_capsule_20260810\daily_execution_status_capsule_qa.csv",
    "reports\daily_execution_status_capsule_20260810\DAILY_EXECUTION_STATUS_CAPSULE_README.md",
    "reports\daily_execution_status_capsule_20260810\daily_execution_status_capsule_report.md",
    "reports\daily_execution_status_capsule_20260810\daily_execution_status_capsule_summary.json",
    "reports\daily_execution_capsule_reentry_audit_20260810\daily_execution_capsule_reentry_checks.csv",
    "reports\daily_execution_capsule_reentry_audit_20260810\daily_execution_capsule_reentry_next_actions.csv",
    "reports\daily_execution_capsule_reentry_audit_20260810\daily_execution_capsule_reentry_qa.csv",
    "reports\daily_execution_capsule_reentry_audit_20260810\DAILY_EXECUTION_CAPSULE_REENTRY_AUDIT_README.md",
    "reports\daily_execution_capsule_reentry_audit_20260810\daily_execution_capsule_reentry_audit_report.md",
    "reports\daily_execution_capsule_reentry_audit_20260810\daily_execution_capsule_reentry_audit_summary.json",
    "reports\manual_action_backfill_template_audit_20260810\manual_action_backfill_required_fields.csv",
    "reports\manual_action_backfill_template_audit_20260810\manual_action_backfill_form_audit.csv",
    "reports\manual_action_backfill_template_audit_20260810\manual_action_backfill_order.csv",
    "reports\manual_action_backfill_template_audit_20260810\manual_action_backfill_template_audit_qa.csv",
    "reports\manual_action_backfill_template_audit_20260810\MANUAL_ACTION_BACKFILL_TEMPLATE_AUDIT_README.md",
    "reports\manual_action_backfill_template_audit_20260810\manual_action_backfill_template_audit_report.md",
    "reports\manual_action_backfill_template_audit_20260810\manual_action_backfill_template_audit_summary.json",
    "reports\manual_form_validation_launcher_guard_20260810\manual_form_validation_launcher_guard.csv",
    "reports\manual_form_validation_launcher_guard_20260810\manual_form_validation_launcher_blockers.csv",
    "reports\manual_form_validation_launcher_guard_20260810\manual_form_validation_launcher_guard_qa.csv",
    "reports\manual_form_validation_launcher_guard_20260810\MANUAL_FORM_VALIDATION_LAUNCHER_GUARD_README.md",
    "reports\manual_form_validation_launcher_guard_20260810\manual_form_validation_launcher_guard_report.md",
    "reports\manual_form_validation_launcher_guard_20260810\manual_form_validation_launcher_guard_summary.json",
    "reports\external_manual_evidence_blocker_certificate_20260810\external_manual_evidence_blockers.csv",
    "reports\external_manual_evidence_blocker_certificate_20260810\external_manual_evidence_allowed_vs_forbidden.csv",
    "reports\external_manual_evidence_blocker_certificate_20260810\external_manual_evidence_blocker_certificate_qa.csv",
    "reports\external_manual_evidence_blocker_certificate_20260810\EXTERNAL_MANUAL_EVIDENCE_BLOCKER_CERTIFICATE_README.md",
    "reports\external_manual_evidence_blocker_certificate_20260810\external_manual_evidence_blocker_certificate_report.md",
    "reports\external_manual_evidence_blocker_certificate_20260810\external_manual_evidence_blocker_certificate_summary.json",
    "reports\local_only_prereview_package_20260811\local_only_prereview_included_items.csv",
    "reports\local_only_prereview_package_20260811\local_only_prereview_excluded_formal_items.csv",
    "reports\local_only_prereview_package_20260811\local_only_prereview_copied_files.csv",
    "reports\local_only_prereview_package_20260811\local_only_prereview_next_actions.csv",
    "reports\local_only_prereview_package_20260811\local_only_prereview_package_qa.csv",
    "reports\local_only_prereview_package_20260811\LOCAL_ONLY_PREREVIEW_PACKAGE_README.md",
    "reports\local_only_prereview_package_20260811\local_only_prereview_package_report.md",
    "reports\local_only_prereview_package_20260811\local_only_prereview_package_summary.json",
    "reports\local_only_prereview_package_20260811\package_files\natcomms_initial_submission_text_preassembly.md",
    "reports\local_only_prereview_package_20260811\package_files\title_abstract_significance.md",
    "reports\local_only_prereview_package_20260811\package_files\cover_letter_skeleton.md",
    "reports\figure_preview_completion_bridge_20260811\figure_preview_file_inventory.csv",
    "reports\figure_preview_completion_bridge_20260811\figure_preview_to_final_gate_bridge.csv",
    "reports\figure_preview_completion_bridge_20260811\figure_preview_completion_bridge_qa.csv",
    "reports\figure_preview_completion_bridge_20260811\FIGURE_PREVIEW_COMPLETION_BRIDGE_README.md",
    "reports\figure_preview_completion_bridge_20260811\figure_preview_completion_bridge_report.md",
    "reports\figure_preview_completion_bridge_20260811\figure_preview_completion_bridge_summary.json",
    "reports\figure_final_candidate_review_packet_20260811\figure_final_candidate_review_manifest.csv",
    "reports\figure_final_candidate_review_packet_20260811\figure_final_candidate_support_controls.csv",
    "reports\figure_final_candidate_review_packet_20260811\figure_final_candidate_gate_matrix.csv",
    "reports\figure_final_candidate_review_packet_20260811\figure_final_candidate_review_packet_qa.csv",
    "reports\figure_final_candidate_review_packet_20260811\FIGURE_FINAL_CANDIDATE_REVIEW_PACKET_README.md",
    "reports\figure_final_candidate_review_packet_20260811\figure_final_candidate_review_packet_report.md",
    "reports\figure_final_candidate_review_packet_20260811\figure_final_candidate_review_packet_summary.json",
    "reports\source_data_panel_map_review_packet_20260811\source_data_panel_map_review_matrix.csv",
    "reports\source_data_panel_map_review_packet_20260811\source_data_panel_map_copied_sources.csv",
    "reports\source_data_panel_map_review_packet_20260811\source_data_panel_map_gate_matrix.csv",
    "reports\source_data_panel_map_review_packet_20260811\source_data_panel_map_review_packet_qa.csv",
    "reports\source_data_panel_map_review_packet_20260811\SOURCE_DATA_PANEL_MAP_REVIEW_PACKET_README.md",
    "reports\source_data_panel_map_review_packet_20260811\source_data_panel_map_review_packet_report.md",
    "reports\source_data_panel_map_review_packet_20260811\source_data_panel_map_review_packet_summary.json",
    "reports\results_figure_source_alignment_packet_20260811\results_figure_source_alignment_matrix.csv",
    "reports\results_figure_source_alignment_packet_20260811\results_claim_risk_guardrails.csv",
    "reports\results_figure_source_alignment_packet_20260811\results_figure_source_alignment_qa.csv",
    "reports\results_figure_source_alignment_packet_20260811\RESULTS_FIGURE_SOURCE_ALIGNMENT_README.md",
    "reports\results_figure_source_alignment_packet_20260811\results_figure_source_alignment_report.md",
    "reports\results_figure_source_alignment_packet_20260811\results_figure_source_alignment_summary.json",
    "reports\availability_repository_consistency_review_20260811\availability_repository_consistency_matrix.csv",
    "reports\availability_repository_consistency_review_20260811\availability_repository_blockers.csv",
    "reports\availability_repository_consistency_review_20260811\availability_repository_metadata_status.csv",
    "reports\availability_repository_consistency_review_20260811\availability_repository_consistency_qa.csv",
    "reports\availability_repository_consistency_review_20260811\AVAILABILITY_REPOSITORY_CONSISTENCY_README.md",
    "reports\availability_repository_consistency_review_20260811\availability_repository_consistency_report.md",
    "reports\availability_repository_consistency_review_20260811\availability_repository_consistency_summary.json",
    "reports\experiment_completion_audit_20260811\experiment_completion_module_scores.csv",
    "reports\experiment_completion_audit_20260811\experiment_completion_blockers.csv",
    "reports\experiment_completion_audit_20260811\experiment_completion_next_actions.csv",
    "reports\experiment_completion_audit_20260811\experiment_completion_audit_qa.csv",
    "reports\experiment_completion_audit_20260811\experiment_completion_audit_report.md",
    "reports\experiment_completion_audit_20260811\experiment_completion_audit_summary.json"
)

foreach ($Artifact in $RequiredArtifacts) {
    $Path = Join-Path $Bench $Artifact
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing required artifact: $Path"
    }
}

Write-Host "M0-M2 checks completed"
