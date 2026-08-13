#!/usr/bin/env python3
"""Build a manual execution receipt template for RB-001 evidence intake.

The receipt is the operator-facing proof that real files were copied into the
canonical inbox, hashes were recorded and the diagnostic-only runner was run.
This script creates and audits the receipt template only; it does not fill the
receipt, create evidence, write protected targets or close gates.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "rb001_manual_execution_receipt_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_RECEIPT = Path.home() / "Desktop" / "RB001_manual_execution_receipt_20260810.csv"
DESKTOP_GUIDE = Path.home() / "Desktop" / "RB001_manual_execution_receipt_guide_20260810.md"

DROP_LOCATIONS = BENCH_ROOT / "reports" / "rb001_return_evidence_drop_kit_20260810" / "rb001_return_evidence_drop_locations.csv"
DIAGNOSTIC_SUMMARY = BENCH_ROOT / "reports" / "rb001_diagnostic_only_runner_20260810" / "rb001_diagnostic_only_runner_summary.json"
SCANNER_SUMMARY = BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_intake_scanner_summary.json"
HASH_RECON_SUMMARY = BENCH_ROOT / "reports" / "rb001_return_evidence_hash_reconciliation_20260810" / "rb001_return_evidence_hash_reconciliation_summary.json"

PLACEHOLDERS = {"", "FILL_AFTER_MANUAL_ACTION", "FILL_AFTER_DROP", "FILL_AFTER_HASH", "YYYY-MM-DD", "pending"}


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
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def row_complete(row: dict[str, str]) -> bool:
    required = [
        "operator_name",
        "action_date",
        "route_id",
        "relative_folder",
        "file_name",
        "sha256",
        "source_person_or_system",
        "diagnostic_runner_returncode",
        "operator_attestation",
    ]
    return all(row.get(field, "").strip() not in PLACEHOLDERS for field in required)


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.28 RB-001 manual execution receipt update"
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
    locations = read_csv(DROP_LOCATIONS)
    diagnostic = read_json(DIAGNOSTIC_SUMMARY)
    scanner = read_json(SCANNER_SUMMARY)
    hash_recon = read_json(HASH_RECON_SUMMARY)

    receipt_rows = [
        {
            "receipt_id": f"RB001-REC-{idx:03d}",
            "operator_name": "FILL_AFTER_MANUAL_ACTION",
            "action_date": "YYYY-MM-DD",
            "route_id": row["route_id"],
            "relative_folder": row["relative_folder"],
            "file_name": "FILL_AFTER_DROP",
            "sha256": "FILL_AFTER_HASH",
            "source_person_or_system": "FILL_AFTER_DROP",
            "diagnostic_runner_returncode": "pending",
            "diagnostic_runner_summary": "reports/rb001_diagnostic_only_runner_20260810/rb001_diagnostic_only_runner_summary.json",
            "operator_attestation": "FILL_AFTER_MANUAL_ACTION",
            "writeback_allowed_by_this_receipt": "no",
        }
        for idx, row in enumerate(locations, start=1)
    ]

    completed_rows = [row for row in receipt_rows if row_complete(row)]
    incomplete_rows = [
        {
            "receipt_id": row["receipt_id"],
            "route_id": row["route_id"],
            "relative_folder": row["relative_folder"],
            "reason": "manual receipt row contains placeholders and is not execution evidence",
        }
        for row in receipt_rows
        if not row_complete(row)
    ]

    acceptance_rows = [
        {
            "criterion": "real_file_copied",
            "required_value": "file_name is real and exists in relative_folder",
            "current_status": "not_met",
            "evidence": f"candidate_return_files={scanner.get('candidate_return_files')}",
        },
        {
            "criterion": "hash_recorded",
            "required_value": "sha256 is filled and matches scanner manifest",
            "current_status": "not_met",
            "evidence": f"reconciled_rows={hash_recon.get('reconciled_rows')}",
        },
        {
            "criterion": "source_recorded",
            "required_value": "source_person_or_system is filled",
            "current_status": "not_met",
            "evidence": f"filled_register_rows={hash_recon.get('filled_register_rows')}",
        },
        {
            "criterion": "diagnostic_runner_completed",
            "required_value": "diagnostic runner returncode is 0 after file drop",
            "current_status": "template_only",
            "evidence": f"latest_runner_returncode={diagnostic.get('runner_returncode')}",
        },
        {
            "criterion": "no_writeback_claim",
            "required_value": "receipt never grants writeback by itself",
            "current_status": "met",
            "evidence": "writeback_allowed_by_this_receipt=no",
        },
    ]

    qa_rows = [
        {"check": "receipt_rows_match_routes", "result": "PASS" if len(receipt_rows) == len(locations) == 7 else "FAIL", "detail": f"receipt_rows={len(receipt_rows)}; route_rows={len(locations)}"},
        {"check": "template_not_misread_as_completed_execution", "result": "PASS" if len(completed_rows) == 0 else "FAIL", "detail": f"completed_rows={len(completed_rows)}"},
        {"check": "all_incomplete_rows_explained", "result": "PASS" if len(incomplete_rows) == 7 else "FAIL", "detail": f"incomplete_rows={len(incomplete_rows)}"},
        {"check": "blocked_state_preserved", "result": "PASS" if scanner.get("candidate_return_files") == 0 and hash_recon.get("writeback_allowed_rows") == 0 else "FAIL", "detail": f"candidate_return_files={scanner.get('candidate_return_files')}; writeback_allowed_rows={hash_recon.get('writeback_allowed_rows')}"},
        {"check": "desktop_receipt_created", "result": "PASS", "detail": "Desktop/RB001_manual_execution_receipt_20260810.csv"},
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    receipt_fields = [
        "receipt_id",
        "operator_name",
        "action_date",
        "route_id",
        "relative_folder",
        "file_name",
        "sha256",
        "source_person_or_system",
        "diagnostic_runner_returncode",
        "diagnostic_runner_summary",
        "operator_attestation",
        "writeback_allowed_by_this_receipt",
    ]
    write_csv(OUT_DIR / "rb001_manual_execution_receipt_template.csv", receipt_rows, receipt_fields)
    write_csv(OUT_DIR / "rb001_manual_execution_receipt_incomplete_rows.csv", incomplete_rows, ["receipt_id", "route_id", "relative_folder", "reason"])
    write_csv(OUT_DIR / "rb001_manual_execution_receipt_acceptance_criteria.csv", acceptance_rows, ["criterion", "required_value", "current_status", "evidence"])
    write_csv(OUT_DIR / "rb001_manual_execution_receipt_qa.csv", qa_rows, ["check", "result", "detail"])
    shutil.copy2(OUT_DIR / "rb001_manual_execution_receipt_template.csv", DESKTOP_RECEIPT)

    guide = [
        "# RB-001 manual execution receipt guide 2026-08-10",
        "",
        "Fill `RB001_manual_execution_receipt_20260810.csv` only after real returned files have been copied into `final_return_evidence_inbox_20260810`.",
        "",
        "Required sequence:",
        "",
        "1. Copy real returned files into the matching route folder.",
        "2. Compute SHA256 for each copied file.",
        "3. Fill the receipt row for that route.",
        "4. Run `reports/rb001_diagnostic_only_runner_20260810/run_rb001_diagnostic_only.ps1`.",
        "5. Record the diagnostic runner return code.",
        "6. Do not treat the receipt as writeback permission.",
        "",
        "Current status: template only; no completed receipt rows exist.",
        "",
    ]
    write_text(OUT_DIR / "RB001_MANUAL_EXECUTION_RECEIPT_GUIDE.md", "\n".join(guide))
    shutil.copy2(OUT_DIR / "RB001_MANUAL_EXECUTION_RECEIPT_GUIDE.md", DESKTOP_GUIDE)

    summary = {
        "package": "rb001_manual_execution_receipt_20260810",
        "receipt_template_rows": len(receipt_rows),
        "completed_receipt_rows": len(completed_rows),
        "incomplete_receipt_rows": len(incomplete_rows),
        "acceptance_criteria_rows": len(acceptance_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "candidate_return_files": scanner.get("candidate_return_files"),
        "filled_register_rows": hash_recon.get("filled_register_rows"),
        "reconciled_rows": hash_recon.get("reconciled_rows"),
        "writeback_allowed_rows": hash_recon.get("writeback_allowed_rows"),
        "submission_ready": False,
        "desktop_receipt": str(DESKTOP_RECEIPT),
        "desktop_guide": str(DESKTOP_GUIDE),
        "status": "rb001_manual_execution_receipt_template_ready_not_filled",
    }

    section = f"""### 19.28 RB-001 manual execution receipt update

Added an operator receipt template for the manual RB-001 evidence drop action. The receipt records who copied real returned files, when, into which route folder, with which SHA256, and whether the diagnostic-only runner returned zero.

New directory: `{OUT_DIR}`

Desktop receipt: `{DESKTOP_RECEIPT}`

Desktop guide: `{DESKTOP_GUIDE}`

Current result:
1. receipt_template_rows = {summary['receipt_template_rows']}
2. completed_receipt_rows = {summary['completed_receipt_rows']}
3. incomplete_receipt_rows = {summary['incomplete_receipt_rows']}
4. acceptance_criteria_rows = {summary['acceptance_criteria_rows']}
5. candidate_return_files = {summary['candidate_return_files']}
6. filled_register_rows = {summary['filled_register_rows']}
7. reconciled_rows = {summary['reconciled_rows']}
8. writeback_allowed_rows = {summary['writeback_allowed_rows']}
9. submission_ready = false

Boundary:
1. This receipt is a manual execution evidence template only.
2. It does not create returned files or fill source/hash fields.
3. It does not grant writeback permission, close gates, upload files or submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "rb001_manual_execution_receipt_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("RB-001 manual execution receipt QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
