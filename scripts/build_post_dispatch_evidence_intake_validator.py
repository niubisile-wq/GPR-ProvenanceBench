#!/usr/bin/env python3
"""Validate whether post-dispatch evidence exists for remaining manual actions."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "post_dispatch_evidence_intake_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

DISPATCH_QUEUE = REPORTS / "manual_dispatch_master_packet_20260810" / "manual_dispatch_master_queue.csv"
SEND_LOG = REPORTS / "natcomms_author_response_tracker_20260810" / "author_response_send_log_template.csv"
RETURN_LOG = REPORTS / "natcomms_author_response_tracker_20260810" / "author_response_return_tracker.csv"
BACKEND_TICKET = REPORTS / "natcomms_author_finalization_reply_packet_20260810" / "figure_backend_decision_ticket.csv"
REPORTING_REPLY = REPORTS / "natcomms_author_finalization_reply_packet_20260810" / "reporting_summary_author_reply_sheet.csv"
RIGHTS_MATRIX = REPORTS / "rights_licence_completion_handoff_20260810" / "rights_licence_decision_matrix.csv"
REFERENCE_REPLACEMENT = REPORTS / "reference_completion_handoff_20260810" / "citation_marker_final_replacement_queue.csv"
EXTERNAL_WORKSPACE = BENCH_ROOT / "external_blind"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.81 Post-dispatch evidence intake validator update"
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


def payload_file_count() -> int:
    if not EXTERNAL_WORKSPACE.exists():
        return 0
    return sum(1 for path in EXTERNAL_WORKSPACE.rglob("*") if path.is_file() and path.name != "README_20260810.md")


def nonblank(value: str | None) -> bool:
    return bool((value or "").strip())


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    dispatch_rows = read_csv(DISPATCH_QUEUE)
    send_rows = read_csv(SEND_LOG)
    return_rows = read_csv(RETURN_LOG)
    backend_rows = read_csv(BACKEND_TICKET)
    reporting_rows = read_csv(REPORTING_REPLY)
    rights_rows = read_csv(RIGHTS_MATRIX)
    reference_rows = read_csv(REFERENCE_REPLACEMENT)

    sent_rows = [
        row for row in send_rows
        if row.get("send_status") == "sent" and nonblank(row.get("sent_datetime_local")) and nonblank(row.get("sender"))
    ]
    returned_rows = [
        row for row in return_rows
        if row.get("return_status") == "returned" and nonblank(row.get("returned_file_path")) and nonblank(row.get("returned_datetime_local"))
    ]
    backend_choices = {row["ticket_id"]: row.get("current_choice", "") for row in backend_rows}
    backend_valid = backend_choices.get("FIG-BACKEND-001") in {"Python", "R"}
    scope_valid = backend_choices.get("FIG-BACKEND-002") in {"Figure 1-Figure 6", "reduced display set with SI relocation"}
    reporting_replies = [row for row in reporting_rows if nonblank(row.get("author_reply"))]
    external_payload_files = payload_file_count()
    rights_closed = all(
        row["current_decision"] not in {"open", ""}
        for row in rights_rows
        if row["component"] != "Third-party raw GPR data"
    )
    reference_replacements_allowed = [
        row for row in reference_rows
        if row.get("replacement_allowed_now", "").lower() == "true"
    ]

    evidence_rows = [
        {
            "dispatch_id": "MD-001",
            "evidence_type": "real_author_sendout",
            "expected_evidence": "all send rows marked sent with timestamp and sender",
            "observed_evidence": f"sent_rows={len(sent_rows)}; total_send_rows={len(send_rows)}",
            "intake_status": "pass" if len(sent_rows) == len(send_rows) and len(send_rows) > 0 else "missing",
            "gate_effect": "author_reply_lifecycle_can_start" if len(sent_rows) == len(send_rows) and len(send_rows) > 0 else "no_gate_closure",
        },
        {
            "dispatch_id": "MD-001",
            "evidence_type": "returned_author_reply_files",
            "expected_evidence": "all required return rows marked returned with returned file path and timestamp",
            "observed_evidence": f"returned_rows={len(returned_rows)}; total_return_rows={len(return_rows)}",
            "intake_status": "pass" if len(returned_rows) == len(return_rows) and len(return_rows) > 0 else "missing",
            "gate_effect": "reply_ingestion_can_start" if len(returned_rows) == len(return_rows) and len(return_rows) > 0 else "no_gate_closure",
        },
        {
            "dispatch_id": "MD-002",
            "evidence_type": "backend_and_scope_choice",
            "expected_evidence": "backend current_choice is Python/R and scope current_choice is one allowed scope",
            "observed_evidence": f"backend_valid={backend_valid}; scope_valid={scope_valid}",
            "intake_status": "pass" if backend_valid and scope_valid else "missing",
            "gate_effect": "figure_rendering_can_start" if backend_valid and scope_valid else "no_gate_closure",
        },
        {
            "dispatch_id": "MD-003",
            "evidence_type": "external_blind_asset_payload",
            "expected_evidence": "external_blind contains real payload files beyond README plus strict-SHA manifest later",
            "observed_evidence": f"external_payload_files={external_payload_files}",
            "intake_status": "pass" if external_payload_files > 0 else "missing",
            "gate_effect": "external_intake_can_start" if external_payload_files > 0 else "no_gate_closure",
        },
        {
            "dispatch_id": "MD-004",
            "evidence_type": "rights_licence_decisions",
            "expected_evidence": "code, derived-data and figure-source rights decisions no longer open",
            "observed_evidence": f"rights_closed={rights_closed}",
            "intake_status": "pass" if rights_closed else "missing",
            "gate_effect": "repository_release_can_progress" if rights_closed else "no_gate_closure",
        },
        {
            "dispatch_id": "MD-005",
            "evidence_type": "reporting_summary_author_replies",
            "expected_evidence": "four Reporting Summary author_reply cells filled",
            "observed_evidence": f"reporting_replies={len(reporting_replies)}; total_reporting_rows={len(reporting_rows)}",
            "intake_status": "pass" if len(reporting_replies) == len(reporting_rows) and len(reporting_rows) > 0 else "missing",
            "gate_effect": "reporting_summary_finalization_can_progress" if len(reporting_replies) == len(reporting_rows) and len(reporting_rows) > 0 else "no_gate_closure",
        },
        {
            "dispatch_id": "MD-006",
            "evidence_type": "reference_replacement_authorized",
            "expected_evidence": "final prose stable and marker replacement rows allowed",
            "observed_evidence": f"replacement_allowed_rows={len(reference_replacements_allowed)}; total_replacement_rows={len(reference_rows)}",
            "intake_status": "pass" if len(reference_replacements_allowed) == len(reference_rows) and len(reference_rows) > 0 else "missing",
            "gate_effect": "final_reference_numbering_can_progress" if len(reference_replacements_allowed) == len(reference_rows) and len(reference_rows) > 0 else "no_gate_closure",
        },
    ]

    next_command_rows = [
        {
            "condition": "real_author_sendout pass",
            "next_command": "py scripts\\build_natcomms_author_response_log_validator.py",
            "blocked_now": "yes" if evidence_rows[0]["intake_status"] != "pass" else "no",
        },
        {
            "condition": "returned_author_reply_files pass",
            "next_command": "py scripts\\build_natcomms_author_reply_ingestion_validator.py",
            "blocked_now": "yes" if evidence_rows[1]["intake_status"] != "pass" else "no",
        },
        {
            "condition": "backend_and_scope_choice pass",
            "next_command": "py scripts\\build_figure_backend_decision_validator.py",
            "blocked_now": "yes" if evidence_rows[2]["intake_status"] != "pass" else "no",
        },
        {
            "condition": "external_blind_asset_payload pass",
            "next_command": "py scripts\\validate_external_blind_intake.py --strict-sha",
            "blocked_now": "yes" if evidence_rows[3]["intake_status"] != "pass" else "no",
        },
        {
            "condition": "rights_licence_decisions pass",
            "next_command": "py scripts\\build_rights_licence_completion_handoff.py",
            "blocked_now": "yes" if evidence_rows[4]["intake_status"] != "pass" else "no",
        },
        {
            "condition": "reporting_summary_author_replies pass",
            "next_command": "py scripts\\build_reporting_summary_completion_handoff.py",
            "blocked_now": "yes" if evidence_rows[5]["intake_status"] != "pass" else "no",
        },
        {
            "condition": "reference_replacement_authorized pass",
            "next_command": "py scripts\\build_reference_completion_handoff.py",
            "blocked_now": "yes" if evidence_rows[6]["intake_status"] != "pass" else "no",
        },
    ]

    qa_rows = [
        {
            "check": "dispatch_queue_imported",
            "result": "PASS" if len(dispatch_rows) == 6 else "FAIL",
            "detail": f"dispatch_rows={len(dispatch_rows)}",
        },
        {
            "check": "all_current_evidence_missing_or_open",
            "result": "PASS" if all(row["intake_status"] == "missing" for row in evidence_rows) else "FAIL",
            "detail": "Current state should not show completed manual evidence unless user filled it.",
        },
        {
            "check": "no_gate_effect_allowed",
            "result": "PASS" if all(row["gate_effect"] == "no_gate_closure" for row in evidence_rows) else "FAIL",
            "detail": "No downstream gate should open from empty evidence.",
        },
        {
            "check": "next_commands_all_blocked",
            "result": "PASS" if all(row["blocked_now"] == "yes" for row in next_command_rows) else "FAIL",
            "detail": f"blocked_commands={sum(1 for row in next_command_rows if row['blocked_now'] == 'yes')}",
        },
        {
            "check": "submission_not_claimed_ready",
            "result": "PASS",
            "detail": "Evidence intake validator only; it does not close gates or submit.",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "post_dispatch_evidence_intake_matrix.csv",
        evidence_rows,
        ["dispatch_id", "evidence_type", "expected_evidence", "observed_evidence", "intake_status", "gate_effect"],
    )
    write_csv(OUT_DIR / "post_dispatch_next_validation_commands.csv", next_command_rows, ["condition", "next_command", "blocked_now"])
    write_csv(OUT_DIR / "post_dispatch_evidence_intake_validator_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = """# Post-dispatch Evidence Intake Validator 2026-08-10

