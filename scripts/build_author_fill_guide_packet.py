#!/usr/bin/env python3
"""Build a concise fill guide for author-facing Nat Comms finalization sheets."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "author_fill_guide_packet_20260810"
AUTHOR_DIR = BENCH_ROOT / "reports" / "natcomms_author_finalization_reply_packet_20260810"
NEXT_DIR = BENCH_ROOT / "reports" / "natcomms_next_execution_packet_20260810"
TRACKER_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_tracker_20260810"
MANUAL_AUDIT_DIR = BENCH_ROOT / "reports" / "manual_field_preservation_audit_20260810"


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


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    author_rows = read_csv(AUTHOR_DIR / "author_finalization_reply_form_cn.csv")
    metadata_rows = read_csv(AUTHOR_DIR / "corresponding_author_metadata_form.csv")
    backend_rows = read_csv(AUTHOR_DIR / "figure_backend_decision_ticket.csv")
    branch_rows = read_csv(AUTHOR_DIR / "track_branch_and_external_validation_reply.csv")
    licence_rows = read_csv(AUTHOR_DIR / "licence_rights_reply_sheet.csv")
    reviewer_rows = read_csv(AUTHOR_DIR / "reviewer_and_policy_reply_sheet.csv")
    reporting_rows = read_csv(AUTHOR_DIR / "reporting_summary_author_reply_sheet.csv")
    task_rows = read_csv(NEXT_DIR / "next_execution_task_queue.csv")
    send_rows = read_csv(TRACKER_DIR / "author_response_send_log_template.csv")
    return_rows = read_csv(TRACKER_DIR / "author_response_return_tracker.csv")
    preservation_rows = read_csv(MANUAL_AUDIT_DIR / "manual_field_preservation_targets.csv")

    core_rows = []
    for row in author_rows:
        area = row["decision_area"]
        if area == "figure_backend":
            allowed = "Python or R only; also fill FIG-BACKEND-001 current_choice."
            example = "Python"
        elif area == "manuscript_branch":
            allowed = "Confirm Track B, or provide real held-label external blind asset holder/institution/timeline."
            example = "Track B confirmed; no real held-label external blind asset is available now."
        elif area == "competing_interests":
            allowed = "A complete competing-interest statement."
            example = "The authors declare no competing interests."
        elif area == "ethics_consent_governance":
            allowed = "Not applicable with reason, or exact ethics/consent/governance details."
            example = "Not applicable; this study uses derived benchmark data and no human participant data."
        elif area == "licence_rights_repository":
            allowed = "Explicit licence, rights and repository/DOI route."
            example = "Code MIT; derived Source Data CC BY 4.0 after institutional rights review; Zenodo DOI to be created after final figures."
        elif area == "final_submission_author_approval":
            allowed = "Do not pre-approve before final files; state approval will be given after final review."
            example = "Final approval pending final manuscript, SI, figures, Source Data and declarations review."
        else:
            allowed = "Free-text author-confirmed value; do not leave blank if required_to_close_gate is nonempty."
            example = "Fill with exact author-confirmed information."
        core_rows.append(
            {
                "field_id": row["field_id"],
                "decision_area": area,
                "fill_column": "author_reply",
                "allowed_or_expected_reply": allowed,
                "safe_example": example,
                "required_to_close_gate": row.get("required_to_close_gate", ""),
                "blocks_if_blank": row.get("blocks_if_blank", ""),
                "validation_command": r"py scripts\build_natcomms_author_reply_ingestion_validator.py",
            }
        )

    backend_guide_rows = []
    for row in backend_rows:
        example = "Python" if row["ticket_id"] == "FIG-BACKEND-001" else "Figure 1-Figure 6"
        backend_guide_rows.append(
            {
                "ticket_id": row["ticket_id"],
                "fill_column": "current_choice",
                "allowed_choices": row.get("allowed_choices", ""),
                "recommended_choice": row.get("recommended_choice", ""),
                "safe_example": example,
                "validation_command": r"py scripts\build_figure_backend_decision_validator.py",
                "boundary": "This enables formal rendering only; it does not render figures.",
            }
        )

    ancillary_rows = []
    for sheet_name, rows, key_field, fill_field, validator in [
        ("corresponding_author_metadata_form.csv", metadata_rows, "metadata_id", "author_reply", r"py scripts\build_natcomms_author_reply_ingestion_validator.py"),
        ("track_branch_and_external_validation_reply.csv", branch_rows, "branch_id", "author_reply", r"py scripts\build_natcomms_author_reply_ingestion_validator.py"),
        ("licence_rights_reply_sheet.csv", licence_rows, "item_id", "author_reply", r"py scripts\build_natcomms_gate_closure_evidence_binder.py"),
        ("reviewer_and_policy_reply_sheet.csv", reviewer_rows, "item_id", "author_reply", r"py scripts\build_natcomms_author_reply_ingestion_validator.py"),
        ("reporting_summary_author_reply_sheet.csv", reporting_rows, "reporting_item", "author_reply", r"py scripts\build_natcomms_author_reply_ingestion_validator.py"),
    ]:
        for row in rows:
            ancillary_rows.append(
                {
                    "sheet": sheet_name,
                    "row_id": row.get(key_field, ""),
                    "fill_column": fill_field,
                    "what_to_fill": "Exact author-confirmed value; no inferred or placeholder reply.",
                    "validation_command": validator,
                }
            )

    send_return_rows = [
        {
            "sheet": "author_response_send_log_template.csv",
            "row_count": len(send_rows),
            "manual_columns": "send_status; sent_datetime_local; sender; notes",
            "allowed_values": "send_status must be not_sent or sent; sent requires sender and sent_datetime_local.",
            "validation_command": r"py scripts\build_natcomms_author_response_log_validator.py",
        },
        {
            "sheet": "author_response_return_tracker.csv",
            "row_count": len(return_rows),
            "manual_columns": "return_status; returned_file_path; returned_datetime_local",
            "allowed_values": "return_status must be not_returned or returned; returned requires file path and timestamp.",
            "validation_command": r"py scripts\build_natcomms_author_response_log_validator.py",
        },
    ]

    owner_rows = []
    for row in task_rows:
        owner_rows.append(
            {
                "task_id": row["task_id"],
                "priority": row["priority"],
                "owner": row["owner"],
                "task": row["task"],
                "input_artifacts": row["input_artifacts"],
                "completion_evidence": row["completion_evidence"],
                "validation_command": row["validation_command"],
                "current_status": row["current_status"],
            }
        )

    prohibited_rows = [
        {
            "item": "backend",
            "prohibited_reply": "recommended; either; TBD",
            "reason": "Formal rendering requires exactly Python or R.",
        },
        {
            "item": "external validation",
            "prohibited_reply": "we have external validation",
            "reason": "Allowed only with strict blind intake and one locked evaluation.",
        },
        {
            "item": "author approval",
            "prohibited_reply": "approved now",
            "reason": "Final approval cannot precede final manuscript/SI/figures/source-data files.",
        },
        {
            "item": "repository DOI",
            "prohibited_reply": "DOI done",
            "reason": "DOI must be an actual created and verified accession, not a plan.",
        },
        {
            "item": "submission readiness",
            "prohibited_reply": "ready",
            "reason": "Submission_ready remains false until every upstream gate has evidence and full checks pass.",
        },
    ]

    qa_rows = [
        {
            "check_id": "QA-001",
            "check": "all 12 AFR fields represented",
            "observed": len(core_rows),
            "expected": 12,
            "pass": len(core_rows) == 12,
        },
        {
            "check_id": "QA-002",
            "check": "backend rows represented",
            "observed": len(backend_guide_rows),
            "expected": 2,
            "pass": len(backend_guide_rows) == 2,
        },
        {
            "check_id": "QA-003",
            "check": "owner tasks represented",
            "observed": len(owner_rows),
            "expected": 6,
            "pass": len(owner_rows) == 6,
        },
        {
            "check_id": "QA-004",
            "check": "manual field preservation imported",
            "observed": len(preservation_rows),
            "expected": 9,
            "pass": len(preservation_rows) == 9,
        },
        {
            "check_id": "QA-005",
            "check": "guide keeps submission blocked",
            "observed": "submission_ready=false",
            "expected": "submission_ready=false",
            "pass": True,
        },
    ]

    summary = {
        "package": "author_fill_guide_packet_20260810",
        "core_author_fields": len(core_rows),
        "backend_decision_rows": len(backend_guide_rows),
        "ancillary_fill_rows": len(ancillary_rows),
        "send_return_rows": len(send_return_rows),
        "owner_task_rows": len(owner_rows),
        "prohibited_reply_rows": len(prohibited_rows),
        "manual_preservation_targets_imported": len(preservation_rows),
        "qa_pass": all(bool(row["pass"]) for row in qa_rows),
        "author_replies_collected": False,
        "backend_selected": False,
        "submission_ready": False,
        "status": "author_fill_guide_packet_ready_for_manual_completion",
    }

    write_csv(
        OUT_DIR / "author_core_reply_fill_guide.csv",
        [
            "field_id",
            "decision_area",
            "fill_column",
            "allowed_or_expected_reply",
            "safe_example",
            "required_to_close_gate",
            "blocks_if_blank",
            "validation_command",
        ],
        core_rows,
    )
    write_csv(
        OUT_DIR / "backend_and_scope_fill_guide.csv",
        [
            "ticket_id",
            "fill_column",
            "allowed_choices",
            "recommended_choice",
            "safe_example",
            "validation_command",
            "boundary",
        ],
        backend_guide_rows,
    )
    write_csv(
        OUT_DIR / "ancillary_reply_sheet_fill_guide.csv",
        ["sheet", "row_id", "fill_column", "what_to_fill", "validation_command"],
        ancillary_rows,
    )
    write_csv(
        OUT_DIR / "send_return_log_fill_guide.csv",
        ["sheet", "row_count", "manual_columns", "allowed_values", "validation_command"],
        send_return_rows,
    )
    write_csv(
        OUT_DIR / "owner_specific_fill_assignments.csv",
        [
            "task_id",
            "priority",
            "owner",
            "task",
            "input_artifacts",
            "completion_evidence",
            "validation_command",
            "current_status",
        ],
        owner_rows,
    )
    write_csv(
        OUT_DIR / "prohibited_short_replies.csv",
        ["item", "prohibited_reply", "reason"],
        prohibited_rows,
    )
    write_csv(
        OUT_DIR / "author_fill_guide_packet_qa.csv",
        ["check_id", "check", "observed", "expected", "pass"],
        qa_rows,
    )

    guide_md = """# 作者/负责人填写指南

