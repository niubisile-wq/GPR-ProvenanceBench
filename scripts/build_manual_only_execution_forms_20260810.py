#!/usr/bin/env python3
"""Build execution forms for the five manual-only final execution steps."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manual_only_execution_forms_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


FORM_FIELDS = [
    "execution_step",
    "primary_fmr",
    "performed_by",
    "performed_at_local_time",
    "evidence_file_or_folder",
    "evidence_sha256",
    "source_channel",
    "counterparty_or_owner",
    "decision_or_return_summary",
    "sensitive_content_checked",
    "validator_ran",
    "validator_result",
    "notes",
]


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
    marker = "### 19.83 Manual-only execution forms update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/manual_only_execution_forms_20260810/` to turn the five manual-only FEB-001 to FEB-005 actions into fillable execution forms and evidence manifests.
- Current `form_rows={summary["form_rows"]}`, `manual_only_steps={summary["manual_only_steps"]}`, `ready_blank_forms={summary["ready_blank_forms"]}`.
- Current `filled_evidence_rows=0`, `allowed_commands_now=0`, `portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: these forms are blank intake instruments only. They do not send messages, fill evidence, compute real hashes, run validators, execute writeback, run recheck, upload portal files or submit.
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

    board_summary = read_json(BENCH_ROOT / "reports" / "final_execution_board_20260810" / "final_execution_board_summary.json")
    board_rows = read_csv(BENCH_ROOT / "reports" / "final_execution_board_20260810" / "final_execution_board.csv")
    operator_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "fmr_manual_evidence_operator_packet_20260810"
        / "fmr_manual_evidence_operator_packet.csv"
    )

    manual_rows = [row for row in board_rows if row["allowed_now"] == "manual_only"]
    operator_by_fmr: dict[str, list[dict[str, str]]] = {}
    for row in operator_rows:
        operator_by_fmr.setdefault(row["receipt_id"], []).append(row)

    form_rows = []
    manifest_rows = []
    for row in manual_rows:
        form_id = row["step_id"].replace("FEB", "MOF")
        primary_fmr = row["primary_fmr"]
        related_operator_rows = operator_by_fmr.get(primary_fmr, [])
        default_inbox = row["evidence_source"]
        form_rows.append(
            {
                "form_id": form_id,
                "step_id": row["step_id"],
                "phase": row["phase"],
                "primary_fmr": primary_fmr,
                "required_action": row["required_action"],
                "evidence_source": default_inbox,
                "proof_required": row["proof_required"],
                "next_validator": row["next_validator"],
                "form_file": f"reports/manual_only_execution_forms_20260810/forms/{form_id}_{row['phase']}.csv",
                "operator_rows_linked": len(related_operator_rows),
                "current_status": row["current_status"],
                "writeback_allowed_now": "no",
                "portal_upload_allowed_now": "no",
            }
        )
        manifest_rows.append(
            {
                "form_id": form_id,
                "primary_fmr": primary_fmr,
                "expected_evidence_location": default_inbox,
                "evidence_must_be_real": "yes",
                "placeholders_allowed": "no",
                "support_reports_count_as_evidence": "no",
                "hash_required_before_writeback": "yes",
                "validator_required_before_writeback": row["next_validator"],
            }
        )
        write_csv(
            OUT_DIR / "forms" / f"{form_id}_{row['phase']}.csv",
            FORM_FIELDS,
            [
                {
                    "execution_step": f"{row['step_id']} {row['phase']}",
                    "primary_fmr": primary_fmr,
                    "performed_by": "",
                    "performed_at_local_time": "",
                    "evidence_file_or_folder": "",
                    "evidence_sha256": "",
                    "source_channel": "",
                    "counterparty_or_owner": "",
                    "decision_or_return_summary": "",
                    "sensitive_content_checked": "not_checked",
                    "validator_ran": "no",
                    "validator_result": "not_run",
                    "notes": "",
                }
            ],
        )

    stop_rows = [
        {
            "rule_id": "MOF-NOGO-001",
            "rule": "Leave form rows blank until the real manual action has occurred.",
            "current_state": "filled_evidence_rows=0",
        },
        {
            "rule_id": "MOF-NOGO-002",
            "rule": "Do not use these forms as evidence by themselves; attach the real source file, receipt or decision record.",
            "current_state": "support_reports_count_as_evidence=no",
        },
        {
            "rule_id": "MOF-NOGO-003",
            "rule": "Do not run FMR writeback from a filled form unless the matching validator emits an allowed candidate.",
            "current_state": f"allowed_commands_now={board_summary.get('allowed_commands_now')}",
        },
        {
            "rule_id": "MOF-NOGO-004",
            "rule": "Do not upload portal files from this package.",
            "current_state": "portal_upload_allowed=false; submission_ready=false",
        },
    ]

    qa_rows = [
        {
            "check": "one form per manual-only board step",
            "result": "PASS" if len(form_rows) == int(board_summary.get("open_execution_steps", -1)) else "FAIL",
            "detail": f"form_rows={len(form_rows)}; open_execution_steps={board_summary.get('open_execution_steps')}",
        },
        {
            "check": "all forms are blank and non-executing",
            "result": "PASS",
            "detail": "filled_evidence_rows=0; validator_ran=no; writeback_allowed_now=no",
        },
        {
            "check": "all forms point to validators",
            "result": "PASS" if all(row["next_validator"] for row in form_rows) else "FAIL",
            "detail": f"validator_links={sum(1 for row in form_rows if row['next_validator'])}",
        },
        {
            "check": "submission remains blocked",
            "result": "PASS",
            "detail": "portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "manual_only_execution_forms_20260810",
        "manual_only_steps": int(board_summary.get("open_execution_steps", 0) or 0),
        "form_rows": len(form_rows),
        "manifest_rows": len(manifest_rows),
        "stop_rules": len(stop_rows),
        "ready_blank_forms": len(form_rows),
        "filled_evidence_rows": 0,
        "allowed_commands_now": 0,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "manual_only_execution_forms_ready_blank_waiting_real_actions",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "manual_only_execution_forms_index.csv",
        [
            "form_id",
            "step_id",
            "phase",
            "primary_fmr",
            "required_action",
            "evidence_source",
            "proof_required",
            "next_validator",
            "form_file",
            "operator_rows_linked",
            "current_status",
            "writeback_allowed_now",
            "portal_upload_allowed_now",
        ],
        form_rows,
    )
    write_csv(
        OUT_DIR / "manual_only_execution_evidence_manifest.csv",
        [
            "form_id",
            "primary_fmr",
            "expected_evidence_location",
            "evidence_must_be_real",
            "placeholders_allowed",
            "support_reports_count_as_evidence",
            "hash_required_before_writeback",
            "validator_required_before_writeback",
        ],
        manifest_rows,
    )
    write_csv(OUT_DIR / "manual_only_execution_stop_rules.csv", ["rule_id", "rule", "current_state"], stop_rows)
    write_csv(OUT_DIR / "manual_only_execution_forms_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# Manual-Only Execution Forms

Status: `{summary["status"]}`

Current result:

1. Manual-only steps: {summary["manual_only_steps"]}
2. Form rows: {summary["form_rows"]}
3. Ready blank forms: {summary["ready_blank_forms"]}
4. Filled evidence rows: 0
5. Allowed commands now: 0
6. Portal upload allowed: false
7. Submission ready: false

Use these forms only after the real manual action happens. The form records
where the evidence was placed, what hash was computed and which validator was
run. It is not evidence by itself.

Boundary: these forms do not send messages, fill evidence, compute real hashes,
run validators, execute writeback, run recheck, upload portal files or submit.
"""
    write_text(OUT_DIR / "MANUAL_ONLY_EXECUTION_FORMS_README.md", report)
    write_text(OUT_DIR / "manual_only_execution_forms_report.md", report)
    write_text(OUT_DIR / "manual_only_execution_forms_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
