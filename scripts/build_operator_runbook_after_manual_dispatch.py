#!/usr/bin/env python3
"""Build an operator runbook for manual evidence intake after dispatch."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "operator_runbook_after_manual_dispatch_20260810"
DESKTOP = Path.home() / "Desktop"
DESKTOP_PLAN = DESKTOP / "8月10日cns.md"
DESKTOP_RUNBOOK = DESKTOP / "NatComms_人工证据填写与重跑说明_20260810.md"
DESKTOP_DISPATCH_ZIP = DESKTOP / "NatComms_manual_dispatch_master_packet_20260810.zip"

WORKSHEET_SUMMARY = REPORTS / "manual_evidence_intake_worksheet_20260810" / "manual_evidence_intake_worksheet_summary.json"
VALIDATOR_SUMMARY = REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_evidence_intake_validator_summary.json"
RERUN_SUMMARY = REPORTS / "post_evidence_safe_rerun_guard_20260810" / "post_evidence_safe_rerun_guard_summary.json"
DISPATCH_SUMMARY = REPORTS / "manual_dispatch_master_packet_20260810" / "manual_dispatch_master_packet_summary.json"
WORKSHEET = REPORTS / "manual_evidence_intake_worksheet_20260810" / "manual_evidence_intake_worksheet.csv"
BRANCH_RERUN = REPORTS / "post_evidence_safe_rerun_guard_20260810" / "post_evidence_branch_rerun_matrix.csv"


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
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 18.84 Operator runbook after manual dispatch update"
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

    worksheet_summary = read_json(WORKSHEET_SUMMARY)
    validator_summary = read_json(VALIDATOR_SUMMARY)
    rerun_summary = read_json(RERUN_SUMMARY)
    dispatch_summary = read_json(DISPATCH_SUMMARY)
    worksheet_rows = read_csv(WORKSHEET)
    branch_rows = read_csv(BRANCH_RERUN)

    dispatch_zip = DESKTOP_DISPATCH_ZIP if DESKTOP_DISPATCH_ZIP.exists() else Path(str(dispatch_summary.get("desktop_zip", "")))

    quickstart_rows = [
        {
            "step": 1,
            "operator_action": "Open the Desktop master dispatch zip and send/request the required materials manually.",
            "file_to_use": str(dispatch_zip),
            "do_not_do": "Do not mark email_sent or gate closure until real evidence exists.",
        },
        {
            "step": 2,
            "operator_action": "When real evidence returns, open the worksheet and fill only the target fields listed.",
            "file_to_use": str(WORKSHEET.relative_to(BENCH_ROOT)),
            "do_not_do": "Do not edit checksum, recommendation, allowed-values, source, evidence or gate-effect fields.",
        },
        {
            "step": 3,
            "operator_action": "Rerun the post-dispatch evidence intake validator.",
            "file_to_use": r"py scripts\build_post_dispatch_evidence_intake_validator.py",
            "do_not_do": "Do not run branch validators until the evidence row passes.",
        },
        {
            "step": 4,
            "operator_action": "Check the safe rerun guard and run only branches marked safe.",
            "file_to_use": str(BRANCH_RERUN.relative_to(BENCH_ROOT)),
            "do_not_do": "Do not run finalization or portal upload while branch commands remain blocked.",
        },
        {
            "step": 5,
            "operator_action": "After branch validators pass, rerun gate binder, dashboard, completion ledger and full M0-M2.",
            "file_to_use": r"powershell -ExecutionPolicy Bypass -File scripts\run_m0_m2_checks.ps1",
            "do_not_do": "Do not interpret full checks as submission-ready unless dashboard says submission_ready=true.",
        },
    ]

    runbook = f"""# NatComms 人工证据填写与安全重跑说明 2026-08-10

当前状态：还不能投稿。这个说明只告诉操作者如何在真实人工证据出现后填写和重跑。

## 先看这三个文件

1. Master dispatch zip: `{dispatch_zip}`
2. Evidence worksheet: `{WORKSHEET}`
3. Safe rerun matrix: `{BRANCH_RERUN}`

## 操作顺序

1. 先真实发送或真实获取材料；没有证据时，不要填写 `sent`、backend、rights、Reporting Summary 或 reference 授权。
2. 有真实证据后，只按 worksheet 的 `target_file`、`fields_to_fill` 和 `allowed_values_or_format` 填写。
3. 填完先运行：

```powershell
py scripts\\build_post_dispatch_evidence_intake_validator.py
```

4. 再查看：

```text
reports\\post_evidence_safe_rerun_guard_20260810\\post_evidence_branch_rerun_matrix.csv
```