这份指南只说明怎么填写已经生成的作者回复表，不替作者作出决定。

## 必填原则

1. 只填写 `author_reply`、`current_choice`、发送日志和返回日志中的人工字段。
2. 不修改 recommendation、evidence、gate、source file 或 checksum 字段。
3. backend 必须明确写 `Python` 或 `R`，不能写“都可以”。
4. figure scope 必须明确写 `Figure 1-Figure 6` 或 `reduced display set with SI relocation`。
5. Track A external validation 只有在真实 held-label blind asset 完成 strict intake 和 locked evaluation 后才能写。
6. final author approval 不能在 final manuscript/SI/figures/source data 生成前提前确认。

## 填完后的验证顺序

1. `py scripts\\build_natcomms_author_response_log_validator.py`
2. `py scripts\\build_natcomms_author_reply_ingestion_validator.py`
3. `py scripts\\build_figure_backend_decision_validator.py`
4. `py scripts\\build_natcomms_gate_closure_evidence_binder.py`
5. `py scripts\\build_natcomms_finalization_command_dashboard_v3.py`
6. `py scripts\\check_manuscript_text_encoding.py`
7. `& scripts\\run_m0_m2_checks.ps1`

当前边界：这份指南不是作者批准，不是回复收集完成，不是 backend 选择，不是 final files，也不是投稿。
"""
    write_text(OUT_DIR / "AUTHOR_FILL_GUIDE_CN.md", guide_md)

    readme = """# Author Fill Guide Packet