This package checks whether real manual-dispatch evidence has appeared after the master dispatch packet.

Boundary: it does not create evidence, send emails, fill replies, choose backend/scope, acquire external assets, clear rights, replace references or close gates.
"""
    write_text(OUT_DIR / "POST_DISPATCH_EVIDENCE_INTAKE_VALIDATOR_README.md", readme)

    report = [
        "# Post-dispatch evidence intake validator report 2026-08-10",
        "",
        "Status: `post_dispatch_evidence_intake_ready_waiting_manual_evidence`",
        "",
        f"- Evidence rows: {len(evidence_rows)}",
        f"- Missing evidence rows: {sum(1 for row in evidence_rows if row['intake_status'] == 'missing')}",
        f"- Next validation commands: {len(next_command_rows)}",
        f"- QA pass: {qa_pass}",
        "",
        "Conclusion: no real post-dispatch evidence is present yet. All downstream validations remain blocked.",
        "",
    ]
    write_text(OUT_DIR / "post_dispatch_evidence_intake_validator_report.md", "\n".join(report))

    summary = {
        "package": "post_dispatch_evidence_intake_validator_20260810",
        "evidence_rows": len(evidence_rows),
        "evidence_rows_passed": sum(1 for row in evidence_rows if row["intake_status"] == "pass"),
        "evidence_rows_missing": sum(1 for row in evidence_rows if row["intake_status"] == "missing"),
        "next_validation_commands": len(next_command_rows),
        "next_validation_commands_blocked": sum(1 for row in next_command_rows if row["blocked_now"] == "yes"),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "email_sent": False,
        "author_replies_collected": False,
        "backend_selected": False,
        "external_asset_acquired": False,
        "third_party_rights_cleared": False,
        "final_reporting_summary_ready": False,
        "final_references_ready": False,
        "submission_ready": False,
        "status": "post_dispatch_evidence_intake_ready_waiting_manual_evidence",
    }

    section = f"""### 18.81 Post-dispatch evidence intake validator update

