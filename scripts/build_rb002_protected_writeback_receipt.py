#!/usr/bin/env python3
"""Build RB-002 protected writeback receipt template.

This creates a manual receipt for future protected evidence writeback. It does
not write evidence, edit protected targets, close gates or run transitions.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "rb002_protected_writeback_receipt_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_RECEIPT = Path.home() / "Desktop" / "RB002_protected_writeback_receipt_20260810.csv"
DESKTOP_GUIDE = Path.home() / "Desktop" / "RB002_protected_writeback_receipt_guide_20260810.md"

READINESS_SUMMARY = BENCH_ROOT / "reports" / "rb002_writeback_readiness_dashboard_20260810" / "rb002_writeback_readiness_dashboard_summary.json"
ROUTE_MATRIX = BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_writeback_route_matrix.csv"
PROTECTED_TARGETS = BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_writeback_protected_targets.csv"

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


def row_complete(row: dict[str, str]) -> bool:
    required = [
        "operator_name",
        "writeback_datetime_local",
        "route_id",
        "target_file",
        "target_field",
        "source_evidence_file",
        "source_evidence_sha256",
        "old_value_snapshot",
        "new_value_written",
        "post_writeback_validation_command",
        "operator_attestation",
    ]
    return all(row.get(field, "").strip() not in PLACEHOLDERS for field in required)


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.32 RB-002 protected writeback receipt update"
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
    readiness = read_json(READINESS_SUMMARY)
    routes = read_csv(ROUTE_MATRIX)
    targets = read_csv(PROTECTED_TARGETS)

    route_rows = []
    for index, row in enumerate(routes, start=1):
        route_rows.append(
            {
                "receipt_id": f"RB002-WB-{index:03d}",
                "operator_name": "FILL_AFTER_WRITEBACK_ALLOWED",
                "writeback_datetime_local": "YYYY-MM-DD HH:MM",
                "route_id": row["route_id"],
                "evidence_type": row["evidence_type"],
                "target_file": row["target_file"],
                "target_field": row["fields_to_fill"],
                "do_not_edit": row["do_not_edit"],
                "source_evidence_file": "FILL_AFTER_WRITEBACK_ALLOWED",
                "source_evidence_sha256": "FILL_AFTER_WRITEBACK_ALLOWED",
                "old_value_snapshot": "FILL_AFTER_MANUAL_WRITEBACK",
                "new_value_written": "FILL_AFTER_MANUAL_WRITEBACK",
                "post_writeback_validation_command": row.get("required_next_proof", "FILL_AFTER_MANUAL_WRITEBACK"),
                "operator_attestation": "FILL_AFTER_MANUAL_WRITEBACK",
                "writeback_allowed_by_current_state": "no",
            }
        )

    target_rows = [
        {
            "artifact": row["artifact"],
            "key_field": row["key_field"],
            "manual_field": row["manual_field"],
            "owner": row["owner"],
            "status": row["status"],
            "writeback_receipt_required": "yes",
        }
        for row in targets
    ]

    completed_rows = [row for row in route_rows if row_complete(row)]
    incomplete_rows = [
        {
            "receipt_id": row["receipt_id"],
            "route_id": row["route_id"],
            "target_file": row["target_file"],
            "reason": "writeback receipt contains placeholders or RB-002 is not allowed",
        }
        for row in route_rows
        if not row_complete(row)
    ]

    acceptance_rows = [
        {"criterion": "RB001_closed", "current": readiness.get("rb001_closed"), "required": "true", "passes_now": "no"},
        {"criterion": "writeback_allowed_rows", "current": readiness.get("writeback_allowed_rows"), "required": ">0", "passes_now": "no"},
        {"criterion": "receipt_rows_completed", "current": len(completed_rows), "required": "one row per actual writeback", "passes_now": "no"},
        {"criterion": "protected_targets_documented", "current": len(target_rows), "required": ">=1", "passes_now": "yes" if len(target_rows) > 0 else "no"},
        {"criterion": "submission_ready", "current": readiness.get("submission_ready"), "required": "false until all gates close", "passes_now": "yes" if readiness.get("submission_ready") is False else "no"},
    ]

    qa_rows = [
        {"check": "all_routes_have_receipt_rows", "result": "PASS" if len(route_rows) == readiness.get("writeback_routes") == 7 else "FAIL", "detail": f"receipt_rows={len(route_rows)}"},
        {"check": "protected_targets_listed", "result": "PASS" if len(target_rows) == 9 else "FAIL", "detail": f"protected_targets={len(target_rows)}"},
        {"check": "template_not_completed", "result": "PASS" if len(completed_rows) == 0 else "FAIL", "detail": f"completed_rows={len(completed_rows)}"},
        {"check": "writeback_not_granted", "result": "PASS" if readiness.get("writeback_allowed_rows") == 0 and readiness.get("rb002_ready") is False else "FAIL", "detail": f"writeback_allowed_rows={readiness.get('writeback_allowed_rows')}; rb002_ready={readiness.get('rb002_ready')}"},
        {"check": "submission_guard_preserved", "result": "PASS" if readiness.get("submission_ready") is False else "FAIL", "detail": f"submission_ready={readiness.get('submission_ready')}"},
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    fields = [
        "receipt_id",
        "operator_name",
        "writeback_datetime_local",
        "route_id",
        "evidence_type",
        "target_file",
        "target_field",
        "do_not_edit",
        "source_evidence_file",
        "source_evidence_sha256",
        "old_value_snapshot",
        "new_value_written",
        "post_writeback_validation_command",
        "operator_attestation",
        "writeback_allowed_by_current_state",
    ]
    write_csv(OUT_DIR / "rb002_protected_writeback_receipt_template.csv", route_rows, fields)
    write_csv(OUT_DIR / "rb002_protected_writeback_targets.csv", target_rows, ["artifact", "key_field", "manual_field", "owner", "status", "writeback_receipt_required"])
    write_csv(OUT_DIR / "rb002_protected_writeback_incomplete_rows.csv", incomplete_rows, ["receipt_id", "route_id", "target_file", "reason"])
    write_csv(OUT_DIR / "rb002_protected_writeback_acceptance_criteria.csv", acceptance_rows, ["criterion", "current", "required", "passes_now"])
    write_csv(OUT_DIR / "rb002_protected_writeback_receipt_qa.csv", qa_rows, ["check", "result", "detail"])
    shutil.copy2(OUT_DIR / "rb002_protected_writeback_receipt_template.csv", DESKTOP_RECEIPT)

    guide = [
        "# RB-002 protected writeback receipt guide 2026-08-10",
        "",
        "Fill this receipt only after RB-001 closes and `writeback_allowed_rows>0`.",
        "",
        "Required sequence:",
        "",
        "1. Confirm RB-001 closeout dashboard reports `rb001_closed=true`.",
        "2. Confirm RB-002 readiness dashboard reports `writeback_allowed_rows>0`.",
        "3. Snapshot the old value before editing any protected target.",
        "4. Write only the listed target fields.",
        "5. Record source evidence file and SHA256.",
        "6. Run the listed validation command after manual writeback.",
        "7. Do not edit any `do_not_edit` field.",
        "",
        "Current status: template only; writeback is not allowed.",
        "",
    ]
    write_text(OUT_DIR / "RB002_PROTECTED_WRITEBACK_RECEIPT_GUIDE.md", "\n".join(guide))
    shutil.copy2(OUT_DIR / "RB002_PROTECTED_WRITEBACK_RECEIPT_GUIDE.md", DESKTOP_GUIDE)

    summary = {
        "package": "rb002_protected_writeback_receipt_20260810",
        "receipt_template_rows": len(route_rows),
        "protected_target_rows": len(target_rows),
        "completed_receipt_rows": len(completed_rows),
        "incomplete_receipt_rows": len(incomplete_rows),
        "acceptance_criteria_rows": len(acceptance_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "rb001_closed": readiness.get("rb001_closed"),
        "writeback_allowed_rows": readiness.get("writeback_allowed_rows"),
        "rb002_ready": readiness.get("rb002_ready"),
        "submission_ready": False,
        "desktop_receipt": str(DESKTOP_RECEIPT),
        "desktop_guide": str(DESKTOP_GUIDE),
        "status": "rb002_protected_writeback_receipt_template_ready_writeback_blocked",
    }

    section = f"""### 19.32 RB-002 protected writeback receipt update

Added a protected writeback receipt template for future RB-002 manual writeback.

New directory: `{OUT_DIR}`

Desktop receipt: `{DESKTOP_RECEIPT}`

Desktop guide: `{DESKTOP_GUIDE}`

Current result:
1. receipt_template_rows = {summary['receipt_template_rows']}
2. protected_target_rows = {summary['protected_target_rows']}
3. completed_receipt_rows = {summary['completed_receipt_rows']}
4. incomplete_receipt_rows = {summary['incomplete_receipt_rows']}
5. rb001_closed = false
6. writeback_allowed_rows = {summary['writeback_allowed_rows']}
7. rb002_ready = false
8. submission_ready = false

Boundary:
1. This is a receipt template only.
2. It does not write protected targets or grant writeback permission.
3. It does not close gates, upload files or submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "rb002_protected_writeback_receipt_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("RB-002 protected writeback receipt QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
