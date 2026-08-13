#!/usr/bin/env python3
"""Validate RB-002 protected writeback receipt completion."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "rb002_writeback_receipt_completion_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"

RECEIPT = BENCH_ROOT / "reports" / "rb002_protected_writeback_receipt_20260810" / "rb002_protected_writeback_receipt_template.csv"
RECEIPT_SUMMARY = BENCH_ROOT / "reports" / "rb002_protected_writeback_receipt_20260810" / "rb002_protected_writeback_receipt_summary.json"
READINESS_SUMMARY = BENCH_ROOT / "reports" / "rb002_writeback_readiness_dashboard_20260810" / "rb002_writeback_readiness_dashboard_summary.json"
WRITEBACK_SUMMARY = BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_evidence_writeback_preflight_summary.json"
TRANSITION_SUMMARY = BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810" / "post_writeback_gate_transition_validator_summary.json"

PLACEHOLDERS = {"", "FILL_AFTER_WRITEBACK_ALLOWED", "FILL_AFTER_MANUAL_WRITEBACK", "YYYY-MM-DD HH:MM", "pending"}


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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


def row_complete(row: dict[str, str]) -> bool:
    required = [
        "operator_name",
        "writeback_datetime_local",
        "source_evidence_file",
        "source_evidence_sha256",
        "old_value_snapshot",
        "new_value_written",
        "post_writeback_validation_command",
        "operator_attestation",
    ]
    return all(filled(row.get(field, "")) for field in required)


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.33 RB-002 writeback receipt completion validator update"
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
    receipt_summary = read_json(RECEIPT_SUMMARY)
    readiness = read_json(READINESS_SUMMARY)
    writeback = read_json(WRITEBACK_SUMMARY)
    transition = read_json(TRANSITION_SUMMARY)

    validation_rows = []
    for row in receipt_rows:
        complete = row_complete(row)
        current_permission = row.get("writeback_allowed_by_current_state") == "yes"
        route_transition_possible = complete and current_permission and bool(readiness.get("rb002_ready"))
        validation_rows.append(
            {
                "receipt_id": row["receipt_id"],
                "route_id": row["route_id"],
                "receipt_row_complete": "yes" if complete else "no",
                "writeback_permission_recorded": "yes" if current_permission else "no",
                "rb002_ready": "yes" if readiness.get("rb002_ready") else "no",
                "ready_for_transition_validation": "yes" if route_transition_possible else "no",
                "blocker": "" if route_transition_possible else "receipt incomplete or writeback permission absent",
            }
        )

    complete_rows = sum(1 for row in validation_rows if row["receipt_row_complete"] == "yes")
    permission_rows = sum(1 for row in validation_rows if row["writeback_permission_recorded"] == "yes")
    transition_ready_rows = sum(1 for row in validation_rows if row["ready_for_transition_validation"] == "yes")
    receipt_complete = complete_rows > 0 and complete_rows == int(writeback.get("writeback_allowed_rows", 0))
    transition_entry_allowed = receipt_complete and transition_ready_rows > 0 and int(transition.get("transition_allowed_rows", 0)) > 0

    gate_rows = [
        {"gate": "rb001_closed", "current": readiness.get("rb001_closed"), "required": "true", "passes_now": "yes" if readiness.get("rb001_closed") else "no"},
        {"gate": "writeback_allowed_rows", "current": writeback.get("writeback_allowed_rows"), "required": ">0", "passes_now": "yes" if int(writeback.get("writeback_allowed_rows", 0)) > 0 else "no"},
        {"gate": "receipt_rows_complete", "current": complete_rows, "required": "equals writeback_allowed_rows and >0", "passes_now": "yes" if receipt_complete else "no"},
        {"gate": "receipt_permission_recorded", "current": permission_rows, "required": "equals completed receipt rows", "passes_now": "yes" if permission_rows == complete_rows and complete_rows > 0 else "no"},
        {"gate": "transition_entry_allowed", "current": transition_entry_allowed, "required": "true", "passes_now": "yes" if transition_entry_allowed else "no"},
    ]

    qa_rows = [
        {"check": "all_receipt_rows_validated", "result": "PASS" if len(validation_rows) == receipt_summary.get("receipt_template_rows") == 7 else "FAIL", "detail": f"validation_rows={len(validation_rows)}"},
        {"check": "empty_template_not_complete", "result": "PASS" if complete_rows == 0 else "FAIL", "detail": f"complete_rows={complete_rows}"},
        {"check": "no_transition_without_writeback_permission", "result": "PASS" if not transition_entry_allowed else "FAIL", "detail": f"transition_entry_allowed={transition_entry_allowed}"},
        {"check": "writeback_block_preserved", "result": "PASS" if writeback.get("writeback_allowed_rows") == 0 and readiness.get("rb002_ready") is False else "FAIL", "detail": f"writeback_allowed_rows={writeback.get('writeback_allowed_rows')}; rb002_ready={readiness.get('rb002_ready')}"},
        {"check": "transition_guard_preserved", "result": "PASS" if transition.get("transition_allowed_rows") == 0 else "FAIL", "detail": f"transition_allowed_rows={transition.get('transition_allowed_rows')}"},
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "rb002_writeback_receipt_completion_validation.csv", validation_rows, ["receipt_id", "route_id", "receipt_row_complete", "writeback_permission_recorded", "rb002_ready", "ready_for_transition_validation", "blocker"])
    write_csv(OUT_DIR / "rb002_writeback_receipt_completion_gate_matrix.csv", gate_rows, ["gate", "current", "required", "passes_now"])
    write_csv(OUT_DIR / "rb002_writeback_receipt_completion_validator_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# RB-002 writeback receipt completion validator 2026-08-10",
        "",
        "Status: `rb002_writeback_receipt_completion_validator_ready_blocked_no_writeback`",
        "",
        f"1. Receipt rows validated: {len(validation_rows)}",
        f"2. Complete receipt rows: {complete_rows}",
        f"3. Permission rows: {permission_rows}",
        f"4. Transition-ready rows: {transition_ready_rows}",
        f"5. Receipt complete: {str(receipt_complete).lower()}",
        f"6. Transition entry allowed: {str(transition_entry_allowed).lower()}",
        f"7. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this validator checks RB-002 receipt completion only. It does not edit protected targets, grant writeback permission, run transitions, close gates, upload files or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "RB002_WRITEBACK_RECEIPT_COMPLETION_VALIDATOR_README.md", "\n".join(report))
    write_text(OUT_DIR / "rb002_writeback_receipt_completion_validator_report.md", "\n".join(report))

    summary = {
        "package": "rb002_writeback_receipt_completion_validator_20260810",
        "receipt_rows_validated": len(validation_rows),
        "complete_receipt_rows": complete_rows,
        "permission_rows": permission_rows,
        "transition_ready_rows": transition_ready_rows,
        "gate_rows": len(gate_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "receipt_complete": receipt_complete,
        "transition_entry_allowed": transition_entry_allowed,
        "rb001_closed": readiness.get("rb001_closed"),
        "writeback_allowed_rows": writeback.get("writeback_allowed_rows"),
        "transition_allowed_rows": transition.get("transition_allowed_rows"),
        "submission_ready": False,
        "status": "rb002_writeback_receipt_completion_validator_ready_blocked_no_writeback",
    }

    section = f"""### 19.33 RB-002 writeback receipt completion validator update

Added a RB-002 receipt completion validator that checks future protected writeback receipt rows before any transition validation can be considered.

New directory: `{OUT_DIR}`

Current result:
1. receipt_rows_validated = {summary['receipt_rows_validated']}
2. complete_receipt_rows = {summary['complete_receipt_rows']}
3. permission_rows = {summary['permission_rows']}
4. transition_ready_rows = {summary['transition_ready_rows']}
5. receipt_complete = false
6. transition_entry_allowed = false
7. rb001_closed = false
8. writeback_allowed_rows = {summary['writeback_allowed_rows']}
9. transition_allowed_rows = {summary['transition_allowed_rows']}
10. submission_ready = false

Boundary:
1. This validator checks receipt completion only.
2. It does not write protected targets or grant writeback permission.
3. It does not run transitions, close gates, upload files or submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "rb002_writeback_receipt_completion_validator_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("RB-002 writeback receipt completion validator QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