Added a post-dispatch evidence intake validator. This checks whether any real manual-dispatch evidence has appeared after the master dispatch packet.

New directory: `{OUT_DIR}`

New files:
1. `post_dispatch_evidence_intake_matrix.csv`
2. `post_dispatch_next_validation_commands.csv`
3. `post_dispatch_evidence_intake_validator_qa.csv`
4. `POST_DISPATCH_EVIDENCE_INTAKE_VALIDATOR_README.md`
5. `post_dispatch_evidence_intake_validator_report.md`
6. `post_dispatch_evidence_intake_validator_summary.json`

Current result:
1. evidence_rows = {summary['evidence_rows']}
2. evidence_rows_passed = {summary['evidence_rows_passed']}
3. evidence_rows_missing = {summary['evidence_rows_missing']}
4. next_validation_commands = {summary['next_validation_commands']}
5. next_validation_commands_blocked = {summary['next_validation_commands_blocked']}
6. qa_pass = {str(qa_pass).lower()}
7. email_sent = false
8. author_replies_collected = false
9. backend_selected = false
10. external_asset_acquired = false
11. third_party_rights_cleared = false
12. final_reporting_summary_ready = false
13. final_references_ready = false
14. submission_ready = false
15. status = `post_dispatch_evidence_intake_ready_waiting_manual_evidence`

Boundary:
1. This step does not create evidence or send email.
2. This step does not choose backend/scope.
3. This step does not acquire external assets or clear rights.
4. This step does not finalize Reporting Summary, references or submission."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "post_dispatch_evidence_intake_validator_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Post-dispatch evidence intake validator QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
