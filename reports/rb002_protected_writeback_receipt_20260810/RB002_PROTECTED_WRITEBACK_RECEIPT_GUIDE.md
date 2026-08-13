# RB-002 protected writeback receipt guide 2026-08-10

Fill this receipt only after RB-001 closes and `writeback_allowed_rows>0`.

Required sequence:

1. Confirm RB-001 closeout dashboard reports `rb001_closed=true`.
2. Confirm RB-002 readiness dashboard reports `writeback_allowed_rows>0`.
3. Snapshot the old value before editing any protected target.
4. Write only the listed target fields.
5. Record source evidence file and SHA256.
6. Run the listed validation command after manual writeback.
7. Do not edit any `do_not_edit` field.

Current status: template only; writeback is not allowed.
