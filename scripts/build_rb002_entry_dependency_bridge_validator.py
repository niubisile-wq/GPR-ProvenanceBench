#!/usr/bin/env python3
"""Bridge RB-002 entry dependencies after RB-001 closeout dependency validation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "rb002_entry_dependency_bridge_validator_20260810"
RB001_BRIDGE_DIR = BENCH_ROOT / "reports" / "rb001_closeout_dependency_bridge_validator_20260810"
WRITEBACK_PREFLIGHT_DIR = BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810"
RB002_DASHBOARD_DIR = BENCH_ROOT / "reports" / "rb002_writeback_readiness_dashboard_20260810"
RB002_RECEIPT_DIR = BENCH_ROOT / "reports" / "rb002_protected_writeback_receipt_20260810"
RB002_COMPLETION_DIR = BENCH_ROOT / "reports" / "rb002_writeback_receipt_completion_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"


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
    marker = "### 19.41 RB-002 entry dependency bridge validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/rb002_entry_dependency_bridge_validator_20260810/`，把 19.40 RB-001 closeout bridge、writeback preflight、RB-002 readiness、protected writeback receipt 和 RB-002 receipt completion 串成 RB-002 entry gate。
- 当前 `rb001_bridge_allows_rb002={str(summary["rb001_bridge_allows_rb002"]).lower()}`，`writeback_preflight_ready={str(summary["writeback_preflight_ready"]).lower()}`，`rb002_dashboard_ready={str(summary["rb002_dashboard_ready"]).lower()}`。
- 当前 `protected_receipt_ready={str(summary["protected_receipt_ready"]).lower()}`，`rb002_receipt_complete={str(summary["rb002_receipt_complete"]).lower()}`，`rb002_entry_allowed={str(summary["rb002_entry_allowed"]).lower()}`。
- 当前 `writeback_allowed_rows=0`，`transition_allowed_rows=0`，`submission_ready=false`。
- 边界：该 bridge 只读依赖状态，不写 protected targets、不填写 RB-002 receipt、不进入 transition、不关闭 gate。
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

    rb001_bridge = read_json(RB001_BRIDGE_DIR / "rb001_closeout_dependency_bridge_validator_summary.json")
    writeback_preflight = read_json(WRITEBACK_PREFLIGHT_DIR / "final_return_evidence_writeback_preflight_summary.json")
    rb002_dashboard = read_json(RB002_DASHBOARD_DIR / "rb002_writeback_readiness_dashboard_summary.json")
    rb002_receipt = read_json(RB002_RECEIPT_DIR / "rb002_protected_writeback_receipt_summary.json")
    rb002_completion = read_json(RB002_COMPLETION_DIR / "rb002_writeback_receipt_completion_validator_summary.json")

    rb001_bridge_allows_rb002 = rb001_bridge.get("rb002_entry_allowed") is True
    writeback_preflight_ready = (
        writeback_preflight.get("qa_pass") is True
        and writeback_preflight.get("writeback_allowed_rows", 0) > 0
        and writeback_preflight.get("manual_actions_executed") is True
        and writeback_preflight.get("evidence_writeback_performed") is True
    )
    rb002_dashboard_ready = rb002_dashboard.get("rb002_ready") is True and rb002_dashboard.get("rb002_ready_rows", 0) > 0
    protected_receipt_ready = (
        rb002_receipt.get("rb001_closed") is True
        and rb002_receipt.get("writeback_allowed_rows", 0) > 0
        and rb002_receipt.get("completed_receipt_rows", 0) > 0
    )
    rb002_receipt_complete = (
        rb002_completion.get("receipt_complete") is True
        and rb002_completion.get("transition_entry_allowed") is True
        and rb002_completion.get("complete_receipt_rows", 0) > 0
    )
    rb002_entry_allowed = (
        rb001_bridge_allows_rb002
        and writeback_preflight_ready
        and rb002_dashboard_ready
        and protected_receipt_ready
        and rb002_receipt_complete
    )
    transition_allowed = rb002_entry_allowed and rb002_completion.get("transition_allowed_rows", 0) > 0

    dependency_rows = [
        {
            "dependency": "rb001_bridge_allows_rb002",
            "source": "19.40 RB-001 bridge",
            "current": rb001_bridge_allows_rb002,
            "required": "true",
            "passes_now": "yes" if rb001_bridge_allows_rb002 else "no",
        },
        {
            "dependency": "writeback_preflight_ready",
            "source": "final return evidence writeback preflight",
            "current": writeback_preflight_ready,
            "required": "true",
            "passes_now": "yes" if writeback_preflight_ready else "no",
        },
        {
            "dependency": "rb002_dashboard_ready",
            "source": "RB-002 readiness dashboard",
            "current": rb002_dashboard_ready,
            "required": "true",
            "passes_now": "yes" if rb002_dashboard_ready else "no",
        },
        {
            "dependency": "protected_receipt_ready",
            "source": "RB-002 protected writeback receipt",
            "current": protected_receipt_ready,
            "required": "true",
            "passes_now": "yes" if protected_receipt_ready else "no",
        },
        {
            "dependency": "rb002_receipt_complete",
            "source": "RB-002 receipt completion validator",
            "current": rb002_receipt_complete,
            "required": "true",
            "passes_now": "yes" if rb002_receipt_complete else "no",
        },
        {
            "dependency": "rb002_entry_allowed",
            "source": "bridge decision",
            "current": rb002_entry_allowed,
            "required": "true",
            "passes_now": "yes" if rb002_entry_allowed else "no",
        },
        {
            "dependency": "transition_allowed",
            "source": "bridge decision",
            "current": transition_allowed,
            "required": "true",
            "passes_now": "yes" if transition_allowed else "no",
        },
        {
            "dependency": "submission_ready",
            "source": "bridge boundary",
            "current": False,
            "required": "false",
            "passes_now": "yes",
        },
    ]

    blocker_rows = [
        {
            "blocker": "RB-001 bridge does not allow RB-002",
            "evidence": f"rb002_entry_allowed={rb001_bridge.get('rb002_entry_allowed')}; rb001_closed={rb001_bridge.get('rb001_closed')}",
            "blocks": "all RB-002 writeback entry",
        },
        {
            "blocker": "writeback preflight has no allowed rows",
            "evidence": f"writeback_allowed_rows={writeback_preflight.get('writeback_allowed_rows')}; evidence_writeback_performed={writeback_preflight.get('evidence_writeback_performed')}",
            "blocks": "protected writeback receipt completion",
        },
        {
            "blocker": "RB-002 dashboard not ready",
            "evidence": f"rb002_ready={rb002_dashboard.get('rb002_ready')}; rb002_ready_rows={rb002_dashboard.get('rb002_ready_rows')}",
            "blocks": "RB-002 entry",
        },
        {
            "blocker": "protected writeback receipt incomplete",
            "evidence": f"completed_receipt_rows={rb002_receipt.get('completed_receipt_rows')}; writeback_allowed_rows={rb002_receipt.get('writeback_allowed_rows')}",
            "blocks": "transition entry",
        },
        {
            "blocker": "RB-002 receipt completion blocked",
            "evidence": f"receipt_complete={rb002_completion.get('receipt_complete')}; transition_entry_allowed={rb002_completion.get('transition_entry_allowed')}",
            "blocks": "transition execution",
        },
    ]

    qa_rows = [
        {
            "check": "all upstream summaries loaded",
            "result": "PASS",
            "detail": "rb001 bridge, preflight, dashboard, receipt and completion summaries loaded.",
        },
        {
            "check": "bridge keeps rb002 entry blocked",
            "result": "PASS" if not rb002_entry_allowed else "FAIL",
            "detail": f"rb002_entry_allowed={rb002_entry_allowed}",
        },
        {
            "check": "bridge keeps transition blocked",
            "result": "PASS" if not transition_allowed else "FAIL",
            "detail": f"transition_allowed={transition_allowed}",
        },
        {
            "check": "writeback remains absent",
            "result": "PASS" if writeback_preflight.get("writeback_allowed_rows") == 0 else "FAIL",
            "detail": f"writeback_allowed_rows={writeback_preflight.get('writeback_allowed_rows')}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "RB-002 bridge cannot make submission ready.",
        },
    ]

    summary = {
        "package": "rb002_entry_dependency_bridge_validator_20260810",
        "rb001_bridge_allows_rb002": rb001_bridge_allows_rb002,
        "writeback_preflight_ready": writeback_preflight_ready,
        "rb002_dashboard_ready": rb002_dashboard_ready,
        "protected_receipt_ready": protected_receipt_ready,
        "rb002_receipt_complete": rb002_receipt_complete,
        "rb002_entry_allowed": rb002_entry_allowed,
        "transition_allowed": transition_allowed,
        "writeback_allowed_rows": writeback_preflight.get("writeback_allowed_rows", 0),
        "transition_allowed_rows": rb002_completion.get("transition_allowed_rows", 0),
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "rb002_entry_dependency_bridge_validator_ready_blocked_by_rb001",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "rb002_entry_dependency_bridge_matrix.csv",
        ["dependency", "source", "current", "required", "passes_now"],
        dependency_rows,
    )
    write_csv(
        OUT_DIR / "rb002_entry_dependency_bridge_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "rb002_entry_dependency_bridge_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# RB-002 Entry Dependency Bridge Validator

This validator bridges RB-001 closeout dependency status, writeback preflight,
RB-002 readiness, protected writeback receipt and RB-002 receipt completion
before any RB-002 entry or transition can be considered.

Boundary: it is read-only. It does not write protected targets, fill RB-002
receipts, run transitions, close gates or make the manuscript submission-ready.
"""
    write_text(OUT_DIR / "RB002_ENTRY_DEPENDENCY_BRIDGE_VALIDATOR_README.md", readme)

    report = f"""# RB-002 Entry Dependency Bridge Validator Report

Status: `{summary["status"]}`

Current result:

1. RB-001 bridge allows RB-002: {str(summary["rb001_bridge_allows_rb002"]).lower()}
2. Writeback preflight ready: {str(summary["writeback_preflight_ready"]).lower()}
3. RB-002 dashboard ready: {str(summary["rb002_dashboard_ready"]).lower()}
4. Protected receipt ready: {str(summary["protected_receipt_ready"]).lower()}
5. RB-002 receipt complete: {str(summary["rb002_receipt_complete"]).lower()}
6. RB-002 entry allowed: {str(summary["rb002_entry_allowed"]).lower()}
7. Transition allowed: {str(summary["transition_allowed"]).lower()}
8. Writeback allowed rows: {summary["writeback_allowed_rows"]}
9. Transition allowed rows: {summary["transition_allowed_rows"]}
10. Submission ready: false

Interpretation: RB-002 entry now has an explicit dependency bridge from RB-001
closeout through protected writeback receipt completion. Current state remains
blocked before any RB-002 writeback or transition.
"""
    write_text(OUT_DIR / "rb002_entry_dependency_bridge_validator_report.md", report)
    write_text(
        OUT_DIR / "rb002_entry_dependency_bridge_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("RB-002 entry dependency bridge validator QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
