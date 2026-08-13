#!/usr/bin/env python3
"""Build a unified final manual receipt intake package from the 19.48 next actions."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_intake_package_20260810"
NEXT_ACTION_DIR = BENCH_ROOT / "reports" / "final_master_next_action_packet_20260810"
FINAL_MASTER_DIR = BENCH_ROOT / "reports" / "final_submission_master_dependency_bridge_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_GUIDE = Path.home() / "Desktop" / "NatComms_19.49_final_manual_receipt_intake_20260810.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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
    marker = "### 19.49 Final manual receipt intake package update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/final_manual_receipt_intake_package_20260810/`，把 19.48 的人工动作统一成最终 receipt intake 模板。
- 桌面同步生成 `NatComms_19.49_final_manual_receipt_intake_20260810.md`，用于人工回填作者发送、作者决策、真实返回文件、图审、DOI/rights 和受控重跑回执。
- 当前 `receipt_rows={summary["receipt_rows"]}`，`completed_receipt_rows=0`，`missing_required_receipts={summary["missing_required_receipts"]}`。
- 当前 `receipt_intake_complete=false`，`system_command_execution_allowed=false`，`portal_upload_allowed=false`，`submission_ready=false`。
- 边界：该 intake package 是空白回执模板，不伪造证据、不计算真实 hash、不执行 writeback/rerun、不上传 portal 文件。
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

    next_summary = read_json(NEXT_ACTION_DIR / "final_master_next_action_packet_summary.json")
    final_master = read_json(FINAL_MASTER_DIR / "final_submission_master_dependency_bridge_validator_summary.json")
    manual_actions = read_csv(NEXT_ACTION_DIR / "final_master_next_manual_actions.csv")
    forbidden_actions = read_csv(NEXT_ACTION_DIR / "final_master_forbidden_submission_actions.csv")

    receipt_rows = [
        {
            "receipt_id": "FMR-001",
            "source_action_priority": 1,
            "receipt_type": "author_sendout_evidence",
            "owner": "corresponding_author",
            "required_evidence": "sent_datetime_local, sender account, recipient list, sent packet path, sent packet SHA256, immutable send log path",
            "target_or_route": "reports/natcomms_author_response_tracker_20260810/author_response_send_log_template.csv",
            "value_to_fill_after_manual_action": "FILL_AFTER_SEND",
            "acceptance_test": "email_sent=true and author response log validator passes",
            "first_validator": "py scripts/build_natcomms_author_response_log_validator.py",
            "current_status": "missing",
            "unlocks_when_valid": "author reply collection",
        },
        {
            "receipt_id": "FMR-002",
            "source_action_priority": 2,
            "receipt_type": "author_decision_values",
            "owner": "author_and_advisor",
            "required_evidence": "backend choice, external asset decision, licence direction, Track B fallback decision, decision timestamp",
            "target_or_route": "reports/author_decision_closure_packet_v2_20260810/author_decision_closure_form_v2.csv",
            "value_to_fill_after_manual_action": "FILL_AFTER_REPLY",
            "acceptance_test": "all four author decision rows resolved with accepted values",
            "first_validator": "py scripts/build_manual_evidence_final_intake_validator.py",
            "current_status": "missing",
            "unlocks_when_valid": "backend/scope, repository and branch framing gates",
        },
        {
            "receipt_id": "FMR-003",
            "source_action_priority": 3,
            "receipt_type": "real_returned_evidence_drop",
            "owner": "author_or_data_holder",
            "required_evidence": "canonical folder, file name, SHA256, source identity, timestamp and operator attestation",
            "target_or_route": "final_return_evidence_inbox_20260810/ plus rb001 receipt template",
            "value_to_fill_after_manual_action": "FILL_AFTER_DROP",
            "acceptance_test": "candidate_return_files > 0 and scanner/hash reconciliation passes",
            "first_validator": "py scripts/build_final_return_evidence_intake_scanner.py",
            "current_status": "missing",
            "unlocks_when_valid": "RB-001 receipt closeout",
        },
        {
            "receipt_id": "FMR-004",
            "source_action_priority": 4,
            "receipt_type": "figure_author_review_decisions",
            "owner": "figure_owner_and_author_team",
            "required_evidence": "Figure 1-Figure 6 approve/revise/reject decision, reviewer identity and comments",
            "target_or_route": "reports/python_figure_author_review_packet_20260810/python_figure_author_review_form.csv",
            "value_to_fill_after_manual_action": "FILL_AFTER_FIGURE_REVIEW",
            "acceptance_test": "required figure rows approved or revision queue explicitly accepted",
            "first_validator": "py scripts/build_python_figure_author_review_intake_validator.py",
            "current_status": "missing",
            "unlocks_when_valid": "final figure candidate preflight",
        },
        {
            "receipt_id": "FMR-005",
            "source_action_priority": 5,
            "receipt_type": "repository_rights_doi_decisions",
            "owner": "repository_or_rights_owner",
            "required_evidence": "repository DOI/accession, code DOI, licence, third-party rights decision and exclusion list",
            "target_or_route": "repository_predeposit_handoff and rights_licence_completion_handoff",
            "value_to_fill_after_manual_action": "FILL_AFTER_RIGHTS_DOI",
            "acceptance_test": "final_availability_ready=true and rights blockers closed",
            "first_validator": "py scripts/build_availability_repository_finalization_validator.py",
            "current_status": "missing",
            "unlocks_when_valid": "Data/Code Availability and portal file preflight",
        },
        {
            "receipt_id": "FMR-006",
            "source_action_priority": 6,
            "receipt_type": "guarded_recheck_receipt",
            "owner": "manuscript_operator",
            "required_evidence": "completed receipt IDs FMR-001 to FMR-005, M0-M2 log path, exit code and summary of changed gates",
            "target_or_route": "reports/latest_run_m0_m2_checks_20260810.log",
            "value_to_fill_after_manual_action": "FILL_AFTER_RECHECK",
            "acceptance_test": "M0-M2 passes after real evidence without portal upload",
            "first_validator": "powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1",
            "current_status": "waiting_for_FMR_001_to_FMR_005",
            "unlocks_when_valid": "19.47 re-evaluation only",
        },
    ]

    field_rows = [
        {"field": "receipt_id", "required": "yes", "format": "FMR-###", "notes": "Do not change predefined IDs."},
        {"field": "owner", "required": "yes", "format": "person or role", "notes": "Must identify accountable human owner."},
        {"field": "required_evidence", "required": "yes", "format": "text", "notes": "Evidence must be real and inspectable."},
        {"field": "value_to_fill_after_manual_action", "required": "yes", "format": "replace placeholder after action", "notes": "Placeholders do not unlock gates."},
        {"field": "current_status", "required": "yes", "format": "missing|complete|rejected|waiting_for_*", "notes": "Current generated state is missing/waiting only."},
        {"field": "first_validator", "required": "yes", "format": "command", "notes": "Run only after real evidence is present."},
    ]

    acceptance_rows = [
        {
            "check": "19.48 imported",
            "expected": "manual_action_rows=6",
            "current": f"manual_action_rows={next_summary.get('manual_action_rows')}",
            "passes_now": "yes" if next_summary.get("manual_action_rows") == 6 else "no",
        },
        {
            "check": "19.47 still blocks submission",
            "expected": "final_submission_master_allowed=false",
            "current": f"final_submission_master_allowed={final_master.get('final_submission_master_allowed')}",
            "passes_now": "yes" if final_master.get("final_submission_master_allowed") is False else "no",
        },
        {
            "check": "all required receipts start incomplete",
            "expected": "completed_receipt_rows=0",
            "current": "completed_receipt_rows=0",
            "passes_now": "yes",
        },
        {
            "check": "forbidden actions preserved",
            "expected": "forbidden_submission_action_rows>=5",
            "current": f"forbidden_submission_action_rows={len(forbidden_actions)}",
            "passes_now": "yes" if len(forbidden_actions) >= 5 else "no",
        },
    ]

    summary = {
        "package": "final_manual_receipt_intake_package_20260810",
        "receipt_rows": len(receipt_rows),
        "completed_receipt_rows": 0,
        "missing_required_receipts": len(receipt_rows),
        "manual_action_rows_imported": len(manual_actions),
        "forbidden_submission_action_rows_imported": len(forbidden_actions),
        "receipt_intake_complete": False,
        "system_command_execution_allowed": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(acceptance_rows),
        "qa_pass": all(row["passes_now"] == "yes" for row in acceptance_rows),
        "status": "final_manual_receipt_intake_package_ready_waiting_real_receipts",
        "desktop_guide": str(DESKTOP_GUIDE),
    }

    guide_lines = [
        "# NatComms 19.49 Final Manual Receipt Intake",
        "",
        "Purpose: collect real human receipts for the 19.48 manual-only actions.",
        "",
        "Current state: no receipt is complete. Portal upload, system execution and submission-ready remain forbidden.",
        "",
        "## Receipt Rows",
        "",
    ]
    for row in receipt_rows:
        guide_lines.extend(
            [
                f"### {row['receipt_id']} - {row['receipt_type']}",
                "",
                f"- Owner: {row['owner']}",
                f"- Required evidence: {row['required_evidence']}",
                f"- Target or route: `{row['target_or_route']}`",
                f"- Acceptance test: {row['acceptance_test']}",
                f"- First validator: `{row['first_validator']}`",
                f"- Current status: {row['current_status']}",
                "",
            ]
        )
    guide_lines.extend(
        [
            "## No-go Rules",
            "",
            "- Do not replace placeholders unless the evidence exists on disk or in an inspectable send/decision record.",
            "- Do not run writeback, transition, portal upload or submission commands from this template.",
            "- Do not mark any receipt complete without SHA256/source/timestamp where required.",
            "- Do not claim `submission_ready=true` unless 19.47 later reports it.",
            "",
        ]
    )
    guide = "\n".join(guide_lines)

    write_csv(
        OUT_DIR / "final_manual_receipt_intake_template.csv",
        [
            "receipt_id",
            "source_action_priority",
            "receipt_type",
            "owner",
            "required_evidence",
            "target_or_route",
            "value_to_fill_after_manual_action",
            "acceptance_test",
            "first_validator",
            "current_status",
            "unlocks_when_valid",
        ],
        receipt_rows,
    )
    write_csv(OUT_DIR / "final_manual_receipt_field_dictionary.csv", ["field", "required", "format", "notes"], field_rows)
    write_csv(
        OUT_DIR / "final_manual_receipt_acceptance_tests.csv",
        ["check", "expected", "current", "passes_now"],
        acceptance_rows,
    )
    write_text(OUT_DIR / "FINAL_MANUAL_RECEIPT_INTAKE_README.md", guide)
    write_text(OUT_DIR / "final_manual_receipt_intake_package_report.md", guide)
    write_text(DESKTOP_GUIDE, guide)
    summary["desktop_guide_exists"] = DESKTOP_GUIDE.exists()
    summary["desktop_plan_updated"] = update_desktop_plan(summary)
    write_text(
        OUT_DIR / "final_manual_receipt_intake_package_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
