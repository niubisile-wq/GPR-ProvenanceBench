# RB-001 return evidence drop kit 2026-08-10

Purpose: place real returned evidence into the canonical inbox without writing protected manuscript, figure, repository, reference or submission targets.

Canonical inbox root for manual placement: `final_return_evidence_inbox_20260810`

## Route Folders

### RTE-001 01_author_sendout
- Folder: `final_return_evidence_inbox_20260810/01_author_sendout`
- Evidence: author sendout proof
- Required files: sent email export or screenshot; recipient list; timestamp; subject; handoff zip SHA256
- Accepted extensions: .md;.txt;.csv;.pdf;.png;.jpg;.zip
- Current candidate files: 0
- First validation command: `py scripts/build_post_dispatch_evidence_intake_validator.py`

### RTE-002 02_author_replies
- Folder: `final_return_evidence_inbox_20260810/02_author_replies`
- Evidence: author replies and backend/scope decision
- Required files: completed reply form; backend/scope decision; administrative confirmations
- Accepted extensions: .csv;.xlsx;.docx;.pdf;.txt;.md;.zip
- Current candidate files: 0
- First validation command: `py scripts/build_natcomms_author_reply_ingestion_validator.py`

### RTE-003 03_figure_review
- Folder: `final_return_evidence_inbox_20260810/03_figure_review`
- Evidence: final figure review decisions
- Required files: completed figure review form; marked preview approvals or revision notes
- Accepted extensions: .csv;.xlsx;.pdf;.png;.jpg;.zip
- Current candidate files: 0
- First validation command: `py scripts/build_python_figure_author_review_intake_validator.py`

### RTE-004 04_repository_rights_doi
- Folder: `final_return_evidence_inbox_20260810/04_repository_rights_doi`
- Evidence: repository DOI, licence and rights
- Required files: repository DOI proof; licence text; third-party rights proof; restricted-data wording
- Accepted extensions: .csv;.xlsx;.docx;.pdf;.txt;.md;.png;.jpg;.zip
- Current candidate files: 0
- First validation command: `py scripts/build_availability_repository_finalization_validator.py`

### RTE-005 05_reporting_summary
- Folder: `final_return_evidence_inbox_20260810/05_reporting_summary`
- Evidence: Reporting Summary answers
- Required files: completed Reporting Summary response file; dependency notes
- Accepted extensions: .csv;.xlsx;.docx;.pdf;.txt;.md;.zip
- Current candidate files: 0
- First validation command: `py scripts/build_reporting_summary_final_lock_validator.py`

### RTE-006 06_references
- Folder: `final_return_evidence_inbox_20260810/06_references`
- Evidence: final reference verification
- Required files: verified reference list; placeholder replacement authorization; exported citation file
- Accepted extensions: .csv;.xlsx;.ris;.bib;.enw;.txt;.md;.docx;.pdf;.zip
- Current candidate files: 0
- First validation command: `py scripts/build_reference_final_lock_validator.py`

### RTE-007 07_submission_portal
- Folder: `final_return_evidence_inbox_20260810/07_submission_portal`
- Evidence: portal upload and submission proof
- Required files: portal metadata screenshots; upload receipt; submission confirmation only after all gates close
- Accepted extensions: .csv;.xlsx;.pdf;.png;.jpg;.txt;.md;.zip
- Current candidate files: 0
- First validation command: `py scripts/build_natcomms_submission_final_lock_validator.py`

## Required Hash Record

After copying a real file into a route folder, calculate SHA256 and fill `rb001_return_evidence_hash_manifest_template.csv`. Do not fill placeholder rows before real files exist.

## Hard Boundaries

1. candidate_return_files=0
2. ready_to_close_rows=0
3. writeback_allowed_rows=0
4. submission_ready=False
5. This kit does not close RB-001; it only makes the evidence drop action unambiguous.
