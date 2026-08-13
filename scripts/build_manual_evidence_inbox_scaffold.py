#!/usr/bin/env python3
"""Create an empty manual evidence inbox scaffold for returned files."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "manual_evidence_inbox_scaffold_20260810"
INBOX_ROOT = BENCH_ROOT / "manual_evidence_inbox_20260810"
DESKTOP = Path.home() / "Desktop"
DESKTOP_PLAN = DESKTOP / "8月10日cns.md"
DESKTOP_README = DESKTOP / "NatComms_人工证据回收Inbox说明_20260810.md"

ACTION_MINIPACK = REPORTS / "today_manual_action_minipack_20260810" / "today_manual_action_minipack.csv"
CAPTURE_TARGETS = REPORTS / "today_manual_action_minipack_20260810" / "today_evidence_capture_targets.csv"
WORKSHEET = REPORTS / "manual_evidence_intake_worksheet_20260810" / "manual_evidence_intake_worksheet.csv"
POST_DISPATCH = REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_evidence_intake_validator_summary.json"


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


def safe_name(value: str) -> str:
    return value.lower().replace(" ", "_").replace("/", "_").replace("-", "_")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 18.90 Manual evidence inbox scaffold update"
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
    INBOX_ROOT.mkdir(parents=True, exist_ok=True)

    action_rows = read_csv(ACTION_MINIPACK)
    capture_rows = read_csv(CAPTURE_TARGETS)
    worksheet_rows = read_csv(WORKSHEET)
    post_dispatch = read_json(POST_DISPATCH)

    worksheet_by_dispatch: dict[str, list[str]] = {}
    for row in worksheet_rows:
        worksheet_by_dispatch.setdefault(row["dispatch_id"], []).append(row["worksheet_id"])

    inbox_rows: list[dict[str, object]] = []
    for row in action_rows:
        folder_name = f"{row['dispatch_id']}_{safe_name(row['linked_gate'])}"
        folder = INBOX_ROOT / folder_name
        folder.mkdir(parents=True, exist_ok=True)
        readme = folder / "README_DO_NOT_EDIT_TRACKERS_HERE.md"
        write_text(
            readme,
            "\n".join(
                [
                    f"# {row['dispatch_id']} evidence inbox",
                    "",
                    "Place raw returned files here first. Do not edit project trackers directly from this folder.",
                    "",
                    f"Linked gate: {row['linked_gate']}",
                    f"Recipient/owner: {row['recipient_or_owner']}",
                    f"Acceptance evidence: {row['acceptance_evidence']}",
                    f"First validator after return: {row['first_validator_after_return']}",
                    "",
                    "Filename template:",
                    f"`{row['dispatch_id']}_YYYYMMDD_sender_short-description.ext`",
                    "",
                    "Do not place label files in analyst-visible folders before prediction freeze.",
                    "",
                ]
            ),
        )
        inbox_rows.append(
            {
                "dispatch_id": row["dispatch_id"],
                "linked_gate": row["linked_gate"],
                "inbox_folder": str(folder.relative_to(BENCH_ROOT)).replace("\\", "/"),
                "readme": str(readme.relative_to(BENCH_ROOT)).replace("\\", "/"),
                "filename_template": f"{row['dispatch_id']}_YYYYMMDD_sender_short-description.ext",
                "worksheet_ids": "; ".join(worksheet_by_dispatch.get(row["dispatch_id"], [])),
                "first_validator_after_return": row["first_validator_after_return"],
                "evidence_written": "no",
            }
        )

    manifest_rows = [
        {
            "manual_step": "1",
            "instruction": "Drop returned raw files into the matching dispatch inbox folder.",
            "do_not_do": "Do not rename files after recording checksums.",
        },
        {
            "manual_step": "2",
            "instruction": "Record only validated file paths and timestamps into the worksheet target trackers.",
            "do_not_do": "Do not paste evidence into fields outside the worksheet map.",
        },
        {
            "manual_step": "3",
            "instruction": "Run post-dispatch evidence intake before any branch validator.",
            "do_not_do": "Do not close gates from inbox file presence alone.",
        },
    ]

    stop_rows = [
        {"rule_id": "INBOX-STOP-001", "rule": "Inbox file presence is not gate evidence until the validator passes."},
        {"rule_id": "INBOX-STOP-002", "rule": "Do not put external blind labels into analyst-visible inbox folders."},
        {"rule_id": "INBOX-STOP-003", "rule": "Do not overwrite tracker files from raw returned attachments."},
        {"rule_id": "INBOX-STOP-004", "rule": "Do not mark email_sent or returned rows from planned/simulated messages."},
        {"rule_id": "INBOX-STOP-005", "rule": "Do not store third-party raw files in public release staging from this inbox."},
    ]

    readme_lines = [
        "# NatComms 人工证据回收 Inbox 说明 2026-08-10",
        "",
        "当前状态：还不能投稿。这个 inbox 只用于临时接收真实人工返回材料，不代表证据已经写入 tracker。",
        "",
        f"Inbox root: `{INBOX_ROOT}`",
        "",
        "## 使用顺序",
        "",
        "1. 把真实返回文件放进对应 `MD-xxx` 文件夹。",
        "2. 按 worksheet 目标文件填写路径、时间、选择或回复。",
        "3. 先运行 post-dispatch intake validator。",
        "4. 只有 validator 通过后，才运行对应 branch validator。",
        "",
        "## 禁止",
        "",
    ]
    for row in stop_rows:
        readme_lines.append(f"- {row['rule_id']}: {row['rule']}")
    readme_lines.append("")

    write_csv(
        OUT_DIR / "manual_evidence_inbox_manifest.csv",
        inbox_rows,
        ["dispatch_id", "linked_gate", "inbox_folder", "readme", "filename_template", "worksheet_ids", "first_validator_after_return", "evidence_written"],
    )
    write_csv(OUT_DIR / "manual_evidence_inbox_operator_steps.csv", manifest_rows, ["manual_step", "instruction", "do_not_do"])
    write_csv(OUT_DIR / "manual_evidence_inbox_stop_rules.csv", stop_rows, ["rule_id", "rule"])
    write_text(OUT_DIR / "MANUAL_EVIDENCE_INBOX_README.md", "\n".join(readme_lines))
    shutil.copy2(OUT_DIR / "MANUAL_EVIDENCE_INBOX_README.md", DESKTOP_README)

    qa_rows = [
        {
            "check": "six_inbox_folders_created",
            "result": "PASS" if len(inbox_rows) == 6 and all((BENCH_ROOT / row["inbox_folder"]).exists() for row in inbox_rows) else "FAIL",
            "detail": f"inbox_rows={len(inbox_rows)}",
        },
        {
            "check": "capture_targets_imported",
            "result": "PASS" if len(capture_rows) == 5 else "FAIL",
            "detail": f"capture_rows={len(capture_rows)}",
        },
        {
            "check": "desktop_readme_created",
            "result": "PASS" if DESKTOP_README.exists() else "FAIL",
            "detail": str(DESKTOP_README),
        },
        {
            "check": "no_evidence_written",
            "result": "PASS" if post_dispatch.get("evidence_rows_passed") == 0 else "FAIL",
            "detail": f"evidence_rows_passed={post_dispatch.get('evidence_rows_passed')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)
    write_csv(OUT_DIR / "manual_evidence_inbox_scaffold_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Manual evidence inbox scaffold report 2026-08-10",
        "",
        "Status: `manual_evidence_inbox_scaffold_ready_empty`",
        "",
        f"1. Inbox folders: {len(inbox_rows)}",
        f"2. Operator steps: {len(manifest_rows)}",
        f"3. Stop rules: {len(stop_rows)}",
        f"4. Desktop README: `{DESKTOP_README}`",
        f"5. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: an empty inbox scaffold is ready for real returned evidence, but no evidence is written or validated.",
        "",
    ]
    write_text(OUT_DIR / "manual_evidence_inbox_scaffold_report.md", "\n".join(report))

    summary = {
        "package": "manual_evidence_inbox_scaffold_20260810",
        "inbox_root": str(INBOX_ROOT),
        "inbox_folders": len(inbox_rows),
        "operator_steps": len(manifest_rows),
        "stop_rules": len(stop_rows),
        "desktop_readme": str(DESKTOP_README),
        "desktop_readme_exists": DESKTOP_README.exists(),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "manual_evidence_written": False,
        "evidence_rows_passed": post_dispatch.get("evidence_rows_passed"),
        "submission_ready": False,
        "status": "manual_evidence_inbox_scaffold_ready_empty",
    }

    section = f"""### 18.90 Manual evidence inbox scaffold update

Added an empty manual evidence inbox scaffold for storing real returned files before worksheet entry and validator reruns.

New directory: `{OUT_DIR}`

Inbox root: `{INBOX_ROOT}`

Desktop README: `{DESKTOP_README}`

New files:
1. `manual_evidence_inbox_manifest.csv`
2. `manual_evidence_inbox_operator_steps.csv`
3. `manual_evidence_inbox_stop_rules.csv`
4. `MANUAL_EVIDENCE_INBOX_README.md`
5. `manual_evidence_inbox_scaffold_qa.csv`
6. `manual_evidence_inbox_scaffold_report.md`
7. `manual_evidence_inbox_scaffold_summary.json`

Current result:
1. inbox_folders = {summary['inbox_folders']}
2. operator_steps = {summary['operator_steps']}
3. stop_rules = {summary['stop_rules']}
4. qa_pass = {str(qa_pass).lower()}
5. manual_evidence_written = false
6. evidence_rows_passed = {summary['evidence_rows_passed']}
7. submission_ready = false

Boundary:
1. This step creates empty inbox folders only.
2. This step does not write tracker evidence.
3. This step does not run branch validators or close gates."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "manual_evidence_inbox_scaffold_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Manual evidence inbox scaffold QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
