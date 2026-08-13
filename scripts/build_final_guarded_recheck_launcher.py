#!/usr/bin/env python3
"""Build a guarded launcher that refuses recheck unless 19.50 allows it."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_guarded_recheck_launcher_20260810"
RECEIPT_VALIDATOR_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_completion_validator_20260810"
RECHECK_RUNNER_DIR = BENCH_ROOT / "reports" / "manual_post_handoff_recheck_runner_20260810"
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
    marker = "### 19.51 Final guarded recheck launcher update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/final_guarded_recheck_launcher_20260810/`，生成 `run_final_guarded_recheck_after_receipts.ps1`，复跑前强制读取 19.50。
- 当前 `guarded_recheck_allowed={str(summary["guarded_recheck_allowed"]).lower()}`，`launcher_will_execute_recheck=false`，`blocked_receipt_rows={summary["blocked_receipt_rows"]}`。
- 当前 `required_complete_receipts=6`，`complete_receipt_rows={summary["complete_receipt_rows"]}`，`incomplete_receipt_rows={summary["incomplete_receipt_rows"]}`。
- 当前 `system_command_execution_allowed=false`，`portal_upload_allowed=false`，`submission_ready=false`。
- 边界：该 launcher 当前只会拒绝执行，不运行 M0-M2、不写入人工证据、不关闭 gate、不上传 portal。
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

    receipt_summary = read_json(RECEIPT_VALIDATOR_DIR / "final_manual_receipt_completion_validator_summary.json")
    receipt_status = read_csv(RECEIPT_VALIDATOR_DIR / "final_manual_receipt_completion_status.csv")
    old_runner_summary = read_json(RECHECK_RUNNER_DIR / "manual_post_handoff_recheck_runner_summary.json")

    guarded_recheck_allowed = receipt_summary.get("guarded_recheck_allowed") is True
    blocked_rows = [row for row in receipt_status if row.get("completion_passes_now") != "yes"]
    launcher_will_execute_recheck = guarded_recheck_allowed

    command_rows = [
        {
            "sequence": 1,
            "command": "py scripts/build_final_manual_receipt_completion_validator.py",
            "purpose": "refresh 19.50 receipt completion state",
            "allowed_now": "yes",
        },
        {
            "sequence": 2,
            "command": "reports/manual_post_handoff_recheck_runner_20260810/run_after_manual_evidence_recheck.ps1",
            "purpose": "guarded diagnostic recheck only after 19.50 passes",
            "allowed_now": "yes" if guarded_recheck_allowed else "no",
        },
        {
            "sequence": 3,
            "command": "powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1",
            "purpose": "full re-evaluation only after all receipts complete",
            "allowed_now": "yes" if guarded_recheck_allowed else "no",
        },
    ]

    blocker_rows = [
        {
            "receipt_id": row.get("receipt_id", ""),
            "receipt_type": row.get("receipt_type", ""),
            "current_status": row.get("current_status", ""),
            "placeholder_value": row.get("placeholder_value", ""),
            "blocks": "final guarded recheck launcher",
        }
        for row in blocked_rows
    ]

    qa_rows = [
        {
            "check": "19.50 summary loaded",
            "result": "PASS",
            "detail": f"guarded_recheck_allowed={guarded_recheck_allowed}",
        },
        {
            "check": "launcher refuses current incomplete receipts",
            "result": "PASS" if not launcher_will_execute_recheck else "FAIL",
            "detail": f"blocked_receipt_rows={len(blocked_rows)}",
        },
        {
            "check": "old runner remains wrapped",
            "result": "PASS" if old_runner_summary.get("commands_executed_by_builder") is False else "FAIL",
            "detail": f"old_runner={old_runner_summary.get('runner_script')}",
        },
        {
            "check": "portal upload remains impossible",
            "result": "PASS" if receipt_summary.get("portal_upload_allowed") is False else "FAIL",
            "detail": f"portal_upload_allowed={receipt_summary.get('portal_upload_allowed')}",
        },
    ]

    launcher = r"""param(
    [switch]$FullM0M2
)

