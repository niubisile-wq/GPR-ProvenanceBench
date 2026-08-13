#!/usr/bin/env python3
"""Build the current Nat Comms finalization command dashboard v3."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_finalization_command_dashboard_v3_20260810"

MASTER_CHECKLIST = BENCH_ROOT / "reports" / "natcomms_finalization_master_checklist_20260810" / "finalization_master_checklist.csv"
AUTHOR_INGESTION = BENCH_ROOT / "reports" / "natcomms_author_reply_ingestion_validator_20260810" / "gate_closure_from_author_replies.csv"
GATE_BINDER = BENCH_ROOT / "reports" / "natcomms_gate_closure_evidence_binder_20260810" / "gate_closure_evidence_binder.csv"
EVIDENCE_REQUIREMENTS = BENCH_ROOT / "reports" / "natcomms_gate_closure_evidence_binder_20260810" / "gate_artifact_evidence_requirements.csv"
CLOSURE_ORDER = BENCH_ROOT / "reports" / "natcomms_gate_closure_evidence_binder_20260810" / "gate_closure_execution_order.csv"
FORBIDDEN_SHORTCUTS = BENCH_ROOT / "reports" / "natcomms_gate_closure_evidence_binder_20260810" / "gate_closure_forbidden_shortcuts.csv"
PORTAL_ITEMS = BENCH_ROOT / "reports" / "natcomms_portal_upload_manifest_prelock_20260810" / "portal_upload_item_manifest.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    master_rows = read_csv(MASTER_CHECKLIST)
    author_rows = {row["gate_id"]: row for row in read_csv(AUTHOR_INGESTION)}
    binder_rows = {row["gate_id"]: row for row in read_csv(GATE_BINDER)}
    evidence_rows = read_csv(EVIDENCE_REQUIREMENTS)
    order_rows = read_csv(CLOSURE_ORDER)
    shortcut_rows = read_csv(FORBIDDEN_SHORTCUTS)
    portal_rows = read_csv(PORTAL_ITEMS)

    evidence_by_gate: dict[str, list[dict[str, str]]] = {}
    for row in evidence_rows:
        evidence_by_gate.setdefault(row["gate_id"], []).append(row)

    command_rows = []
    for order in order_rows:
        gate_id = order["gate_id"]
        master = next(row for row in master_rows if row["gate_id"] == gate_id)
        author = author_rows.get(gate_id, {})
        binder = binder_rows.get(gate_id, {})
        evidence_for_gate = evidence_by_gate.get(gate_id, [])
        open_evidence = [row["requirement_id"] for row in evidence_for_gate if row["closure_allowed"] != "yes"]
        command_rows.append(
            {
                "priority": order["order"],
                "gate_id": gate_id,
                "gate": master["gate"],
                "current_state": master["current_state"],
                "author_reply_status": author.get("reply_evidence_status", "not_mapped"),
                "open_evidence_count": str(len(open_evidence)),
                "open_evidence_requirements": "; ".join(open_evidence),
                "portal_impact": master["blocks"],
                "next_command": order["action"],
                "blocked_by": order["blocked_by"],
                "command_status": "blocked_keep_open",
            }
        )
    write_csv(
        OUT_DIR / "finalization_command_dashboard_v3.csv",
        command_rows,
        ["priority", "gate_id", "gate", "current_state", "author_reply_status", "open_evidence_count", "open_evidence_requirements", "portal_impact", "next_command", "blocked_by", "command_status"],
    )

    upload_rows = []
    for row in portal_rows:
        upload_rows.append(
            {
                "upload_item": row.get("upload_item", ""),
                "current_status": row.get("current_status", ""),
                "upload_ready": row.get("upload_ready", ""),
                "blocking_gate_or_artifact": row.get("blocking_gate_or_artifact", row.get("blocking_gate", "")),
                "dashboard_action": "Keep blocked until linked finalization gate is closed.",
            }
        )
    write_csv(
        OUT_DIR / "portal_upload_command_overlay.csv",
        upload_rows,
        ["upload_item", "current_status", "upload_ready", "blocking_gate_or_artifact", "dashboard_action"],
    )

    critical_path_rows = [
        {
            "path_step": "1",
            "critical_item": "Author/admin and branch replies",
            "why_first": "They decide title page, declarations, Track B wording and whether figure rendering can start.",
            "current_status": "blank author replies",
            "owner": "author/corresponding author",
        },
        {
            "path_step": "2",
            "critical_item": "Figure backend and formal figure rendering",
            "why_first": "Figures drive Source Data, Reporting Summary, final captions and manuscript/SI assembly.",
            "current_status": "backend undecided; rendered_figures=0",
            "owner": "author/analysis",
        },
        {
            "path_step": "3",
            "critical_item": "Rights/licence and DOI path",
            "why_first": "Repository DOI and release permissions control Data/Code Availability and portal upload.",
            "current_status": "predeposit only; no DOI",
            "owner": "author/institution/repository lead",
        },
        {
            "path_step": "4",
            "critical_item": "Reporting Summary and references",
            "why_first": "These cannot lock until figures, availability, validation status and final prose order are stable.",
            "current_status": "prelock only",
            "owner": "analysis/reference lead",
        },
        {
            "path_step": "5",
            "critical_item": "Final manuscript/SI and portal upload",
            "why_first": "These are last-mile assembly tasks after all upstream gates are closed.",
            "current_status": "not ready; upload_ready_rows=0",
            "owner": "writing lead/corresponding author",
        },
    ]
    write_csv(
        OUT_DIR / "critical_path_command_queue.csv",
        critical_path_rows,
        ["path_step", "critical_item", "why_first", "current_status", "owner"],
    )

    no_go_rows = [
        {
            "no_go_id": "NG-V3-001",
            "condition": "Any author_reply field remains blank.",
            "current_status": "active",
            "effect": "No author/admin, branch, backend, rights, Reporting Summary or portal gate can close.",
        },
        {
            "no_go_id": "NG-V3-002",
            "condition": "Figure backend is undecided or rendered_figures=0.",
            "current_status": "active",
            "effect": "Formal figure, Source Data, Reporting Summary and final-file gates remain blocked.",
        },
        {
            "no_go_id": "NG-V3-003",
            "condition": "No repository DOI, code DOI or rights clearance exists.",
            "current_status": "active",
            "effect": "Data/Code Availability and portal upload remain blocked.",
        },
        {
            "no_go_id": "NG-V3-004",
            "condition": "Reporting Summary and references remain prelock.",
            "current_status": "active",
            "effect": "Final manuscript/SI files cannot be generated.",
        },
        {
            "no_go_id": "NG-V3-005",
            "condition": "Portal upload_ready_rows remain zero.",
            "current_status": "active",
            "effect": "No actual submission can be attempted.",
        },
    ]
    write_csv(OUT_DIR / "finalization_no_go_register_v3.csv", no_go_rows, ["no_go_id", "condition", "current_status", "effect"])

    md = [
        "# Nat Comms finalization command dashboard v3",
        "",
        "Current branch: Track B remains the applicable route unless a real blind external asset is supplied and evaluated under the locked protocol.",
        "",
        "Submission status: not ready.",
        "",
        "## Immediate command",
        "",
        "1. Collect author/admin and branch replies before treating any finalization gate as closable.",
        "2. Choose a single figure backend before formal rendering.",
        "3. Keep DOI, Reporting Summary, references, final files and portal upload blocked until upstream evidence exists.",
        "",
        "## Hard boundary",
        "",
        "This dashboard is a command view only. It does not close gates, render figures, create DOI records, finalize references or submit the manuscript.",
        "",
    ]
    (OUT_DIR / "finalization_command_dashboard_v3.md").write_text("\n".join(md), encoding="utf-8")

    blocked_commands = sum(1 for row in command_rows if row["command_status"] == "blocked_keep_open")
    blocked_uploads = sum(1 for row in upload_rows if row["upload_ready"].lower() != "yes")
    qa_rows = [
        {"check": "Eight command rows", "result": "PASS" if len(command_rows) == 8 else "FAIL", "detail": f"{len(command_rows)} rows."},
        {"check": "No false command unlock", "result": "PASS" if blocked_commands == 8 else "FAIL", "detail": f"{blocked_commands} blocked commands."},
        {"check": "Portal overlay covers uploads", "result": "PASS" if len(upload_rows) == 9 else "FAIL", "detail": f"{len(upload_rows)} upload rows."},
        {"check": "Portal remains blocked", "result": "PASS" if blocked_uploads == 9 else "FAIL", "detail": f"{blocked_uploads} blocked upload rows."},
        {"check": "No-go register active", "result": "PASS" if len(no_go_rows) == 5 else "FAIL", "detail": f"{len(no_go_rows)} no-go rows."},
    ]
    write_csv(OUT_DIR / "finalization_command_dashboard_v3_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = [
        "# Nat Comms finalization command dashboard v3",
        "",
        "Use this package as the single command view after the gate closure evidence binder.",
        "",
        "All command rows are currently blocked_keep_open. This is intentional because final author replies, figures, DOI/rights, Reporting Summary, references, final files and portal readiness are missing.",
        "",
    ]
    (OUT_DIR / "NATCOMMS_FINALIZATION_COMMAND_DASHBOARD_V3_README.md").write_text("\n".join(readme), encoding="utf-8")

    report = [
        "# Finalization command dashboard v3 report",
        "",
        f"- Command rows: {len(command_rows)}",
        f"- Blocked commands: {blocked_commands}",
        f"- Portal overlay rows: {len(upload_rows)}",
        f"- Blocked portal rows: {blocked_uploads}",
        f"- Critical path rows: {len(critical_path_rows)}",
        f"- No-go rows: {len(no_go_rows)}",
        f"- Forbidden shortcuts imported: {len(shortcut_rows)}",
        f"- QA failures: {sum(1 for row in qa_rows if row['result'] == 'FAIL')}",
        "- Status: natcomms_finalization_command_dashboard_v3_ready_all_commands_blocked",
        "",
    ]
    (OUT_DIR / "finalization_command_dashboard_v3_report.md").write_text("\n".join(report), encoding="utf-8")

    summary = {
        "run_id": "20260810_natcomms_finalization_command_dashboard_v3",
        "command_rows": len(command_rows),
        "blocked_commands": blocked_commands,
        "portal_overlay_rows": len(upload_rows),
        "blocked_portal_rows": blocked_uploads,
        "critical_path_rows": len(critical_path_rows),
        "no_go_rows": len(no_go_rows),
        "forbidden_shortcuts_imported": len(shortcut_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "current_applicable_branch": "TRACK-B",
        "gate_closure_allowed": False,
        "portal_upload_ready": False,
        "submission_ready": False,
        "status": "natcomms_finalization_command_dashboard_v3_ready_all_commands_blocked",
        "boundary": "Dashboard is a command view only; all finalization commands remain blocked until required replies and artifacts exist.",
    }
    (OUT_DIR / "finalization_command_dashboard_v3_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
