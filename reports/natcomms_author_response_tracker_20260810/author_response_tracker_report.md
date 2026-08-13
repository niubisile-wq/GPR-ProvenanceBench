# Nat Comms Author Response Tracker Report

Status: `natcomms_author_response_tracker_ready_waiting_manual_sendout`

Generated rows:

1. Send log rows: 5
2. Return tracker rows: 8
3. Validation plan rows: 5
4. Post-reply rerun commands: 4
5. Stop rules: 5

Canonical sendout bundle after v2 overlay:

1. Bundle zip: `reports\natcomms_author_sendout_bundle_v2_20260810\NatComms_author_sendout_bundle_v2_20260810.zip`
2. Bundle zip SHA256: `7b64c7f43f10c909a8f77ed940ea8a8e92eb31b102686cb0f7998779fa8e5c36`
3. Overlay applied: true
4. Email sent: false

Boundary flags:

1. `email_sent=false`
2. `author_replies_collected=false`
3. `backend_selected=false`
4. `submission_ready=false`

Interpretation: the canonical response tracker now points to the v2 sendout
bundle and external v2 zip fingerprint. The manual send/reply cycle is still
controlled by explicit send timestamps and returned-file paths. All downstream
gates must remain blocked until real returned files are logged and validators
pass.
