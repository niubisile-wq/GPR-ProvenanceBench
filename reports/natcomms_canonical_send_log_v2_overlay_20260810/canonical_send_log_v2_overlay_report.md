# Nat Comms Canonical Send Log v2 Overlay Report

Status: `natcomms_canonical_send_log_v2_overlay_applied_not_sent`

Current result:

1. Send log rows: 5
2. Rows overlaid: 5
3. Stale v1 rows before: 5
4. Stale v1 rows after: 0
5. V2 reference rows after: 5
6. Manual status preserved: true
7. Tracker summary updated: true
8. Tracker summary SHA matches v2: true
9. Email sent: false
10. Author replies collected: false
11. Submission ready: false

Interpretation: canonical response-log validation now uses the v2 sendout zip
reference and v2 external fingerprint while preserving the unsent manual state.
