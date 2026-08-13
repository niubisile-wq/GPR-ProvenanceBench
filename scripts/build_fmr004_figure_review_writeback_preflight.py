#!/usr/bin/env python3
"""Build a guarded preflight for FMR-004 figure-review writeback."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "fmr004_figure_review_writeback_preflight_20260810"
FMR_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_intake_package_20260810"
REVIEW_PACKET_DIR = BENCH_ROOT / "reports" / "python_figure_author_review_packet_20260810"
REVIEW_INTAKE_DIR = BENCH_ROOT / "reports" / "python_figure_author_review_intake_validator_20260810"
REVIEW_WRITEBACK_DIR = BENCH_ROOT / "reports" / "python_figure_author_review_writeback_queue_20260810"
FINAL_CANDIDATE_DIR = BENCH_ROOT / "reports" / "python_figure_final_candidate_preflight_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


APPROVED_VALUE = "approve_preview_for_final_candidate"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.67 FMR-004 figure review writeback preflight update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/fmr004_figure_review_writeback_preflight_20260810/` to guard future FMR-004 writeback from figure author-review decisions.
- Current `review_rows={summary["review_rows"]}`, `approved_rows={summary["approved_rows"]}`, `blank_rows={summary["blank_rows"]}`, `candidate_return_files={summary["candidate_return_files"]}`.
- Current `fmr004_candidate_rows={summary["fmr004_candidate_rows"]}`, `fmr004_writeback_allowed={str(summary["fmr004_writeback_allowed"]).lower()}`, `real_fmr_template_modified=false`.
- Boundary: all six figure rows must have explicit accepted approvals, writeback queue evidence and final-candidate generation permission before FMR-004 can move from `FILL_AFTER_FIGURE_REVIEW/missing`. This preflight does not write the FMR intake template, render final figures, run guarded recheck or submit.
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

    fmr_rows = read_csv(FMR_DIR / "final_manual_receipt_intake_template.csv")
    review_rows = read_csv(REVIEW_PACKET_DIR / "python_figure_author_review_form.csv")
    packet_summary = read_json(REVIEW_PACKET_DIR / "python_figure_author_review_packet_summary.json")
    intake_summary = read_json(REVIEW_INTAKE_DIR / "python_figure_author_review_intake_summary.json")
    writeback_summary = read_json(REVIEW_WRITEBACK_DIR / "python_figure_author_review_writeback_summary.json")
    final_candidate_summary = read_json(FINAL_CANDIDATE_DIR / "python_figure_final_candidate_preflight_summary.json")

    fmr004_rows = [row for row in fmr_rows if row.get("receipt_id") == "FMR-004"]
    required_review_rows = int(packet_summary.get("author_review_rows", 0) or 0)
    approved_rows = int(intake_summary.get("approved_rows", 0) or 0)
    revision_rows = int(intake_summary.get("revision_rows", 0) or 0)
    rejected_rows = int(intake_summary.get("rejected_rows", 0) or 0)
    blank_rows = int(intake_summary.get("blank_rows", 0) or 0)
    invalid_rows = int(intake_summary.get("invalid_rows", 0) or 0)
    candidate_return_files = int(writeback_summary.get("candidate_return_files", 0) or 0)
    writeback_allowed_rows = int(writeback_summary.get("writeback_allowed_rows", 0) or 0)
    manual_writeback_performed = writeback_summary.get("manual_writeback_performed") is True
    intake_final_candidate_allowed = intake_summary.get("final_candidate_generation_allowed") is True
    final_candidate_allowed = final_candidate_summary.get("final_candidate_generation_allowed") is True
    final_figures_ready = final_candidate_summary.get("final_figures_ready") is True

    all_approved = required_review_rows == 6 and approved_rows == 6 and blank_rows == 0 and invalid_rows == 0
    fmr004_writeback_allowed = (
        len(fmr004_rows) == 1
        and all_approved
        and candidate_return_files > 0
        and writeback_allowed_rows == 6
        and manual_writeback_performed
        and intake_final_candidate_allowed
        and final_candidate_allowed
        and final_figures_ready
    )

    review_status_rows = []
    for row in review_rows:
        approval = row.get("author_approval_status", "").strip()
        approved_now = approval == APPROVED_VALUE
        review_status_rows.append(
            {
                "figure_id": row.get("figure_id", ""),
                "author_review_required": row.get("author_review_required", ""),
                "author_approval_status": approval,
                "approved_now": "yes" if approved_now else "no",
                "author_comment": row.get("author_comment", ""),
                "blocking_reason": "" if approved_now else "author_approval_status is not approve_preview_for_final_candidate",
            }
        )

    candidate_rows = []
    if fmr004_writeback_allowed:
        fmr004 = fmr004_rows[0]
        candidate_rows.append(
            {
                "receipt_id": "FMR-004",
                "target_or_route": fmr004.get("target_or_route", ""),
                "current_status_after_writeback": "complete",
                "value_to_fill_after_manual_action": "All six figure author-review rows approved and final figure candidates ready.",
                "first_validator": fmr004.get("first_validator", ""),
                "writeback_allowed": "yes",
            }
        )

    guard_rows = [
        {
            "guard": "single_FMR_004_row_present",
            "current": len(fmr004_rows),
            "required": 1,
            "passes_now": "yes" if len(fmr004_rows) == 1 else "no",
        },
        {
            "guard": "six_required_figure_review_rows_present",
            "current": required_review_rows,
            "required": 6,
            "passes_now": "yes" if required_review_rows == 6 else "no",
        },
        {
            "guard": "all_figures_explicitly_approved",
            "current": f"approved={approved_rows}; blank={blank_rows}; invalid={invalid_rows}; revision={revision_rows}; rejected={rejected_rows}",
            "required": "approved=6; blank=0; invalid=0; revision=0; rejected=0",
            "passes_now": "yes" if all_approved and revision_rows == 0 and rejected_rows == 0 else "no",
        },
        {
            "guard": "writeback_queue_has_real_return_evidence",
            "current": f"candidate_return_files={candidate_return_files}; writeback_allowed_rows={writeback_allowed_rows}; manual_writeback_performed={manual_writeback_performed}",
            "required": "candidate_return_files>0; writeback_allowed_rows=6; manual_writeback_performed=true",
            "passes_now": "yes" if candidate_return_files > 0 and writeback_allowed_rows == 6 and manual_writeback_performed else "no",
        },
        {
            "guard": "final_candidate_generation_allowed_and_ready",
            "current": f"intake_allowed={intake_final_candidate_allowed}; final_candidate_allowed={final_candidate_allowed}; final_figures_ready={final_figures_ready}",
            "required": "all true",
            "passes_now": "yes" if intake_final_candidate_allowed and final_candidate_allowed and final_figures_ready else "no",
        },
    ]

    blocker_rows = []
    if not all_approved:
        blocker_rows.append(
            {
                "blocker": "figure author-review approvals missing",
                "evidence": f"approved_rows={approved_rows}; blank_rows={blank_rows}; invalid_rows={invalid_rows}",
                "blocks": "FMR-004 writeback candidate and final figure candidate generation",
            }
        )
    if candidate_return_files == 0 or writeback_allowed_rows != 6 or not manual_writeback_performed:
        blocker_rows.append(
            {
                "blocker": "figure review writeback evidence not complete",
                "evidence": f"candidate_return_files={candidate_return_files}; writeback_allowed_rows={writeback_allowed_rows}; manual_writeback_performed={manual_writeback_performed}",
                "blocks": "FMR-004 writeback candidate",
            }
        )
    if not final_candidate_allowed or not final_figures_ready:
        blocker_rows.append(
            {
                "blocker": "final figure candidate gate not ready",
                "evidence": f"final_candidate_generation_allowed={final_candidate_allowed}; final_figures_ready={final_figures_ready}",
                "blocks": "FMR-004 writeback candidate and final manuscript figure assembly",
            }
        )

    qa_rows = [
        {
            "check": "FMR-004 row imported",
            "result": "PASS" if len(fmr004_rows) == 1 else "FAIL",
            "detail": f"fmr004_rows={len(fmr004_rows)}",
        },
        {
            "check": "six figure review rows imported",
            "result": "PASS" if len(review_rows) == 6 else "FAIL",
            "detail": f"review_rows={len(review_rows)}",
        },
        {
            "check": "blank approvals do not unlock writeback",
            "result": "PASS" if approved_rows == 6 or not fmr004_writeback_allowed else "FAIL",
            "detail": f"approved_rows={approved_rows}; blank_rows={blank_rows}; fmr004_writeback_allowed={fmr004_writeback_allowed}",
        },
        {
            "check": "candidate generation follows figure-review gates",
            "result": "PASS" if len(candidate_rows) == (1 if fmr004_writeback_allowed else 0) else "FAIL",
            "detail": f"candidate_rows={len(candidate_rows)}; fmr004_writeback_allowed={fmr004_writeback_allowed}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "guarded_recheck_allowed=false; portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "fmr004_figure_review_writeback_preflight_20260810",
        "fmr004_rows": len(fmr004_rows),
        "review_rows": len(review_rows),
        "required_review_rows": required_review_rows,
        "approved_rows": approved_rows,
        "revision_rows": revision_rows,
        "rejected_rows": rejected_rows,
        "blank_rows": blank_rows,
        "invalid_rows": invalid_rows,
        "candidate_return_files": candidate_return_files,
        "writeback_allowed_rows": writeback_allowed_rows,
        "manual_writeback_performed": manual_writeback_performed,
        "final_candidate_generation_allowed": final_candidate_allowed,
        "final_figures_ready": final_figures_ready,
        "fmr004_candidate_rows": len(candidate_rows),
        "fmr004_writeback_allowed": fmr004_writeback_allowed,
        "real_fmr_template_modified": False,
        "guarded_recheck_allowed": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "blocker_rows": len(blocker_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": (
            "fmr004_figure_review_writeback_preflight_candidate_ready"
            if fmr004_writeback_allowed
            else "fmr004_figure_review_writeback_preflight_ready_blocked_waiting_figure_approvals"
        ),
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "fmr004_figure_review_status.csv",
        ["figure_id", "author_review_required", "author_approval_status", "approved_now", "author_comment", "blocking_reason"],
        review_status_rows,
    )
    write_csv(
        OUT_DIR / "fmr004_figure_review_writeback_guard_matrix.csv",
        ["guard", "current", "required", "passes_now"],
        guard_rows,
    )
    write_csv(
        OUT_DIR / "fmr004_figure_review_writeback_candidates.csv",
        [
            "receipt_id",
            "target_or_route",
            "current_status_after_writeback",
            "value_to_fill_after_manual_action",
            "first_validator",
            "writeback_allowed",
        ],
        candidate_rows,
    )
    write_csv(
        OUT_DIR / "fmr004_figure_review_writeback_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "fmr004_figure_review_writeback_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    report = f"""# FMR-004 Figure Review Writeback Preflight

