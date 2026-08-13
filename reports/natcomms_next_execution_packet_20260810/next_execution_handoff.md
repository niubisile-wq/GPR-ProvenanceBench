# Nat Comms next execution handoff

Current state: all finalization commands remain blocked. This package turns the command dashboard into assignable work items only.

## First work item

Send or manually fill the author/corresponding-author reply tables. Do not proceed to final figure rendering or final manuscript assembly until the reply validator has been rerun on filled replies.

## Required reruns after author replies

1. `py GPR-ProvenanceBench\scripts\build_natcomms_author_reply_ingestion_validator.py`
2. `py GPR-ProvenanceBench\scripts\build_natcomms_gate_closure_evidence_binder.py`
3. `py GPR-ProvenanceBench\scripts\build_natcomms_finalization_command_dashboard_v3.py`
4. `py GPR-ProvenanceBench\scripts\run_m0_m2_checks.ps1`

Boundary: this handoff does not collect author replies, choose Python/R, render figures, create DOI records, finalize references, generate final files or submit the manuscript.
