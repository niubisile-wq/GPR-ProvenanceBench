#!/usr/bin/env python3
"""Build the final human-execution closeout board from current blocked gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_human_execution_closeout_board_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

SUMMARY_PATHS = {
    "master": BENCH_ROOT / "reports" / "natcomms_finalization_master_checklist_20260810" / "finalization_master_checklist_summary.json",
    "manual_intake": BENCH_ROOT / "reports" / "manual_evidence_final_intake_validator_20260810" / "manual_evidence_final_intake_validator_summary.json",
    "dispatch": BENCH_ROOT / "reports" / "natcomms_author_sendout_dispatch_preflight_20260810" / "author_sendout_dispatch_preflight_summary.json",
    "decisions": BENCH_ROOT / "reports" / "author_decision_closure_packet_v2_20260810" / "author_decision_closure_packet_v2_summary.json",
    "figure_review": BENCH_ROOT / "reports" / "python_figure_author_review_intake_validator_20260810" / "python_figure_author_review_intake_summary.json",
    "figure_candidate": BENCH_ROOT / "reports" / "python_figure_final_candidate_preflight_20260810" / "python_figure_final_candidate_preflight_summary.json",
    "figure_portal": BENCH_ROOT / "reports" / "python_figure_portal_upload_blocker_20260810" / "python_figure_portal_upload_blocker_summary.json",
    "availability": BENCH_ROOT / "reports" / "availability_repository_finalization_validator_20260810" / "availability_repository_finalization_validator_summary.json",
    "reporting": BENCH_ROOT / "reports" / "reporting_summary_final_lock_validator_20260810" / "reporting_summary_final_lock_validator_summary.json",
    "references": BENCH_ROOT / "reports" / "reference_final_lock_validator_20260810" / "reference_final_lock_validator_summary.json",
    "submission": BENCH_ROOT / "reports" / "natcomms_submission_final_lock_validator_20260810" / "natcomms_submission_final_lock_validator_summary.json",
}


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.13 Final human execution closeout board update"
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            updated = text[:start].rstrip() + "\n\n" + section.strip() + "\n"
        else:
            updated = text[:start].rstrip() + "\n\n" + section.strip() + "\n\n" + text[next_start:].lstrip("\n")
    else:
        updated = text.rstrip() + "\n\n" + section.strip() + "\n"
    DESKTOP_PLAN.write_text(updated, encoding="utf-8", newline="\n")
    return True


def yn(value: object) -> str:
    return "yes" if value is True else "no"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = {name: read_json(path) for name, path in SUMMARY_PATHS.items()}

    action_rows = [
        {
            "action_id": "HEC-001",
            "sequence": 1,
            "owner": "corresponding_author",
            "action": "Send the prepared author decision and reply packet, then capture send evidence.",
            "required_evidence": "email_sent=true plus immutable send log and bundle checksum evidence",
            "current_status": "blocked" if summaries["dispatch"].get("email_sent") is False else "closed",
            "unlocks": "author replies, backend/scope choice and downstream manual evidence intake",
        },
        {
            "action_id": "HEC-002",
            "sequence": 2,
            "owner": "corresponding_author_and_coauthors",
            "action": "Collect all author replies, backend/scope decisions and administrative confirmations.",
            "required_evidence": "twelve nonblank author reply fields and accepted decision values",
            "current_status": "blocked" if summaries["manual_intake"].get("blank_author_reply_fields", 0) else "closed",
            "unlocks": "manual evidence intake and gate closure evidence binder",
        },
        {
            "action_id": "HEC-003",
            "sequence": 3,
            "owner": "figure_owner",
            "action": "Collect figure preview approvals or revision decisions for Figure 1-Figure 6.",
            "required_evidence": "six nonblank review rows with approved/revise/reject decisions",
            "current_status": "blocked" if summaries["figure_review"].get("approved_rows") == 0 else "closed",
            "unlocks": "final candidate generation and final export QA",
        },
        {
            "action_id": "HEC-004",
            "sequence": 4,
            "owner": "data_repository_owner",
            "action": "Create repository records, select licences, clear third-party rights and record DOI identifiers.",
            "required_evidence": "repository DOI, code DOI, licence, rights-clearance proof and upload checksums",
            "current_status": "blocked" if summaries["availability"].get("final_availability_ready") is False else "closed",
            "unlocks": "Data Availability, Code Availability and portal upload files",
        },
        {
            "action_id": "HEC-005",
            "sequence": 5,
            "owner": "reporting_summary_owner",
            "action": "Complete final Reporting Summary answers after author, figure and repository gates close.",
            "required_evidence": "eight Reporting Summary items lockable with no unresolved/high-risk wording",
            "current_status": "blocked" if summaries["reporting"].get("final_reporting_summary_ready") is False else "closed",
            "unlocks": "final submission file lock",
        },
        {
            "action_id": "HEC-006",
            "sequence": 6,
            "owner": "reference_owner",
            "action": "Manually verify citations and export final numbered references.",
            "required_evidence": "manual verification closed and final reference export allowed",
            "current_status": "blocked" if summaries["references"].get("final_references_ready") is False else "closed",
            "unlocks": "manuscript reference finalization",
        },
        {
            "action_id": "HEC-007",
            "sequence": 7,
            "owner": "submission_owner",
            "action": "Only after all upstream gates close, assemble final files and perform portal upload.",
            "required_evidence": "open_master_gates=0, portal_upload_ready=true and submission_ready=true",
            "current_status": "blocked" if summaries["submission"].get("submission_ready") is False else "closed",
            "unlocks": "actual Nature Communications submission",
        },
    ]

    evidence_rows = [
        {
            "evidence_id": "EV-001",
            "gate": "author_sendout",
            "required_field_or_file": "email_sent and send evidence log",
            "current_value": yn(summaries["dispatch"].get("email_sent")),
            "acceptable_now": "no",
        },
        {
            "evidence_id": "EV-002",
            "gate": "author_replies",
            "required_field_or_file": "12 author reply fields",
            "current_value": f"blank={summaries['manual_intake'].get('blank_author_reply_fields')}",
            "acceptable_now": "no",
        },
        {
            "evidence_id": "EV-003",
            "gate": "figure_approvals",
            "required_field_or_file": "Figure 1-Figure 6 approval decisions",
            "current_value": f"approved={summaries['figure_review'].get('approved_rows')}; blank={summaries['figure_review'].get('blank_rows')}",
            "acceptable_now": "no",
        },
        {
            "evidence_id": "EV-004",
            "gate": "repository_rights_doi",
            "required_field_or_file": "DOI, licence and third-party rights proof",
            "current_value": f"doi={yn(summaries['availability'].get('repository_doi_created'))}; rights={yn(summaries['availability'].get('third_party_rights_cleared'))}",
            "acceptable_now": "no",
        },
        {
            "evidence_id": "EV-005",
            "gate": "reporting_summary",
            "required_field_or_file": "all Reporting Summary items lockable",
            "current_value": f"lockable={summaries['reporting'].get('lockable_reporting_items_now')}",
            "acceptable_now": "no",
        },
        {
            "evidence_id": "EV-006",
            "gate": "references",
            "required_field_or_file": "manual verification and final export",
            "current_value": f"verification_closed={summaries['references'].get('manual_verification_rows_closed')}; export_allowed={summaries['references'].get('final_export_allowed_rows')}",
            "acceptable_now": "no",
        },
        {
            "evidence_id": "EV-007",
            "gate": "portal_submission",
            "required_field_or_file": "all portal upload rows ready",
            "current_value": f"upload_ready={summaries['submission'].get('portal_upload_ready_rows')}; open_master_gates={summaries['submission'].get('open_master_gates')}",
            "acceptable_now": "no",
        },
    ]

    no_go_rows = [
        {
            "rule_id": "NG-001",
            "forbidden_action": "Do not mark submission_ready true.",
            "reason": "Eight master finalization gates remain open.",
            "enforced_by": "natcomms_submission_final_lock_validator",
        },
        {
            "rule_id": "NG-002",
            "forbidden_action": "Do not rerun branch/finalization commands after manual edits.",
            "reason": "safe_rerun_rows=0 and branch_commands_safe_to_run_now=0.",
            "enforced_by": "manual_evidence_final_intake_validator",
        },
        {
            "rule_id": "NG-003",
            "forbidden_action": "Do not generate final figures.",
            "reason": "approved_rows=0 and final_candidate_generation_allowed=false.",
            "enforced_by": "python_figure_author_review_intake_validator",
        },
        {
            "rule_id": "NG-004",
            "forbidden_action": "Do not finalize repository/data/code availability wording.",
            "reason": "repository DOI, code DOI, licence and rights gates remain false.",
            "enforced_by": "availability_repository_finalization_validator",
        },
        {
            "rule_id": "NG-005",
            "forbidden_action": "Do not replace citation markers or export final references.",
            "reason": "manual reference verification is not closed and final_export_allowed_rows=0.",
            "enforced_by": "reference_final_lock_validator",
        },
        {
            "rule_id": "NG-006",
            "forbidden_action": "Do not upload files to the Nature Communications portal.",
            "reason": "portal_upload_ready_rows=0 and portal_file_upload_allowed_rows=0.",
            "enforced_by": "natcomms_submission_final_lock_validator",
        },
    ]

    dependency_rows = [
        {
            "dependency_id": "DEP-001",
            "must_finish_before": "HEC-002",
            "dependency": "HEC-001",
            "status": "open",
            "reason": "Author replies cannot be collected until the sendout is actually sent.",
        },
        {
            "dependency_id": "DEP-002",
            "must_finish_before": "HEC-003",
            "dependency": "HEC-002",
            "status": "open",
            "reason": "Figure finalization requires author review decisions.",
        },
        {
            "dependency_id": "DEP-003",
            "must_finish_before": "HEC-005",
            "dependency": "HEC-002, HEC-003, HEC-004",
            "status": "open",
            "reason": "Reporting Summary depends on author confirmations, figure state and repository availability.",
        },
        {
            "dependency_id": "DEP-004",
            "must_finish_before": "HEC-007",
            "dependency": "HEC-002, HEC-003, HEC-004, HEC-005, HEC-006",
            "status": "open",
            "reason": "Portal upload and final submission require all upstream gates closed.",
        },
    ]

    blocked_actions = [row for row in action_rows if row["current_status"] != "closed"]
    closed_actions = [row for row in action_rows if row["current_status"] == "closed"]
    qa_rows = [
        {
            "check": "all_closeout_actions_still_blocked",
            "result": "PASS" if len(blocked_actions) == 7 and len(closed_actions) == 0 else "FAIL",
            "detail": f"blocked={len(blocked_actions)}; closed={len(closed_actions)}",
        },
        {
            "check": "manual_intake_still_blocked",
            "result": "PASS" if summaries["manual_intake"].get("manual_evidence_final_intake_allowed") is False else "FAIL",
            "detail": f"manual_evidence_final_intake_allowed={summaries['manual_intake'].get('manual_evidence_final_intake_allowed')}",
        },
        {
            "check": "figures_not_final",
            "result": "PASS" if summaries["figure_candidate"].get("rendered_figures_final") == 0 and summaries["figure_candidate"].get("final_figures_ready") is False else "FAIL",
            "detail": f"rendered_final={summaries['figure_candidate'].get('rendered_figures_final')}; final_figures_ready={summaries['figure_candidate'].get('final_figures_ready')}",
        },
        {
            "check": "availability_reporting_references_not_final",
            "result": "PASS"
            if summaries["availability"].get("final_availability_ready") is False
            and summaries["reporting"].get("final_reporting_summary_ready") is False
            and summaries["references"].get("final_references_ready") is False
            else "FAIL",
            "detail": f"availability={summaries['availability'].get('final_availability_ready')}; reporting={summaries['reporting'].get('final_reporting_summary_ready')}; references={summaries['references'].get('final_references_ready')}",
        },
        {
            "check": "submission_still_blocked",
            "result": "PASS" if summaries["submission"].get("submission_ready") is False and summaries["submission"].get("open_master_gates") == 8 else "FAIL",
            "detail": f"submission_ready={summaries['submission'].get('submission_ready')}; open_master_gates={summaries['submission'].get('open_master_gates')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "final_human_execution_action_queue.csv", action_rows, ["action_id", "sequence", "owner", "action", "required_evidence", "current_status", "unlocks"])
    write_csv(OUT_DIR / "final_human_execution_evidence_matrix.csv", evidence_rows, ["evidence_id", "gate", "required_field_or_file", "current_value", "acceptable_now"])
    write_csv(OUT_DIR / "final_human_execution_no_go_rules.csv", no_go_rows, ["rule_id", "forbidden_action", "reason", "enforced_by"])
    write_csv(OUT_DIR / "final_human_execution_dependency_order.csv", dependency_rows, ["dependency_id", "must_finish_before", "dependency", "status", "reason"])
    write_csv(OUT_DIR / "final_human_execution_closeout_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Final human execution closeout board 2026-08-10",
        "",
        "Status: `final_human_execution_closeout_board_ready_all_actions_blocked`",
        "",
        f"1. Closeout actions: {len(action_rows)}",
        f"2. Blocked closeout actions: {len(blocked_actions)}",
        f"3. Required evidence rows: {len(evidence_rows)}",
        f"4. No-go rules: {len(no_go_rows)}",
        f"5. Dependency rows: {len(dependency_rows)}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this board converts existing blockers into an execution queue only. It does not send emails, collect replies, approve figures, create DOI records, clear rights, finalize references, upload portal files or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "FINAL_HUMAN_EXECUTION_CLOSEOUT_BOARD_README.md", "\n".join(report))
    write_text(OUT_DIR / "final_human_execution_closeout_board_report.md", "\n".join(report))

    summary = {
        "package": "final_human_execution_closeout_board_20260810",
        "action_rows": len(action_rows),
        "blocked_action_rows": len(blocked_actions),
        "closed_action_rows": len(closed_actions),
        "evidence_rows": len(evidence_rows),
        "no_go_rules": len(no_go_rows),
        "dependency_rows": len(dependency_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "email_sent": summaries["dispatch"].get("email_sent"),
        "blank_author_reply_fields": summaries["manual_intake"].get("blank_author_reply_fields"),
        "approved_figure_rows": summaries["figure_review"].get("approved_rows"),
        "final_figures_ready": summaries["figure_candidate"].get("final_figures_ready"),
        "final_availability_ready": summaries["availability"].get("final_availability_ready"),
        "final_reporting_summary_ready": summaries["reporting"].get("final_reporting_summary_ready"),
        "final_references_ready": summaries["references"].get("final_references_ready"),
        "open_master_gates": summaries["submission"].get("open_master_gates"),
        "portal_upload_ready_rows": summaries["submission"].get("portal_upload_ready_rows"),
        "submission_ready": False,
        "status": "final_human_execution_closeout_board_ready_all_actions_blocked",
    }

    section = f"""### 19.13 Final human execution closeout board update