$ErrorActionPreference = "Stop"
$Bench = (Get-Item $PSScriptRoot).Parent.Parent.FullName
Set-Location $Bench

py scripts\build_final_manual_receipt_completion_validator.py
if ($LASTEXITCODE -ne 0) {
    throw "19.50 receipt completion validator failed"
}

$SummaryPath = Join-Path $Bench "reports\final_manual_receipt_completion_validator_20260810\final_manual_receipt_completion_validator_summary.json"
$Summary = Get-Content -LiteralPath $SummaryPath -Raw | ConvertFrom-Json

if (-not $Summary.guarded_recheck_allowed) {
    Write-Host "FINAL GUARDED RECHECK REFUSED"
    Write-Host "Reason: 19.50 guarded_recheck_allowed=false."
    Write-Host "Complete receipt rows:" $Summary.complete_receipt_rows
    Write-Host "Incomplete receipt rows:" $Summary.incomplete_receipt_rows
    Write-Host "No M0-M2, writeback, gate closure, portal upload or submission command was executed."
    exit 0
}

Write-Host "19.50 permits guarded recheck. Running status-only recheck runner."
powershell -ExecutionPolicy Bypass -File reports\manual_post_handoff_recheck_runner_20260810\run_after_manual_evidence_recheck.ps1
if ($LASTEXITCODE -ne 0) {
    throw "Guarded recheck runner failed"
}

if ($FullM0M2) {
    powershell -ExecutionPolicy Bypass -File scripts\run_m0_m2_checks.ps1
    if ($LASTEXITCODE -ne 0) {
        throw "Full M0-M2 failed"
    }
}

Write-Host "FINAL GUARDED RECHECK COMPLETE. Portal upload and submission still require 19.47 to pass."
"""

    summary = {
        "package": "final_guarded_recheck_launcher_20260810",
        "guarded_recheck_allowed": guarded_recheck_allowed,
        "launcher_will_execute_recheck": launcher_will_execute_recheck,
        "receipt_rows": receipt_summary.get("receipt_rows", 0),
        "complete_receipt_rows": receipt_summary.get("complete_receipt_rows", 0),
        "incomplete_receipt_rows": receipt_summary.get("incomplete_receipt_rows", 0),
        "blocked_receipt_rows": len(blocked_rows),
        "system_command_execution_allowed": launcher_will_execute_recheck,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "final_guarded_recheck_launcher_ready_refuses_current_state",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "final_guarded_recheck_command_gate.csv",
        ["sequence", "command", "purpose", "allowed_now"],
        command_rows,
    )
    write_csv(
        OUT_DIR / "final_guarded_recheck_blockers.csv",
        ["receipt_id", "receipt_type", "current_status", "placeholder_value", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "final_guarded_recheck_launcher_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )
    write_text(OUT_DIR / "run_final_guarded_recheck_after_receipts.ps1", launcher)

    readme = """# Final Guarded Recheck Launcher

This package creates a launcher that refreshes the 19.50 final manual receipt
completion validator before any post-receipt recheck can run.

Boundary: in the current state the launcher refuses execution. It does not write
manual evidence, close gates, upload portal files or mark the manuscript
submission-ready.
"""
    write_text(OUT_DIR / "FINAL_GUARDED_RECHECK_LAUNCHER_README.md", readme)
    report = f"""# Final Guarded Recheck Launcher Report

Status: `{summary["status"]}`

Current result:

1. Guarded recheck allowed: {str(summary["guarded_recheck_allowed"]).lower()}
2. Launcher will execute recheck: {str(summary["launcher_will_execute_recheck"]).lower()}
3. Complete receipt rows: {summary["complete_receipt_rows"]}
4. Incomplete receipt rows: {summary["incomplete_receipt_rows"]}
5. Portal upload allowed: {str(summary["portal_upload_allowed"]).lower()}
6. Submission ready: {str(summary["submission_ready"]).lower()}
"""
    write_text(OUT_DIR / "final_guarded_recheck_launcher_report.md", report)
    write_text(
        OUT_DIR / "final_guarded_recheck_launcher_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
