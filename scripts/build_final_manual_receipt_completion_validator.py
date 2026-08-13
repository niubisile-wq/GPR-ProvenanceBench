#!/usr/bin/env python3
"""Validate completion of the 19.49 final manual receipt intake template."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_completion_validator_20260810"
RECEIPT_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_intake_package_20260810"
FINAL_MASTER_DIR = BENCH_ROOT / "reports" / "final_submission_master_dependency_bridge_validator_20260810"
NEXT_ACTION_DIR = BENCH_ROOT / "reports" / "final_master_next_action_packet_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


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


def is_complete(row: dict[str, str]) -> bool:
    status = row.get("current_status", "").strip().lower()
    placeholder = row.get("value_to_fill_after_manual_action", "").strip()
    return status == "complete" and not placeholder.startswith("FILL_AFTER")


def _obsolete_update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.50 Final manual receipt completion validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/final_manual_receipt_completion_validator_20260810/`，校验 19.49 的 FMR-001 到 FMR-006 是否真实完成。
- 当前 `receipt_rows={summary["receipt_rows"]}`，`complete_receipt_rows={summary["complete_receipt_rows"]}`，`incomplete_receipt_rows={summary["incomplete_receipt_rows"]}`。
- 当前 `receipt_completion_allowed={str(summary["receipt_completion_allowed"]).lower()}`，`guarded_recheck_allowed={str(summary["guarded_recheck_allowed"]).lower()}`，`final_master_reentry_allowed={str(summary["final_master_reentry_allowed"]).lower()}`。
- 当前 `system_command_execution_allowed=false`，`portal_upload_allowed=false`，`submission_ready=false`。
- 边界：该 validator 只读，不把占位符当证据、不替人填写 receipt、不运行 recheck、不上传 portal 文件。
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


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.50 Final manual receipt completion validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/final_manual_receipt_completion_validator_20260810/` to validate whether FMR-001 through FMR-006 from 19.49 are genuinely complete.
- Current `receipt_rows={summary["receipt_rows"]}`, `complete_receipt_rows={summary["complete_receipt_rows"]}`, `incomplete_receipt_rows={summary["incomplete_receipt_rows"]}`.
- Current `receipt_completion_allowed={str(summary["receipt_completion_allowed"]).lower()}`, `guarded_recheck_allowed={str(summary["guarded_recheck_allowed"]).lower()}`, `final_master_reentry_allowed={str(summary["final_master_reentry_allowed"]).lower()}`.
- Current `system_command_execution_allowed=false`, `portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: this validator is read-only; it does not accept placeholders as evidence, fill receipts, run recheck or upload portal files.
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

    receipt_summary = read_json(RECEIPT_DIR / "final_manual_receipt_intake_package_summary.json")
    final_master = read_json(FINAL_MASTER_DIR / "final_submission_master_dependency_bridge_validator_summary.json")
    next_summary = read_json(NEXT_ACTION_DIR / "final_master_next_action_packet_summary.json")
    receipts = read_csv(RECEIPT_DIR / "final_manual_receipt_intake_template.csv")

    receipt_status_rows = []
    for row in receipts:
        complete = is_complete(row)
        current_status = row.get("current_status", "")
        placeholder = row.get("value_to_fill_after_manual_action", "")
        receipt_status_rows.append(
            {
                "receipt_id": row.get("receipt_id", ""),
                "receipt_type": row.get("receipt_type", ""),
                "owner": row.get("owner", ""),
                "current_status": current_status,
                "placeholder_value": placeholder,
                "completion_passes_now": "yes" if complete else "no",
                "blocking_reason": "" if complete else "Receipt is not complete or still contains a FILL_AFTER placeholder.",
                "first_validator": row.get("first_validator", ""),
            }
        )

    complete_receipt_rows = sum(1 for row in receipt_status_rows if row["completion_passes_now"] == "yes")
    incomplete_receipt_rows = len(receipt_status_rows) - complete_receipt_rows
    receipt_completion_allowed = incomplete_receipt_rows == 0 and len(receipt_status_rows) == 6
    guarded_recheck_allowed = (
        receipt_completion_allowed
        and final_master.get("final_submission_master_allowed") is False
        and next_summary.get("system_command_execution_allowed") is False
    )
    final_master_reentry_allowed = guarded_recheck_allowed
    submission_ready = False

    gate_rows = [
        {
            "gate": "all_receipts_complete",
            "current": receipt_completion_allowed,
            "required": "true",
            "passes_now": "yes" if receipt_completion_allowed else "no",
        },
        {
            "gate": "19.47_still_blocks_submission_before_recheck",
            "current": final_master.get("final_submission_master_allowed"),
            "required": "false before real recheck",
            "passes_now": "yes" if final_master.get("final_submission_master_allowed") is False else "no",
        },
        {
            "gate": "guarded_recheck_allowed",
            "current": guarded_recheck_allowed,
            "required": "true only after all receipts complete",
            "passes_now": "yes" if guarded_recheck_allowed else "no",
        },
        {
            "gate": "portal_upload_allowed",
            "current": False,
            "required": "false in receipt validator",
            "passes_now": "yes",
        },
        {
            "gate": "submission_ready",
            "current": submission_ready,
            "required": "false in receipt validator",
            "passes_now": "yes",
        },
    ]

    blocker_rows = [
        {
            "blocker": row["receipt_id"],
            "evidence": f"current_status={row['current_status']}; placeholder_value={row['placeholder_value']}",
            "blocks": "guarded recheck and final master re-entry",
        }
        for row in receipt_status_rows
        if row["completion_passes_now"] == "no"
    ]

    qa_rows = [
        {
            "check": "receipt template imported",
            "result": "PASS" if len(receipts) == 6 else "FAIL",
            "detail": f"receipt_rows={len(receipts)}",
        },
        {
            "check": "all receipts correctly remain incomplete",
            "result": "PASS" if incomplete_receipt_rows == 6 else "FAIL",
            "detail": f"incomplete_receipt_rows={incomplete_receipt_rows}",
        },
        {
            "check": "19.49 summary agrees with zero completed receipts",
            "result": "PASS" if receipt_summary.get("completed_receipt_rows") == 0 else "FAIL",
            "detail": f"completed_receipt_rows={receipt_summary.get('completed_receipt_rows')}",
        },
        {
            "check": "guarded recheck remains blocked",
            "result": "PASS" if not guarded_recheck_allowed else "FAIL",
            "detail": f"guarded_recheck_allowed={guarded_recheck_allowed}",
        },
        {
            "check": "submission remains false",
            "result": "PASS" if not submission_ready else "FAIL",
            "detail": f"submission_ready={submission_ready}",
        },
    ]

    summary = {
        "package": "final_manual_receipt_completion_validator_20260810",
        "receipt_rows": len(receipts),
        "complete_receipt_rows": complete_receipt_rows,
        "incomplete_receipt_rows": incomplete_receipt_rows,
        "receipt_completion_allowed": receipt_completion_allowed,
        "guarded_recheck_allowed": guarded_recheck_allowed,
        "final_master_reentry_allowed": final_master_reentry_allowed,
        "system_command_execution_allowed": False,
        "portal_upload_allowed": False,
        "submission_ready": submission_ready,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "final_manual_receipt_completion_validator_ready_blocked_waiting_receipts",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "final_manual_receipt_completion_status.csv",
        [
            "receipt_id",
            "receipt_type",
            "owner",
            "current_status",
            "placeholder_value",
            "completion_passes_now",
            "blocking_reason",
            "first_validator",
        ],
        receipt_status_rows,
    )
    write_csv(
        OUT_DIR / "final_manual_receipt_completion_gate_matrix.csv",
        ["gate", "current", "required", "passes_now"],
        gate_rows,
    )
    write_csv(
        OUT_DIR / "final_manual_receipt_completion_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "final_manual_receipt_completion_validator_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# Final Manual Receipt Completion Validator

This validator checks whether the 19.49 final manual receipt intake rows are
complete enough to permit a guarded M0-M2 recheck and re-entry into the final
submission master bridge.

Boundary: read-only. It does not fill receipts, accept placeholders as evidence,
run rechecks, upload portal files or mark the manuscript submission-ready.
"""
    write_text(OUT_DIR / "FINAL_MANUAL_RECEIPT_COMPLETION_VALIDATOR_README.md", readme)

    report = f"""# Final Manual Receipt Completion Validator Report

Status: `{summary["status"]}`

Current result:

1. Complete receipt rows: {summary["complete_receipt_rows"]}
2. Incomplete receipt rows: {summary["incomplete_receipt_rows"]}
3. Receipt completion allowed: {str(summary["receipt_completion_allowed"]).lower()}
4. Guarded recheck allowed: {str(summary["guarded_recheck_allowed"]).lower()}
5. Final master re-entry allowed: {str(summary["final_master_reentry_allowed"]).lower()}
6. Submission ready: {str(summary["submission_ready"]).lower()}

Boundary: this package only validates receipt completeness. It cannot replace
real send logs, hashes, author replies, figure approvals, DOI/rights decisions
or a successful guarded recheck.
"""
    write_text(OUT_DIR / "final_manual_receipt_completion_validator_report.md", report)
    write_text(
        OUT_DIR / "final_manual_receipt_completion_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
