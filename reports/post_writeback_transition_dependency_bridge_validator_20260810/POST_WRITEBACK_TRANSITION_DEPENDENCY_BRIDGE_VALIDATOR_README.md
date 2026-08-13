# Post-writeback Transition Dependency Bridge Validator

This validator bridges RB-002 entry, post-writeback transition validation and
the guarded execution runner before any route-specific command can execute.

Boundary: it is read-only. It does not run route validators, execute the guarded
runner, close gates, upload files or make the manuscript submission-ready.
