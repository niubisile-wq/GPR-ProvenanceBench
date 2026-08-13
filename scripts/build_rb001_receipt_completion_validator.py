#!/usr/bin/env python3
"""Validate whether RB-001 manual execution receipt is complete.

This is a readiness validator for the manual receipt, scanner file manifest and
hash/source reconciliation. It does not create evidence, edit receipt rows,
write protected targets or close gates.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "rb001_receipt_completion_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"

RECEIPT = BENCH_ROOT / "reports" / "rb001_manual_execution_receipt_20260810" / "rb001_manual_execution_receipt_template.csv"
SCANNER_MANIFEST = BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_file_manifest.csv"
HASH_RECON = BENCH_ROOT / "reports" / "rb001_return_evidence_hash_reconciliation_20260810" / "rb001_return_evidence_hash_reconciliation.csv"
RECEIPT_SUMMARY = BENCH_ROOT / "reports" / "rb001_manual_execution_receipt_20260810" / "rb001_manual_execution_receipt_summary.json"
DIAGNOSTIC_SUMMARY = BENCH_ROOT / "reports" / "rb001_diagnostic_only_runner_20260810" / "rb001_diagnostic_only_runner_summary.json"
DRY_RUN_SUMMARY = BENCH_ROOT / "reports" / "rb001_post_drop_dry_run_gate_20260810" / "rb001_post_drop_dry_run_gate_summary.json"

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


def filled(value: str) -> bool:
    return value.strip() not in PLACEHOLDERS


def receipt_row_complete(row: dict[str, str]) -> bool:
    required = [
        "operator_name",
        "action_date",
        "file_name",
        "sha256",
        "source_person_or_system",
        "diagnostic_runner_returncode",
        "operator_attestation",
    ]
    return all(filled(row.get(field, "")) for field in required) and row.get("diagnostic_runner_returncode") == "0"


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.29 RB-001 receipt completion validator update"
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
    receipt_rows = read_csv(RECEIPT)
    scanner_rows = read_csv(SCANNER_MANIFEST)
    recon_rows = read_csv(HASH_RECON)
    receipt_summary = read_json(RECEIPT_SUMMARY)
    diagnostic_summary = read_json(DIAGNOSTIC_SUMMARY)
    dry_run_summary = read_json(DRY_RUN_SUMMARY)

    scanner_keys = {(row["route_id"], row["file_name"], row["sha256"].lower()) for row in scanner_rows}
    recon_keys = {
        (row["route_id"], row["file_name"], row["sha256"].lower())
        for row in recon_rows
        if row.get("reconciliation_status") == "registered_hash_match"
    }

    validation_rows: list[dict[str, object]] = []
    for row in receipt_rows:
        key = (row["route_id"], row["file_name"], row["sha256"].lower())
        row_complete = receipt_row_complete(row)
        scanner_match = key in scanner_keys
        recon_match = key in recon_keys
        writeback_claim_safe = row.get("writeback_allowed_by_this_receipt") == "no"
        receipt_ready = row_complete and scanner_match and recon_match and writeback_claim_safe
        validation_rows.append(
            {
                "receipt_id": row["receipt_id"],
                "route_id": row["route_id"],
                "receipt_row_complete": "yes" if row_complete else "no",
                "scanner_manifest_match": "yes" if scanner_match else "no",
                "hash_reconciliation_match": "yes" if recon_match else "no",
                "diagnostic_returncode_recorded_zero": "yes" if row.get("diagnostic_runner_returncode") == "0" else "no",
                "writeback_claim_safe": "yes" if writeback_claim_safe else "no",
                "receipt_ready_for_writeback_preflight": "yes" if receipt_ready else "no",
                "blocker": "" if receipt_ready else "missing real file, completed receipt fields, scanner match or hash/source reconciliation",
            }
        )

    completed_receipt_rows = sum(1 for row in validation_rows if row["receipt_row_complete"] == "yes")
    scanner_match_rows = sum(1 for row in validation_rows if row["scanner_manifest_match"] == "yes")
    recon_match_rows = sum(1 for row in validation_rows if row["hash_reconciliation_match"] == "yes")
    ready_rows = sum(1 for row in validation_rows if row["receipt_ready_for_writeback_preflight"] == "yes")
    receipt_complete = ready_rows > 0 and ready_rows == len(scanner_rows) and len(scanner_rows) > 0
    writeback_preflight_entry_allowed = receipt_complete and int(dry_run_summary.get("writeback_allowed_rows", 0)) > 0

    gate_rows = [
        {"gate": "real_files_present", "current": len(scanner_rows), "required": ">0", "passes_now": "yes" if len(scanner_rows) > 0 else "no"},
        {"gate": "receipt_rows_completed", "current": completed_receipt_rows, "required": ">= scanner file rows and >0", "passes_now": "yes" if completed_receipt_rows >= len(scanner_rows) and len(scanner_rows) > 0 else "no"},
        {"gate": "scanner_matches_receipt", "current": scanner_match_rows, "required": "all completed receipt rows", "passes_now": "yes" if scanner_match_rows == completed_receipt_rows and completed_receipt_rows > 0 else "no"},
        {"gate": "hash_reconciliation_matches", "current": recon_match_rows, "required": "all scanner file rows", "passes_now": "yes" if recon_match_rows == len(scanner_rows) and len(scanner_rows) > 0 else "no"},
        {"gate": "diagnostic_runner_recorded", "current": diagnostic_summary.get("runner_returncode"), "required": "0 after real file drop", "passes_now": "no"},
        {"gate": "receipt_complete", "current": receipt_complete, "required": "true", "passes_now": "yes" if receipt_complete else "no"},
        {"gate": "writeback_preflight_entry_allowed", "current": writeback_preflight_entry_allowed, "required": "true", "passes_now": "yes" if writeback_preflight_entry_allowed else "no"},
    ]

    qa_rows = [
        {"check": "all_receipt_rows_validated", "result": "PASS" if len(validation_rows) == receipt_summary.get("receipt_template_rows") == 7 else "FAIL", "detail": f"validation_rows={len(validation_rows)}"},
        {"check": "empty_state_not_complete", "result": "PASS" if not receipt_complete and len(scanner_rows) == 0 else "FAIL", "detail": f"receipt_complete={receipt_complete}; scanner_rows={len(scanner_rows)}"},
        {"check": "no_writeback_entry_without_real_files", "result": "PASS" if not writeback_preflight_entry_allowed else "FAIL", "detail": f"writeback_preflight_entry_allowed={writeback_preflight_entry_allowed}"},
        {"check": "no_false_ready_rows", "result": "PASS" if ready_rows == 0 else "FAIL", "detail": f"ready_rows={ready_rows}"},
        {"check": "submission_guard_preserved", "result": "PASS" if dry_run_summary.get("submission_ready") is False else "FAIL", "detail": f"submission_ready={dry_run_summary.get('submission_ready')}"},
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "rb001_receipt_completion_validation.csv",
        validation_rows,
        ["receipt_id", "route_id", "receipt_row_complete", "scanner_manifest_match", "hash_reconciliation_match", "diagnostic_returncode_recorded_zero", "writeback_claim_safe", "receipt_ready_for_writeback_preflight", "blocker"],
    )
    write_csv(OUT_DIR / "rb001_receipt_completion_gate_matrix.csv", gate_rows, ["gate", "current", "required", "passes_now"])
    write_csv(OUT_DIR / "rb001_receipt_completion_validator_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# RB-001 receipt completion validator 2026-08-10",
        "",
        "Status: `rb001_receipt_completion_validator_ready_empty_receipt_blocked`",
        "",
        f"1. Receipt rows validated: {len(validation_rows)}",
        f"2. Scanner file rows: {len(scanner_rows)}",
        f"3. Completed receipt rows: {completed_receipt_rows}",
        f"4. Scanner match rows: {scanner_match_rows}",
        f"5. Hash reconciliation match rows: {recon_match_rows}",
        f"6. Ready rows: {ready_rows}",
        f"7. Receipt complete: {str(receipt_complete).lower()}",
        f"8. Writeback preflight entry allowed: {str(writeback_preflight_entry_allowed).lower()}",
        f"9. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this validator checks readiness only. It does not fill receipt rows, create returned files, write protected targets, close gates, upload files or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "RB001_RECEIPT_COMPLETION_VALIDATOR_README.md", "\n".join(report))
    write_text(OUT_DIR / "rb001_receipt_completion_validator_report.md", "\n".join(report))

    summary = {
        "package": "rb001_receipt_completion_validator_20260810",
        "receipt_rows_validated": len(validation_rows),
        "scanner_file_rows": len(scanner_rows),
        "completed_receipt_rows": completed_receipt_rows,
        "scanner_match_rows": scanner_match_rows,
        "hash_reconciliation_match_rows": recon_match_rows,
        "ready_rows": ready_rows,
        "gate_rows": len(gate_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "receipt_complete": receipt_complete,
        "writeback_preflight_entry_allowed": writeback_preflight_entry_allowed,
        "submission_ready": False,
        "status": "rb001_receipt_completion_validator_ready_empty_receipt_blocked",
    }

    section = f"""### 19.29 RB-001 receipt completion validator update

Added a receipt completion validator that checks whether manual receipt rows, scanner file manifest rows and hash/source reconciliation rows agree before writeback preflight can be considered.

New directory: `{OUT_DIR}`

Current result:
1. receipt_rows_validated = {summary['receipt_rows_validated']}
2. scanner_file_rows = {summary['scanner_file_rows']}
3. completed_receipt_rows = {summary['completed_receipt_rows']}
4. scanner_match_rows = {summary['scanner_match_rows']}
5. hash_reconciliation_match_rows = {summary['hash_reconciliation_match_rows']}
6. ready_rows = {summary['ready_rows']}
7. receipt_complete = false
8. writeback_preflight_entry_allowed = false
9. submission_ready = false

Boundary:
1. This validator checks readiness only.
2. It does not fill receipt rows or create returned files.
3. It does not write protected targets, close gates, upload files or submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "rb001_receipt_completion_validator_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("RB-001 receipt completion validator QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
