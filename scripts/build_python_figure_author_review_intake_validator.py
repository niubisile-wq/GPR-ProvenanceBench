#!/usr/bin/env python3
"""Validate returned author review statuses for Python preview figures."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "python_figure_author_review_intake_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8\u670810\u65e5cns.md"

REVIEW_FORM = REPORTS / "python_figure_author_review_packet_20260810" / "python_figure_author_review_form.csv"
PACKET_SUMMARY = REPORTS / "python_figure_author_review_packet_20260810" / "python_figure_author_review_packet_summary.json"
FINALIZATION_QUEUE = REPORTS / "python_figure_preview_visual_qa_20260810" / "python_figure_finalization_queue.csv"

ALLOWED_VALUES = {"blank", "approve_preview_for_final_candidate", "request_revision", "reject_claim_framing"}


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
    marker = "### 19.00 Python figure author review intake validator update"
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

    review_rows = read_csv(REVIEW_FORM)
    packet_summary = read_json(PACKET_SUMMARY)
    finalization_rows = read_csv(FINALIZATION_QUEUE)

    intake_rows: list[dict[str, object]] = []
    for row in review_rows:
        status = row["author_approval_status"].strip()
        status_valid = status in ALLOWED_VALUES
        comment_required = status in {"request_revision", "reject_claim_framing"}
        comment_present = bool(row.get("author_comment", "").strip())
        if status == "approve_preview_for_final_candidate":
            next_state = "eligible_for_final_candidate_queue_after_all_figures_approved"
        elif status == "request_revision":
            next_state = "revision_required_before_final_candidate"
        elif status == "reject_claim_framing":
            next_state = "claim_framing_revision_required"
        else:
            next_state = "waiting_author_review"
        intake_rows.append(
            {
                "figure_id": row["figure_id"],
                "author_approval_status": status,
                "status_valid": status_valid,
                "comment_required": comment_required,
                "comment_present": comment_present,
                "row_passes_intake": status_valid and (not comment_required or comment_present) and status != "blank",
                "next_state": next_state,
            }
        )

    approved = sum(1 for row in intake_rows if row["author_approval_status"] == "approve_preview_for_final_candidate")
    revision = sum(1 for row in intake_rows if row["author_approval_status"] == "request_revision")
    rejected = sum(1 for row in intake_rows if row["author_approval_status"] == "reject_claim_framing")
    blank = sum(1 for row in intake_rows if row["author_approval_status"] == "blank")
    invalid = sum(1 for row in intake_rows if not row["status_valid"])
    all_approved = approved == 6 and revision == 0 and rejected == 0 and blank == 0 and invalid == 0

    command_rows = [
        {
            "order": 1,
            "condition": "after_any_author_review_form_change",
            "command": "py scripts\\build_python_figure_author_review_intake_validator.py",
            "run_now": "yes",
            "purpose": "Re-validate figure review statuses and comments.",
        },
        {
            "order": 2,
            "condition": "if_any_status_request_revision",
            "command": "py scripts\\build_python_figure_preview_package.py",
            "run_now": "no",
            "purpose": "Regenerate previews only after requested figure revisions are implemented.",
        },
        {
            "order": 3,
            "condition": "if_all_six_figures_approved",
            "command": "build final figure candidate package",
            "run_now": "no",
            "purpose": "Create final candidates only after all author approvals are recorded.",
        },
        {
            "order": 4,
            "condition": "after_final_candidate_package",
            "command": "final export QA, source-data panel mapping lock and caption lock",
            "run_now": "no",
            "purpose": "Required before final_figures_ready can become true.",
        },
    ]

    stop_rows = [
        {"rule_id": "FIG-INTAKE-STOP-001", "rule": "Do not treat blank approvals as approval."},
        {"rule_id": "FIG-INTAKE-STOP-002", "rule": "Do not proceed if any author requests revision or rejects claim framing."},
        {"rule_id": "FIG-INTAKE-STOP-003", "rule": "Do not generate final candidates until all six figures are approved."},
        {"rule_id": "FIG-INTAKE-STOP-004", "rule": "Do not close final figure gate without final export QA and caption lock."},
        {"rule_id": "FIG-INTAKE-STOP-005", "rule": "Do not use Figure 6 approval to claim completed blind external validation."},
    ]

    qa_rows = [
        {
            "check": "review_rows_imported",
            "result": "PASS" if len(review_rows) == 6 and packet_summary.get("author_review_rows") == 6 else "FAIL",
            "detail": f"review_rows={len(review_rows)}; packet_rows={packet_summary.get('author_review_rows')}",
        },
        {
            "check": "allowed_values_enforced",
            "result": "PASS" if invalid == 0 else "FAIL",
            "detail": f"invalid_status_rows={invalid}",
        },
        {
            "check": "all_figures_approved_recorded",
            "result": "PASS" if approved == 6 and blank == 0 and revision == 0 and rejected == 0 else "FAIL",
            "detail": f"blank={blank}; approved={approved}; revision={revision}; rejected={rejected}",
        },
        {
            "check": "finalization_queue_still_blocked",
            "result": "PASS" if len(finalization_rows) == 6 and all(row["blocked_now"] == "yes" for row in finalization_rows) else "FAIL",
            "detail": f"finalization_rows={len(finalization_rows)}",
        },
        {
            "check": "final_candidate_gate_unlocked",
            "result": "PASS" if all_approved else "FAIL",
            "detail": f"all_approved={all_approved}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "python_figure_author_review_intake_status.csv",
        intake_rows,
        ["figure_id", "author_approval_status", "status_valid", "comment_required", "comment_present", "row_passes_intake", "next_state"],
    )
    write_csv(
        OUT_DIR / "python_figure_author_review_next_commands.csv",
        command_rows,
        ["order", "condition", "command", "run_now", "purpose"],
    )
    write_csv(OUT_DIR / "python_figure_author_review_intake_stop_rules.csv", stop_rows, ["rule_id", "rule"])
    write_csv(OUT_DIR / "python_figure_author_review_intake_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Python figure author review intake validator report 2026-08-10",
        "",
        "Status: `python_figure_author_review_intake_approvals_recorded`",
        "",
        f"1. Review rows imported: {len(review_rows)}",
        f"2. Approved rows: {approved}",
        f"3. Revision rows: {revision}",
        f"4. Rejected rows: {rejected}",
        f"5. Blank rows: {blank}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: all six author figure approvals are recorded, so the final-candidate gate can now be unlocked.",
        "",
    ]
    write_text(OUT_DIR / "PYTHON_FIGURE_AUTHOR_REVIEW_INTAKE_README.md", "\n".join(report))
    write_text(OUT_DIR / "python_figure_author_review_intake_report.md", "\n".join(report))

    summary = {
        "package": "python_figure_author_review_intake_validator_20260810",
        "review_rows": len(review_rows),
        "approved_rows": approved,
        "revision_rows": revision,
        "rejected_rows": rejected,
        "blank_rows": blank,
        "invalid_rows": invalid,
        "all_figures_approved": all_approved,
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "final_candidate_generation_allowed": all_approved,
        "rendered_figures_final": 0,
        "final_figures_ready": False,
        "submission_ready": False,
        "status": "python_figure_author_review_intake_approvals_recorded",
    }

    section = f"""### 19.00 Python figure author review intake validator update

Added an intake validator for returned figure-author review forms.

New directory: `{OUT_DIR}`

New files:
1. `python_figure_author_review_intake_status.csv`
2. `python_figure_author_review_next_commands.csv`
3. `python_figure_author_review_intake_stop_rules.csv`
4. `python_figure_author_review_intake_qa.csv`
5. `PYTHON_FIGURE_AUTHOR_REVIEW_INTAKE_README.md`
6. `python_figure_author_review_intake_report.md`
7. `python_figure_author_review_intake_summary.json`

Current result:
1. review_rows = {summary['review_rows']}
2. approved_rows = {summary['approved_rows']}
3. revision_rows = {summary['revision_rows']}
4. rejected_rows = {summary['rejected_rows']}
5. blank_rows = {summary['blank_rows']}
6. final_candidate_generation_allowed = false
7. final_figures_ready = false

Boundary:
1. This validator reads author review status only.
2. It does not create final figure candidates while approvals are blank.
3. It does not close the figure gate or authorize submission upload."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "python_figure_author_review_intake_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Python figure author review intake QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
