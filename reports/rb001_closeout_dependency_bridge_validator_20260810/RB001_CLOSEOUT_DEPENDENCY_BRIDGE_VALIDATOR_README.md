# RB-001 Closeout Dependency Bridge Validator

This validator bridges the returned-file crosswalk, hash manifest readiness,
manual receipt completion, RB-001 closeout dashboard and RB-002 readiness before
any closeout or writeback preflight can be considered.

Boundary: it is read-only. It does not copy files, calculate hashes, fill
receipts, close RB-001, write protected targets, enter RB-002 or make the
manuscript submission-ready.