Added a final human-execution closeout board that converts all remaining finalization blockers into an ordered manual action queue.

New directory: `{OUT_DIR}`

New files:
1. `final_human_execution_action_queue.csv`
2. `final_human_execution_evidence_matrix.csv`
3. `final_human_execution_no_go_rules.csv`
4. `final_human_execution_dependency_order.csv`
5. `final_human_execution_closeout_qa.csv`
6. `FINAL_HUMAN_EXECUTION_CLOSEOUT_BOARD_README.md`
7. `final_human_execution_closeout_board_report.md`
8. `final_human_execution_closeout_board_summary.json`

Current result:
1. action_rows = {summary['action_rows']}
2. blocked_action_rows = {summary['blocked_action_rows']}
3. closed_action_rows = {summary['closed_action_rows']}
4. evidence_rows = {summary['evidence_rows']}
5. no_go_rules = {summary['no_go_rules']}
6. dependency_rows = {summary['dependency_rows']}
7. email_sent = false
8. approved_figure_rows = {summary['approved_figure_rows']}
9. final_availability_ready = false
10. final_reporting_summary_ready = false
11. final_references_ready = false
12. submission_ready = false

Boundary:
1. This board is an execution-control artifact only.
2. It does not send emails, collect replies, approve figures, create DOI records, clear rights, finalize references or upload portal files.
3. It preserves the current Track B/no-submission boundary until real human evidence is present."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "final_human_execution_closeout_board_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Final human execution closeout board QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
