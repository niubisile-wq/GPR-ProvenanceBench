#!/usr/bin/env python3
"""Build writeback queue for returned Python figure author-review files."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "python_figure_author_review_writeback_queue_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8\u670810\u65e5cns.md"

RETURN_SUMMARY = REPORTS / "python_figure_author_review_return_inbox_20260810" / "python_figure_author_review_return_inbox_summary.json"
RETURN_AUDIT = REPORTS / "python_figure_author_review_return_inbox_20260810" / "python_figure_author_review_return_file_audit.csv"
REVIEW_FORM = REPORTS / "python_figure_author_review_packet_20260810" / "python_figure_author_review_form.csv"
INTAKE_SUMMARY = REPORTS / "python_figure_author_review_intake_validator_20260810" / "python_figure_author_review_intake_summary.json"


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
    marker = "### 19.02 Python figure author review writeback queue update"
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


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    return_summary = read_json(RETURN_SUMMARY)
    return_files = read_csv(RETURN_AUDIT)
    review_rows = read_csv(REVIEW_FORM)
    intake_summary = read_json(INTAKE_SUMMARY)

    queue_rows = []
    for row in review_rows:
        queue_rows.append(
            {
                "figure_id": row["figure_id"],
                "source_inbox": "reports/python_figure_author_review_return_inbox_20260810/returned_author_review_files",
                "candidate_return_files": len(return_files),
                "target_file": "reports/python_figure_author_review_packet_20260810/python_figure_author_review_form.csv",
                "target_row_key": row["figure_id"],
                "editable_fields": "author_approval_status; author_comment",
                "do_not_edit_fields": "figure_id; preview_file_png; preview_file_pdf; core_conclusion; required_boundary; current_visual_status; allowed_values",
                "allowed_author_approval_status": "approve_preview_for_final_candidate; request_revision; reject_claim_framing",
                "after_manual_writeback_validator": "py scripts\\build_python_figure_author_review_intake_validator.py",
                "writeback_allowed_now": "no",
                "reason": "No candidate returned author-review file is present." if len(return_files) == 0 else "Manual transcription required before validator rerun.",
            }
        )

    protection_rows = [
        {
            "target_file": "reports/python_figure_author_review_packet_20260810/python_figure_author_review_form.csv",
            "protected_field": field,
            "reason": "Changing this field would alter the figure claim, source path, boundary or allowed-value contract rather than record author review.",
            "overwrite_allowed": "no",
        }
        for field in ["figure_id", "preview_file_png", "preview_file_pdf", "core_conclusion", "required_boundary", "current_visual_status", "allowed_values"]
    ]

    command_rows = [
        {"order": 1, "command": "Place returned file in reports\\python_figure_author_review_return_inbox_20260810\\returned_author_review_files", "run_now": "manual_only", "purpose": "Receive author-returned review form."},
        {"order": 2, "command": "py scripts\\build_python_figure_author_review_return_inbox.py", "run_now": "yes", "purpose": "Audit returned file presence and checksums."},
        {"order": 3, "command": "Manually transcribe only author_approval_status and author_comment into python_figure_author_review_form.csv", "run_now": "no", "purpose": "Write canonical review state after a real returned file is inspected."},
        {"order": 4, "command": "py scripts\\build_python_figure_author_review_intake_validator.py", "run_now": "no", "purpose": "Validate allowed values and decide next figure action."},
        {"order": 5, "command": "py scripts\\build_python_figure_author_review_writeback_queue.py", "run_now": "yes", "purpose": "Refresh this queue after inbox or review-form state changes."},
    ]

    qa_rows = [
        {
            "check": "review_rows_mapped",
            "result": "PASS" if len(queue_rows) == 6 else "FAIL",
            "detail": f"queue_rows={len(queue_rows)}",
        },
        {
            "check": "return_inbox_empty_detected",
            "result": "PASS" if return_summary.get("candidate_return_files") == 0 and len(return_files) == 0 else "FAIL",
            "detail": f"candidate_return_files={return_summary.get('candidate_return_files')}; audit_rows={len(return_files)}",
        },
        {
            "check": "writeback_blocked_now",
            "result": "PASS" if all(row["writeback_allowed_now"] == "no" for row in queue_rows) else "FAIL",
            "detail": "all rows blocked until returned file exists and is manually inspected",
        },
        {
            "check": "protected_fields_indexed",
            "result": "PASS" if len(protection_rows) == 7 else "FAIL",
            "detail": f"protected_fields={len(protection_rows)}",
        },
        {
            "check": "final_candidate_still_blocked",
            "result": "PASS" if intake_summary.get("final_candidate_generation_allowed") is False else "FAIL",
            "detail": f"final_candidate_generation_allowed={intake_summary.get('final_candidate_generation_allowed')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "python_figure_author_review_writeback_queue.csv",
        queue_rows,
        ["figure_id", "source_inbox", "candidate_return_files", "target_file", "target_row_key", "editable_fields", "do_not_edit_fields", "allowed_author_approval_status", "after_manual_writeback_validator", "writeback_allowed_now", "reason"],
    )
    write_csv(OUT_DIR / "python_figure_author_review_protected_fields.csv", protection_rows, ["target_file", "protected_field", "reason", "overwrite_allowed"])
    write_csv(OUT_DIR / "python_figure_author_review_writeback_commands.csv", command_rows, ["order", "command", "run_now", "purpose"])
    write_csv(OUT_DIR / "python_figure_author_review_writeback_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Python figure author-review writeback queue report 2026-08-10",
        "",
        "Status: `python_figure_author_review_writeback_queue_ready_blocked_empty_inbox`",
        "",
        f"1. Figure writeback rows: {len(queue_rows)}",
        f"2. Protected fields: {len(protection_rows)}",
        f"3. Candidate returned files: {len(return_files)}",
        f"4. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: writeback targets are mapped, but writeback is blocked because no returned author-review file exists.",
        "",
    ]
    write_text(OUT_DIR / "PYTHON_FIGURE_AUTHOR_REVIEW_WRITEBACK_README.md", "\n".join(report))
    write_text(OUT_DIR / "python_figure_author_review_writeback_report.md", "\n".join(report))

    summary = {
        "package": "python_figure_author_review_writeback_queue_20260810",
        "writeback_rows": len(queue_rows),
        "protected_fields": len(protection_rows),
        "command_rows": len(command_rows),
        "candidate_return_files": len(return_files),
        "writeback_allowed_rows": sum(1 for row in queue_rows if row["writeback_allowed_now"] == "yes"),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "manual_writeback_performed": False,
        "approved_rows": intake_summary.get("approved_rows"),
        "blank_rows": intake_summary.get("blank_rows"),
        "final_candidate_generation_allowed": False,
        "final_figures_ready": False,
        "submission_ready": False,
        "status": "python_figure_author_review_writeback_queue_ready_blocked_empty_inbox",
    }

    section = f"""### 19.02 Python figure author review writeback queue update

Added a writeback queue from the returned figure-review inbox to the canonical figure author-review form.

New directory: `{OUT_DIR}`

New files:
1. `python_figure_author_review_writeback_queue.csv`
2. `python_figure_author_review_protected_fields.csv`
3. `python_figure_author_review_writeback_commands.csv`
4. `python_figure_author_review_writeback_qa.csv`
5. `PYTHON_FIGURE_AUTHOR_REVIEW_WRITEBACK_README.md`
6. `python_figure_author_review_writeback_report.md`
7. `python_figure_author_review_writeback_summary.json`

Current result:
1. writeback_rows = {summary['writeback_rows']}
2. protected_fields = {summary['protected_fields']}
3. candidate_return_files = {summary['candidate_return_files']}
4. writeback_allowed_rows = {summary['writeback_allowed_rows']}
5. manual_writeback_performed = false
6. final_candidate_generation_allowed = false
7. final_figures_ready = false

Boundary:
1. This queue maps possible manual writeback only.
2. It does not edit the canonical review form.
3. It does not generate final figures or close the figure gate."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "python_figure_author_review_writeback_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Python figure author-review writeback queue QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
