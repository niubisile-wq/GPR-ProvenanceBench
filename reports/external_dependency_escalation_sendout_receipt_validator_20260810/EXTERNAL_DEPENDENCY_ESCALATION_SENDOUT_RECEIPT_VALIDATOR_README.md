# External Dependency Escalation Sendout Receipt Validator

This validator creates and checks sendout receipt rows for the 19.53 external
dependency escalation packet.

Boundary: read-only. It preserves existing manual EDS entries and verifies
sent-message SHA256 when paths are filled. It does not send email, fabricate
send evidence, fill FMR-001, run rechecks, upload portal files or mark the
manuscript submitted.
