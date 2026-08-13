#!/usr/bin/env python3
"""Bridge post-writeback transition dependencies to RB-002 entry and guarded execution."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "post_writeback_transition_dependency_bridge_validator_20260810"
RB002_BRIDGE_DIR = BENCH_ROOT / "reports" / "rb002_entry_dependency_bridge_validator_20260810"
TRANSITION_DIR = BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810"
RUNNER_DIR = BENCH_ROOT / "reports" / "post_return_guarded_execution_runner_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


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
    marker = "### 19.42 Post-writeback transition dependency bridge validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/post_writeback_transition_dependency_bridge_validator_20260810/`，把 19.41 RB-002 entry bridge、post-writeback transition validator 和 guarded execution runner 绑定成 transition/route-command 的总前置门。
- 当前 `rb002_entry_allowed={str(summary["rb002_entry_allowed"]).lower()}`，`post_writeback_transition_ready={str(summary["post_writeback_transition_ready"]).lower()}`，`guarded_runner_ready={str(summary["guarded_runner_ready"]).lower()}`。
- 当前 `transition_bridge_allowed={str(summary["transition_bridge_allowed"]).lower()}`，`route_command_execution_allowed={str(summary["route_command_execution_allowed"]).lower()}`，`gate_closure_allowed={str(summary["gate_closure_allowed"]).lower()}`。
- 当前 `commands_allowed_now=0`，`transition_allowed_rows=0`，`submission_ready=false`。
- 边界：该 bridge 只读依赖状态，不运行 route validators、不执行 guarded runner、不关闭 gate、不提交 manuscript。
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

    rb002_bridge = read_json(RB002_BRIDGE_DIR / "rb002_entry_dependency_bridge_validator_summary.json")
    transition_summary = read_json(TRANSITION_DIR / "post_writeback_gate_transition_validator_summary.json")
    runner_summary = read_json(RUNNER_DIR / "post_return_guarded_execution_runner_summary.json")
    route_matrix = read_csv(TRANSITION_DIR / "post_writeback_route_transition_matrix.csv")
    guarded_plan = read_csv(RUNNER_DIR / "post_return_guarded_command_plan.csv")

    rb002_entry_allowed = rb002_bridge.get("rb002_entry_allowed") is True
    post_writeback_transition_ready = (
        transition_summary.get("qa_pass") is True
        and transition_summary.get("transition_allowed_rows", 0) > 0
        and transition_summary.get("open_evidence_requirements", 1) == 0
        and transition_summary.get("gate_closure_allowed") is True
    )
    guarded_runner_ready = (
        runner_summary.get("qa_pass") is True
        and runner_summary.get("commands_allowed_now", 0) > 0
        and runner_summary.get("global_guards_passing", 0) == runner_summary.get("global_guards", -1)
    )
    transition_bridge_allowed = rb002_entry_allowed and post_writeback_transition_ready
    route_command_execution_allowed = transition_bridge_allowed and guarded_runner_ready
    gate_closure_allowed = route_command_execution_allowed and transition_summary.get("open_master_gates", 1) == 0
    submission_ready = gate_closure_allowed and transition_summary.get("submission_ready") is True

    route_rows = []
    for row in route_matrix:
        route_rows.append(
            {
                "route_id": row.get("route_id", ""),
                "command": row.get("command", ""),
                "mapped_gate_id": row.get("mapped_gate_id", ""),
                "command_currently_allowed": row.get("command_currently_allowed", ""),
                "transition_allowed_now": row.get("transition_allowed_now", ""),
                "bridge_execution_allowed": "yes" if route_command_execution_allowed and row.get("transition_allowed_now") == "yes" else "no",
                "reason": "Blocked by RB-002 entry bridge or post-writeback transition guard.",
            }
        )

    dependency_rows = [
        {
            "dependency": "rb002_entry_allowed",
            "source": "19.41 RB-002 entry bridge",
            "current": rb002_entry_allowed,
            "required": "true",
            "passes_now": "yes" if rb002_entry_allowed else "no",
        },
        {
            "dependency": "post_writeback_transition_ready",
            "source": "post-writeback transition validator",
            "current": post_writeback_transition_ready,
            "required": "true",
            "passes_now": "yes" if post_writeback_transition_ready else "no",
        },
        {
            "dependency": "guarded_runner_ready",
            "source": "post-return guarded execution runner",
            "current": guarded_runner_ready,
            "required": "true",
            "passes_now": "yes" if guarded_runner_ready else "no",
        },
        {
            "dependency": "transition_bridge_allowed",
            "source": "bridge decision",
            "current": transition_bridge_allowed,
            "required": "true",
            "passes_now": "yes" if transition_bridge_allowed else "no",
        },
        {
            "dependency": "route_command_execution_allowed",
            "source": "bridge decision",
            "current": route_command_execution_allowed,
            "required": "true",
            "passes_now": "yes" if route_command_execution_allowed else "no",
        },
        {
            "dependency": "gate_closure_allowed",
            "source": "bridge decision",
            "current": gate_closure_allowed,
            "required": "true",
            "passes_now": "yes" if gate_closure_allowed else "no",
        },
        {
            "dependency": "submission_ready",
            "source": "bridge boundary",
            "current": submission_ready,
            "required": "false in current state",
            "passes_now": "yes" if not submission_ready else "no",
        },
    ]

    blocker_rows = [
        {
            "blocker": "RB-002 entry bridge blocked",
            "evidence": f"rb002_entry_allowed={rb002_bridge.get('rb002_entry_allowed')}; transition_allowed={rb002_bridge.get('transition_allowed')}",
            "blocks": "post-writeback transition",
        },
        {
            "blocker": "no transition rows allowed",
            "evidence": f"transition_allowed_rows={transition_summary.get('transition_allowed_rows')}; open_evidence_requirements={transition_summary.get('open_evidence_requirements')}",
            "blocks": "route command execution",
        },
        {
            "blocker": "guarded runner refuses commands",
            "evidence": f"commands_allowed_now={runner_summary.get('commands_allowed_now')}; commands_blocked_now={runner_summary.get('commands_blocked_now')}",
            "blocks": "route command execution",
        },
        {
            "blocker": "master gates remain open",
            "evidence": f"open_master_gates={transition_summary.get('open_master_gates')}; portal_upload_ready_rows={transition_summary.get('portal_upload_ready_rows')}",
            "blocks": "gate closure and portal upload",
        },
    ]

    qa_rows = [
        {
            "check": "all upstream summaries loaded",
            "result": "PASS",
            "detail": "rb002 bridge, transition and runner summaries loaded.",
        },
        {
            "check": "bridge keeps transition blocked",
            "result": "PASS" if not transition_bridge_allowed else "FAIL",
            "detail": f"transition_bridge_allowed={transition_bridge_allowed}",
        },
        {
            "check": "bridge keeps route commands blocked",
            "result": "PASS" if not route_command_execution_allowed else "FAIL",
            "detail": f"route_command_execution_allowed={route_command_execution_allowed}",
        },
        {
            "check": "runner has zero allowed commands",
            "result": "PASS" if runner_summary.get("commands_allowed_now") == 0 else "FAIL",
            "detail": f"commands_allowed_now={runner_summary.get('commands_allowed_now')}",
        },
        {
            "check": "submission remains false",
            "result": "PASS" if not submission_ready else "FAIL",
            "detail": f"submission_ready={submission_ready}",
        },
    ]

    summary = {
        "package": "post_writeback_transition_dependency_bridge_validator_20260810",
        "rb002_entry_allowed": rb002_entry_allowed,
        "post_writeback_transition_ready": post_writeback_transition_ready,
        "guarded_runner_ready": guarded_runner_ready,
        "transition_bridge_allowed": transition_bridge_allowed,
        "route_command_execution_allowed": route_command_execution_allowed,
        "gate_closure_allowed": gate_closure_allowed,
        "commands_allowed_now": runner_summary.get("commands_allowed_now", 0),
        "transition_allowed_rows": transition_summary.get("transition_allowed_rows", 0),
        "open_master_gates": transition_summary.get("open_master_gates", 0),
        "submission_ready": submission_ready,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "post_writeback_transition_dependency_bridge_validator_ready_blocked_by_rb002",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "post_writeback_transition_dependency_bridge_matrix.csv",
        ["dependency", "source", "current", "required", "passes_now"],
        dependency_rows,
    )
    write_csv(
        OUT_DIR / "post_writeback_transition_route_execution_bridge.csv",
        ["route_id", "command", "mapped_gate_id", "command_currently_allowed", "transition_allowed_now", "bridge_execution_allowed", "reason"],
        route_rows,
    )
    write_csv(
        OUT_DIR / "post_writeback_transition_dependency_bridge_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "post_writeback_transition_dependency_bridge_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# Post-writeback Transition Dependency Bridge Validator

This validator bridges RB-002 entry, post-writeback transition validation and
the guarded execution runner before any route-specific command can execute.

Boundary: it is read-only. It does not run route validators, execute the guarded
runner, close gates, upload files or make the manuscript submission-ready.
"""
    write_text(OUT_DIR / "POST_WRITEBACK_TRANSITION_DEPENDENCY_BRIDGE_VALIDATOR_README.md", readme)

    report = f"""# Post-writeback Transition Dependency Bridge Validator Report

Status: `{summary["status"]}`

Current result:

1. RB-002 entry allowed: {str(summary["rb002_entry_allowed"]).lower()}
2. Post-writeback transition ready: {str(summary["post_writeback_transition_ready"]).lower()}
3. Guarded runner ready: {str(summary["guarded_runner_ready"]).lower()}
4. Transition bridge allowed: {str(summary["transition_bridge_allowed"]).lower()}
5. Route command execution allowed: {str(summary["route_command_execution_allowed"]).lower()}
6. Gate closure allowed: {str(summary["gate_closure_allowed"]).lower()}
7. Commands allowed now: {summary["commands_allowed_now"]}
8. Transition allowed rows: {summary["transition_allowed_rows"]}
9. Open master gates: {summary["open_master_gates"]}
10. Submission ready: false

Interpretation: transition and route-specific execution now explicitly depend
on the RB-002 entry bridge. Current state remains blocked before any transition
or guarded route command execution.
"""
    write_text(OUT_DIR / "post_writeback_transition_dependency_bridge_validator_report.md", report)
    write_text(
        OUT_DIR / "post_writeback_transition_dependency_bridge_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("Post-writeback transition dependency bridge validator QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
