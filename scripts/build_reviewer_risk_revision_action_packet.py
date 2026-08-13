#!/usr/bin/env python3
"""Convert reviewer-risk audit into executable revision actions."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
IN_DIR = BENCH_ROOT / "reports" / "pre_submission_reviewer_risk_audit_20260810"
GAP_DIR = BENCH_ROOT / "reports" / "submission_gap_closure_matrix_20260810"
OUT_DIR = BENCH_ROOT / "reports" / "reviewer_risk_revision_action_packet_20260810"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_action_rows(risk_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    action_specs = {
        "Missing real blind external validation": {
            "action_id": "RRA-001",
            "owner": "author/external holder",
            "execution_mode": "external_input_required",
            "next_action": "Secure one independent held-label GPR asset, freeze predictions before label release, and run one locked evaluation.",
            "acceptance_evidence": "Named asset holder, checksum manifest, frozen prediction file, timestamped label unlock, locked metrics table.",
            "manuscript_update": "Either add one bounded external-validation result or explicitly downgrade all external-validation language.",
            "stop_rule": "Do not claim blind external validation from protocol templates or dry runs.",
        },
        "Main figures not rendered": {
            "action_id": "RRA-002",
            "owner": "analysis/figure lead",
            "execution_mode": "local_after_backend_choice",
            "next_action": "Render the final Figure 1-Figure 6 set or a justified reduced figure set, then run panel-level visual QA.",
            "acceptance_evidence": "Final SVG/PDF/PNG exports, source-data map, panel checklist, visual QA pass record.",
            "manuscript_update": "Replace conceptual figure references with final figure numbers and panel calls.",
            "stop_rule": "Do not lock results prose against unrendered or unreviewed figures.",
        },
        "Repository and rights unresolved": {
            "action_id": "RRA-003",
            "owner": "author/institution",
            "execution_mode": "author_decision_required",
            "next_action": "Choose repository route, code licence, derived-data licence and third-party exclusion list before DOI creation.",
            "acceptance_evidence": "Licence decision, rights checklist, release manifest, repository metadata, DOI/accession or documented restriction.",
            "manuscript_update": "Finalize Data Availability and Code Availability statements only after identifiers or restrictions are real.",
            "stop_rule": "Do not write public repository, data DOI or code DOI until identifiers exist.",
        },
        "Broad-interest case not fully established": {
            "action_id": "RRA-004",
            "owner": "corresponding author/writing lead",
            "execution_mode": "local_writing_revision",
            "next_action": "Sharpen the cross-field argument from GPR-only performance to environment-shift and benchmark-trust implications.",
            "acceptance_evidence": "Revised title/abstract/introduction significance paragraph and workflow schematic caption.",
            "manuscript_update": "Lead with relevance, novelty and trust in that order; keep the implication narrower than current evidence.",
            "stop_rule": "Do not imply field-wide robustness or universal leakage without external evidence.",
        },
        "References not final": {
            "action_id": "RRA-005",
            "owner": "reference lead",
            "execution_mode": "manual_verification_required",
            "next_action": "Replace candidate [P#] markers with verified Nature-style numbered references after final prose lock.",
            "acceptance_evidence": "Verified reference library, numbered in-text citations, bibliography, citation-to-claim audit.",
            "manuscript_update": "Remove placeholder citation markers and confirm prior-work distinction.",
            "stop_rule": "Do not treat candidate citation markers as final references.",
        },
    }

    rows: list[dict[str, str]] = []
    for row in risk_rows:
        spec = action_specs[row["risk"]]
        rows.append(
            {
                "priority": row["priority"],
                "action_id": spec["action_id"],
                "reviewer_risk": row["risk"],
                "reviewer_axis": row["reviewer_axis"],
                "owner": spec["owner"],
                "execution_mode": spec["execution_mode"],
                "next_action": spec["next_action"],
                "acceptance_evidence": spec["acceptance_evidence"],
                "manuscript_update": spec["manuscript_update"],
                "stop_rule": spec["stop_rule"],
            }
        )
    return rows


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    risk_rows = read_csv(IN_DIR / "reviewer_risk_priority_queue.csv")
    gap_rows = read_csv(GAP_DIR / "submission_gap_closure_matrix.csv")
    action_rows = build_action_rows(risk_rows)

    write_csv(
        OUT_DIR / "reviewer_risk_to_action_matrix.csv",
        action_rows,
        [
            "priority",
            "action_id",
            "reviewer_risk",
            "reviewer_axis",
            "owner",
            "execution_mode",
            "next_action",
            "acceptance_evidence",
            "manuscript_update",
            "stop_rule",
        ],
    )

    sprint_rows = [
        {
            "day_window": "Day 0-1",
            "focus": "Author decisions",
            "actions": "Confirm figure backend, external blind asset route, repository route and licence constraints.",
            "exit_condition": "Decision log has no empty owner-critical fields.",
        },
        {
            "day_window": "Day 1-4",
            "focus": "Figures and source data",
            "actions": "Render figure set after backend choice; create panel-level source-data anchors and visual QA records.",
            "exit_condition": "Figure files, source-data map and QA checklist exist for every retained panel.",
        },
        {
            "day_window": "Day 1-7",
            "focus": "Blind external validation",
            "actions": "If an asset holder exists, execute blind handoff, prediction freeze, label unlock and one-shot evaluation.",
            "exit_condition": "Locked metrics table exists, or manuscript framing is downgraded with no external-validation claim.",
        },
        {
            "day_window": "Day 4-10",
            "focus": "Repository and rights",
            "actions": "Finalize release manifest, exclusions, licences, repository metadata and DOI/accession path.",
            "exit_condition": "Public identifiers or explicit restriction language can be truthfully inserted.",
        },
        {
            "day_window": "Day 7-14",
            "focus": "Manuscript lock",
            "actions": "Update claims, figure calls, availability statements, Reporting Summary and numbered references.",
            "exit_condition": "Submission-readiness dashboard has no open hard gate, or the paper is explicitly held.",
        },
    ]
    write_csv(OUT_DIR / "next_14_day_revision_sprint.csv", sprint_rows, ["day_window", "focus", "actions", "exit_condition"])

    acceptance_rows = [
        {
            "gate": "blind_external_validation",
            "minimum_acceptance_test": "Prediction file exists before label unlock, labels are released once, and locked metrics are written.",
            "current_state": "open",
        },
        {
            "gate": "formal_figures",
            "minimum_acceptance_test": "Every retained figure panel has final export, source data and visual QA status.",
            "current_state": "open",
        },
        {
            "gate": "repository_rights_doi",
            "minimum_acceptance_test": "Release manifest, licence, rights checklist and DOI/accession or restriction statement exist.",
            "current_state": "open",
        },
        {
            "gate": "broad_interest_framing",
            "minimum_acceptance_test": "Title, abstract, introduction opening and schematic caption state cross-field relevance without overclaiming.",
            "current_state": "draft_only",
        },
        {
            "gate": "references",
            "minimum_acceptance_test": "No [P#] placeholders remain and each numbered citation supports its local claim.",
            "current_state": "open",
        },
    ]
    write_csv(OUT_DIR / "evidence_closure_acceptance_tests.csv", acceptance_rows, ["gate", "minimum_acceptance_test", "current_state"])

    escalation_rows = [
        {
            "trigger": "No real blind asset by Day 7",
            "decision_needed": "Hold submission for external validation or downgrade to benchmark/resource framing.",
            "recommended_default": "Downgrade framing rather than imply external validation.",
        },
        {
            "trigger": "Figure backend still undecided after Day 1",
            "decision_needed": "Select Python or R.",
            "recommended_default": "Python because the current evidence pipeline is Python-based.",
        },
        {
            "trigger": "Repository rights remain unresolved by Day 10",
            "decision_needed": "Choose restricted-release language or delay repository DOI claims.",
            "recommended_default": "Use explicit restriction language until rights are cleared.",
        },
    ]
    write_csv(OUT_DIR / "decision_escalation_sheet.csv", escalation_rows, ["trigger", "decision_needed", "recommended_default"])

    instructions = """# Reviewer-risk revision instructions 2026-08-10

