# Nat Comms Return Tracker to RB-001 Crosswalk Validator

This validator maps Nat Comms returned-file tracker rows to RB-001 canonical
drop routes and checks whether returned-file intake can proceed toward scanner
and hash reconciliation.

Boundary: it is read-only. It does not copy returned files, calculate hashes,
edit the hash manifest, write protected targets, close gates or make the
manuscript submission-ready.