Status: `{summary["status"]}`

Current result:

1. FMR-004 rows: {summary["fmr004_rows"]}
2. Review rows: {summary["review_rows"]}
3. Approved rows: {summary["approved_rows"]}
4. Blank rows: {summary["blank_rows"]}
5. Candidate return files: {summary["candidate_return_files"]}
6. Writeback allowed rows: {summary["writeback_allowed_rows"]}
7. Final candidate generation allowed: {str(summary["final_candidate_generation_allowed"]).lower()}
8. Final figures ready: {str(summary["final_figures_ready"]).lower()}
9. FMR-004 candidate rows: {summary["fmr004_candidate_rows"]}
10. FMR-004 writeback allowed: {str(summary["fmr004_writeback_allowed"]).lower()}
11. Real FMR template modified: false
12. Guarded recheck allowed: false
13. Portal upload allowed: false
14. Submission ready: false

Boundary: FMR-004 remains blocked until all six figure author-review rows have
explicit accepted approvals, writeback evidence is complete, final figure
candidate generation is allowed and final figures are ready. This preflight does
not write the FMR intake template, render final figures, run guarded recheck,
upload portal files or mark the manuscript submitted.
"""
    write_text(OUT_DIR / "FMR004_FIGURE_REVIEW_WRITEBACK_PREFLIGHT_README.md", report)
    write_text(OUT_DIR / "fmr004_figure_review_writeback_preflight_report.md", report)
    write_text(
        OUT_DIR / "fmr004_figure_review_writeback_preflight_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
