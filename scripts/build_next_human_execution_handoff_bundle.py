#!/usr/bin/env python3
"""Build a Desktop handoff bundle for the next human execution step."""

from __future__ import annotations

import csv
import json
import shutil
import zipfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "next_human_execution_handoff_bundle_20260810"
DESKTOP = Path.home() / "Desktop"
DESKTOP_PLAN = DESKTOP / "8月10日cns.md"
DESKTOP_ZIP = DESKTOP / "NatComms_下一步人工执行handoff_20260810.zip"

SOURCE_FILES = [
    (DESKTOP / "NatComms_manual_dispatch_master_packet_20260810.zip", "00_master_dispatch/NatComms_manual_dispatch_master_packet_20260810.zip"),
    (DESKTOP / "NatComms_今日人工动作最小包_20260810.md", "01_start_here/NatComms_今日人工动作最小包_20260810.md"),
    (DESKTOP / "NatComms_人工证据回收Inbox说明_20260810.md", "01_start_here/NatComms_人工证据回收Inbox说明_20260810.md"),
    (DESKTOP / "NatComms_人工证据填写与重跑说明_20260810.md", "01_start_here/NatComms_人工证据填写与重跑说明_20260810.md"),
    (REPORTS / "manual_evidence_lifecycle_dashboard_20260810" / "manual_evidence_lifecycle_dashboard.csv", "02_lifecycle/manual_evidence_lifecycle_dashboard.csv"),
    (REPORTS / "manual_evidence_lifecycle_dashboard_20260810" / "manual_evidence_lifecycle_next_actions.csv", "02_lifecycle/manual_evidence_lifecycle_next_actions.csv"),
    (REPORTS / "manual_evidence_lifecycle_dashboard_20260810" / "manual_evidence_lifecycle_blockers.csv", "02_lifecycle/manual_evidence_lifecycle_blockers.csv"),
    (REPORTS / "inbox_to_tracker_writeback_queue_20260810" / "inbox_to_tracker_writeback_queue.csv", "03_writeback/inbox_to_tracker_writeback_queue.csv"),
    (REPORTS / "manual_evidence_inbox_audit_20260810" / "manual_evidence_inbox_folder_audit.csv", "03_writeback/manual_evidence_inbox_folder_audit.csv"),
    (REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_next_validation_commands.csv", "04_validators/post_dispatch_next_validation_commands.csv"),
    (REPORTS / "gate_closure_execution_board_20260810" / "gate_closure_execution_board.csv", "04_validators/gate_closure_execution_board.csv"),
]

SUMMARIES = [
    REPORTS / "today_manual_action_minipack_20260810" / "today_manual_action_minipack_summary.json",
    REPORTS / "manual_evidence_lifecycle_dashboard_20260810" / "manual_evidence_lifecycle_dashboard_summary.json",
    REPORTS / "inbox_to_tracker_writeback_queue_20260810" / "inbox_to_tracker_writeback_queue_summary.json",
    REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_evidence_intake_validator_summary.json",
    REPORTS / "gate_closure_execution_board_20260810" / "gate_closure_execution_board_summary.json",
]


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
    marker = "### 18.94 Next human execution handoff bundle update"
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


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    summaries = [read_json(path) for path in SUMMARIES]
    state = {
        "manual_actions_executed": False,
        "candidate_evidence_files": 0,
        "writeback_allowed_rows": 0,
        "evidence_rows_passed": 0,
        "gate_closure_allowed": False,
        "submission_ready": False,
    }
    for summary in summaries:
        for key in list(state):
            if key in summary:
                state[key] = summary[key]

    manifest_rows = []
    missing = []
    for source, archive_name in SOURCE_FILES:
        exists = source.exists()
        if not exists:
            missing.append(str(source))
        manifest_rows.append(
            {
                "source_path": str(source),
                "archive_name": archive_name,
                "exists": exists,
                "size_bytes": source.stat().st_size if exists else 0,
            }
        )

    handoff_readme = [
        "# NatComms 下一步人工执行 handoff 2026-08-10",
        "",
        "当前状态：还不能投稿。这个压缩包只用于人工执行下一步，不代表已经发送、已经收到证据或已经关 gate。",
        "",
        "## 打开顺序",
        "",
        "1. 先看 `01_start_here/NatComms_今日人工动作最小包_20260810.md`。",
        "2. 发送或请求真实材料后，把返回文件放进 `manual_evidence_inbox_20260810` 对应文件夹。",
        "3. 跑 inbox audit，再看 writeback queue。",
        "4. 只有 post-dispatch validator 通过后，才跑后续 branch validators。",
        "",
        "## 当前状态",
        "",
    ]
    for key, value in state.items():
        handoff_readme.append(f"- {key}: `{value}`")
    handoff_readme.extend(
        [
            "",
            "## 禁止",
            "",
            "- 不要把这个 handoff zip 当成已发送证据。",
            "- 不要从 recommended choice 直接写 tracker。",
            "- 不要把 inbox 文件存在当成 gate closure。",
            "- 不要在 submission_ready=false 时上传 portal。",
            "",
        ]
    )
    readme_path = OUT_DIR / "NEXT_HUMAN_EXECUTION_HANDOFF_README.md"
    write_text(readme_path, "\n".join(handoff_readme))
    manifest_rows.append(
        {
            "source_path": str(readme_path),
            "archive_name": "README_NEXT_HUMAN_EXECUTION_HANDOFF.md",
            "exists": True,
            "size_bytes": readme_path.stat().st_size,
        }
    )

    write_csv(OUT_DIR / "next_human_execution_handoff_manifest.csv", manifest_rows, ["source_path", "archive_name", "exists", "size_bytes"])

    if DESKTOP_ZIP.exists():
        DESKTOP_ZIP.unlink()
    with zipfile.ZipFile(DESKTOP_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for row in manifest_rows:
            if row["exists"]:
                zf.write(row["source_path"], row["archive_name"])

    local_zip = OUT_DIR / "NatComms_next_human_execution_handoff_20260810.zip"
    shutil.copy2(DESKTOP_ZIP, local_zip)

    with zipfile.ZipFile(DESKTOP_ZIP, "r") as zf:
        zip_members = zf.namelist()

    qa_rows = [
        {
            "check": "all_sources_present",
            "result": "PASS" if not missing else "FAIL",
            "detail": "; ".join(missing),
        },
        {
            "check": "desktop_zip_created",
            "result": "PASS" if DESKTOP_ZIP.exists() else "FAIL",
            "detail": str(DESKTOP_ZIP),
        },
        {
            "check": "zip_has_expected_members",
            "result": "PASS" if len(zip_members) == len(manifest_rows) else "FAIL",
            "detail": f"zip_members={len(zip_members)}; manifest_rows={len(manifest_rows)}",
        },
        {
            "check": "not_executed_state_preserved",
            "result": "PASS" if state["manual_actions_executed"] is False and state["submission_ready"] is False else "FAIL",
            "detail": f"manual_actions_executed={state['manual_actions_executed']}; submission_ready={state['submission_ready']}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)
    write_csv(OUT_DIR / "next_human_execution_handoff_bundle_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Next human execution handoff bundle report 2026-08-10",
        "",
        "Status: `next_human_execution_handoff_ready_not_executed`",
        "",
        f"1. Manifest rows: {len(manifest_rows)}",
        f"2. Zip members: {len(zip_members)}",
        f"3. Desktop zip: `{DESKTOP_ZIP}`",
        f"4. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: the next human-execution handoff bundle is ready, but no manual action or evidence state is changed.",
        "",
    ]
    write_text(OUT_DIR / "next_human_execution_handoff_bundle_report.md", "\n".join(report))

    summary = {
        "package": "next_human_execution_handoff_bundle_20260810",
        "manifest_rows": len(manifest_rows),
        "zip_members": len(zip_members),
        "desktop_zip": str(DESKTOP_ZIP),
        "desktop_zip_exists": DESKTOP_ZIP.exists(),
        "local_zip": str(local_zip),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "manual_actions_executed": state["manual_actions_executed"],
        "candidate_evidence_files": state["candidate_evidence_files"],
        "writeback_allowed_rows": state["writeback_allowed_rows"],
        "evidence_rows_passed": state["evidence_rows_passed"],
        "gate_closure_allowed": state["gate_closure_allowed"],
        "submission_ready": state["submission_ready"],
        "status": "next_human_execution_handoff_ready_not_executed",
    }

    section = f"""### 18.94 Next human execution handoff bundle update

Added a Desktop handoff zip that consolidates the next human-execution entry points: master dispatch zip, same-day action guide, inbox instructions, lifecycle dashboard, writeback queue, validator commands and gate board.

New directory: `{OUT_DIR}`

Desktop zip: `{DESKTOP_ZIP}`

New files:
1. `next_human_execution_handoff_manifest.csv`
2. `NEXT_HUMAN_EXECUTION_HANDOFF_README.md`
3. `next_human_execution_handoff_bundle_qa.csv`
4. `next_human_execution_handoff_bundle_report.md`
5. `next_human_execution_handoff_bundle_summary.json`
6. `NatComms_next_human_execution_handoff_20260810.zip`
7. Desktop `NatComms_下一步人工执行handoff_20260810.zip`

Current result:
1. manifest_rows = {summary['manifest_rows']}
2. zip_members = {summary['zip_members']}
3. qa_pass = {str(qa_pass).lower()}
4. manual_actions_executed = false
5. candidate_evidence_files = {summary['candidate_evidence_files']}
6. evidence_rows_passed = {summary['evidence_rows_passed']}
7. submission_ready = false

Boundary:
1. This step only packages instructions and current status.
2. This step does not send messages or write evidence.
3. This step does not close gates or authorize upload."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "next_human_execution_handoff_bundle_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Next human execution handoff bundle QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
