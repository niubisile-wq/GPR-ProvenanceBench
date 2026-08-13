# NatComms 19.57 Sendout Evidence Intake Preflight

Status: `external_dependency_sendout_evidence_intake_preflight_ready_waiting_real_sent_messages`

Use this package after the five 19.55 manual send tasks have actually been
sent by a human account.

Manual drop zone:

`<REPO_ROOT>\manual_evidence\external_dependency_sendout_20260810`

Fill this metadata file:

`<REPO_ROOT>\reports\external_dependency_sendout_evidence_intake_preflight_20260810\external_dependency_sendout_evidence_metadata_template.csv`

Required fields per row:

1. `sent_datetime_local`
2. `sender`
3. `recipient_or_channel`
4. `sent_message_path`

The script computes `sent_message_sha256` from each file and writes candidate
EDS rows to:

`reports/external_dependency_sendout_evidence_intake_preflight_20260810/external_dependency_sendout_evidence_writeback_candidates.csv`

Current result:

1. Metadata rows: 5
2. Complete metadata rows: 0
3. Writeback candidate rows: 0
4. EDS writeback allowed: false
5. Portal upload allowed: false
6. Submission ready: false

Boundary: this preflight does not send email, overwrite the real EDS template,
fill FMR rows, run recheck, upload portal files or mark the manuscript
submitted.
