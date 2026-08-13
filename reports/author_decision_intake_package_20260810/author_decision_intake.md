# Author decision intake package 2026-08-10

This package collects decisions that cannot be closed by local scripting alone.

## Immediate decisions

| ID | Decision | Recommended default | Blocks |
| --- | --- | --- | --- |
| D001 | Figure rendering backend | Python | Formal figure rendering, visual QA, panel-level Source Data mapping. |
| D002 | External blind asset route | Track B third-party blind asset | Blind external validation, final main claim strength, Reporting Summary blinding/external validation fields. |
| D003 | Code licence | MIT or BSD-3-Clause after institutional approval | Code Availability final wording, public code release, code DOI. |
| D004 | Derived data licence | CC BY 4.0 for derived non-raw artifacts after third-party rights review | Data Availability final wording, source-data deposit, release package. |
| D005 | Repository route | GitHub+Zenodo for code and Zenodo/OSF for derived data if rights permit | Repository identifiers, Data Availability, Code Availability, FAIR metadata. |
| D006 | Manuscript framing if external validation remains open | Benchmark/resource framing unless real blind external validation is acquired | Title, abstract, cover letter, Table 3 placement, claim strength. |
| D007 | Final reference style conversion timing | Convert after final prose lock | Final bibliography and citation numbering. |

## Current open gates from dashboard

| Priority | Gate | Status | Current best action |
| --- | --- | --- | --- |
| 1 | Real blind external validation | NO-GO | Acquire or restore a separate advisor-held/third-party GPR asset. |
| 2 | Main figure rendering | not_started | Choose Python or R before running the Nature figure workflow. |
| 3 | Repository identifiers | missing | Resolve release rights and create archive only after final source-data scope is locked. |
| 4 | Reporting Summary | incomplete | Fill from frozen Methods and final figure/table set. |
| 5 | Third-party rights | not_cleared | Review release readiness audit and exclude non-redistributable files from public package. |
| 6 | Final reference numbering | not_locked | Keep `[P#]` markers until prose and figure/table references stop moving. |

## Boundary

This intake package does not close any gate. It defines the exact choices required before figure rendering, repository deposit, external validation and final Reporting Summary can proceed.
