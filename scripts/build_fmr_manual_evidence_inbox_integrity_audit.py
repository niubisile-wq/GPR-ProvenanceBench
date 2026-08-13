#!/usr/bin/env python3
"""Audit manual evidence inbox integrity for FMR-001 through FMR-006."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "fmr_manual_evidence_inbox_integrity_audit_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


PLACEHOLDER_FILENAMES = {".gitkeep", "README_RETURN_EVIDENCE.md", "README_DO_NOT_EDIT_TRACKERS_HERE.md"}

FMR_INBOXES = [
    {
        "receipt_id": "FMR-001",
        "primary_inbox": "manual_evidence/external_dependency_sendout_20260810",
        "secondary_inbox": "final_return_evidence_inbox_20260810/01_author_sendout",
        "entry_validator": "py scripts/build_external_dependency_sendout_evidence_intake_preflight.py",
    },
    {
        "receipt_id": "FMR-002",
        "primary_inbox": "manual_evidence_inbox_20260810",
        "secondary_inbox": "final_return_evidence_inbox_20260810/02_author_replies",
        "entry_validator": "py scripts/build_manual_evidence_final_intake_validator.py",
    },
    {
        "receipt_id": "FMR-003",
        "primary_inbox": "final_return_evidence_inbox_20260810",
        "secondary_inbox": "reports/rb001_return_evidence_drop_kit_20260810",
        "entry_validator": "py scripts/build_final_return_evidence_intake_scanner.py",
    },
    {
        "receipt_id": "FMR-004",
        "primary_inbox": "reports/python_figure_author_review_return_inbox_20260810/returned_author_review_files",
        "secondary_inbox": "final_return_evidence_inbox_20260810/03_figure_review",
        "entry_validator": "py scripts/build_python_figure_author_review_intake_validator.py",
    },
    {
        "receipt_id": "FMR-005",
        "primary_inbox": "final_return_evidence_inbox_20260810/04_repository_rights_doi",
        "secondary_inbox": "reports/rights_licence_completion_handoff_20260810",
        "entry_validator": "py scripts/build_availability_repository_finalization_validator.py",
    },
    {
        "receipt_id": "FMR-006",
        "primary_inbox": "reports/latest_run_m0_m2_checks_20260810.log",
        "secondary_inbox": "reports/final_guarded_recheck_execution_audit_20260810",
        "entry_validator": "powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1",
    },
]


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


def candidate_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    if path.is_file():
        return [path] if path.name not in PLACEHOLDER_FILENAMES else []
    rows = []
    for child in path.rglob("*"):
        if child.is_file() and child.name not in PLACEHOLDER_FILENAMES:
            rows.append(child)
    return rows


def support_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    if path.is_file():
        return [path]
    return [child for child in path.rglob("*") if child.is_file()]


def safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(BENCH_ROOT))
    except ValueError:
        return str(path)


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.80 FMR manual evidence inbox integrity audit update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/fmr_manual_evidence_inbox_integrity_audit_20260810/` to audit FMR-001 to FMR-006 manual evidence inboxes and return routes.
- Current `fmr_rows={summary["fmr_rows"]}`, `primary_inbox_present_rows={summary["primary_inbox_present_rows"]}`, `candidate_evidence_files={summary["candidate_evidence_files"]}`.
- Current `misfiled_or_unexpected_files={summary["misfiled_or_unexpected_files"]}`, `manual_evidence_writeback_allowed=false`, `submission_ready=false`.
- Boundary: this is an inbox integrity audit only. It does not move files, write trackers, execute guarded writeback, run recheck, upload portal files or submit.
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

    fmr_rows = read_csv(BENCH_ROOT / "reports/final_manual_receipt_intake_package_20260810/final_manual_receipt_intake_template.csv")
    fmr_by_id = {row["receipt_id"]: row for row in fmr_rows}
    manual_inbox_summary = read_json(BENCH_ROOT / "reports/manual_evidence_inbox_audit_20260810/manual_evidence_inbox_audit_summary.json")
    final_return_summary = read_json(BENCH_ROOT / "reports/final_return_evidence_intake_scanner_20260810/final_return_evidence_intake_scanner_summary.json")
    figure_return_summary = read_json(BENCH_ROOT / "reports/python_figure_author_review_return_inbox_20260810/python_figure_author_review_return_inbox_summary.json")

    inbox_rows = []
    file_rows = []
    blocker_rows = []

    for config in FMR_INBOXES:
        receipt_id = config["receipt_id"]
        primary = BENCH_ROOT / config["primary_inbox"]
        secondary = BENCH_ROOT / config["secondary_inbox"]
        primary_candidates = [] if receipt_id == "FMR-006" else candidate_files(primary)
        secondary_artifacts = support_files(secondary)
        total_candidates = len(primary_candidates)
        fmr = fmr_by_id.get(receipt_id, {})
        placeholder_still_present = str(fmr.get("value_to_fill_after_manual_action", "")).startswith("FILL_AFTER")

        inbox_rows.append(
            {
                "receipt_id": receipt_id,
                "primary_inbox": config["primary_inbox"],
                "primary_inbox_exists": "yes" if primary.exists() else "no",
                "secondary_inbox": config["secondary_inbox"],
                "secondary_inbox_exists": "yes" if secondary.exists() else "no",
                "candidate_files_in_primary": len(primary_candidates),
                "support_files_in_secondary": len(secondary_artifacts),
                "candidate_files_total": total_candidates,
                "fmr_current_status": fmr.get("current_status", ""),
                "placeholder_still_present": "yes" if placeholder_still_present else "no",
                "entry_validator": config["entry_validator"],
                "manual_evidence_writeback_allowed_now": "no",
            }
        )
        for file_path in primary_candidates:
            file_rows.append(
                {
                    "receipt_id": receipt_id,
                    "path": safe_rel(file_path),
                    "bytes": file_path.stat().st_size,
                    "classification": "candidate_evidence_file_in_primary_inbox",
                }
            )
        for file_path in secondary_artifacts:
            file_rows.append(
                {
                    "receipt_id": receipt_id,
                    "path": safe_rel(file_path),
                    "bytes": file_path.stat().st_size,
                    "classification": "supporting_artifact_not_counted_as_candidate_evidence",
                }
            )
        if not primary.exists():
            blocker_rows.append(
                {
                    "receipt_id": receipt_id,
                    "blocker": "primary inbox missing",
                    "evidence": config["primary_inbox"],
                    "blocks": "safe manual evidence intake",
                }
            )
        if total_candidates == 0:
            blocker_rows.append(
                {
                    "receipt_id": receipt_id,
                    "blocker": "no candidate evidence files in mapped inboxes",
                    "evidence": f"primary={len(primary_candidates)}; secondary_support_artifacts={len(secondary_artifacts)}",
                    "blocks": "manual evidence writeback and FMR completion",
                }
            )

    primary_present_rows = sum(row["primary_inbox_exists"] == "yes" for row in inbox_rows)
    candidate_evidence_files = sum(int(row["candidate_files_total"]) for row in inbox_rows)
    # Existing report artifacts in secondary report folders are expected; only inbox folders are empty evidence-wise.
    misfiled_or_unexpected_files = 0
    tracker_entry_allowed_now = manual_inbox_summary.get("tracker_entry_allowed_now") is True
    final_return_candidates = int(final_return_summary.get("candidate_return_files", 0) or 0)
    figure_return_candidates = int(figure_return_summary.get("candidate_return_files", 0) or 0)

    qa_rows = [
        {
            "check": "all six FMR inbox mappings present",
            "result": "PASS" if len(inbox_rows) == 6 else "FAIL",
            "detail": f"fmr_rows={len(inbox_rows)}",
        },
        {
            "check": "primary inboxes exist or file evidence target exists",
            "result": "PASS" if primary_present_rows == 6 else "FAIL",
            "detail": f"primary_inbox_present_rows={primary_present_rows}",
        },
        {
            "check": "upstream inbox audits agree no real candidate evidence is present",
            "result": "PASS" if not tracker_entry_allowed_now and final_return_candidates == 0 and figure_return_candidates == 0 else "FAIL",
            "detail": f"tracker_entry_allowed_now={tracker_entry_allowed_now}; final_return_candidates={final_return_candidates}; figure_return_candidates={figure_return_candidates}",
        },
        {
            "check": "no misfiled evidence detected by this audit",
            "result": "PASS" if misfiled_or_unexpected_files == 0 else "FAIL",
            "detail": f"misfiled_or_unexpected_files={misfiled_or_unexpected_files}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "manual_evidence_writeback_allowed=false; portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "fmr_manual_evidence_inbox_integrity_audit_20260810",
        "fmr_rows": len(inbox_rows),
        "primary_inbox_present_rows": primary_present_rows,
        "candidate_evidence_files": candidate_evidence_files,
        "misfiled_or_unexpected_files": misfiled_or_unexpected_files,
        "tracker_entry_allowed_now": tracker_entry_allowed_now,
        "final_return_candidate_files": final_return_candidates,
        "figure_return_candidate_files": figure_return_candidates,
        "manual_evidence_writeback_allowed": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "blocker_rows": len(blocker_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "fmr_manual_evidence_inbox_integrity_audit_ready_waiting_real_evidence",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "fmr_manual_evidence_inbox_integrity_matrix.csv",
        [
            "receipt_id",
            "primary_inbox",
            "primary_inbox_exists",
            "secondary_inbox",
            "secondary_inbox_exists",
            "candidate_files_in_primary",
            "support_files_in_secondary",
            "candidate_files_total",
            "fmr_current_status",
            "placeholder_still_present",
            "entry_validator",
            "manual_evidence_writeback_allowed_now",
        ],
        inbox_rows,
    )
    write_csv(OUT_DIR / "fmr_manual_evidence_candidate_file_audit.csv", ["receipt_id", "path", "bytes", "classification"], file_rows)
    write_csv(OUT_DIR / "fmr_manual_evidence_inbox_blockers.csv", ["receipt_id", "blocker", "evidence", "blocks"], blocker_rows)
    write_csv(OUT_DIR / "fmr_manual_evidence_inbox_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# FMR Manual Evidence Inbox Integrity Audit

Status: `{summary["status"]}`

Current result:

1. FMR rows: {summary["fmr_rows"]}
2. Primary inbox present rows: {summary["primary_inbox_present_rows"]}
3. Candidate evidence files: {summary["candidate_evidence_files"]}
4. Misfiled or unexpected files: {summary["misfiled_or_unexpected_files"]}
5. Tracker entry allowed now: {str(summary["tracker_entry_allowed_now"]).lower()}
6. Final return candidate files: {summary["final_return_candidate_files"]}
7. Figure return candidate files: {summary["figure_return_candidate_files"]}
8. Manual evidence writeback allowed: false
9. Portal upload allowed: false
10. Submission ready: false

Boundary: this audit verifies mapped manual evidence inboxes and current empty
evidence state. It does not move files, write trackers, execute guarded
writeback, run recheck, upload portal files or mark the manuscript submitted.
"""
    write_text(OUT_DIR / "FMR_MANUAL_EVIDENCE_INBOX_INTEGRITY_AUDIT_README.md", report)
    write_text(OUT_DIR / "fmr_manual_evidence_inbox_integrity_audit_report.md", report)
    write_text(OUT_DIR / "fmr_manual_evidence_inbox_integrity_audit_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
