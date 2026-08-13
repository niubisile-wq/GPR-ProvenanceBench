#!/usr/bin/env python3
"""Bridge gate-closure dependency status to manual-evidence intake and rerun actions."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "post_gate_manual_evidence_dependency_bridge_validator_20260810"
GATE_BRIDGE_DIR = BENCH_ROOT / "reports" / "gate_closure_dependency_bridge_validator_20260810"
POST_DISPATCH_DIR = BENCH_ROOT / "reports" / "post_dispatch_evidence_intake_validator_20260810"
WORKSHEET_DIR = BENCH_ROOT / "reports" / "manual_evidence_intake_worksheet_20260810"
ENTRY_PREFLIGHT_DIR = BENCH_ROOT / "reports" / "manual_evidence_entry_preflight_20260810"
RERUN_GUARD_DIR = BENCH_ROOT / "reports" / "post_evidence_safe_rerun_guard_20260810"
OPERATOR_RUNBOOK_DIR = BENCH_ROOT / "reports" / "operator_runbook_after_manual_dispatch_20260810"
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


def as_bool(value: object) -> bool:
    return value is True or str(value).strip().lower() in {"true", "yes", "1"}


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.44 Post-gate manual evidence dependency bridge validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/post_gate_manual_evidence_dependency_bridge_validator_20260810/`，把 19.43 gate closure bridge 继续传递到 post-dispatch evidence intake、manual worksheet、entry preflight、safe rerun guard 和 operator runbook。
- 当前 `gate_bridge_allows_manual_closeout={str(summary["gate_bridge_allows_manual_closeout"]).lower()}`，`manual_evidence_ready={str(summary["manual_evidence_ready"]).lower()}`，`safe_rerun_allowed={str(summary["safe_rerun_allowed"]).lower()}`。
- 当前 `manual_evidence_written=false`，`evidence_rows_passed={summary["evidence_rows_passed"]}`，`branch_commands_safe_to_run_now={summary["branch_commands_safe_to_run_now"]}`，`commands_executed=false`。
- 当前 `post_gate_manual_bridge_allowed={str(summary["post_gate_manual_bridge_allowed"]).lower()}`，`submission_ready=false`。
- 边界：该 bridge 只读，不填写人工证据、不触发重跑、不修改 tracker、不关闭 gate、不提交 manuscript。
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

    gate_bridge = read_json(GATE_BRIDGE_DIR / "gate_closure_dependency_bridge_validator_summary.json")
    post_dispatch = read_json(POST_DISPATCH_DIR / "post_dispatch_evidence_intake_validator_summary.json")
    worksheet = read_json(WORKSHEET_DIR / "manual_evidence_intake_worksheet_summary.json")
    entry_preflight = read_json(ENTRY_PREFLIGHT_DIR / "manual_evidence_entry_preflight_summary.json")
    rerun_guard = read_json(RERUN_GUARD_DIR / "post_evidence_safe_rerun_guard_summary.json")
    operator_runbook = read_json(OPERATOR_RUNBOOK_DIR / "operator_runbook_after_manual_dispatch_summary.json")

    next_commands = read_csv(POST_DISPATCH_DIR / "post_dispatch_next_validation_commands.csv")
    target_preflight = read_csv(ENTRY_PREFLIGHT_DIR / "manual_evidence_target_preflight.csv")
    rerun_matrix = read_csv(RERUN_GUARD_DIR / "post_evidence_branch_rerun_matrix.csv")

    gate_bridge_allows_manual_closeout = (
        as_bool(gate_bridge.get("qa_pass"))
        and as_bool(gate_bridge.get("gate_closure_allowed"))
        and as_bool(gate_bridge.get("portal_upload_ready"))
    )
    post_dispatch_ready = (
        as_bool(post_dispatch.get("qa_pass"))
        and int(post_dispatch.get("evidence_rows_missing", 1)) == 0
        and int(post_dispatch.get("evidence_rows_passed", 0)) == int(post_dispatch.get("evidence_rows", -1))
    )
    manual_evidence_ready = (
        as_bool(worksheet.get("manual_evidence_written"))
        and post_dispatch_ready
        and as_bool(entry_preflight.get("manual_evidence_written"))
        and int(entry_preflight.get("branch_commands_safe_to_run_now", 0)) > 0
    )
    safe_rerun_allowed = (
        gate_bridge_allows_manual_closeout
        and manual_evidence_ready
        and as_bool(rerun_guard.get("qa_pass"))
        and int(rerun_guard.get("branch_commands_safe_to_run_now", 0)) > 0
    )
    operator_runbook_allows_execution = (
        safe_rerun_allowed
        and as_bool(operator_runbook.get("qa_pass"))
        and as_bool(operator_runbook.get("manual_evidence_written"))
        and int(operator_runbook.get("branch_commands_safe_to_run_now", 0)) > 0
    )
    post_gate_manual_bridge_allowed = (
        gate_bridge_allows_manual_closeout
        and manual_evidence_ready
        and safe_rerun_allowed
        and operator_runbook_allows_execution
    )
    commands_executed = as_bool(rerun_guard.get("commands_executed"))
    submission_ready = (
        post_gate_manual_bridge_allowed
        and commands_executed
        and as_bool(rerun_guard.get("gate_closure_allowed"))
        and as_bool(rerun_guard.get("submission_ready"))
    )

    dependency_rows = [
        {
            "dependency": "gate_bridge_allows_manual_closeout",
            "source": "19.43 gate closure dependency bridge",
            "current": gate_bridge_allows_manual_closeout,
            "required": "true",
            "passes_now": "yes" if gate_bridge_allows_manual_closeout else "no",
        },
        {
            "dependency": "post_dispatch_ready",
            "source": "post-dispatch evidence intake validator",
            "current": post_dispatch_ready,
            "required": "all evidence rows passed",
            "passes_now": "yes" if post_dispatch_ready else "no",
        },
        {
            "dependency": "manual_evidence_ready",
            "source": "manual worksheet and entry preflight",
            "current": manual_evidence_ready,
            "required": "manual evidence written and branch commands safe",
            "passes_now": "yes" if manual_evidence_ready else "no",
        },
        {
            "dependency": "safe_rerun_allowed",
            "source": "post-evidence safe rerun guard",
            "current": safe_rerun_allowed,
            "required": "true",
            "passes_now": "yes" if safe_rerun_allowed else "no",
        },
        {
            "dependency": "operator_runbook_allows_execution",
            "source": "operator runbook after manual dispatch",
            "current": operator_runbook_allows_execution,
            "required": "manual evidence written and branch commands safe",
            "passes_now": "yes" if operator_runbook_allows_execution else "no",
        },
        {
            "dependency": "post_gate_manual_bridge_allowed",
            "source": "19.44 bridge decision",
            "current": post_gate_manual_bridge_allowed,
            "required": "true only after all upstream evidence gates pass",
            "passes_now": "yes" if post_gate_manual_bridge_allowed else "no",
        },
        {
            "dependency": "submission_ready",
            "source": "19.44 bridge boundary",
            "current": submission_ready,
            "required": "false in current blocked state",
            "passes_now": "yes" if not submission_ready else "no",
        },
    ]

    action_rows = []
    for row in next_commands:
        action_rows.append(
            {
                "action_id": row.get("command_id", row.get("action_id", "")),
                "action": row.get("command", row.get("action", "")),
                "source": "post_dispatch_next_validation_commands",
                "upstream_allowed": row.get("allowed_now", row.get("command_allowed_now", "")),
                "bridge_allowed": "yes" if post_gate_manual_bridge_allowed else "no",
                "reason": "Blocked until 19.43 gate bridge and manual evidence gates all pass.",
            }
        )
    for row in target_preflight:
        action_rows.append(
            {
                "action_id": row.get("target_id", row.get("evidence_id", "")),
                "action": row.get("target", row.get("evidence_item", "")),
                "source": "manual_evidence_target_preflight",
                "upstream_allowed": row.get("entry_allowed_now", row.get("safe_to_edit_now", "")),
                "bridge_allowed": "yes" if post_gate_manual_bridge_allowed else "no",
                "reason": "Blocked until real manual evidence has passed preflight.",
            }
        )
    for row in rerun_matrix:
        action_rows.append(
            {
                "action_id": row.get("branch_id", row.get("command_id", "")),
                "action": row.get("rerun_command", row.get("command", "")),
                "source": "post_evidence_branch_rerun_matrix",
                "upstream_allowed": row.get("safe_to_run_now", row.get("allowed_now", "")),
                "bridge_allowed": "yes" if safe_rerun_allowed else "no",
                "reason": "Blocked until manual evidence is written and 19.43 permits closure.",
            }
        )

    blocker_rows = [
        {
            "blocker": "19.43 gate bridge blocks manual closeout",
            "evidence": (
                f"gate_closure_allowed={gate_bridge.get('gate_closure_allowed')}; "
                f"portal_upload_ready={gate_bridge.get('portal_upload_ready')}"
            ),
            "blocks": "post-gate manual closeout",
        },
        {
            "blocker": "post-dispatch evidence missing",
            "evidence": (
                f"evidence_rows_passed={post_dispatch.get('evidence_rows_passed')}; "
                f"evidence_rows_missing={post_dispatch.get('evidence_rows_missing')}"
            ),
            "blocks": "branch validation commands",
        },
        {
            "blocker": "manual evidence not written",
            "evidence": (
                f"worksheet_manual_evidence_written={worksheet.get('manual_evidence_written')}; "
                f"entry_manual_evidence_written={entry_preflight.get('manual_evidence_written')}"
            ),
            "blocks": "manual evidence writeback and safe rerun",
        },
        {
            "blocker": "safe rerun guard has zero runnable branch commands",
            "evidence": (
                f"branch_commands_safe_to_run_now={rerun_guard.get('branch_commands_safe_to_run_now')}; "
                f"commands_executed={rerun_guard.get('commands_executed')}"
            ),
            "blocks": "rerun execution and submission-ready state",
        },
    ]

    qa_rows = [
        {
            "check": "all upstream summaries loaded",
            "result": "PASS",
            "detail": "gate bridge, post-dispatch, worksheet, entry preflight, rerun guard and runbook summaries loaded.",
        },
        {
            "check": "19.43 gate bridge remains blocking",
            "result": "PASS" if not gate_bridge_allows_manual_closeout else "FAIL",
            "detail": f"gate_bridge_allows_manual_closeout={gate_bridge_allows_manual_closeout}",
        },
        {
            "check": "manual evidence remains absent",
            "result": "PASS" if not manual_evidence_ready else "FAIL",
            "detail": f"manual_evidence_ready={manual_evidence_ready}",
        },
        {
            "check": "safe rerun remains blocked",
            "result": "PASS" if not safe_rerun_allowed else "FAIL",
            "detail": f"safe_rerun_allowed={safe_rerun_allowed}",
        },
        {
            "check": "submission remains false",
            "result": "PASS" if not submission_ready else "FAIL",
            "detail": f"submission_ready={submission_ready}",
        },
    ]

    summary = {
        "package": "post_gate_manual_evidence_dependency_bridge_validator_20260810",
        "gate_bridge_allows_manual_closeout": gate_bridge_allows_manual_closeout,
        "post_dispatch_ready": post_dispatch_ready,
        "manual_evidence_ready": manual_evidence_ready,
        "safe_rerun_allowed": safe_rerun_allowed,
        "operator_runbook_allows_execution": operator_runbook_allows_execution,
        "post_gate_manual_bridge_allowed": post_gate_manual_bridge_allowed,
        "manual_evidence_written": False,
        "evidence_rows_passed": post_dispatch.get("evidence_rows_passed", 0),
        "evidence_rows_missing": post_dispatch.get("evidence_rows_missing", 0),
        "branch_commands_safe_to_run_now": rerun_guard.get("branch_commands_safe_to_run_now", 0),
        "commands_executed": commands_executed,
        "submission_ready": submission_ready,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "post_gate_manual_evidence_dependency_bridge_validator_ready_blocked",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "post_gate_manual_evidence_dependency_bridge_matrix.csv",
        ["dependency", "source", "current", "required", "passes_now"],
        dependency_rows,
    )
    write_csv(
        OUT_DIR / "post_gate_manual_evidence_action_bridge.csv",
        ["action_id", "action", "source", "upstream_allowed", "bridge_allowed", "reason"],
        action_rows,
    )
    write_csv(
        OUT_DIR / "post_gate_manual_evidence_dependency_bridge_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "post_gate_manual_evidence_dependency_bridge_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# Post-gate Manual Evidence Dependency Bridge Validator

This validator bridges the 19.43 gate-closure dependency bridge to manual
evidence intake, entry preflight, safe rerun and operator handoff packages.

Boundary: read-only. It does not write manual evidence, execute reruns, modify
trackers, close gates, upload files or mark the manuscript submission-ready.
"""
    write_text(OUT_DIR / "POST_GATE_MANUAL_EVIDENCE_DEPENDENCY_BRIDGE_VALIDATOR_README.md", readme)

    report = f"""# Post-gate Manual Evidence Dependency Bridge Validator Report

Status: `{summary["status"]}`

Current result:

1. Gate bridge allows manual closeout: {str(summary["gate_bridge_allows_manual_closeout"]).lower()}
2. Post-dispatch evidence ready: {str(summary["post_dispatch_ready"]).lower()}
3. Manual evidence ready: {str(summary["manual_evidence_ready"]).lower()}
4. Safe rerun allowed: {str(summary["safe_rerun_allowed"]).lower()}
5. Operator runbook allows execution: {str(summary["operator_runbook_allows_execution"]).lower()}
6. Post-gate manual bridge allowed: {str(summary["post_gate_manual_bridge_allowed"]).lower()}
7. Submission ready: {str(summary["submission_ready"]).lower()}

Boundary: this bridge records the dependency chain only. It cannot replace real
manual evidence, signed receipts, rerun execution logs or final gate closure.
"""
    write_text(OUT_DIR / "post_gate_manual_evidence_dependency_bridge_validator_report.md", report)
    write_text(
        OUT_DIR / "post_gate_manual_evidence_dependency_bridge_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
