#!/usr/bin/env python3
"""Bridge transition, gate-closure and final-lock dependencies."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "gate_closure_dependency_bridge_validator_20260810"
TRANSITION_BRIDGE_DIR = BENCH_ROOT / "reports" / "post_writeback_transition_dependency_bridge_validator_20260810"
GATE_BINDER_DIR = BENCH_ROOT / "reports" / "natcomms_gate_closure_evidence_binder_20260810"
GATE_BOARD_DIR = BENCH_ROOT / "reports" / "gate_closure_execution_board_20260810"
FINAL_LOCK_DIR = BENCH_ROOT / "reports" / "natcomms_submission_final_lock_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


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


def as_bool(value: object) -> bool:
    return value is True or str(value).strip().lower() in {"true", "yes", "1"}


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.43 Gate closure dependency bridge validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/gate_closure_dependency_bridge_validator_20260810/`，把 19.42 transition bridge、gate closure evidence binder、gate closure execution board 和 NatComms submission final lock 串成最终关门前置链。
- 当前 `transition_bridge_allows_gate_closure={str(summary["transition_bridge_allows_gate_closure"]).lower()}`，`binder_allows_gate_closure={str(summary["binder_allows_gate_closure"]).lower()}`，`execution_board_allows_gate_closure={str(summary["execution_board_allows_gate_closure"]).lower()}`。
- 当前 `final_lock_allows_submission={str(summary["final_lock_allows_submission"]).lower()}`，`portal_upload_ready={str(summary["portal_upload_ready"]).lower()}`，`submission_ready=false`。
- 当前 `open_master_gates={summary["open_master_gates"]}`，`open_evidence_requirements={summary["open_evidence_requirements"]}`，`commands_allowed_now={summary["commands_allowed_now"]}`。
- 边界：该 bridge 只读，不关闭 gate、不执行命令、不上传 portal 文件、不生成最终提交结论。
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

    transition_bridge = read_json(
        TRANSITION_BRIDGE_DIR / "post_writeback_transition_dependency_bridge_validator_summary.json"
    )
    binder = read_json(GATE_BINDER_DIR / "gate_closure_evidence_binder_summary.json")
    execution_board = read_json(GATE_BOARD_DIR / "gate_closure_execution_board_summary.json")
    final_lock = read_json(FINAL_LOCK_DIR / "natcomms_submission_final_lock_validator_summary.json")

    binder_rows = read_csv(GATE_BINDER_DIR / "gate_closure_evidence_binder.csv")
    board_rows = read_csv(GATE_BOARD_DIR / "gate_closure_execution_board.csv")
    final_lock_blockers = read_csv(FINAL_LOCK_DIR / "natcomms_submission_final_lock_blockers.csv")

    transition_bridge_allows_gate_closure = as_bool(transition_bridge.get("gate_closure_allowed"))
    binder_allows_gate_closure = (
        as_bool(binder.get("qa_pass"))
        and int(binder.get("open_evidence_requirements", 1)) == 0
        and as_bool(binder.get("gate_closure_allowed"))
    )
    execution_board_allows_gate_closure = (
        as_bool(execution_board.get("qa_pass"))
        and as_bool(execution_board.get("gate_closure_allowed"))
        and as_bool(execution_board.get("portal_upload_ready"))
    )
    final_lock_allows_submission = (
        as_bool(final_lock.get("qa_pass"))
        and as_bool(final_lock.get("gate_closure_allowed"))
        and as_bool(final_lock.get("portal_upload_ready"))
        and as_bool(final_lock.get("submission_ready"))
        and int(final_lock.get("open_master_gates", 1)) == 0
    )

    gate_closure_dependency_ready = (
        transition_bridge_allows_gate_closure
        and binder_allows_gate_closure
        and execution_board_allows_gate_closure
    )
    gate_closure_allowed = gate_closure_dependency_ready and final_lock_allows_submission
    portal_upload_ready = gate_closure_allowed and as_bool(final_lock.get("portal_upload_ready"))
    submission_ready = gate_closure_allowed and portal_upload_ready and as_bool(final_lock.get("submission_ready"))

    dependency_rows = [
        {
            "dependency": "transition_bridge_allows_gate_closure",
            "source": "19.42 post-writeback transition dependency bridge",
            "current": transition_bridge_allows_gate_closure,
            "required": "true",
            "passes_now": "yes" if transition_bridge_allows_gate_closure else "no",
        },
        {
            "dependency": "binder_allows_gate_closure",
            "source": "NatComms gate closure evidence binder",
            "current": binder_allows_gate_closure,
            "required": "true and open_evidence_requirements=0",
            "passes_now": "yes" if binder_allows_gate_closure else "no",
        },
        {
            "dependency": "execution_board_allows_gate_closure",
            "source": "gate closure execution board",
            "current": execution_board_allows_gate_closure,
            "required": "true and portal_upload_ready=true",
            "passes_now": "yes" if execution_board_allows_gate_closure else "no",
        },
        {
            "dependency": "final_lock_allows_submission",
            "source": "NatComms submission final lock validator",
            "current": final_lock_allows_submission,
            "required": "true with open_master_gates=0",
            "passes_now": "yes" if final_lock_allows_submission else "no",
        },
        {
            "dependency": "gate_closure_allowed",
            "source": "19.43 bridge decision",
            "current": gate_closure_allowed,
            "required": "true only after all upstream gates pass",
            "passes_now": "yes" if gate_closure_allowed else "no",
        },
        {
            "dependency": "portal_upload_ready",
            "source": "19.43 bridge decision",
            "current": portal_upload_ready,
            "required": "false in current blocked state",
            "passes_now": "yes" if not portal_upload_ready else "no",
        },
        {
            "dependency": "submission_ready",
            "source": "19.43 bridge boundary",
            "current": submission_ready,
            "required": "false in current blocked state",
            "passes_now": "yes" if not submission_ready else "no",
        },
    ]

    command_rows = []
    for row in board_rows:
        current_allowed = row.get("closure_allowed_now", row.get("command_currently_allowed", ""))
        command_rows.append(
            {
                "gate_id": row.get("gate_id", ""),
                "gate": row.get("gate", row.get("gate_name", "")),
                "current_allowed": current_allowed,
                "bridge_allowed": "yes" if gate_closure_allowed and str(current_allowed).lower() == "yes" else "no",
                "reason": "Blocked until transition bridge, evidence binder, execution board and final lock all pass.",
            }
        )

    blocker_rows = [
        {
            "blocker": "transition bridge blocks gate closure",
            "evidence": (
                f"gate_closure_allowed={transition_bridge.get('gate_closure_allowed')}; "
                f"route_command_execution_allowed={transition_bridge.get('route_command_execution_allowed')}"
            ),
            "blocks": "gate closure execution",
        },
        {
            "blocker": "evidence binder has open requirements",
            "evidence": (
                f"open_evidence_requirements={binder.get('open_evidence_requirements')}; "
                f"binder_rows={len(binder_rows)}"
            ),
            "blocks": "master gate closure",
        },
        {
            "blocker": "execution board keeps gates open",
            "evidence": (
                f"gate_closure_allowed={execution_board.get('gate_closure_allowed')}; "
                f"portal_upload_ready={execution_board.get('portal_upload_ready')}"
            ),
            "blocks": "portal upload",
        },
        {
            "blocker": "final lock refuses submission",
            "evidence": (
                f"open_master_gates={final_lock.get('open_master_gates')}; "
                f"portal_file_upload_allowed_rows={final_lock.get('portal_file_upload_allowed_rows')}; "
                f"blocker_rows={len(final_lock_blockers)}"
            ),
            "blocks": "submission-ready state",
        },
    ]

    qa_rows = [
        {
            "check": "all upstream summaries loaded",
            "result": "PASS",
            "detail": "transition bridge, binder, execution board and final lock summaries loaded.",
        },
        {
            "check": "transition bridge remains blocking",
            "result": "PASS" if not transition_bridge_allows_gate_closure else "FAIL",
            "detail": f"transition_bridge_allows_gate_closure={transition_bridge_allows_gate_closure}",
        },
        {
            "check": "binder keeps open requirements visible",
            "result": "PASS" if int(binder.get("open_evidence_requirements", 0)) > 0 else "FAIL",
            "detail": f"open_evidence_requirements={binder.get('open_evidence_requirements')}",
        },
        {
            "check": "execution board keeps portal blocked",
            "result": "PASS" if not execution_board_allows_gate_closure else "FAIL",
            "detail": f"execution_board_allows_gate_closure={execution_board_allows_gate_closure}",
        },
        {
            "check": "final submission remains false",
            "result": "PASS" if not submission_ready else "FAIL",
            "detail": f"submission_ready={submission_ready}",
        },
    ]

    summary = {
        "package": "gate_closure_dependency_bridge_validator_20260810",
        "transition_bridge_allows_gate_closure": transition_bridge_allows_gate_closure,
        "binder_allows_gate_closure": binder_allows_gate_closure,
        "execution_board_allows_gate_closure": execution_board_allows_gate_closure,
        "final_lock_allows_submission": final_lock_allows_submission,
        "gate_closure_dependency_ready": gate_closure_dependency_ready,
        "gate_closure_allowed": gate_closure_allowed,
        "portal_upload_ready": portal_upload_ready,
        "submission_ready": submission_ready,
        "open_master_gates": final_lock.get("open_master_gates", 0),
        "open_evidence_requirements": binder.get("open_evidence_requirements", 0),
        "commands_allowed_now": transition_bridge.get("commands_allowed_now", 0),
        "portal_file_upload_allowed_rows": final_lock.get("portal_file_upload_allowed_rows", 0),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "gate_closure_dependency_bridge_validator_ready_blocked",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "gate_closure_dependency_bridge_matrix.csv",
        ["dependency", "source", "current", "required", "passes_now"],
        dependency_rows,
    )
    write_csv(
        OUT_DIR / "gate_closure_command_bridge.csv",
        ["gate_id", "gate", "current_allowed", "bridge_allowed", "reason"],
        command_rows,
    )
    write_csv(
        OUT_DIR / "gate_closure_dependency_bridge_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "gate_closure_dependency_bridge_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# Gate Closure Dependency Bridge Validator

This validator bridges 19.42 post-writeback transition gating, the NatComms gate
closure evidence binder, the gate closure execution board and the NatComms
submission final lock validator.

Boundary: read-only. It does not close gates, execute commands, upload portal
files or mark the manuscript submission-ready.
"""
    write_text(OUT_DIR / "GATE_CLOSURE_DEPENDENCY_BRIDGE_VALIDATOR_README.md", readme)

    report = f"""# Gate Closure Dependency Bridge Validator Report

Status: `{summary["status"]}`

Current result:

1. Transition bridge allows gate closure: {str(summary["transition_bridge_allows_gate_closure"]).lower()}
2. Binder allows gate closure: {str(summary["binder_allows_gate_closure"]).lower()}
3. Execution board allows gate closure: {str(summary["execution_board_allows_gate_closure"]).lower()}
4. Final lock allows submission: {str(summary["final_lock_allows_submission"]).lower()}
5. Gate closure allowed: {str(summary["gate_closure_allowed"]).lower()}
6. Portal upload ready: {str(summary["portal_upload_ready"]).lower()}
7. Submission ready: {str(summary["submission_ready"]).lower()}

Boundary: this package only reports dependencies. It cannot convert open gates
into closed gates without real returned evidence, completed receipts and final
manual acceptance.
"""
    write_text(OUT_DIR / "gate_closure_dependency_bridge_validator_report.md", report)
    write_text(
        OUT_DIR / "gate_closure_dependency_bridge_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
