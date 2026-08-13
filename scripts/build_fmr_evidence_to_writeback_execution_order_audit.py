#!/usr/bin/env python3
"""Build an execution-order audit from FMR evidence intake to guarded recheck."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "fmr_evidence_to_writeback_execution_order_audit_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


FMR_SEQUENCE = [
    {
        "receipt_id": "FMR-001",
        "evidence_validator": "py scripts/build_external_dependency_sendout_evidence_intake_preflight.py",
        "preflight": "py scripts/build_fmr001_sendout_completion_writeback_preflight.py",
        "applier": "py scripts/build_fmr001_guarded_writeback_applier.py --execute-writeback",
        "post_applier_validator": "py scripts/build_final_manual_receipt_completion_validator.py",
        "summary": "reports/fmr001_guarded_writeback_applier_20260810/fmr001_guarded_writeback_applier_summary.json",
    },
    {
        "receipt_id": "FMR-002",
        "evidence_validator": "py scripts/build_fmr002_author_decision_writeback_preflight.py",
        "preflight": "py scripts/build_fmr002_author_decision_writeback_preflight.py",
        "applier": "py scripts/build_fmr002_guarded_writeback_applier.py --execute-writeback",
        "post_applier_validator": "py scripts/build_final_manual_receipt_completion_validator.py",
        "summary": "reports/fmr002_guarded_writeback_applier_20260810/fmr002_guarded_writeback_applier_summary.json",
    },
    {
        "receipt_id": "FMR-003",
        "evidence_validator": "py scripts/build_final_return_evidence_intake_scanner.py",
        "preflight": "py scripts/build_fmr003_returned_evidence_writeback_preflight.py",
        "applier": "py scripts/build_fmr003_guarded_writeback_applier.py --execute-writeback",
        "post_applier_validator": "py scripts/build_final_manual_receipt_completion_validator.py",
        "summary": "reports/fmr003_guarded_writeback_applier_20260810/fmr003_guarded_writeback_applier_summary.json",
    },
    {
        "receipt_id": "FMR-004",
        "evidence_validator": "py scripts/build_python_figure_author_review_intake_validator.py",
        "preflight": "py scripts/build_fmr004_figure_review_writeback_preflight.py",
        "applier": "py scripts/build_fmr004_guarded_writeback_applier.py --execute-writeback",
        "post_applier_validator": "py scripts/build_final_manual_receipt_completion_validator.py",
        "summary": "reports/fmr004_guarded_writeback_applier_20260810/fmr004_guarded_writeback_applier_summary.json",
    },
    {
        "receipt_id": "FMR-005",
        "evidence_validator": "py scripts/build_availability_repository_finalization_validator.py",
        "preflight": "py scripts/build_fmr005_repository_rights_doi_writeback_preflight.py",
        "applier": "py scripts/build_fmr005_guarded_writeback_applier.py --execute-writeback",
        "post_applier_validator": "py scripts/build_final_manual_receipt_completion_validator.py",
        "summary": "reports/fmr005_guarded_writeback_applier_20260810/fmr005_guarded_writeback_applier_summary.json",
    },
    {
        "receipt_id": "FMR-006",
        "evidence_validator": "powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1",
        "preflight": "py scripts/build_fmr006_guarded_recheck_receipt_writeback_preflight.py",
        "applier": "py scripts/build_fmr006_guarded_writeback_applier.py --execute-writeback",
        "post_applier_validator": "py scripts/build_final_manual_receipt_completion_validator.py",
        "summary": "reports/fmr006_guarded_writeback_applier_20260810/fmr006_guarded_writeback_applier_summary.json",
    },
]


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
    marker = "### 19.79 FMR evidence-to-writeback execution order audit update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/fmr_evidence_to_writeback_execution_order_audit_20260810/` to lock the future execution order from evidence intake through guarded writeback and post-evidence recheck.
- Current `ordered_fmr_rows={summary["ordered_fmr_rows"]}`, `commands_allowed_now={summary["commands_allowed_now"]}`, `writeback_executed_rows={summary["writeback_executed_rows"]}`.
- Current `receipt_completion_allowed={str(summary["receipt_completion_allowed"]).lower()}`, `guarded_recheck_allowed={str(summary["guarded_recheck_allowed"]).lower()}`, `submission_ready=false`.
- Boundary: this is an order audit only. It does not execute evidence validators, run `--execute-writeback`, run guarded recheck, upload portal files or submit.
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

    coverage_summary = read_json(BENCH_ROOT / "reports/fmr_guarded_writeback_coverage_audit_20260810/fmr_guarded_writeback_coverage_audit_summary.json")
    completion_summary = read_json(BENCH_ROOT / "reports/final_manual_receipt_completion_validator_20260810/final_manual_receipt_completion_validator_summary.json")
    recheck_summary = read_json(BENCH_ROOT / "reports/final_guarded_recheck_execution_audit_20260810/final_guarded_recheck_execution_audit_summary.json")

    order_rows = []
    command_rows = []
    blocker_rows = []

    for idx, item in enumerate(FMR_SEQUENCE, start=1):
        applier_summary = read_json(BENCH_ROOT / item["summary"])
        writeback_preflight_allowed = applier_summary.get("writeback_preflight_allowed") is True
        writeback_executed = applier_summary.get("writeback_executed") is True
        real_modified = applier_summary.get("real_fmr_template_modified") is True
        current_command_allowed = writeback_preflight_allowed and not writeback_executed

        order_rows.append(
            {
                "order": idx,
                "receipt_id": item["receipt_id"],
                "evidence_validator": item["evidence_validator"],
                "preflight": item["preflight"],
                "guarded_applier": item["applier"],
                "post_applier_validator": item["post_applier_validator"],
                "writeback_preflight_allowed_now": str(writeback_preflight_allowed).lower(),
                "writeback_executed_now": str(writeback_executed).lower(),
                "real_fmr_template_modified_now": str(real_modified).lower(),
                "current_command_allowed": str(current_command_allowed).lower(),
            }
        )
        command_rows.append(
            {
                "order": idx,
                "receipt_id": item["receipt_id"],
                "command_type": "guarded_writeback_after_real_evidence",
                "command": item["applier"],
                "allowed_now": "yes" if current_command_allowed else "no",
                "required_before_running": "corresponding evidence validator and writeback preflight produce one complete candidate; explicit operator approval",
            }
        )
        if not current_command_allowed:
            blocker_rows.append(
                {
                    "receipt_id": item["receipt_id"],
                    "blocker": "guarded writeback command not currently allowed",
                    "evidence": f"writeback_preflight_allowed={writeback_preflight_allowed}; writeback_executed={writeback_executed}",
                    "blocks": item["applier"],
                }
            )

    receipt_completion_allowed = completion_summary.get("receipt_completion_allowed") is True
    guarded_recheck_allowed = completion_summary.get("guarded_recheck_allowed") is True
    launcher_execution_allowed = recheck_summary.get("launcher_execution_allowed") is True
    recheck_executed = recheck_summary.get("recheck_executed") is True

    global_gate_rows = [
        {
            "gate": "all_fmr_guarded_writeback_layers_covered",
            "current": coverage_summary.get("coverage_complete_rows"),
            "required": 6,
            "passes_now": "yes" if coverage_summary.get("coverage_complete_rows") == 6 else "no",
        },
        {
            "gate": "no_real_writeback_executed_before_evidence",
            "current": f"writeback_executed_rows={coverage_summary.get('writeback_executed_rows')}; real_fmr_template_modified_rows={coverage_summary.get('real_fmr_template_modified_rows')}",
            "required": "both 0 in current blocked state",
            "passes_now": "yes" if coverage_summary.get("writeback_executed_rows") == 0 and coverage_summary.get("real_fmr_template_modified_rows") == 0 else "no",
        },
        {
            "gate": "receipt_completion_allows_guarded_recheck",
            "current": f"receipt_completion_allowed={receipt_completion_allowed}; guarded_recheck_allowed={guarded_recheck_allowed}",
            "required": "both true before FMR-006 post-evidence recheck",
            "passes_now": "yes" if receipt_completion_allowed and guarded_recheck_allowed else "no",
        },
        {
            "gate": "launcher_allows_and_recheck_executed",
            "current": f"launcher_execution_allowed={launcher_execution_allowed}; recheck_executed={recheck_executed}",
            "required": "both true before final-master re-entry",
            "passes_now": "yes" if launcher_execution_allowed and recheck_executed else "no",
        },
    ]

    commands_allowed_now = sum(row["current_command_allowed"] == "true" for row in order_rows)
    writeback_executed_rows = sum(row["writeback_executed_now"] == "true" for row in order_rows)
    real_modified_rows = sum(row["real_fmr_template_modified_now"] == "true" for row in order_rows)
    qa_rows = [
        {
            "check": "six ordered FMR rows present",
            "result": "PASS" if len(order_rows) == 6 else "FAIL",
            "detail": f"ordered_fmr_rows={len(order_rows)}",
        },
        {
            "check": "coverage audit is complete before order audit",
            "result": "PASS" if coverage_summary.get("coverage_complete_rows") == 6 and coverage_summary.get("qa_pass") is True else "FAIL",
            "detail": f"coverage_complete_rows={coverage_summary.get('coverage_complete_rows')}; coverage_qa_pass={coverage_summary.get('qa_pass')}",
        },
        {
            "check": "no commands are allowed in current no-evidence state",
            "result": "PASS" if commands_allowed_now == 0 else "FAIL",
            "detail": f"commands_allowed_now={commands_allowed_now}",
        },
        {
            "check": "no writeback has executed",
            "result": "PASS" if writeback_executed_rows == 0 and real_modified_rows == 0 else "FAIL",
            "detail": f"writeback_executed_rows={writeback_executed_rows}; real_modified_rows={real_modified_rows}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "fmr_evidence_to_writeback_execution_order_audit_20260810",
        "ordered_fmr_rows": len(order_rows),
        "commands_allowed_now": commands_allowed_now,
        "writeback_executed_rows": writeback_executed_rows,
        "real_fmr_template_modified_rows": real_modified_rows,
        "receipt_completion_allowed": receipt_completion_allowed,
        "guarded_recheck_allowed": guarded_recheck_allowed,
        "launcher_execution_allowed": launcher_execution_allowed,
        "recheck_executed": recheck_executed,
        "blocker_rows": len(blocker_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "portal_upload_allowed": False,
        "submission_ready": False,
        "status": "fmr_evidence_to_writeback_execution_order_audit_ready_all_current_commands_blocked",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "fmr_evidence_to_writeback_execution_order.csv",
        [
            "order",
            "receipt_id",
            "evidence_validator",
            "preflight",
            "guarded_applier",
            "post_applier_validator",
            "writeback_preflight_allowed_now",
            "writeback_executed_now",
            "real_fmr_template_modified_now",
            "current_command_allowed",
        ],
        order_rows,
    )
    write_csv(
        OUT_DIR / "fmr_guarded_writeback_command_manifest.csv",
        ["order", "receipt_id", "command_type", "command", "allowed_now", "required_before_running"],
        command_rows,
    )
    write_csv(OUT_DIR / "fmr_execution_order_global_gates.csv", ["gate", "current", "required", "passes_now"], global_gate_rows)
    write_csv(OUT_DIR / "fmr_execution_order_blockers.csv", ["receipt_id", "blocker", "evidence", "blocks"], blocker_rows)
    write_csv(OUT_DIR / "fmr_execution_order_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# FMR Evidence-to-Writeback Execution Order Audit

Status: `{summary["status"]}`

Current result:

1. Ordered FMR rows: {summary["ordered_fmr_rows"]}
2. Commands allowed now: {summary["commands_allowed_now"]}
3. Writeback executed rows: {summary["writeback_executed_rows"]}
4. Real FMR template modified rows: {summary["real_fmr_template_modified_rows"]}
5. Receipt completion allowed: {str(summary["receipt_completion_allowed"]).lower()}
6. Guarded recheck allowed: {str(summary["guarded_recheck_allowed"]).lower()}
7. Launcher execution allowed: {str(summary["launcher_execution_allowed"]).lower()}
8. Recheck executed: {str(summary["recheck_executed"]).lower()}
9. Portal upload allowed: false
10. Submission ready: false

Boundary: this audit locks execution order only. It does not execute evidence
validators, run `--execute-writeback`, execute guarded recheck, upload portal
files or mark the manuscript submitted.
"""
    write_text(OUT_DIR / "FMR_EVIDENCE_TO_WRITEBACK_EXECUTION_ORDER_AUDIT_README.md", report)
    write_text(OUT_DIR / "fmr_evidence_to_writeback_execution_order_audit_report.md", report)
    write_text(OUT_DIR / "fmr_evidence_to_writeback_execution_order_audit_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
