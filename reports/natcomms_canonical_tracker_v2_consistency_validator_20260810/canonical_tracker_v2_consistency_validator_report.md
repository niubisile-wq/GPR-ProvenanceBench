# Nat Comms Canonical Tracker v2 Consistency Validator Report

Status: `natcomms_canonical_tracker_v2_consistency_validator_passed_guarded_not_sent`

Current result:

1. Send log rows: 5
2. Send log v2 rows: 5
3. Send log stale v1 rows: 0
4. Send log SHA match rows: 5
5. Tracker summary path matches v2: true
6. Tracker summary SHA matches v2: true
7. Overlay summary pass: true
8. Response log guarded: true
9. Receipt validator guarded: true
10. Submission ready: false

Interpretation: the canonical tracker is internally aligned to the v2 sendout
package while real sendout, returned-file intake and RB-001 drop remain blocked.
