#!/usr/bin/env python3
"""Build an execution board for closing submission gates after real evidence arrives."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "gate_closure_execution_board_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

GATE_LEDGER = REPORTS / "submission_completion_ledger_20260810" / "submission_completion_gate_ledger.csv"
FINAL_VERIFICATION = REPORTS / "submission_completion_ledger_20260810" / "submission_final_verification_queue.csv"
GLOBAL_RERUN = REPORTS / "post_evidence_safe_rerun_guard_20260810" / "post_evidence_global_rerun_order.csv"
PREFLIGHT_BLOCKERS = REPORTS / "manual_evidence_entry_preflight_20260810" / "manual_evidence_preflight_blockers.csv"
PORTAL_GAP = REPORTS / "portal_submission_file_preflight_20260810" / "portal_gate_to_file_gap_matrix.csv"
DASHBOARD = REPORTS / "submission_readiness_dashboard_20260810" / "submission_readiness_dashboard_summary.json"


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
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 18.88 Gate closure execution board update"
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


def gate_manual_entry(gate: str) -> str:
    mapping = {
        "Real blind external validation": "MEW-004 external_blind_asset_payload plus strict-SHA manifest",
        "Main figure rendering": "MEW-003 backend_and_scope_choice",
        "Repository identifiers": "MEW-005 rights_licence_decisions plus repository DOI/code DOI records",
        "Reporting Summary": "MEW-006 reporting_summary_author_replies",
        "Third-party rights": "MEW-005 rights_licence_decisions",
        "Final reference numbering": "MEW-007 reference_replacement_authorized",
    }
    return mapping.get(gate, "manual evidence worksheet")


def gate_hard_prerequisite(gate: str) -> str:
    mapping = {
        "Real blind external validation": "real unused asset acquired; labels held outside analyst workflow; predictions frozen before label unlock",
        "Main figure rendering": "author/backend choice is Python or R and figure scope is selected",
        "Repository identifiers": "rights/licence scope resolved and final source-data scope known",
        "Reporting Summary": "final Methods, final figure/table set and author confirmations available",
        "Third-party rights": "written permission/exclusion decision for every derived/raw data category",
        "Final reference numbering": "final prose, final figure/table calls and stable reference order",
    }
    return mapping.get(gate, "real evidence exists")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    gates = read_csv(GATE_LEDGER)
    final_verification = read_csv(FINAL_VERIFICATION)
    global_rerun = read_csv(GLOBAL_RERUN)
    blockers = read_csv(PREFLIGHT_BLOCKERS)
    portal_gap = read_csv(PORTAL_GAP)
    dashboard = read_json(DASHBOARD)

    affected_by_gate = {row["gate"]: row.get("affected_portal_items", "") for row in portal_gap}
    validation_by_gate = {row["gate"]: row.get("final_validation_to_run", "") for row in portal_gap}

    board_rows = []
    for gate in gates:
        board_rows.append(
            {
                "priority": gate["priority"],
                "gate": gate["gate"],
                "current_status": gate["current_status"],
                "closure_state": gate["closure_state"],
                "hard_prerequisite_before_attempt": gate_hard_prerequisite(gate["gate"]),
                "manual_entry_or_evidence_source": gate_manual_entry(gate["gate"]),
                "required_evidence_to_close": gate["required_evidence_to_close"],
                "affected_portal_items": affected_by_gate.get(gate["gate"], "cross-cutting"),
                "first_validation_to_run": validation_by_gate.get(gate["gate"], gate["final_validation_to_run"]),
                "closure_allowed_now": "no",
            }
        )

    command_rows = []
    for row in global_rerun:
        command_rows.append(
            {
                "order": row["order"],
                "command": row["command"],
                "purpose": row["purpose"],
                "run_now": row["run_now"],
                "execution_condition": "only after relevant manual evidence row passes intake" if row["run_now"] == "no" else "safe diagnostic command only",
            }
        )

    stop_rows = [
        {
            "rule_id": "GATE-STOP-001",
            "rule": "Do not close a gate from recommended/default choices alone.",
            "evidence_required": "real author, rights, repository, figure, or external-validation evidence",
        },
        {
            "rule_id": "GATE-STOP-002",
            "rule": "Do not run branch validators while manual evidence intake still reports missing rows.",
            "evidence_required": "post_dispatch_evidence_intake_validator row intake_status=present/passed",
        },
        {
            "rule_id": "GATE-STOP-003",
            "rule": "Do not run portal upload checks before all six final verification rows are satisfied.",
            "evidence_required": "submission_completion_ledger final verification current_state=satisfied for every row",
        },
        {
            "rule_id": "GATE-STOP-004",
            "rule": "Do not convert M0-M2 pass into submission readiness.",
            "evidence_required": "dashboard submission_ready=true and portal_upload_ready=true",
        },
        {
            "rule_id": "GATE-STOP-005",
            "rule": "Do not remove external-validation limitations without a locked one-shot evaluation.",
            "evidence_required": "strict-SHA manifest, frozen prediction and post-unlock evaluation result",
        },
    ]

    qa_rows = [
        {
            "check": "six_gates_indexed",
            "result": "PASS" if len(board_rows) == 6 else "FAIL",
            "detail": f"board_rows={len(board_rows)}",
        },
        {
            "check": "command_order_imported",
            "result": "PASS" if len(command_rows) >= 7 else "FAIL",
            "detail": f"command_rows={len(command_rows)}",
        },
        {
            "check": "manual_blockers_imported",
            "result": "PASS" if len(blockers) == 7 else "FAIL",
            "detail": f"blocker_rows={len(blockers)}",
        },
        {
            "check": "closure_block_preserved",
            "result": "PASS" if dashboard.get("submission_ready") is False and all(row["closure_allowed_now"] == "no" for row in board_rows) else "FAIL",
            "detail": f"submission_ready={dashboard.get('submission_ready')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "gate_closure_execution_board.csv",
        board_rows,
        [
            "priority",
            "gate",
            "current_status",
            "closure_state",
            "hard_prerequisite_before_attempt",
            "manual_entry_or_evidence_source",
            "required_evidence_to_close",
            "affected_portal_items",
            "first_validation_to_run",
            "closure_allowed_now",
        ],
    )
    write_csv(
        OUT_DIR / "gate_closure_command_order.csv",
        command_rows,
        ["order", "command", "purpose", "run_now", "execution_condition"],
    )
    write_csv(OUT_DIR / "gate_closure_stop_rules.csv", stop_rows, ["rule_id", "rule", "evidence_required"])
    write_csv(OUT_DIR / "gate_closure_execution_board_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Gate closure execution board report 2026-08-10",
        "",
        "Status: `gate_closure_execution_board_ready_gates_open`",
        "",
        f"1. Gate rows: {len(board_rows)}",
        f"2. Command rows: {len(command_rows)}",
        f"3. Stop rules: {len(stop_rows)}",
        f"4. Final verification rows imported: {len(final_verification)}",
        f"5. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: closure order is indexed, but every gate remains open and no closure is authorized.",
        "",
    ]
    write_text(OUT_DIR / "GATE_CLOSURE_EXECUTION_BOARD_README.md", "\n".join(report))
    write_text(OUT_DIR / "gate_closure_execution_board_report.md", "\n".join(report))

    summary = {
        "package": "gate_closure_execution_board_20260810",
        "gate_rows": len(board_rows),
        "command_rows": len(command_rows),
        "stop_rules": len(stop_rows),
        "final_verification_rows_imported": len(final_verification),
        "manual_blocker_rows_imported": len(blockers),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "gate_closure_allowed": False,
        "portal_upload_ready": False,
        "submission_ready": False,
        "status": "gate_closure_execution_board_ready_gates_open",
    }

    section = f"""### 18.88 Gate closure execution board update

Added a gate closure execution board that turns the six open submission gates into closure prerequisites, evidence sources, validation commands and stop rules.

New directory: `{OUT_DIR}`

New files:
1. `gate_closure_execution_board.csv`
2. `gate_closure_command_order.csv`
3. `gate_closure_stop_rules.csv`
4. `gate_closure_execution_board_qa.csv`
5. `GATE_CLOSURE_EXECUTION_BOARD_README.md`
6. `gate_closure_execution_board_report.md`
7. `gate_closure_execution_board_summary.json`

Current result:
1. gate_rows = {summary['gate_rows']}
2. command_rows = {summary['command_rows']}
3. stop_rules = {summary['stop_rules']}
4. qa_pass = {str(qa_pass).lower()}
5. gate_closure_allowed = false
6. portal_upload_ready = false
7. submission_ready = false

Boundary:
1. This step does not fill manual evidence.
2. This step does not run branch validators.
3. This step does not close gates or authorize portal upload."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "gate_closure_execution_board_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Gate closure execution board QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
