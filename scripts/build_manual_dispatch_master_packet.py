#!/usr/bin/env python3
"""Build a desktop manual-dispatch master packet for remaining human actions."""

from __future__ import annotations

import csv
import json
import shutil
import zipfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "manual_dispatch_master_packet_20260810"
ATTACH_DIR = OUT_DIR / "attachments"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"
DESKTOP_ZIP = Path.home() / "Desktop" / "NatComms_manual_dispatch_master_packet_20260810.zip"

SOURCE_FILES = [
    ("author_sendout", REPORTS / "natcomms_author_sendout_bundle_v2_20260810" / "NatComms_author_sendout_bundle_v2_20260810.zip"),
    ("author_sendout", REPORTS / "natcomms_author_sendout_bundle_v2_20260810" / "author_sendout_email_ready_draft_cn.md"),
    ("author_sendout", REPORTS / "natcomms_manual_sendout_execution_guard_20260810" / "manual_sendout_execution_checklist.csv"),
    ("backend_scope", REPORTS / "figure_backend_scope_decision_handoff_20260810" / "FIGURE_BACKEND_SCOPE_DECISION_HANDOFF.md"),
    ("backend_scope", REPORTS / "figure_backend_scope_decision_handoff_20260810" / "backend_option_recommendation_matrix.csv"),
    ("backend_scope", REPORTS / "natcomms_author_finalization_reply_packet_20260810" / "figure_backend_decision_ticket.csv"),
    ("external_asset", REPORTS / "external_asset_triage_register_20260810" / "external_asset_contact_packet_queue.csv"),
    ("external_asset", REPORTS / "blind_external_acquisition_package_20260810" / "external_blind_asset_request_letter.md"),
    ("external_asset", REPORTS / "blind_external_acquisition_package_20260810" / "external_asset_rights_checklist.csv"),
    ("rights_licence", REPORTS / "rights_licence_completion_handoff_20260810" / "rights_licence_decision_matrix.csv"),
    ("rights_licence", REPORTS / "rights_licence_completion_handoff_20260810" / "rights_completion_command_queue.csv"),
    ("reporting_summary", REPORTS / "reporting_summary_completion_handoff_20260810" / "reporting_summary_author_handoff_queue.csv"),
    ("reporting_summary", REPORTS / "reporting_summary_completion_handoff_20260810" / "reporting_summary_item_completion_matrix.csv"),
    ("references", REPORTS / "reference_completion_handoff_20260810" / "reference_manual_verification_queue.csv"),
    ("references", REPORTS / "reference_completion_handoff_20260810" / "citation_marker_final_replacement_queue.csv"),
]

