#!/usr/bin/env python3
"""Validate the crosswalk from Nat Comms returned-file tracker rows to RB-001 drop routes."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_return_tracker_to_rb001_crosswalk_validator_20260810"
TRACKER_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_tracker_20260810"
DROP_KIT_DIR = BENCH_ROOT / "reports" / "rb001_return_evidence_drop_kit_20260810"
POST_DISPATCH_DIR = BENCH_ROOT / "reports" / "post_dispatch_evidence_intake_validator_20260810"
RB001_DASHBOARD_DIR = BENCH_ROOT / "reports" / "rb001_closeout_dashboard_20260810"
RECEIPT_DIR = BENCH_ROOT / "reports" / "natcomms_sendout_evidence_receipt_completion_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

ATTACHMENT_ROUTE = {
    "ATT-001": "RTE-002",
    "ATT-002": "RTE-002",
    "ATT-003": "RTE-002",
    "ATT-004": "RTE-002",
    "ATT-005": "RTE-002",
    "ATT-006": "RTE-004",
    "ATT-007": "RTE-005",
    "ATT-008": "RTE-002",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.38 NatComms return tracker to RB-001 crosswalk validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/natcomms_return_tracker_to_rb001_crosswalk_validator_20260810/`，把 NatComms returned-file tracker 的 8 个附件回执映射到 RB-001 canonical drop routes，防止返回文件落错目录或绕过 hash manifest。
- 当前 `return_tracker_rows={summary["return_tracker_rows"]}`，`mapped_return_rows={summary["mapped_return_rows"]}`，`returned_rows={summary["returned_rows"]}`，`drop_ready_rows={summary["drop_ready_rows"]}`。
- 当前 `return_tracker_to_rb001_ready={str(summary["return_tracker_to_rb001_ready"]).lower()}`，`rb001_drop_allowed={str(summary["rb001_drop_allowed"]).lower()}`，`scanner_allowed_now={str(summary["scanner_allowed_now"]).lower()}`。
- 当前 `candidate_return_files=0`，`writeback_allowed_rows=0`，`submission_ready=false`。
- 边界：该 validator 只读 tracker/drop-kit/post-dispatch 状态，不复制返回文件、不计算 hash、不写回、不关闭 gate。
"""
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            text = text[:start].rstrip()
        else:
            text = text[:start].rstrip() + "\n\n" + text[next_start:].lstrip("\n")
    text = text.rstrip() + block
    DESKTOP_PLAN.write_text(text + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    return_rows = read_csv(TRACKER_DIR / "author_response_return_tracker.csv")
    send_rows = read_csv(TRACKER_DIR / "author_response_send_log_template.csv")
    route_rows = read_csv(DROP_KIT_DIR / "rb001_return_evidence_drop_locations.csv")
    hash_template_rows = read_csv(DROP_KIT_DIR / "rb001_return_evidence_hash_manifest_template.csv")
    post_dispatch = read_json(POST_DISPATCH_DIR / "post_dispatch_evidence_intake_validator_summary.json")
    rb001_summary = read_json(RB001_DASHBOARD_DIR / "rb001_closeout_dashboard_summary.json")
    receipt_summary = read_json(RECEIPT_DIR / "sendout_evidence_receipt_completion_validator_summary.json")

    route_by_id = {row["route_id"]: row for row in route_rows}
    hash_template_by_route = {row["route_id"]: row for row in hash_template_rows}

    crosswalk_rows = []
    for row in return_rows:
        route_id = ATTACHMENT_ROUTE.get(row.get("attachment_id", ""), "")
        route = route_by_id.get(route_id, {})
        returned = row.get("return_status") == "returned"
        has_path = bool(row.get("returned_file_path"))
        has_time = bool(row.get("returned_datetime_local"))
        hash_template = hash_template_by_route.get(route_id, {})
        drop_ready = returned and has_path and has_time and bool(route_id) and route.get("folder_exists") == "True"
        crosswalk_rows.append(
            {
                "attachment_id": row.get("attachment_id", ""),
                "recipient": row.get("recipient", ""),
                "bundle_file": row.get("bundle_file", ""),
                "return_status": row.get("return_status", ""),
                "returned_file_path_filled": has_path,
                "returned_datetime_filled": has_time,
                "rb001_route_id": route_id,
                "rb001_relative_folder": route.get("relative_folder", ""),
                "rb001_expected_evidence": route.get("required_files", ""),
                "hash_manifest_route_present": bool(hash_template),
                "drop_ready": drop_ready,
                "issue": "" if drop_ready else "not_returned_or_missing_path_timestamp",
            }
        )

    send_log_ready = all(
        row.get("send_status") == "sent" and row.get("sent_datetime_local") and row.get("sender")
        for row in send_rows
    )
    mapped_return_rows = sum(1 for row in crosswalk_rows if row["rb001_route_id"])
    returned_rows = sum(1 for row in crosswalk_rows if row["return_status"] == "returned")
    drop_ready_rows = sum(1 for row in crosswalk_rows if row["drop_ready"])
    all_returns_mapped = mapped_return_rows == len(return_rows)
    all_returned_rows_drop_ready = len(return_rows) > 0 and drop_ready_rows == len(return_rows)
    return_tracker_to_rb001_ready = send_log_ready and all_returns_mapped and all_returned_rows_drop_ready
    rb001_drop_allowed = (
        return_tracker_to_rb001_ready
        and receipt_summary.get("return_intake_allowed") is True
        and post_dispatch.get("evidence_rows_missing") == 0
    )
    scanner_allowed_now = rb001_drop_allowed and rb001_summary.get("candidate_return_files", 0) > 0

    gate_rows = [
        {
            "gate": "send_log_ready",
            "current": send_log_ready,
            "required": "true",
            "passes_now": "yes" if send_log_ready else "no",
        },
        {
            "gate": "all_return_tracker_rows_mapped",
            "current": mapped_return_rows,
            "required": len(return_rows),
            "passes_now": "yes" if all_returns_mapped else "no",
        },
        {
            "gate": "all_return_tracker_rows_returned",
            "current": returned_rows,
            "required": len(return_rows),
            "passes_now": "yes" if returned_rows == len(return_rows) and len(return_rows) > 0 else "no",
        },
        {
            "gate": "all_returned_rows_drop_ready",
            "current": drop_ready_rows,
            "required": len(return_rows),
            "passes_now": "yes" if all_returned_rows_drop_ready else "no",
        },
        {
            "gate": "sendout_receipt_return_intake_allowed",
            "current": receipt_summary.get("return_intake_allowed"),
            "required": "true",
            "passes_now": "yes" if receipt_summary.get("return_intake_allowed") is True else "no",
        },
        {
            "gate": "post_dispatch_evidence_complete",
            "current": post_dispatch.get("evidence_rows_missing"),
            "required": "0",
            "passes_now": "yes" if post_dispatch.get("evidence_rows_missing") == 0 else "no",
        },
        {
            "gate": "rb001_drop_allowed",
            "current": rb001_drop_allowed,
            "required": "true",
            "passes_now": "yes" if rb001_drop_allowed else "no",
        },
        {
            "gate": "scanner_allowed_now",
            "current": scanner_allowed_now,
            "required": "true",
            "passes_now": "yes" if scanner_allowed_now else "no",
        },
        {
            "gate": "writeback_allowed_rows",
            "current": rb001_summary.get("writeback_allowed_rows"),
            "required": "0 before scanner/hash/manual review",
            "passes_now": "yes" if rb001_summary.get("writeback_allowed_rows") == 0 else "no",
        },
        {
            "gate": "submission_ready",
            "current": False,
            "required": "false",
            "passes_now": "yes",
        },
    ]

    next_action_rows = [
        {
            "order": 1,
            "condition": "real sendout performed",
            "action": "Fill canonical send log sender and sent_datetime_local for all five recipient rows.",
            "allowed_now": "after_real_send_only",
        },
        {
            "order": 2,
            "condition": "returned files received",
            "action": "Fill returned_file_path and returned_datetime_local for all required return tracker rows.",
            "allowed_now": "after_real_returns_only",
        },
        {
            "order": 3,
            "condition": "return tracker complete",
            "action": "Copy each returned file into its mapped RB-001 canonical folder and fill hash manifest after SHA256 calculation.",
            "allowed_now": "manual_only_after_returns",
        },
        {
            "order": 4,
            "condition": "hash manifest complete",
            "action": "Run final return evidence scanner and hash reconciliation diagnostics only.",
            "allowed_now": "blocked_now",
        },
        {
            "order": 5,
            "condition": "scanner/reconciliation pass and manual receipt complete",
            "action": "Only then consider RB-001 closeout and downstream writeback preflight.",
            "allowed_now": "blocked_now",
        },
    ]

    qa_rows = [
        {
            "check": "return rows present",
            "result": "PASS" if len(return_rows) == 8 else "FAIL",
            "detail": f"rows={len(return_rows)}",
        },
        {
            "check": "all return rows have RB-001 route mapping",
            "result": "PASS" if all_returns_mapped else "FAIL",
            "detail": f"mapped={mapped_return_rows}",
        },
        {
            "check": "empty return tracker blocks drop",
            "result": "PASS" if not rb001_drop_allowed and returned_rows == 0 else "FAIL",
            "detail": f"returned_rows={returned_rows}; rb001_drop_allowed={rb001_drop_allowed}",
        },
        {
            "check": "scanner remains blocked",
            "result": "PASS" if not scanner_allowed_now else "FAIL",
            "detail": f"candidate_return_files={rb001_summary.get('candidate_return_files')}",
        },
        {
            "check": "writeback remains blocked",
            "result": "PASS" if rb001_summary.get("writeback_allowed_rows") == 0 else "FAIL",
            "detail": f"writeback_allowed_rows={rb001_summary.get('writeback_allowed_rows')}",
        },
    ]

    summary = {
        "package": "natcomms_return_tracker_to_rb001_crosswalk_validator_20260810",
        "send_log_rows": len(send_rows),
        "send_log_ready": send_log_ready,
        "return_tracker_rows": len(return_rows),
        "mapped_return_rows": mapped_return_rows,
        "returned_rows": returned_rows,
        "drop_ready_rows": drop_ready_rows,
        "return_tracker_to_rb001_ready": return_tracker_to_rb001_ready,
        "rb001_drop_allowed": rb001_drop_allowed,
        "scanner_allowed_now": scanner_allowed_now,
        "candidate_return_files": rb001_summary.get("candidate_return_files", 0),
        "writeback_allowed_rows": rb001_summary.get("writeback_allowed_rows", 0),
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "natcomms_return_tracker_to_rb001_crosswalk_validator_ready_blocked_no_returns",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "return_tracker_to_rb001_crosswalk.csv",
        [
            "attachment_id",
            "recipient",
            "bundle_file",
            "return_status",
            "returned_file_path_filled",
            "returned_datetime_filled",
            "rb001_route_id",
            "rb001_relative_folder",
            "rb001_expected_evidence",
            "hash_manifest_route_present",
            "drop_ready",
            "issue",
        ],
        crosswalk_rows,
    )
    write_csv(
        OUT_DIR / "return_tracker_to_rb001_gate_matrix.csv",
        ["gate", "current", "required", "passes_now"],
        gate_rows,
    )
    write_csv(
        OUT_DIR / "return_tracker_to_rb001_next_actions.csv",
        ["order", "condition", "action", "allowed_now"],
        next_action_rows,
    )
    write_csv(
        OUT_DIR / "return_tracker_to_rb001_crosswalk_validator_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# Nat Comms Return Tracker to RB-001 Crosswalk Validator

This validator maps Nat Comms returned-file tracker rows to RB-001 canonical
drop routes and checks whether returned-file intake can proceed toward scanner
and hash reconciliation.

Boundary: it is read-only. It does not copy returned files, calculate hashes,
edit the hash manifest, write protected targets, close gates or make the
manuscript submission-ready.
"""
    write_text(OUT_DIR / "NATCOMMS_RETURN_TRACKER_TO_RB001_CROSSWALK_VALIDATOR_README.md", readme)

    report = f"""# Nat Comms Return Tracker to RB-001 Crosswalk Validator Report

Status: `{summary["status"]}`

Current result:

1. Send log rows: {summary["send_log_rows"]}
2. Send log ready: {str(summary["send_log_ready"]).lower()}
3. Return tracker rows: {summary["return_tracker_rows"]}
4. Mapped return rows: {summary["mapped_return_rows"]}
5. Returned rows: {summary["returned_rows"]}
6. Drop-ready rows: {summary["drop_ready_rows"]}
7. Return tracker to RB-001 ready: {str(summary["return_tracker_to_rb001_ready"]).lower()}
8. RB-001 drop allowed: {str(summary["rb001_drop_allowed"]).lower()}
9. Scanner allowed now: {str(summary["scanner_allowed_now"]).lower()}
10. Writeback allowed rows: {summary["writeback_allowed_rows"]}
11. Submission ready: false

Interpretation: the returned-file tracker is mapped to RB-001 drop routes, but
no real returns are recorded. Scanner, hash reconciliation, writeback and
submission readiness remain blocked.
"""
    write_text(OUT_DIR / "return_tracker_to_rb001_crosswalk_validator_report.md", report)
    write_text(
        OUT_DIR / "return_tracker_to_rb001_crosswalk_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("NatComms return tracker to RB-001 crosswalk validator QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
