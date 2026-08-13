#!/usr/bin/env python3
"""Build a one-page human execution brief from the readiness monitor."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manual_execution_brief_20260810"
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
    marker = "### 19.86 Manual execution brief update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/manual_execution_brief_20260810/` and Desktop brief `NatComms_19.86_manual_execution_brief_20260810.md` to give the execution owner a single-page view of the five human-only actions and hard no-go commands.
- Current `brief_action_rows={summary["brief_action_rows"]}`, `hard_no_go_rows={summary["hard_no_go_rows"]}`, `desktop_brief_exists={str(summary["desktop_brief_exists"]).lower()}`.
- Current `ready_for_downstream_validator_rows=0`, `ready_for_writeback_rows=0`, `allowed_commands_now=0`, `submission_ready=false`.
- Boundary: this brief is an instruction artifact only. It does not send messages, fill forms, create evidence, run validators, execute writeback, run recheck, upload portal files or submit.
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

    monitor_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "manual_evidence_readiness_monitor_20260810"
        / "manual_evidence_readiness_monitor_summary.json"
    )
    monitor_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "manual_evidence_readiness_monitor_20260810"
        / "manual_evidence_readiness_monitor.csv"
    )
    form_index = {
        row["form_id"]: row
        for row in read_csv(
            BENCH_ROOT
            / "reports"
            / "manual_only_execution_forms_20260810"
            / "manual_only_execution_forms_index.csv"
        )
    }

    brief_rows = []
    for row in monitor_rows:
        form = form_index.get(row["form_id"], {})
        brief_rows.append(
            {
                "order": row["form_id"].replace("MOF-", ""),
                "form_id": row["form_id"],
                "primary_fmr": row["primary_fmr"],
                "phase": row["phase"],
                "do_now": form.get("required_action", row["next_action"]),
                "put_evidence_here": form.get("evidence_source", ""),
                "fill_this_form": form.get("form_file", ""),
                "proof_required": form.get("proof_required", ""),
                "after_real_evidence": "run 19.84 validation first; downstream validator remains blocked until the form passes",
                "current_status": row["monitor_status"],
            }
        )

    no_go_rows = [
        {
            "rule_id": "MEB-NOGO-001",
            "do_not_do": "Do not run any --execute-writeback command.",
            "reason": "ready_for_writeback_rows=0",
        },
        {
            "rule_id": "MEB-NOGO-002",
            "do_not_do": "Do not run downstream validators from incomplete forms.",
            "reason": "ready_for_downstream_validator_rows=0",
        },
        {
            "rule_id": "MEB-NOGO-003",
            "do_not_do": "Do not run guarded recheck.",
            "reason": "complete_receipt_rows=0",
        },
        {
            "rule_id": "MEB-NOGO-004",
            "do_not_do": "Do not upload portal files or mark submitted.",
            "reason": "submission_ready=false",
        },
    ]

    qa_rows = [
        {
            "check": "brief covers all human-only next actions",
            "result": "PASS" if len(brief_rows) == monitor_summary.get("human_only_next_action_rows") else "FAIL",
            "detail": f"brief_action_rows={len(brief_rows)}; human_only_next_action_rows={monitor_summary.get('human_only_next_action_rows')}",
        },
        {
            "check": "brief preserves no-command state",
            "result": "PASS" if monitor_summary.get("allowed_commands_now") == 0 else "FAIL",
            "detail": f"allowed_commands_now={monitor_summary.get('allowed_commands_now')}",
        },
        {
            "check": "brief preserves submission blocked state",
            "result": "PASS" if not monitor_summary.get("submission_ready") else "FAIL",
            "detail": f"submission_ready={monitor_summary.get('submission_ready')}",
        },
    ]

    brief_lines = [
        "# NatComms 19.86 Manual Execution Brief",
        "",
        "Current status: only real human evidence actions are allowed.",
        "",
        "Allowed now:",
    ]
    for row in brief_rows:
        brief_lines.extend(
            [
                "",
                f"{row['order']}. {row['primary_fmr']} / {row['phase']}",
                f"- Do now: {row['do_now']}",
                f"- Put evidence here: `{row['put_evidence_here']}`",
                f"- Fill form: `{row['fill_this_form']}`",
                f"- Proof required: {row['proof_required']}",
                f"- After evidence: {row['after_real_evidence']}",
            ]
        )
    brief_lines.extend(["", "Hard no-go commands:"])
    for row in no_go_rows:
        brief_lines.append(f"- {row['do_not_do']} Reason: {row['reason']}.")
    brief_lines.extend(
        [
            "",
            "Boundary: this brief does not send messages, create evidence, run validators, execute writeback, run recheck, upload portal files or submit.",
        ]
    )
    brief_text = "\n".join(brief_lines) + "\n"

    summary = {
        "package": "manual_execution_brief_20260810",
        "brief_action_rows": len(brief_rows),
        "hard_no_go_rows": len(no_go_rows),
        "ready_for_downstream_validator_rows": int(monitor_summary.get("ready_for_downstream_validator_rows", 0) or 0),
        "ready_for_writeback_rows": int(monitor_summary.get("ready_for_writeback_rows", 0) or 0),
        "allowed_commands_now": 0,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "desktop_brief": str(DESKTOP_BRIEF),
        "desktop_brief_exists": True,
        "status": "manual_execution_brief_ready_human_actions_only",
    }

    write_csv(
        OUT_DIR / "manual_execution_brief_actions.csv",
        [
            "order",
            "form_id",
            "primary_fmr",
            "phase",
            "do_now",
            "put_evidence_here",
            "fill_this_form",
            "proof_required",
            "after_real_evidence",
            "current_status",
        ],
        brief_rows,
    )
    write_csv(OUT_DIR / "manual_execution_brief_no_go.csv", ["rule_id", "do_not_do", "reason"], no_go_rows)
    write_csv(OUT_DIR / "manual_execution_brief_qa.csv", ["check", "result", "detail"], qa_rows)
    write_text(OUT_DIR / "MANUAL_EXECUTION_BRIEF_README.md", brief_text)
    write_text(OUT_DIR / "manual_execution_brief_report.md", brief_text)
    write_text(DESKTOP_BRIEF, brief_text)
    summary["desktop_plan_updated"] = update_desktop_plan(summary)
    write_text(OUT_DIR / "manual_execution_brief_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