This package converts the current author-facing CSV sheets into a practical
fill guide with allowed values, safe examples, owner assignments and validation
commands.

It does not create author replies, select a backend, send email, render figures,
close gates or make the submission ready.
"""
    write_text(OUT_DIR / "AUTHOR_FILL_GUIDE_PACKET_README.md", readme)

    report = f"""# Author Fill Guide Packet Report

Status: `{summary["status"]}`

Current state:

1. Core author fields: {summary["core_author_fields"]}
2. Backend decision rows: {summary["backend_decision_rows"]}
3. Ancillary fill rows: {summary["ancillary_fill_rows"]}
4. Send/return guide rows: {summary["send_return_rows"]}
5. Owner task rows: {summary["owner_task_rows"]}
6. Prohibited short-reply rows: {summary["prohibited_reply_rows"]}
7. Manual preservation targets imported: {summary["manual_preservation_targets_imported"]}
8. Author replies collected: false
9. Backend selected: false
10. Submission ready: false

Boundary: this package reduces manual-entry ambiguity only. It is not evidence
that any reply has been collected or any finalization gate has closed.
"""
    write_text(OUT_DIR / "author_fill_guide_packet_report.md", report)
    write_text(
        OUT_DIR / "author_fill_guide_packet_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("Author fill guide packet QA failed")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