## One-sentence argument

In GPR recognition evaluation, the current evidence shows that environment and provenance structure can reshape apparent generalization, supported mainly by Res-SAM environment-transfer fragility across five model families, with Mojahid and 4TU retained as bounded secondary and stress-test evidence.

## Revision order

1. Close or explicitly downgrade blind external validation.
2. Render and QA the final figure set before locking results prose.
3. Resolve repository, licence and rights language before final Data and Code Availability.
4. Sharpen the broad-interest argument around environment shift and benchmark trust.
5. Replace candidate citation markers only after prose and figure calls are stable.

## Claim discipline

- Use "show" only for internally audited Res-SAM evidence.
- Use "suggest" or "indicate" for directional Mojahid support.
- Use "stress-test" or "failure-mode" language for 4TU.
- Do not describe TIGPR as a currently executable core validation asset.
- Do not describe protocol-only blind validation as completed validation.

## Stop rules

- No external-validation claim without a real held-label asset and locked evaluation.
- No figure-dependent claim without final rendered panels and source data.
- No public-deposition claim without real DOI/accession, licence and rights clearance.
- No final Reporting Summary claim while hard gates remain open.
"""
    (OUT_DIR / "manuscript_revision_instructions.md").write_text(instructions, encoding="utf-8")

    summary = {
        "run_id": "20260810_reviewer_risk_revision_action_packet",
        "risk_actions": len(action_rows),
        "sprint_rows": len(sprint_rows),
        "acceptance_tests": len(acceptance_rows),
        "escalation_rows": len(escalation_rows),
        "open_gap_rows": len(gap_rows),
        "submission_ready": False,
        "status": "reviewer_risk_revision_action_packet_ready_submission_not_ready",
        "boundary": "This packet converts reviewer risks into actions and acceptance tests; it does not close external validation, figures, DOI, rights, Reporting Summary or references.",
    }
    (OUT_DIR / "reviewer_risk_revision_action_packet_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report = [
        "# Reviewer-risk revision action packet report 2026-08-10",
        "",
        f"- Risk actions: {summary['risk_actions']}",
        f"- Next-14-day sprint rows: {summary['sprint_rows']}",
        f"- Evidence acceptance tests: {summary['acceptance_tests']}",
        f"- Decision escalation rows: {summary['escalation_rows']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: reviewer risks have been converted into executable revision actions, but submission hard gates remain open.",
        "",
    ]
    (OUT_DIR / "reviewer_risk_revision_action_packet_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
