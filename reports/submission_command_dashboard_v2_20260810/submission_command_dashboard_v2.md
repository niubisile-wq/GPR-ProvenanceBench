# Submission command dashboard v2 2026-08-10

Current decision: submission is not ready.

Current manuscript branch: Track B. The paper should be positioned as a benchmark/resource and evidence-boundary manuscript unless real blind external validation is completed.

## Hard gates

### blind_external_validation
- State: NO-GO
- Owner: author/advisor/data holder
- Next action: Use Track B unless a real held-label external asset passes strict intake and locked evaluation.
- Minimum evidence: Strict-SHA manifest, label holdout, frozen prediction file, label unlock record and one locked metrics table.
- Forbidden until closed: Completed blind validation; external generalization; deployment robustness.

### formal_figures
- State: open_backend_choice_needed
- Owner: author/analyst
- Next action: Choose exactly one backend, Python or R, then render final figure set with visual QA.
- Minimum evidence: Final exports, panel labels, source-data panel map and visual QA pass record.
- Forbidden until closed: Final figure claims; final figure legends; final source-data claims.

### repository_rights_doi
- State: open
- Owner: author/institution/repository lead
- Next action: Resolve licence, rights and repository route; then create data DOI/accession and code archive DOI.
- Minimum evidence: Repository landing page, data DOI/accession, code DOI, licence and rights checklist.
- Forbidden until closed: Data deposited; code archived; public release ready.

### reporting_summary
- State: prelock_not_final
- Owner: author/analyst
- Next action: Lock only after figures, external validation status, availability statements and methods are final.
- Minimum evidence: Every Reporting Summary item has final answer and evidence trigger satisfied.
- Forbidden until closed: Final Reporting Summary ready.

### references
- State: prelock_not_final
- Owner: author/reference lead
- Next action: Verify DOI/publisher pages and claim support after final prose and figure calls lock.
- Minimum evidence: No [P#] markers remain; numbered references support local claims; bibliography verified.
- Forbidden until closed: Final numbered references.

### broad_interest_framing
- State: draft_only
- Owner: writing lead
- Next action: Use benchmark-trust framing, then align title/abstract/Introduction with final branch and figure schematic.
- Minimum evidence: Title, abstract, Introduction opening and schematic caption remain cross-field but bounded.
- Forbidden until closed: Overbroad field-wide robustness or universal leakage claims.

## Current acceptance tests

- blind_external_validation: open | Prediction file exists before label unlock, labels are released once, and locked metrics are written.
- formal_figures: open | Every retained figure panel has final export, source data and visual QA status.
- repository_rights_doi: open | Release manifest, licence, rights checklist and DOI/accession or restriction statement exist.
- broad_interest_framing: draft_only | Title, abstract, introduction opening and schematic caption state cross-field relevance without overclaiming.
- references: open | No [P#] placeholders remain and each numbered citation supports its local claim.
