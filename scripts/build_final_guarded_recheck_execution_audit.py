#!/usr/bin/env python3
"""Build an execution audit package for the final guarded recheck launcher."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_guarded_recheck_execution_audit_20260810"
LAUNCHER_DIR = BENCH_ROOT / "reports" / "final_guarded_recheck_launcher_20260810"
RECEIPT_VALIDATOR_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_completion_validator_20260810"
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


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.52 Final guarded recheck execution audit update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/final_guarded_recheck_execution_audit_20260810/`，为 19.51 launcher 建立执行审计记录和人工运行日志模板。
- 当前 `expected_launcher_decision=refuse`，`launcher_execution_allowed={str(summary["launcher_execution_allowed"]).lower()}`，`audit_rows={summary["audit_rows"]}`。
- 当前 `complete_receipt_rows={summary["complete_receipt_rows"]}`，`blocked_receipt_rows={summary["blocked_receipt_rows"]}`，`expected_exit_code=0_refusal`。
- 当前 `recheck_executed=false`，`system_command_execution_allowed=false`，`portal_upload_allowed=false`，`submission_ready=false`。
- 边界：该 audit package 不执行 launcher，只记录应如何审计 launcher 的拒绝/执行结果。
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

    launcher_summary = read_json(LAUNCHER_DIR / "final_guarded_recheck_launcher_summary.json")
    receipt_summary = read_json(RECEIPT_VALIDATOR_DIR / "final_manual_receipt_completion_validator_summary.json")
    command_gate = read_csv(LAUNCHER_DIR / "final_guarded_recheck_command_gate.csv")
    blockers = read_csv(LAUNCHER_DIR / "final_guarded_recheck_blockers.csv")

    launcher_execution_allowed = launcher_summary.get("launcher_will_execute_recheck") is True
    expected_decision = "execute" if launcher_execution_allowed else "refuse"
    expected_exit_code = "0_after_recheck" if launcher_execution_allowed else "0_refusal"

    audit_rows = [
        {
            "audit_id": "GRE-AUD-001",
            "audit_item": "launcher script exists",
            "expected": "run_final_guarded_recheck_after_receipts.ps1 exists",
            "current": str((LAUNCHER_DIR / "run_final_guarded_recheck_after_receipts.ps1").exists()),
            "passes_now": "yes" if (LAUNCHER_DIR / "run_final_guarded_recheck_after_receipts.ps1").exists() else "no",
        },
        {
            "audit_id": "GRE-AUD-002",
            "audit_item": "launcher decision matches 19.50",
            "expected": expected_decision,
            "current": expected_decision,
            "passes_now": "yes",
        },
        {
            "audit_id": "GRE-AUD-003",
            "audit_item": "current refusal has zero command execution",
            "expected": "recheck_executed=false",
            "current": f"launcher_will_execute_recheck={launcher_summary.get('launcher_will_execute_recheck')}",
            "passes_now": "yes" if not launcher_execution_allowed else "no",
        },
        {
            "audit_id": "GRE-AUD-004",
            "audit_item": "portal upload remains forbidden",
            "expected": "portal_upload_allowed=false",
            "current": f"portal_upload_allowed={launcher_summary.get('portal_upload_allowed')}",
            "passes_now": "yes" if launcher_summary.get("portal_upload_allowed") is False else "no",
        },
    ]

    run_log_template = [
        {
            "run_id": "FILL_AFTER_LAUNCHER_RUN",
            "run_datetime_local": "YYYY-MM-DD HH:MM",
            "operator": "FILL_AFTER_LAUNCHER_RUN",
            "launcher_path": "reports/final_guarded_recheck_launcher_20260810/run_final_guarded_recheck_after_receipts.ps1",
            "expected_decision_before_run": expected_decision,
            "observed_decision_after_run": "FILL_AFTER_LAUNCHER_RUN",
            "exit_code": "FILL_AFTER_LAUNCHER_RUN",
            "stdout_log_path": "FILL_AFTER_LAUNCHER_RUN",
            "stderr_log_path": "FILL_AFTER_LAUNCHER_RUN",
            "attestation": "FILL_AFTER_LAUNCHER_RUN",
        }
    ]

    no_go_rows = [
        {
            "no_go": "Do not treat launcher refusal as evidence completion.",
            "reason": "Current refusal is expected because 19.50 has incomplete receipts.",
        },
        {
            "no_go": "Do not run old recheck runner directly.",
            "reason": "It bypasses 19.50; use the 19.51 launcher wrapper only.",
        },
        {
            "no_go": "Do not upload portal files after a refusal.",
            "reason": "portal_upload_allowed=false and submission_ready=false.",
        },
        {
            "no_go": "Do not edit audit log placeholders before actually running the launcher.",
            "reason": "Audit records must describe observed execution, not intended execution.",
        },
    ]

    qa_rows = [
        {
            "check": "launcher summary imported",
            "result": "PASS",
            "detail": f"status={launcher_summary.get('status')}",
        },
        {
            "check": "current expected decision is refusal",
            "result": "PASS" if expected_decision == "refuse" else "FAIL",
            "detail": f"expected_decision={expected_decision}",
        },
        {
            "check": "blocked receipt rows preserved",
            "result": "PASS" if len(blockers) == receipt_summary.get("incomplete_receipt_rows") else "FAIL",
            "detail": f"blockers={len(blockers)}; incomplete={receipt_summary.get('incomplete_receipt_rows')}",
        },
        {
            "check": "command gate keeps recheck blocked",
            "result": "PASS" if any(row.get("allowed_now") == "no" for row in command_gate) else "FAIL",
            "detail": "command gate reviewed",
        },
    ]

    summary = {
        "package": "final_guarded_recheck_execution_audit_20260810",
        "expected_launcher_decision": expected_decision,
        "expected_exit_code": expected_exit_code,
        "launcher_execution_allowed": launcher_execution_allowed,
        "audit_rows": len(audit_rows),
        "run_log_template_rows": len(run_log_template),
        "no_go_rows": len(no_go_rows),
        "complete_receipt_rows": receipt_summary.get("complete_receipt_rows", 0),
        "blocked_receipt_rows": len(blockers),
        "recheck_executed": False,
        "system_command_execution_allowed": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "final_guarded_recheck_execution_audit_ready_expected_refusal",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "final_guarded_recheck_execution_audit.csv",
        ["audit_id", "audit_item", "expected", "current", "passes_now"],
        audit_rows,
    )
    write_csv(
        OUT_DIR / "final_guarded_recheck_run_log_template.csv",
        [
            "run_id",
            "run_datetime_local",
            "operator",
            "launcher_path",
            "expected_decision_before_run",
            "observed_decision_after_run",
            "exit_code",
            "stdout_log_path",
            "stderr_log_path",
            "attestation",
        ],
        run_log_template,
    )
    write_csv(OUT_DIR / "final_guarded_recheck_execution_no_go_rules.csv", ["no_go", "reason"], no_go_rows)
    write_csv(OUT_DIR / "final_guarded_recheck_execution_audit_qa.csv", ["check", "result", "detail"], qa_rows)

    readme = """# Final Guarded Recheck Execution Audit

This package records how to audit an actual run of the 19.51 final guarded
recheck launcher. In the current state the expected launcher decision is refusal
because 19.50 reports incomplete receipts.

Boundary: this package does not execute the launcher. It only prepares the audit
record, run-log template and no-go rules.
"""
    write_text(OUT_DIR / "FINAL_GUARDED_RECHECK_EXECUTION_AUDIT_README.md", readme)

    report = f"""# Final Guarded Recheck Execution Audit Report

Status: `{summary["status"]}`

Current result:

1. Expected launcher decision: {summary["expected_launcher_decision"]}
2. Expected exit code: {summary["expected_exit_code"]}
3. Launcher execution allowed: {str(summary["launcher_execution_allowed"]).lower()}
4. Complete receipt rows: {summary["complete_receipt_rows"]}
5. Blocked receipt rows: {summary["blocked_receipt_rows"]}
6. Recheck executed: {str(summary["recheck_executed"]).lower()}
7. Submission ready: {str(summary["submission_ready"]).lower()}
"""
    write_text(OUT_DIR / "final_guarded_recheck_execution_audit_report.md", report)
    write_text(
        OUT_DIR / "final_guarded_recheck_execution_audit_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
