#!/usr/bin/env python3
"""Build a manual sendout execution guard for the Nat Comms author packet."""

from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_manual_sendout_execution_guard_20260810"
BUNDLE_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_bundle_v2_20260810"
TRACKER_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_tracker_20260810"
LOG_VALIDATOR_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_log_validator_20260810"
MANUAL_AUDIT_DIR = BENCH_ROOT / "reports" / "manual_field_preservation_audit_20260810"

BUNDLE_SUMMARY = BUNDLE_DIR / "author_sendout_bundle_v2_summary.json"
REPORT_ZIP = BUNDLE_DIR / "NatComms_author_sendout_bundle_v2_20260810.zip"
DESKTOP_ZIP = Path.home() / "Desktop" / "NatComms_author_sendout_bundle_v2_20260810.zip"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"


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


def zip_member_count(path: Path) -> int:
    if not path.exists():
        return 0
    with zipfile.ZipFile(path, "r") as handle:
        return len([item for item in handle.infolist() if not item.is_dir()])


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.68 Nature Communications manual sendout execution guard 更新"
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            text = text[:start].rstrip()
            updated = text + "\n\n" + section.strip() + "\n"
        else:
            text_before = text[:start].rstrip()
            text_after = text[next_start:].lstrip("\n")
            updated = text_before + "\n\n" + section.strip() + "\n\n" + text_after
    else:
        updated = text.rstrip() + "\n\n" + section.strip() + "\n"
    DESKTOP_PLAN.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bundle_summary = read_json(BUNDLE_SUMMARY)
    report_zip_count = zip_member_count(REPORT_ZIP)
    desktop_zip_count = zip_member_count(DESKTOP_ZIP)

    execution_rows = [
        {
            "step_id": "SEND-001",
            "stage": "before_send",
            "required_action": "Confirm the Desktop v2 zip is the only recommended sendout bundle.",
            "evidence_to_record": str(DESKTOP_ZIP),
            "pass_condition": "Desktop zip exists and contains the expected v2 bundle files.",
            "current_status": "ready",
        },
        {
            "step_id": "SEND-002",
            "stage": "before_send",
            "required_action": "Use author_sendout_email_ready_draft_cn.md as the email body.",
            "evidence_to_record": "Copy the final sent subject/body into the send log notes.",
            "pass_condition": "No wording claims approval, submission readiness, selected backend, DOI or final files.",
            "current_status": "ready",
        },
        {
            "step_id": "SEND-003",
            "stage": "manual_send",
            "required_action": "Send the v2 zip manually outside the script.",
            "evidence_to_record": "Sender, recipient, datetime, channel and exact zip filename.",
            "pass_condition": "A real send record is entered by the human sender.",
            "current_status": "not_done",
        },
        {
            "step_id": "SEND-004",
            "stage": "after_send",
            "required_action": "Fill author_response_send_log_template.csv after real sendout.",
            "evidence_to_record": str(TRACKER_DIR / "author_response_send_log_template.csv"),
            "pass_condition": "All required send rows are marked sent with timestamp and sender.",
            "current_status": "waiting_manual_sendout",
        },
        {
            "step_id": "SEND-005",
            "stage": "after_send",
            "required_action": "Run the response log validator before any reply ingestion.",
            "evidence_to_record": str(LOG_VALIDATOR_DIR / "author_response_lifecycle_gate_decision.csv"),
            "pass_condition": "Ingestion remains blocked until all sent and returned records are present.",
            "current_status": "waiting_manual_sendout",
        },
        {
            "step_id": "SEND-006",
            "stage": "return_intake",
            "required_action": "Store each returned file and fill author_response_return_tracker.csv.",
            "evidence_to_record": str(TRACKER_DIR / "author_response_return_tracker.csv"),
            "pass_condition": "Every required returned file has path, datetime and validation status.",
            "current_status": "waiting_returned_files",
        },
        {
            "step_id": "SEND-007",
            "stage": "return_intake",
            "required_action": "Copy author choices into protected fields only; do not regenerate blank forms first.",
            "evidence_to_record": str(MANUAL_AUDIT_DIR / "manual_field_preservation_targets.csv"),
            "pass_condition": "Protected manual fields are preserved across reruns.",
            "current_status": "waiting_returned_files",
        },
        {
            "step_id": "SEND-008",
            "stage": "post_return_validation",
            "required_action": "Run validators in the listed order after all required replies are filled.",
            "evidence_to_record": str(OUT_DIR / "post_send_validation_command_queue.csv"),
            "pass_condition": "Each command exits zero and summary gates reflect actual evidence only.",
            "current_status": "waiting_returned_files",
        },
        {
            "step_id": "SEND-009",
            "stage": "boundary",
            "required_action": "Keep submission_ready=false until final figures, DOI/rights, Reporting Summary and final files are complete.",
            "evidence_to_record": "finalization dashboard plus full M0-M2 check log",
            "pass_condition": "No final submission state is asserted from sendout alone.",
            "current_status": "active_guardrail",
        },
    ]
    write_csv(
        OUT_DIR / "manual_sendout_execution_checklist.csv",
        ["step_id", "stage", "required_action", "evidence_to_record", "pass_condition", "current_status"],
        execution_rows,
    )

    evidence_rows = [
        {
            "record_id": "EVID-001",
            "field": "sent_zip_path",
            "allowed_value_or_rule": str(DESKTOP_ZIP),
            "manual_owner": "sender",
            "when_to_fill": "after real manual sendout",
            "current_value": "",
        },
        {
            "record_id": "EVID-002",
            "field": "sent_datetime_local",
            "allowed_value_or_rule": "ISO-like local datetime, e.g. 2026-08-10 21:30 Asia/Shanghai",
            "manual_owner": "sender",
            "when_to_fill": "after real manual sendout",
            "current_value": "",
        },
        {
            "record_id": "EVID-003",
            "field": "recipient_list_confirmed",
            "allowed_value_or_rule": "corresponding_author; author_analysis; repository_or_institutional_admin; reporting_summary_owner",
            "manual_owner": "sender",
            "when_to_fill": "before send",
            "current_value": "",
        },
        {
            "record_id": "EVID-004",
            "field": "email_body_boundary_checked",
            "allowed_value_or_rule": "yes only after checking no final-readiness claims",
            "manual_owner": "sender",
            "when_to_fill": "before send",
            "current_value": "",
        },
        {
            "record_id": "EVID-005",
            "field": "all_returned_files_stored",
            "allowed_value_or_rule": "yes only when every required reply form has a local returned path",
            "manual_owner": "sender",
            "when_to_fill": "after return intake",
            "current_value": "",
        },
    ]
    write_csv(
        OUT_DIR / "sendout_evidence_capture_template.csv",
        ["record_id", "field", "allowed_value_or_rule", "manual_owner", "when_to_fill", "current_value"],
        evidence_rows,
    )

    integrity_rows = [
        {
            "check_id": "RET-001",
            "returned_file_group": "author reply forms",
            "check": "Every required CSV is returned or explicitly marked not applicable with reason.",
            "tool_or_file": str(TRACKER_DIR / "author_response_return_tracker.csv"),
            "must_pass_before": "author_reply_ingestion_validator",
        },
        {
            "check_id": "RET-002",
            "returned_file_group": "backend decision",
            "check": "Backend choice is exactly Python or R; scope is one of the allowed scope strings.",
            "tool_or_file": str(BENCH_ROOT / "reports" / "figure_backend_decision_validator_20260810" / "figure_backend_decision_validation.csv"),
            "must_pass_before": "figure_rendering",
        },
        {
            "check_id": "RET-003",
            "returned_file_group": "track decision",
            "check": "Track A requires a real held-label blind asset; otherwise Track B remains the bounded route.",
            "tool_or_file": str(BENCH_ROOT / "reports" / "natcomms_author_reply_ingestion_validator_20260810" / "gate_closure_from_author_replies.csv"),
            "must_pass_before": "external_validation_claims",
        },
        {
            "check_id": "RET-004",
            "returned_file_group": "licence and rights",
            "check": "Licence, third-party rights and repository route are explicit before any public deposit claim.",
            "tool_or_file": str(BENCH_ROOT / "reports" / "natcomms_gate_closure_evidence_binder_20260810" / "gate_closure_evidence_binder.csv"),
            "must_pass_before": "repository_release",
        },
        {
            "check_id": "RET-005",
            "returned_file_group": "final approval",
            "check": "Final author approval cannot be accepted until final manuscript/SI/figures/source data exist.",
            "tool_or_file": str(BENCH_ROOT / "reports" / "natcomms_finalization_command_dashboard_v3_20260810" / "finalization_command_dashboard_v3.csv"),
            "must_pass_before": "portal_upload",
        },
    ]
    write_csv(
        OUT_DIR / "return_file_integrity_checklist.csv",
        ["check_id", "returned_file_group", "check", "tool_or_file", "must_pass_before"],
        integrity_rows,
    )

    command_rows = [
        {
            "order": 1,
            "command": "py scripts\\build_natcomms_author_response_log_validator.py",
            "purpose": "Verify manual send/return lifecycle logs before ingestion.",
        },
        {
            "order": 2,
            "command": "py scripts\\build_natcomms_author_reply_ingestion_validator.py",
            "purpose": "Ingest protected author/manual fields without treating blanks as approval.",
        },
        {
            "order": 3,
            "command": "py scripts\\build_figure_backend_decision_validator.py",
            "purpose": "Confirm whether figure rendering is allowed after backend/scope choices.",
        },
        {
            "order": 4,
            "command": "py scripts\\build_natcomms_gate_closure_evidence_binder.py",
            "purpose": "Bind every candidate gate closure to explicit evidence.",
        },
        {
            "order": 5,
            "command": "py scripts\\build_natcomms_finalization_command_dashboard_v3.py",
            "purpose": "Refresh the finalization dashboard and no-go register.",
        },
        {
            "order": 6,
            "command": "powershell -ExecutionPolicy Bypass -File scripts\\run_m0_m2_checks.ps1",
            "purpose": "Run the complete reproducibility and artifact existence chain.",
        },
    ]
    write_csv(OUT_DIR / "post_send_validation_command_queue.csv", ["order", "command", "purpose"], command_rows)

    readme = """# Nat Comms Manual Sendout Execution Guard

Purpose: convert the author sendout bundle v2 into a controlled manual execution
workflow. This package defines what must be checked before sendout, what must be
recorded after sendout, how returned files are checked, and which validators must
be rerun.

Boundary: this package does not send email, collect replies, choose Python/R,
render figures, create DOI records, close gates, generate final files or submit
the manuscript.
"""
    write_text(OUT_DIR / "NATCOMMS_MANUAL_SENDOUT_EXECUTION_GUARD_README.md", readme)

    report = f"""# Nat Comms Manual Sendout Execution Guard

Status: `natcomms_manual_sendout_execution_guard_ready_waiting_manual_sendout`

Inputs checked:

1. Bundle summary: `{BUNDLE_SUMMARY}`
2. Report zip: `{REPORT_ZIP}`
3. Desktop zip: `{DESKTOP_ZIP}`

Current result:

1. Manual execution steps: {len(execution_rows)}
2. Evidence capture rows: {len(evidence_rows)}
3. Return integrity checks: {len(integrity_rows)}
4. Post-send validation commands: {len(command_rows)}
5. Report zip member count: {report_zip_count}
6. Desktop zip member count: {desktop_zip_count}
7. Email sent: false
8. Author replies collected: false
9. Backend selected: false
10. Submission ready: false

Use this package immediately after sending the Desktop v2 zip. Until the human
sender records real send evidence, downstream reply ingestion must remain
blocked.
"""
    write_text(OUT_DIR / "manual_sendout_execution_guard_report.md", report)

    qa_rows = [
        {
            "check": "Bundle v2 summary exists",
            "result": "PASS" if BUNDLE_SUMMARY.exists() else "FAIL",
            "detail": str(BUNDLE_SUMMARY),
        },
        {
            "check": "Bundle v2 QA passed",
            "result": "PASS" if bundle_summary.get("qa_pass") is True else "FAIL",
            "detail": f"qa_pass={bundle_summary.get('qa_pass')}",
        },
        {
            "check": "Desktop zip exists",
            "result": "PASS" if DESKTOP_ZIP.exists() else "FAIL",
            "detail": str(DESKTOP_ZIP),
        },
        {
            "check": "Zip member counts match",
            "result": "PASS" if report_zip_count > 0 and report_zip_count == desktop_zip_count else "FAIL",
            "detail": f"report_zip_members={report_zip_count}; desktop_zip_members={desktop_zip_count}",
        },
        {
            "check": "Manual send remains unasserted",
            "result": "PASS" if bundle_summary.get("email_sent") is False else "FAIL",
            "detail": "email_sent must stay false until real manual sendout.",
        },
        {
            "check": "Author replies remain unasserted",
            "result": "PASS" if bundle_summary.get("author_replies_collected") is False else "FAIL",
            "detail": "author_replies_collected must stay false until returned files are validated.",
        },
        {
            "check": "Submission readiness remains blocked",
            "result": "PASS" if bundle_summary.get("submission_ready") is False else "FAIL",
            "detail": "sendout preparation alone cannot make the manuscript ready.",
        },
    ]
    write_csv(OUT_DIR / "manual_sendout_execution_guard_qa.csv", ["check", "result", "detail"], qa_rows)

    desktop_section = f"""### 18.68 Nature Communications manual sendout execution guard 更新

已新增 Nature Communications manual sendout execution guard 包。这个包把桌面 v2 作者发送包之后的人工动作拆成可审计步骤：发送前核对、真实发送证据记录、返回文件完整性检查、返回后验证命令顺序和禁止提前关闭 gate 的边界。

新增目录：
`{OUT_DIR}`

新增材料：
1. `manual_sendout_execution_checklist.csv`
2. `sendout_evidence_capture_template.csv`
3. `return_file_integrity_checklist.csv`
4. `post_send_validation_command_queue.csv`
5. `manual_sendout_execution_guard_qa.csv`
6. `NATCOMMS_MANUAL_SENDOUT_EXECUTION_GUARD_README.md`
7. `manual_sendout_execution_guard_report.md`
8. `manual_sendout_execution_guard_summary.json`

当前结果：
1. manual_execution_steps = {len(execution_rows)}
2. evidence_capture_rows = {len(evidence_rows)}
3. return_integrity_checks = {len(integrity_rows)}
4. post_send_validation_commands = {len(command_rows)}
5. desktop_zip_exists = {str(DESKTOP_ZIP.exists()).lower()}
6. zip_member_count_match = {str(report_zip_count == desktop_zip_count and report_zip_count > 0).lower()}
7. qa_pass = {str(all(row["result"] != "FAIL" for row in qa_rows)).lower()}
8. email_sent = false
9. author_replies_collected = false
10. backend_selected = false
11. submission_ready = false
12. 当前状态：`natcomms_manual_sendout_execution_guard_ready_waiting_manual_sendout`

边界：
1. 这一步不发送邮件。
2. 这一步不创建作者回复。
3. 这一步不选择 Python 或 R。
4. 这一步不渲染 figures。
5. 这一步不创建 DOI。
6. 这一步不关闭任何 gate。
7. 这一步不生成 final manuscript/SI/source data。
8. 这一步不提交 manuscript。
"""
    desktop_plan_updated = update_desktop_plan(desktop_section)

    summary = {
        "package": "natcomms_manual_sendout_execution_guard_20260810",
        "manual_execution_steps": len(execution_rows),
        "evidence_capture_rows": len(evidence_rows),
        "return_integrity_checks": len(integrity_rows),
        "post_send_validation_commands": len(command_rows),
        "report_zip_members": report_zip_count,
        "desktop_zip_members": desktop_zip_count,
        "zip_member_count_match": report_zip_count > 0 and report_zip_count == desktop_zip_count,
        "desktop_plan_updated": desktop_plan_updated,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "email_sent": False,
        "author_replies_collected": False,
        "backend_selected": False,
        "submission_ready": False,
        "status": "natcomms_manual_sendout_execution_guard_ready_waiting_manual_sendout",
    }
    write_text(OUT_DIR / "manual_sendout_execution_guard_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not summary["qa_pass"]:
        raise SystemExit("Manual sendout execution guard QA failed")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