5. 只有 `blocked_now=no` 的分支命令可以继续跑。
6. 最后再运行完整检查：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\\run_m0_m2_checks.ps1
```

## 当前数字

1. worksheet rows: {worksheet_summary.get('worksheet_rows')}
2. evidence rows passed: {validator_summary.get('evidence_rows_passed')}
3. branch commands safe now: {rerun_summary.get('branch_commands_safe_to_run_now')}
4. submission_ready: false

## 禁止操作

1. 不要用 recommended choice 代替作者选择。
2. 不要把 template dry run 写成 blind external validation。
3. 不要在没有 DOI/licence/rights 证据时写 public availability。
4. 不要在 final prose 和 figure/table calls 稳定前替换 `[P#]`。
5. 不要在 dashboard 仍为 `submission_ready=false` 时投稿。
"""

    write_csv(OUT_DIR / "operator_runbook_quickstart.csv", quickstart_rows, ["step", "operator_action", "file_to_use", "do_not_do"])
    write_text(OUT_DIR / "OPERATOR_RUNBOOK_AFTER_MANUAL_DISPATCH.md", runbook)
    shutil.copy2(OUT_DIR / "OPERATOR_RUNBOOK_AFTER_MANUAL_DISPATCH.md", DESKTOP_RUNBOOK)

    qa_rows = [
        {
            "check": "worksheet_and_rerun_guard_imported",
            "result": "PASS" if worksheet_summary.get("qa_pass") and rerun_summary.get("qa_pass") else "FAIL",
            "detail": f"worksheet_rows={len(worksheet_rows)}; branch_rows={len(branch_rows)}",
        },
        {
            "check": "desktop_runbook_created",
            "result": "PASS" if DESKTOP_RUNBOOK.exists() else "FAIL",
            "detail": str(DESKTOP_RUNBOOK),
        },
        {
            "check": "runbook_preserves_not_ready_state",
            "result": "PASS" if validator_summary.get("submission_ready") is False and rerun_summary.get("submission_ready") is False else "FAIL",
            "detail": f"evidence_rows_passed={validator_summary.get('evidence_rows_passed')}",
        },
        {
            "check": "no_manual_evidence_written",
            "result": "PASS",
            "detail": "Runbook is documentation only.",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)
    write_csv(OUT_DIR / "operator_runbook_after_manual_dispatch_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Operator runbook after manual dispatch report 2026-08-10",
        "",
        "Status: `operator_runbook_ready_manual_evidence_not_entered`",
        "",
        f"1. Quickstart rows: {len(quickstart_rows)}",
        f"2. Desktop runbook: `{DESKTOP_RUNBOOK}`",
        f"3. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: a one-page operator runbook is available on Desktop, but no manual evidence is entered and submission remains not ready.",
        "",
    ]
    write_text(OUT_DIR / "operator_runbook_after_manual_dispatch_report.md", "\n".join(report))

    summary = {
        "package": "operator_runbook_after_manual_dispatch_20260810",
        "quickstart_rows": len(quickstart_rows),
        "desktop_runbook": str(DESKTOP_RUNBOOK),
        "desktop_runbook_exists": DESKTOP_RUNBOOK.exists(),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "manual_evidence_written": False,
        "branch_commands_safe_to_run_now": rerun_summary.get("branch_commands_safe_to_run_now"),
        "submission_ready": False,
        "status": "operator_runbook_ready_manual_evidence_not_entered",
    }

    section = f"""### 18.84 Operator runbook after manual dispatch update

Added a one-page operator runbook for manual evidence entry and safe rerun after dispatch.

New directory: `{OUT_DIR}`

Desktop runbook: `{DESKTOP_RUNBOOK}`

New files:
1. `operator_runbook_quickstart.csv`
2. `OPERATOR_RUNBOOK_AFTER_MANUAL_DISPATCH.md`
3. `operator_runbook_after_manual_dispatch_qa.csv`
4. `operator_runbook_after_manual_dispatch_report.md`
5. `operator_runbook_after_manual_dispatch_summary.json`

Current result:
1. quickstart_rows = {summary['quickstart_rows']}
2. desktop_runbook_exists = {str(summary['desktop_runbook_exists']).lower()}
3. qa_pass = {str(qa_pass).lower()}
4. manual_evidence_written = false
5. branch_commands_safe_to_run_now = {summary['branch_commands_safe_to_run_now']}
6. submission_ready = false
7. status = `operator_runbook_ready_manual_evidence_not_entered`

Boundary:
1. This step does not enter manual evidence.
2. This step does not run branch validators.
3. This step does not close gates or make the manuscript submission-ready."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "operator_runbook_after_manual_dispatch_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Operator runbook QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
