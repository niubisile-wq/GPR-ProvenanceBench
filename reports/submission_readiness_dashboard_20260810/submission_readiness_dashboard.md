# Submission readiness dashboard 2026-08-10

This dashboard consolidates manuscript, figure/table, citation, companion-artifact and release gates into one current-state view.

## Current Decision

The package is not submission-ready. The strongest current evidence remains Res-SAM environment-transfer fragility, with Mojahid directional support and 4TU stress-test/feasibility evidence. Blind external validation is still NO-GO.

## Readiness Areas

| Area | Status | Submission impact |
| --- | --- | --- |
| Manuscript assembly | not_ready | Controls whether the package can be treated as manuscript-ready. |
| Blind external validation | NO-GO | Main generalization claim cannot be final without a real blind external asset. |
| Figures | planned_anchors_locked_not_rendered | Main figures are planned but not submission-ready. |
| Tables | table_drafts_ready_not_typeset_final | Table source layer is ready; final typesetting remains open. |
| Narrative citations | candidate_citation_markers_inserted_not_final_references | Citation placeholders are resolved, but final reference placement is not locked. |
| Companion artifacts | not_ready | Data Availability, Code Availability and Reporting Summary cannot be finalized. |
| Source-data deposit | not_ready | Source-data skeleton is auditable but not final deposit. |
| Public release | not_ready | Code/data release cannot be claimed as completed. |
| Sanitized staging | internal_preview_only | Cannot be cited as a public repository. |

## Priority Queue

| Priority | Gate | Status | Current best action |
| --- | --- | --- | --- |
| 1 | Real blind external validation | NO-GO | Acquire or restore a separate advisor-held/third-party GPR asset. |
| 2 | Main figure rendering | not_started | Choose Python or R before running the Nature figure workflow. |
| 3 | Repository identifiers | missing | Resolve release rights and create archive only after final source-data scope is locked. |
| 4 | Reporting Summary | incomplete | Fill from frozen Methods and final figure/table set. |
| 5 | Third-party rights | not_cleared | Review release readiness audit and exclude non-redistributable files from public package. |
| 6 | Final reference numbering | not_locked | Keep `[P#]` markers until prose and figure/table references stop moving. |

## Boundary

This is a dashboard only. It does not convert planned figures into rendered figures, does not create repository identifiers and does not satisfy blind external validation.
