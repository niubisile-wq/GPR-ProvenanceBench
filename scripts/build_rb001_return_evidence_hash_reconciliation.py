#!/usr/bin/env python3
"""Reconcile RB-001 returned-file hashes against the operator source register.

This validator compares the scanner-generated file manifest with the
operator-facing source/hash register template. It is read-only: no evidence is
created, no protected target is written and no gate is closed.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "rb001_return_evidence_hash_reconciliation_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"

SCANNER_MANIFEST = BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_file_manifest.csv"
SCANNER_SUMMARY = BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_intake_scanner_summary.json"
DROP_KIT_TEMPLATE = BENCH_ROOT / "reports" / "rb001_return_evidence_drop_kit_20260810" / "rb001_return_evidence_hash_manifest_template.csv"
DROP_KIT_SUMMARY = BENCH_ROOT / "reports" / "rb001_return_evidence_drop_kit_20260810" / "rb001_return_evidence_drop_kit_summary.json"

PLACEHOLDER_VALUES = {"", "FILL_AFTER_DROP", "FILL_AFTER_HASH", "YYYY-MM-DD"}


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


def is_filled_register_row(row: dict[str, str]) -> bool:
    required = ["expected_file_name", "source_person_or_system", "received_date", "sha256"]
    return all(row.get(field, "").strip() not in PLACEHOLDER_VALUES for field in required)


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.25 RB-001 return evidence hash reconciliation update"
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
    scanner_summary = read_json(SCANNER_SUMMARY)
    drop_summary = read_json(DROP_KIT_SUMMARY)
    scanner_rows = read_csv(SCANNER_MANIFEST)
    register_rows = read_csv(DROP_KIT_TEMPLATE)

    filled_register_rows = [row for row in register_rows if is_filled_register_row(row)]
    register_by_key = {
        (row["route_id"], row["expected_file_name"], row["sha256"].lower()): row
        for row in filled_register_rows
    }

    reconciliation_rows: list[dict[str, object]] = []
    missing_register_rows: list[dict[str, object]] = []
    hash_mismatch_rows: list[dict[str, object]] = []

    for row in scanner_rows:
        key = (row["route_id"], row["file_name"], row["sha256"].lower())
        matching_register = register_by_key.get(key)
        route_file_registers = [
            item
            for item in filled_register_rows
            if item["route_id"] == row["route_id"] and item["expected_file_name"] == row["file_name"]
        ]
        if matching_register:
            status = "registered_hash_match"
            source = matching_register["source_person_or_system"]
            received_date = matching_register["received_date"]
        elif route_file_registers:
            status = "registered_hash_mismatch"
            source = route_file_registers[0]["source_person_or_system"]
            received_date = route_file_registers[0]["received_date"]
            hash_mismatch_rows.append(
                {
                    "route_id": row["route_id"],
                    "file_name": row["file_name"],
                    "scanner_sha256": row["sha256"],
                    "registered_sha256": route_file_registers[0]["sha256"],
                    "reason": "File name is registered but SHA256 differs.",
                }
            )
        else:
            status = "missing_source_register"
            source = ""
            received_date = ""
            missing_register_rows.append(
                {
                    "route_id": row["route_id"],
                    "file_name": row["file_name"],
                    "sha256": row["sha256"],
                    "reason": "Scanner found a returned file without a filled source/hash register row.",
                }
            )
        reconciliation_rows.append(
            {
                "route_id": row["route_id"],
                "file_name": row["file_name"],
                "sha256": row["sha256"],
                "extension_allowed": row["extension_allowed"],
                "source_person_or_system": source,
                "received_date": received_date,
                "reconciliation_status": status,
                "writeback_allowed_now": "no",
            }
        )

    command_rows = [
        {"step": 1, "command": "Fill rb001_return_evidence_hash_manifest_template.csv only after real files exist.", "allowed_now": "manual_only_after_file_drop", "stop_rule": "Do not replace placeholders without a real file and SHA256."},
        {"step": 2, "command": "py scripts/build_final_return_evidence_intake_scanner.py", "allowed_now": "diagnostic_only", "stop_rule": "Do not treat scanner output alone as source authorization."},
        {"step": 3, "command": "py scripts/build_rb001_return_evidence_hash_reconciliation.py", "allowed_now": "diagnostic_only", "stop_rule": "Do not write back while missing_register_rows or hash_mismatch_rows are nonzero."},
        {"step": 4, "command": "py scripts/build_final_return_evidence_writeback_preflight.py", "allowed_now": "no", "stop_rule": "Do not run for closure until file hashes and source registrations reconcile."},
    ]

    qa_rows = [
        {"check": "scanner_manifest_readable", "result": "PASS" if isinstance(scanner_rows, list) else "FAIL", "detail": f"scanner_rows={len(scanner_rows)}"},
        {"check": "register_template_routes_present", "result": "PASS" if len(register_rows) == drop_summary.get("manifest_template_rows") == 7 else "FAIL", "detail": f"register_rows={len(register_rows)}"},
        {"check": "empty_state_preserves_no_missing_registers", "result": "PASS" if scanner_summary.get("candidate_return_files") != 0 or len(missing_register_rows) == 0 else "FAIL", "detail": f"candidate_return_files={scanner_summary.get('candidate_return_files')}; missing_register_rows={len(missing_register_rows)}"},
        {"check": "no_hash_mismatch", "result": "PASS" if len(hash_mismatch_rows) == 0 else "FAIL", "detail": f"hash_mismatch_rows={len(hash_mismatch_rows)}"},
        {"check": "writeback_guard_preserved", "result": "PASS" if scanner_summary.get("candidate_return_files") == 0 and drop_summary.get("writeback_allowed_rows") == 0 else "FAIL", "detail": f"candidate_return_files={scanner_summary.get('candidate_return_files')}; writeback_allowed_rows={drop_summary.get('writeback_allowed_rows')}"},
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "rb001_return_evidence_hash_reconciliation.csv", reconciliation_rows, ["route_id", "file_name", "sha256", "extension_allowed", "source_person_or_system", "received_date", "reconciliation_status", "writeback_allowed_now"])
    write_csv(OUT_DIR / "rb001_return_evidence_missing_source_register.csv", missing_register_rows, ["route_id", "file_name", "sha256", "reason"])
    write_csv(OUT_DIR / "rb001_return_evidence_hash_mismatch.csv", hash_mismatch_rows, ["route_id", "file_name", "scanner_sha256", "registered_sha256", "reason"])
    write_csv(OUT_DIR / "rb001_return_evidence_hash_reconciliation_commands.csv", command_rows, ["step", "command", "allowed_now", "stop_rule"])
    write_csv(OUT_DIR / "rb001_return_evidence_hash_reconciliation_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# RB-001 return evidence hash reconciliation 2026-08-10",
        "",
        "Status: `rb001_return_evidence_hash_reconciliation_ready_empty_no_writeback`",
        "",
        f"1. Scanner file rows: {len(scanner_rows)}",
        f"2. Filled register rows: {len(filled_register_rows)}",
        f"3. Reconciled rows: {len(reconciliation_rows)}",
        f"4. Missing source-register rows: {len(missing_register_rows)}",
        f"5. Hash mismatch rows: {len(hash_mismatch_rows)}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this is a file-level reconciliation layer only. It does not create returned files, approve source authority, write protected target files, close gates, upload files or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "RB001_RETURN_EVIDENCE_HASH_RECONCILIATION_README.md", "\n".join(report))
    write_text(OUT_DIR / "rb001_return_evidence_hash_reconciliation_report.md", "\n".join(report))

    summary = {
        "package": "rb001_return_evidence_hash_reconciliation_20260810",
        "scanner_file_rows": len(scanner_rows),
        "register_template_rows": len(register_rows),
        "filled_register_rows": len(filled_register_rows),
        "reconciled_rows": len(reconciliation_rows),
        "missing_source_register_rows": len(missing_register_rows),
        "hash_mismatch_rows": len(hash_mismatch_rows),
        "command_rows": len(command_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "candidate_return_files": scanner_summary.get("candidate_return_files"),
        "writeback_allowed_rows": drop_summary.get("writeback_allowed_rows"),
        "submission_ready": False,
        "status": "rb001_return_evidence_hash_reconciliation_ready_empty_no_writeback",
    }

    section = f"""### 19.25 RB-001 return evidence hash reconciliation update

Added a read-only reconciliation layer between the scanner-generated returned-file SHA256 manifest and the operator source/hash register template.

New directory: `{OUT_DIR}`

Current result:
1. scanner_file_rows = {summary['scanner_file_rows']}
2. register_template_rows = {summary['register_template_rows']}
3. filled_register_rows = {summary['filled_register_rows']}
4. reconciled_rows = {summary['reconciled_rows']}
5. missing_source_register_rows = {summary['missing_source_register_rows']}
6. hash_mismatch_rows = {summary['hash_mismatch_rows']}
7. candidate_return_files = {summary['candidate_return_files']}
8. writeback_allowed_rows = {summary['writeback_allowed_rows']}
9. submission_ready = false

Boundary:
1. This layer reconciles file hashes and source registration only.
2. It does not create evidence or approve source authority.
3. It does not write protected targets, close gates, upload files or submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "rb001_return_evidence_hash_reconciliation_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("RB-001 return evidence hash reconciliation QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
