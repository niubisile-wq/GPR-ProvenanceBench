# Nat Comms author sendout bundle instructions

This bundle is ready for manual sendout, but it has not been sent.

Send the files under `attachments/` together with `author_sendout_email_ready_draft_cn.md` as the email body.

After replies return, rerun:

1. `py GPR-ProvenanceBench\scripts\build_natcomms_author_reply_ingestion_validator.py`
2. `py GPR-ProvenanceBench\scripts\build_natcomms_gate_closure_evidence_binder.py`
3. `py GPR-ProvenanceBench\scripts\build_natcomms_finalization_command_dashboard_v3.py`
4. `py GPR-ProvenanceBench\scripts\run_m0_m2_checks.ps1`

Boundary: this bundle does not send email, collect replies, select a backend, render figures, create DOI records, close gates or submit the manuscript.
