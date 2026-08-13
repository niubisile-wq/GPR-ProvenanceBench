# Target journal freeze record

## Record metadata

- Freeze date: 2026-08-12
- Decision status: FROZEN
- Decision owner: Author
- Record purpose: Lock the primary submission target and prevent further journal drift during manuscript preparation.

## Frozen target

- Journal: Nondestructive Testing and Evaluation
- Standard abbreviation: Nondestruct. Test. Eval.
- Publisher: Taylor & Francis Ltd., part of Informa PLC
- Journal URL: https://www.tandfonline.com/journals/gnte20/about-this-journal
- Print ISSN: 1058-9759
- Online ISSN: 1477-2671
- Submission system: ScholarOne Manuscripts
- Peer-review model: Single anonymized
- Publication model: Hybrid open access
- Default publication route: Traditional non-open-access publication
- OA exception: Open access may be selected later if an institutional agreement, funder mandate, or approved publication budget is confirmed.

## Selection basis

- 2025 CAS partition: Materials Science, Zone 2
- Scope fit: The journal explicitly covers nondestructive testing and evaluation, sensor technology, validation, simulation, modelling, and processing and analysis of NDE data.
- Modality fit: Ground-penetrating radar is an established NDT modality and has prior representation in the journal.
- Contribution fit: The manuscript is an evaluation and reliability study rather than a new-model paper.
- Official journal metrics recorded at freeze:
  - 17 days average from submission to first decision, including desk decisions
  - 36 days average from submission to first post-review decision
  - 10 days average from acceptance to online publication
  - 25% acceptance rate
- Planning estimate: Allow 3-5 months from submission to acceptance under a normal revision cycle; this is a planning estimate, not a publisher guarantee.

## Frozen manuscript positioning

The paper will be positioned as a nondestructive-evaluation reliability study:

> Acquisition-environment transfer exposes fragile generalization in GPR-based nondestructive recognition, showing that conventional random splits can overestimate deployment reliability and motivating provenance-aware validation.

The manuscript will not be positioned primarily as:

- a new neural-network architecture paper
- a leaderboard-style model comparison
- proof of universal cross-domain generalization
- a completed true blind external-validation study

## Evidence hierarchy to preserve

- Primary finding: Res-SAM cross-environment transfer exposes the strongest generalization fragility.
- Secondary finding: Mojahid split sensitivity is real but modest.
- Boundary evidence: 4TU is a stress test and feasibility boundary, not the main confirmation.
- Public fallback evidence: IOAI Radar is a completed public benchmark, not true blind external validation.
- Reporting rule: Claims must remain bounded by dataset provenance, acquisition environment, and the available validation design.

## Operational consequences

- Manuscript title, abstract, introduction, results ordering, discussion, figures, and cover letter must now be tailored to this journal.
- NDT reliability, validation, sensor/acquisition context, and deployment consequences must be foregrounded.
- Generic AI novelty language and unsupported generalization claims must be removed.
- Experiments remain closed for the current hypothesis set.
- Submission-ready status remains false until the publication gates below are closed.

## Open publication gates

- Final manuscript and journal-specific formatting
- Final figures and source-data package
- Public repository, rights, and license confirmation
- Data and code availability statements
- Complete and verified reference list
- Cover letter and author declarations
- Final decision on traditional versus open-access publication
- Explicit wording that distinguishes the IOAI public benchmark from true blind external validation

## Change control

This target may be unfrozen only if one of the following occurs:

- the author explicitly changes the target journal
- the journal issues a desk or scope rejection
- indexing, partition, warning-list, publication-policy, or institutional-eligibility status materially changes
- a new experiment materially changes the paper's central contribution or intended audience
- publication cost or rights constraints make submission impractical

Any unfreeze must be documented in a new dated decision record. This file remains the historical freeze record and must not be overwritten.

## Status snapshot

- target_journal: frozen
- target_journal_name: Nondestructive Testing and Evaluation
- experiment_execution: complete
- experiment_closure: complete
- manuscript_tailoring: pending
- submission_ready: false