SUMMARY_FILES = {
    "author_sendout": REPORTS / "natcomms_author_sendout_bundle_v2_20260810" / "author_sendout_bundle_v2_summary.json",
    "manual_sendout": REPORTS / "natcomms_manual_sendout_execution_guard_20260810" / "manual_sendout_execution_guard_summary.json",
    "next_execution": REPORTS / "natcomms_next_execution_packet_20260810" / "next_execution_packet_summary.json",
    "backend_scope": REPORTS / "figure_backend_scope_decision_handoff_20260810" / "figure_backend_scope_decision_handoff_summary.json",
    "external_asset": REPORTS / "external_asset_triage_register_20260810" / "external_asset_triage_register_summary.json",
    "rights_licence": REPORTS / "rights_licence_completion_handoff_20260810" / "rights_licence_completion_handoff_summary.json",
    "reporting_summary": REPORTS / "reporting_summary_completion_handoff_20260810" / "reporting_summary_completion_handoff_summary.json",
    "references": REPORTS / "reference_completion_handoff_20260810" / "reference_completion_handoff_summary.json",
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


def copy_attachment(category: str, source: Path) -> dict[str, object]:
    target_dir = ATTACH_DIR / category
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    shutil.copy2(source, target)
    return {
        "category": category,
        "source_path": str(source.relative_to(BENCH_ROOT)),
        "packet_path": str(target.relative_to(OUT_DIR)),
        "exists": target.exists(),
        "size_bytes": target.stat().st_size if target.exists() else 0,
    }


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.79 Manual dispatch master packet update"
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


def write_zip() -> int:
    if DESKTOP_ZIP.exists():
        DESKTOP_ZIP.unlink()
    with zipfile.ZipFile(DESKTOP_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in OUT_DIR.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(OUT_DIR).as_posix())
    with zipfile.ZipFile(DESKTOP_ZIP, "r") as archive:
        return len(archive.namelist())


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ATTACH_DIR.mkdir(parents=True, exist_ok=True)

    summaries = {name: read_json(path) for name, path in SUMMARY_FILES.items()}
    inventory_rows = [copy_attachment(category, path) for category, path in SOURCE_FILES]

    dispatch_rows = [
        {
            "dispatch_id": "MD-001",
            "priority": 1,
            "recipient_or_owner": "corresponding author / coauthors",
            "action": "Send NatComms author sendout bundle v2 and record real send evidence.",
            "packet_material": "attachments/author_sendout",
            "acceptance_evidence": "send log completed with timestamp, sender and recipient route; returned forms tracked later.",
            "current_status": "ready_not_sent",
        },
        {
            "dispatch_id": "MD-002",
            "priority": 2,
            "recipient_or_owner": "corresponding author / analysis lead",
            "action": "Choose exactly one figure backend and one figure scope in figure_backend_decision_ticket.csv.",
            "packet_material": "attachments/backend_scope",
            "acceptance_evidence": "backend validator reports backend_selected=true, scope_confirmed=true and rendering_allowed=true.",
            "current_status": "ready_waiting_choice",
        },
        {
            "dispatch_id": "MD-003",
            "priority": 3,
            "recipient_or_owner": "advisor / collaborator / third-party data holder",
            "action": "Send Track B external blind asset request and rights checklist.",
            "packet_material": "attachments/external_asset",
            "acceptance_evidence": "real unlabeled asset, strict-SHA manifest, sealed labels and rights statement are returned.",
            "current_status": "ready_not_sent",
        },
        {
            "dispatch_id": "MD-004",
            "priority": 4,
            "recipient_or_owner": "repository/rights lead",
            "action": "Resolve software licence, derived-data licence and raw third-party exclusion/permission decisions.",
            "packet_material": "attachments/rights_licence",
            "acceptance_evidence": "licence_selected=true, third_party_rights_cleared=true or raw-data exclusion finalized.",
            "current_status": "ready_waiting_rights_review",
        },
        {
            "dispatch_id": "MD-005",
            "priority": 5,
            "recipient_or_owner": "corresponding author / statistics reviewer / rights lead",
            "action": "Answer Reporting Summary author confirmations.",
            "packet_material": "attachments/reporting_summary",
            "acceptance_evidence": "four author confirmation rows completed and Reporting Summary completion handoff rerun.",
            "current_status": "ready_waiting_author_confirmations",
        },
        {
            "dispatch_id": "MD-006",
            "priority": 6,
            "recipient_or_owner": "writing lead",
            "action": "Defer final reference replacement until final prose and figure/table calls are stable.",
            "packet_material": "attachments/references",
            "acceptance_evidence": "manual verification complete, final marker replacement allowed, final RIS/ENW regenerated.",
            "current_status": "blocked_until_final_prose",
        },
    ]

    stop_rows = [
        {"stop_id": "STOP-001", "rule": "Do not mark author email_sent=true until a real manual send record exists."},
        {"stop_id": "STOP-002", "rule": "Do not choose backend/scope on behalf of authors; recommendations are not selected values."},
        {"stop_id": "STOP-003", "rule": "Do not treat external-blind templates or dry runs as real external validation."},
        {"stop_id": "STOP-004", "rule": "Do not select licences, create DOI records or clear rights without author/rights evidence."},
        {"stop_id": "STOP-005", "rule": "Do not finalize Reporting Summary while author confirmations and upstream gates are open."},
        {"stop_id": "STOP-006", "rule": "Do not replace [P#] markers before final prose, figure/table calls and reference order are stable."},
    ]

    qa_rows = [
        {
            "check": "all_expected_attachments_copied",
            "result": "PASS" if all(row["exists"] for row in inventory_rows) and len(inventory_rows) == len(SOURCE_FILES) else "FAIL",
            "detail": f"copied={sum(1 for row in inventory_rows if row['exists'])}; expected={len(SOURCE_FILES)}",
        },
        {
            "check": "manual_actions_not_claimed_done",
            "result": "PASS" if summaries["author_sendout"].get("email_sent") is False and summaries["backend_scope"].get("backend_selected") is False else "FAIL",
            "detail": "author email and backend choice remain open.",
        },
        {
            "check": "external_and_rights_gates_remain_open",
            "result": "PASS" if summaries["external_asset"].get("blind_external_gate_closed") is False and summaries["rights_licence"].get("third_party_rights_cleared") is False else "FAIL",
            "detail": "external validation and rights are not closed.",
        },
        {
            "check": "reporting_and_reference_gates_remain_open",
            "result": "PASS" if summaries["reporting_summary"].get("final_reporting_summary_ready") is False and summaries["references"].get("final_references_ready") is False else "FAIL",
            "detail": "Reporting Summary and final references remain not final.",
        },
        {
            "check": "desktop_zip_created",
            "result": "PENDING",
            "detail": "Filled after zip creation.",
        },
    ]

    write_csv(
        OUT_DIR / "manual_dispatch_master_queue.csv",
        dispatch_rows,
        ["dispatch_id", "priority", "recipient_or_owner", "action", "packet_material", "acceptance_evidence", "current_status"],
    )
    write_csv(OUT_DIR / "manual_dispatch_packet_inventory.csv", inventory_rows, ["category", "source_path", "packet_path", "exists", "size_bytes"])
    write_csv(OUT_DIR / "manual_dispatch_stop_rules.csv", stop_rows, ["stop_id", "rule"])

    readme = """# Manual Dispatch Master Packet 2026-08-10

This packet consolidates the remaining manual dispatch actions into one desktop-ready package.

Use it to send the author bundle, request backend/scope decisions, contact the external data holder, route rights/licence decisions, collect Reporting Summary confirmations and defer final reference replacement until final prose is stable.

Boundary: this packet does not send emails, choose backend/scope, collect author replies, acquire external data, clear rights, finalize Reporting Summary, replace references or submit the manuscript.
"""
    write_text(OUT_DIR / "MANUAL_DISPATCH_MASTER_PACKET_README.md", readme)

    report = [
        "# Manual dispatch master packet report 2026-08-10",
        "",
        "Status: `manual_dispatch_master_packet_ready_not_sent`",
        "",
        f"- Dispatch actions: {len(dispatch_rows)}",
        f"- Attachment files copied: {len(inventory_rows)}",
        f"- Stop rules: {len(stop_rows)}",
        "",
        "Conclusion: manual dispatch materials are consolidated into one packet, but no manual action is recorded as completed.",
        "",
    ]
    write_text(OUT_DIR / "manual_dispatch_master_packet_report.md", "\n".join(report))

    zip_members = write_zip()
    qa_rows[-1] = {
        "check": "desktop_zip_created",
        "result": "PASS" if DESKTOP_ZIP.exists() and zip_members >= len(inventory_rows) else "FAIL",
        "detail": f"desktop_zip={DESKTOP_ZIP}; zip_members={zip_members}",
    }
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)
    write_csv(OUT_DIR / "manual_dispatch_master_packet_qa.csv", qa_rows, ["check", "result", "detail"])

    summary = {
        "package": "manual_dispatch_master_packet_20260810",
        "dispatch_actions": len(dispatch_rows),
        "attachment_files_copied": len(inventory_rows),
        "stop_rules": len(stop_rows),
        "desktop_zip": str(DESKTOP_ZIP),
        "desktop_zip_exists": DESKTOP_ZIP.exists(),
        "desktop_zip_members": zip_members,
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
        "status": "manual_dispatch_master_packet_ready_not_sent",
    }

    section = f"""### 18.79 Manual dispatch master packet update

Added a manual dispatch master packet. This consolidates the remaining human/external actions into one desktop-ready zip while preserving all gates as open.

New directory: `{OUT_DIR}`

Desktop zip: `{DESKTOP_ZIP}`

New files:
1. `manual_dispatch_master_queue.csv`
2. `manual_dispatch_packet_inventory.csv`
3. `manual_dispatch_stop_rules.csv`
4. `manual_dispatch_master_packet_qa.csv`
5. `MANUAL_DISPATCH_MASTER_PACKET_README.md`
6. `manual_dispatch_master_packet_report.md`
7. `manual_dispatch_master_packet_summary.json`
8. `attachments/`

Current result:
1. dispatch_actions = {summary['dispatch_actions']}
2. attachment_files_copied = {summary['attachment_files_copied']}
3. stop_rules = {summary['stop_rules']}
4. desktop_zip_exists = {str(summary['desktop_zip_exists']).lower()}
5. desktop_zip_members = {zip_members}
6. qa_pass = {str(qa_pass).lower()}
7. email_sent = false
8. author_replies_collected = false
9. backend_selected = false
10. external_asset_acquired = false
11. third_party_rights_cleared = false
12. final_reporting_summary_ready = false
13. final_references_ready = false
14. submission_ready = false
15. status = `manual_dispatch_master_packet_ready_not_sent`

Boundary:
1. This step does not send email.
2. This step does not choose backend/scope.
3. This step does not collect author replies.
4. This step does not acquire external data or clear rights.
5. This step does not finalize Reporting Summary, references or submission."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "manual_dispatch_master_packet_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Manual dispatch master packet QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
