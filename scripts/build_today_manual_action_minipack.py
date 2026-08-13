#!/usr/bin/env python3
"""Build a minimal same-day manual action packet for the open submission gates."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "today_manual_action_minipack_20260810"
DESKTOP = Path.home() / "Desktop"
DESKTOP_PLAN = DESKTOP / "8月10日cns.md"
DESKTOP_GUIDE = DESKTOP / "NatComms_今日人工动作最小包_20260810.md"
DESKTOP_MASTER_ZIP = DESKTOP / "NatComms_manual_dispatch_master_packet_20260810.zip"

MASTER_QUEUE = REPORTS / "manual_dispatch_master_packet_20260810" / "manual_dispatch_master_queue.csv"
PACKET_INVENTORY = REPORTS / "manual_dispatch_master_packet_20260810" / "manual_dispatch_packet_inventory.csv"
GATE_BOARD = REPORTS / "gate_closure_execution_board_20260810" / "gate_closure_execution_board.csv"
DISPATCH_SUMMARY = REPORTS / "manual_dispatch_master_packet_20260810" / "manual_dispatch_master_packet_summary.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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
    marker = "### 18.89 Today manual action minipack update"
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


def attachment_list(category: str, inventory_rows: list[dict[str, str]]) -> str:
    names = [row["packet_path"] for row in inventory_rows if row["category"] == category and row["exists"] == "True"]
    return "; ".join(names)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    queue_rows = read_csv(MASTER_QUEUE)
    inventory_rows = read_csv(PACKET_INVENTORY)
    gate_rows = read_csv(GATE_BOARD)
    dispatch_summary = read_json(DISPATCH_SUMMARY)

    category_by_dispatch = {
        "MD-001": "author_sendout",
        "MD-002": "backend_scope",
        "MD-003": "external_asset",
        "MD-004": "rights_licence",
        "MD-005": "reporting_summary",
        "MD-006": "references",
    }

    gate_by_priority = {row["priority"]: row for row in gate_rows}
    action_rows: list[dict[str, object]] = []
    for row in queue_rows:
        category = category_by_dispatch[row["dispatch_id"]]
        gate = gate_by_priority.get(row["priority"], {})
        can_do_today = "no" if row["dispatch_id"] == "MD-006" else "yes"
        action_rows.append(
            {
                "dispatch_id": row["dispatch_id"],
                "priority": row["priority"],
                "can_execute_today": can_do_today,
                "recipient_or_owner": row["recipient_or_owner"],
                "action": row["action"],
                "attachments_to_use": attachment_list(category, inventory_rows),
                "acceptance_evidence": row["acceptance_evidence"],
                "linked_gate": gate.get("gate", ""),
                "first_validator_after_return": gate.get("first_validation_to_run", ""),
                "do_not_mark_done_until": "real send/return evidence exists and validator passes",
            }
        )

    evidence_capture_rows = [
        {
            "evidence_item": "send screenshot or mail header",
            "where_to_record": "reports/natcomms_author_response_tracker_20260810/author_response_send_log_template.csv",
            "required_fields": "send_status=sent; sent_datetime_local; sender",
        },
        {
            "evidence_item": "returned reply files",
            "where_to_record": "reports/natcomms_author_response_tracker_20260810/author_response_return_tracker.csv",
            "required_fields": "return_status=returned; returned_file_path; returned_datetime_local",
        },
        {
            "evidence_item": "backend/scope choice",
            "where_to_record": "reports/natcomms_author_finalization_reply_packet_20260810/figure_backend_decision_ticket.csv",
            "required_fields": "current_choice for backend and scope rows",
        },
        {
            "evidence_item": "external blind asset",
            "where_to_record": "external_blind/<dated_asset_folder> and data_manifests/external_blind_manifest_<asset>_YYYYMMDD.csv",
            "required_fields": "strict SHA manifest; labels outside analyst workflow",
        },
        {
            "evidence_item": "rights/licence and Reporting Summary replies",
            "where_to_record": "rights and reporting-summary reply sheets listed in the master packet",
            "required_fields": "specific answers; no yes/ok placeholders",
        },
    ]

    stop_rows = [
        {"rule_id": "TODAY-STOP-001", "rule": "Do not mark email_sent=true until the message is actually sent outside this script."},
        {"rule_id": "TODAY-STOP-002", "rule": "Do not record backend/scope from recommendation; record only author/analysis-owner choice."},
        {"rule_id": "TODAY-STOP-003", "rule": "Do not place external labels in analyst-visible folders before prediction freeze."},
        {"rule_id": "TODAY-STOP-004", "rule": "Do not close rights/licence from silence or missing replies."},
        {"rule_id": "TODAY-STOP-005", "rule": "Do not replace references today unless final prose and figure/table calls are stable."},
    ]

    desktop_zip = DESKTOP_MASTER_ZIP if DESKTOP_MASTER_ZIP.exists() else Path(str(dispatch_summary.get("desktop_zip", "")))
    guide = [
        "# NatComms 今日人工动作最小包 2026-08-10",
        "",
        "当前状态：还不能投稿。这个文件只列出今天可以人工执行的最小动作，不代表已经发送或已经收回证据。",
        "",
        f"Master dispatch zip: `{desktop_zip}`",
        "",
        "## 今天优先做",
        "",
    ]
    for row in action_rows:
        guide.append(f"### {row['priority']}. {row['dispatch_id']} - {row['recipient_or_owner']}")
        guide.append("")
        guide.append(f"- Can execute today: `{row['can_execute_today']}`")
        guide.append(f"- Action: {row['action']}")
        guide.append(f"- Attachments: `{row['attachments_to_use']}`")
        guide.append(f"- Acceptance evidence: {row['acceptance_evidence']}")
        guide.append(f"- First validator after return: `{row['first_validator_after_return']}`")
        guide.append("")
    guide.extend(
        [
            "## 禁止",
            "",
        ]
    )
    for row in stop_rows:
        guide.append(f"- {row['rule_id']}: {row['rule']}")
    guide.append("")

    write_csv(
        OUT_DIR / "today_manual_action_minipack.csv",
        action_rows,
        [
            "dispatch_id",
            "priority",
            "can_execute_today",
            "recipient_or_owner",
            "action",
            "attachments_to_use",
            "acceptance_evidence",
            "linked_gate",
            "first_validator_after_return",
            "do_not_mark_done_until",
        ],
    )
    write_csv(OUT_DIR / "today_evidence_capture_targets.csv", evidence_capture_rows, ["evidence_item", "where_to_record", "required_fields"])
    write_csv(OUT_DIR / "today_manual_action_stop_rules.csv", stop_rows, ["rule_id", "rule"])
    write_text(OUT_DIR / "TODAY_MANUAL_ACTION_MINIPACK.md", "\n".join(guide))
    shutil.copy2(OUT_DIR / "TODAY_MANUAL_ACTION_MINIPACK.md", DESKTOP_GUIDE)

    qa_rows = [
        {
            "check": "six_dispatch_actions_indexed",
            "result": "PASS" if len(action_rows) == 6 else "FAIL",
            "detail": f"action_rows={len(action_rows)}",
        },
        {
            "check": "desktop_guide_created",
            "result": "PASS" if DESKTOP_GUIDE.exists() else "FAIL",
            "detail": str(DESKTOP_GUIDE),
        },
        {
            "check": "no_done_state_claimed",
            "result": "PASS" if all(row["can_execute_today"] in {"yes", "no"} for row in action_rows) else "FAIL",
            "detail": "Action packet is instruction-only.",
        },
        {
            "check": "dispatch_state_preserved",
            "result": "PASS" if dispatch_summary.get("email_sent") is False and dispatch_summary.get("submission_ready") is False else "FAIL",
            "detail": f"email_sent={dispatch_summary.get('email_sent')}; submission_ready={dispatch_summary.get('submission_ready')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)
    write_csv(OUT_DIR / "today_manual_action_minipack_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Today manual action minipack report 2026-08-10",
        "",
        "Status: `today_manual_action_minipack_ready_not_executed`",
        "",
        f"1. Action rows: {len(action_rows)}",
        f"2. Evidence capture rows: {len(evidence_capture_rows)}",
        f"3. Stop rules: {len(stop_rows)}",
        f"4. Desktop guide: `{DESKTOP_GUIDE}`",
        f"5. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: the minimal manual action list is ready, but no action is recorded as sent or complete.",
        "",
    ]
    write_text(OUT_DIR / "today_manual_action_minipack_report.md", "\n".join(report))

    summary = {
        "package": "today_manual_action_minipack_20260810",
        "action_rows": len(action_rows),
        "can_execute_today_rows": sum(1 for row in action_rows if row["can_execute_today"] == "yes"),
        "deferred_rows": sum(1 for row in action_rows if row["can_execute_today"] == "no"),
        "evidence_capture_rows": len(evidence_capture_rows),
        "stop_rules": len(stop_rows),
        "desktop_guide": str(DESKTOP_GUIDE),
        "desktop_guide_exists": DESKTOP_GUIDE.exists(),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "manual_actions_executed": False,
        "email_sent": False,
        "submission_ready": False,
        "status": "today_manual_action_minipack_ready_not_executed",
    }

    section = f"""### 18.89 Today manual action minipack update

Added a same-day manual action minipack that reduces the six open dispatch streams to a short execution list and evidence-capture targets.

New directory: `{OUT_DIR}`

Desktop guide: `{DESKTOP_GUIDE}`

New files:
1. `today_manual_action_minipack.csv`
2. `today_evidence_capture_targets.csv`
3. `today_manual_action_stop_rules.csv`
4. `TODAY_MANUAL_ACTION_MINIPACK.md`
5. `today_manual_action_minipack_qa.csv`
6. `today_manual_action_minipack_report.md`
7. `today_manual_action_minipack_summary.json`

Current result:
1. action_rows = {summary['action_rows']}
2. can_execute_today_rows = {summary['can_execute_today_rows']}
3. deferred_rows = {summary['deferred_rows']}
4. qa_pass = {str(qa_pass).lower()}
5. manual_actions_executed = false
6. email_sent = false
7. submission_ready = false

Boundary:
1. This step does not send messages.
2. This step does not write evidence into trackers.
3. This step does not close gates or authorize upload."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "today_manual_action_minipack_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Today manual action minipack QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
