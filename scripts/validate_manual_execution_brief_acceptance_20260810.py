#!/usr/bin/env python3
"""Validate acceptance readiness of the manual execution brief."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manual_execution_brief_acceptance_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_BRIEF = Path.home() / "Desktop" / "NatComms_19.86_manual_execution_brief_20260810.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.87 Manual execution brief acceptance update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/manual_execution_brief_acceptance_20260810/` to verify that the Desktop 19.86 brief matches its action/no-go CSVs and is safe to hand to a human executor.
- Current `acceptance_rows={summary["acceptance_rows"]}`, `accepted_rows={summary["accepted_rows"]}`, `handoff_acceptance_ready={str(summary["handoff_acceptance_ready"]).lower()}`.
- Current `manual_actions_executed=false`, `allowed_commands_now=0`, `portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: this acceptance check validates the handoff artifact only. It does not execute the human actions, create evidence, run validators, execute writeback, run recheck, upload portal files or submit.
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

    brief_summary = read_json(BENCH_ROOT / "reports" / "manual_execution_brief_20260810" / "manual_execution_brief_summary.json")
    action_rows = read_csv(BENCH_ROOT / "reports" / "manual_execution_brief_20260810" / "manual_execution_brief_actions.csv")
    no_go_rows = read_csv(BENCH_ROOT / "reports" / "manual_execution_brief_20260810" / "manual_execution_brief_no_go.csv")
    monitor_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "manual_evidence_readiness_monitor_20260810"
        / "manual_evidence_readiness_monitor_summary.json"
    )
    desktop_text = DESKTOP_BRIEF.read_text(encoding="utf-8-sig") if DESKTOP_BRIEF.exists() else ""

    acceptance_rows = [
        {
            "check_id": "MEA-001",
            "check": "Desktop brief exists",
            "expected": "true",
            "observed": str(DESKTOP_BRIEF.exists()).lower(),
            "passes": "yes" if DESKTOP_BRIEF.exists() else "no",
        },
        {
            "check_id": "MEA-002",
            "check": "Desktop brief contains all five FMR action labels",
            "expected": "FMR-001 through FMR-005 present",
            "observed": ";".join(f"FMR-00{i}={'FMR-00' + str(i) in desktop_text}" for i in range(1, 6)),
            "passes": "yes" if all(f"FMR-00{i}" in desktop_text for i in range(1, 6)) else "no",
        },
        {
            "check_id": "MEA-003",
            "check": "Action CSV matches brief summary",
            "expected": str(brief_summary.get("brief_action_rows")),
            "observed": str(len(action_rows)),
            "passes": "yes" if len(action_rows) == brief_summary.get("brief_action_rows") else "no",
        },
        {
            "check_id": "MEA-004",
            "check": "No-go CSV matches brief summary",
            "expected": str(brief_summary.get("hard_no_go_rows")),
            "observed": str(len(no_go_rows)),
            "passes": "yes" if len(no_go_rows) == brief_summary.get("hard_no_go_rows") else "no",
        },
        {
            "check_id": "MEA-005",
            "check": "No-go text is present in Desktop brief",
            "expected": "all no-go rows present",
            "observed": str(sum(1 for row in no_go_rows if row["do_not_do"] in desktop_text)),
            "passes": "yes" if all(row["do_not_do"] in desktop_text for row in no_go_rows) else "no",
        },
        {
            "check_id": "MEA-006",
            "check": "Monitor still allows no commands",
            "expected": "0",
            "observed": str(monitor_summary.get("allowed_commands_now")),
            "passes": "yes" if monitor_summary.get("allowed_commands_now") == 0 else "no",
        },
        {
            "check_id": "MEA-007",
            "check": "Submission remains blocked",
            "expected": "false",
            "observed": str(monitor_summary.get("submission_ready")).lower(),
            "passes": "yes" if not monitor_summary.get("submission_ready") else "no",
        },
    ]

    accepted_rows = sum(1 for row in acceptance_rows if row["passes"] == "yes")
    handoff_acceptance_ready = accepted_rows == len(acceptance_rows)

    handoff_rows = [
        {
            "handoff_item": "Desktop execution brief",
            "path": str(DESKTOP_BRIEF),
            "ready_for_human_handoff": "yes" if handoff_acceptance_ready else "no",
            "manual_actions_executed": "no",
            "allowed_next_state": "human reads brief and performs real external/manual actions",
        },
        {
            "handoff_item": "Machine-readable action table",
            "path": "reports/manual_execution_brief_20260810/manual_execution_brief_actions.csv",
            "ready_for_human_handoff": "yes" if handoff_acceptance_ready else "no",
            "manual_actions_executed": "no",
            "allowed_next_state": "human fills MOF forms only after real evidence exists",
        },
        {
            "handoff_item": "Machine-readable no-go table",
            "path": "reports/manual_execution_brief_20260810/manual_execution_brief_no_go.csv",
            "ready_for_human_handoff": "yes" if handoff_acceptance_ready else "no",
            "manual_actions_executed": "no",
            "allowed_next_state": "no system writeback, recheck, portal upload or submission",
        },
    ]

    qa_rows = [
        {
            "check": "acceptance rows all pass",
            "result": "PASS" if handoff_acceptance_ready else "FAIL",
            "detail": f"accepted_rows={accepted_rows}; acceptance_rows={len(acceptance_rows)}",
        },
        {
            "check": "handoff does not imply execution",
            "result": "PASS",
            "detail": "manual_actions_executed=false",
        },
        {
            "check": "commands remain blocked",
            "result": "PASS" if monitor_summary.get("allowed_commands_now") == 0 else "FAIL",
            "detail": f"allowed_commands_now={monitor_summary.get('allowed_commands_now')}",
        },
    ]

    summary = {
        "package": "manual_execution_brief_acceptance_20260810",
        "acceptance_rows": len(acceptance_rows),
        "accepted_rows": accepted_rows,
        "handoff_rows": len(handoff_rows),
        "handoff_acceptance_ready": handoff_acceptance_ready,
        "manual_actions_executed": False,
        "allowed_commands_now": 0,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "manual_execution_brief_acceptance_ready_handoff_only",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "manual_execution_brief_acceptance_checks.csv",
        ["check_id", "check", "expected", "observed", "passes"],
        acceptance_rows,
    )
    write_csv(
        OUT_DIR / "manual_execution_brief_handoff_manifest.csv",
        ["handoff_item", "path", "ready_for_human_handoff", "manual_actions_executed", "allowed_next_state"],
        handoff_rows,
    )
    write_csv(OUT_DIR / "manual_execution_brief_acceptance_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# Manual Execution Brief Acceptance

Status: `{summary["status"]}`

Current result:

1. Acceptance rows: {summary["acceptance_rows"]}
2. Accepted rows: {summary["accepted_rows"]}
3. Handoff rows: {summary["handoff_rows"]}
4. Handoff acceptance ready: {str(summary["handoff_acceptance_ready"]).lower()}
5. Manual actions executed: false
6. Allowed commands now: 0
7. Portal upload allowed: false
8. Submission ready: false

Boundary: this acceptance check validates the handoff artifact only. It does
not execute the human actions, create evidence, run validators, execute
writeback, run recheck, upload portal files or submit.
"""
    write_text(OUT_DIR / "MANUAL_EXECUTION_BRIEF_ACCEPTANCE_README.md", report)
    write_text(OUT_DIR / "manual_execution_brief_acceptance_report.md", report)
    write_text(OUT_DIR / "manual_execution_brief_acceptance_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
