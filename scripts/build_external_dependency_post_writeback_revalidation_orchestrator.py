#!/usr/bin/env python3
"""Build a guarded post-EDS-writeback revalidation orchestrator."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "external_dependency_post_writeback_revalidation_orchestrator_20260810"
EDS_WRITEBACK_DIR = BENCH_ROOT / "reports" / "external_dependency_eds_guarded_writeback_applier_20260810"
SENDOUT_VALIDATOR_DIR = BENCH_ROOT / "reports" / "external_dependency_escalation_sendout_receipt_validator_20260810"
SAFE_SEND_DIR = BENCH_ROOT / "reports" / "external_dependency_safe_send_execution_packet_20260810"
FINAL_RECEIPT_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_completion_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


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
    marker = "### 19.59 Post-writeback revalidation orchestrator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/external_dependency_post_writeback_revalidation_orchestrator_20260810/` to define the guarded revalidation sequence after future EDS writeback.
- Current `writeback_executed={str(summary["writeback_executed"]).lower()}`, `revalidation_sequence_allowed={str(summary["revalidation_sequence_allowed"]).lower()}`, `commands_allowed_now={summary["commands_allowed_now"]}`.
- Current `fmr001_unlock_allowed_after_revalidation={str(summary["fmr001_unlock_allowed_after_revalidation"]).lower()}`, `guarded_recheck_allowed=false`, `portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: this orchestrator is read-only in the current state. It does not run revalidation commands, fill FMR rows, close gates, upload portal files or submit.
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

    writeback_summary = read_json(EDS_WRITEBACK_DIR / "external_dependency_eds_guarded_writeback_applier_summary.json")
    sendout_summary = read_json(SENDOUT_VALIDATOR_DIR / "external_dependency_escalation_sendout_receipt_validator_summary.json")
    safe_send_summary = read_json(SAFE_SEND_DIR / "external_dependency_safe_send_execution_summary.json")
    final_receipt_summary = read_json(FINAL_RECEIPT_DIR / "final_manual_receipt_completion_validator_summary.json")

    writeback_executed = writeback_summary.get("writeback_executed") is True
    real_eds_template_modified = writeback_summary.get("real_eds_template_modified") is True
    revalidation_sequence_allowed = writeback_executed and real_eds_template_modified

    sequence_rows = [
        {
            "sequence_step": "REVAL-001",
            "purpose": "Revalidate real EDS template after guarded writeback.",
            "command": "py scripts/build_external_dependency_escalation_sendout_receipt_validator.py",
            "allowed_now": "yes" if revalidation_sequence_allowed else "no",
            "blocking_reason": "" if revalidation_sequence_allowed else "19.58 has not executed real EDS writeback.",
        },
        {
            "sequence_step": "REVAL-002",
            "purpose": "Refresh safe-send state from the revalidated EDS summary.",
            "command": "py scripts/build_external_dependency_safe_send_execution_packet.py",
            "allowed_now": "yes" if revalidation_sequence_allowed else "no",
            "blocking_reason": "" if revalidation_sequence_allowed else "19.58 has not executed real EDS writeback.",
        },
        {
            "sequence_step": "REVAL-003",
            "purpose": "Re-run final manual receipt completion after FMR rows are manually updated.",
            "command": "py scripts/build_final_manual_receipt_completion_validator.py",
            "allowed_now": "no",
            "blocking_reason": "FMR-001 through FMR-006 are still incomplete; this orchestrator does not fill FMR rows.",
        },
        {
            "sequence_step": "REVAL-004",
            "purpose": "Run final guarded recheck only after all final manual receipts are complete.",
            "command": "reports/final_guarded_recheck_launcher_20260810/run_final_guarded_recheck_after_receipts.ps1",
            "allowed_now": "no",
            "blocking_reason": "19.50 guarded_recheck_allowed is false.",
        },
    ]

    command_rows = [
        {
            "command_id": row["sequence_step"],
            "command": row["command"],
            "execute_now": "no",
            "reason": "Current package is an orchestrator/no-go audit; commands are not executed automatically.",
        }
        for row in sequence_rows
    ]

    commands_allowed_now = sum(1 for row in sequence_rows if row["allowed_now"] == "yes")
    fmr001_unlock_allowed_after_revalidation = (
        revalidation_sequence_allowed
        and sendout_summary.get("fmr001_unlock_allowed") is True
        and safe_send_summary.get("fmr001_unlock_allowed") is True
    )

    blocker_rows = []
    if not revalidation_sequence_allowed:
        blocker_rows.append(
            {
                "blocker": "EDS writeback not executed",
                "evidence": f"writeback_executed={writeback_executed}; real_eds_template_modified={real_eds_template_modified}",
                "blocks": "19.54/19.55 post-writeback revalidation sequence",
            }
        )
    if final_receipt_summary.get("guarded_recheck_allowed") is not True:
        blocker_rows.append(
            {
                "blocker": "final manual receipts incomplete",
                "evidence": f"complete_receipt_rows={final_receipt_summary.get('complete_receipt_rows')}; guarded_recheck_allowed={final_receipt_summary.get('guarded_recheck_allowed')}",
                "blocks": "final guarded recheck and final master re-entry",
            }
        )

    qa_rows = [
        {
            "check": "19.58 writeback summary imported",
            "result": "PASS",
            "detail": f"writeback_executed={writeback_executed}",
        },
        {
            "check": "commands are not auto-executed",
            "result": "PASS" if all(row["execute_now"] == "no" for row in command_rows) else "FAIL",
            "detail": f"command_rows={len(command_rows)}",
        },
        {
            "check": "current no-go state preserved",
            "result": "PASS" if not fmr001_unlock_allowed_after_revalidation else "FAIL",
            "detail": f"fmr001_unlock_allowed_after_revalidation={fmr001_unlock_allowed_after_revalidation}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "external_dependency_post_writeback_revalidation_orchestrator_20260810",
        "writeback_executed": writeback_executed,
        "real_eds_template_modified": real_eds_template_modified,
        "revalidation_sequence_allowed": revalidation_sequence_allowed,
        "commands_allowed_now": commands_allowed_now,
        "commands_executed": False,
        "fmr001_unlock_allowed_after_revalidation": fmr001_unlock_allowed_after_revalidation,
        "guarded_recheck_allowed": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "blocker_rows": len(blocker_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": (
            "external_dependency_post_writeback_revalidation_orchestrator_ready_commands_listed"
            if revalidation_sequence_allowed
            else "external_dependency_post_writeback_revalidation_orchestrator_ready_refusing_current_state"
        ),
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "external_dependency_post_writeback_revalidation_sequence.csv",
        ["sequence_step", "purpose", "command", "allowed_now", "blocking_reason"],
        sequence_rows,
    )
    write_csv(
        OUT_DIR / "external_dependency_post_writeback_revalidation_command_manifest.csv",
        ["command_id", "command", "execute_now", "reason"],
        command_rows,
    )
    write_csv(
        OUT_DIR / "external_dependency_post_writeback_revalidation_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "external_dependency_post_writeback_revalidation_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    report = f"""# External Dependency Post-writeback Revalidation Orchestrator

Status: `{summary["status"]}`

Current result:

1. Writeback executed: {str(summary["writeback_executed"]).lower()}
2. Real EDS template modified: {str(summary["real_eds_template_modified"]).lower()}
3. Revalidation sequence allowed: {str(summary["revalidation_sequence_allowed"]).lower()}
4. Commands allowed now: {summary["commands_allowed_now"]}
5. Commands executed: false
6. FMR-001 unlock allowed after revalidation: {str(summary["fmr001_unlock_allowed_after_revalidation"]).lower()}
7. Guarded recheck allowed: false
8. Portal upload allowed: false
9. Submission ready: false

Boundary: this orchestrator is read-only in the current state. It does not run
revalidation commands, fill FMR rows, close gates, upload portal files or mark
the manuscript submitted.
"""
    write_text(OUT_DIR / "EXTERNAL_DEPENDENCY_POST_WRITEBACK_REVALIDATION_ORCHESTRATOR_README.md", report)
    write_text(OUT_DIR / "external_dependency_post_writeback_revalidation_orchestrator_report.md", report)
    write_text(
        OUT_DIR / "external_dependency_post_writeback_revalidation_orchestrator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
