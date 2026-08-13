#!/usr/bin/env python3
"""Audit the manual evidence inbox before tracker entry."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "manual_evidence_inbox_audit_20260810"
INBOX_MANIFEST = REPORTS / "manual_evidence_inbox_scaffold_20260810" / "manual_evidence_inbox_manifest.csv"
POST_DISPATCH = REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_evidence_intake_validator_summary.json"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

SCAFFOLD_FILES = {"README_DO_NOT_EDIT_TRACKERS_HERE.md"}
SENSITIVE_NAME_MARKERS = ["label", "labels", "answer", "answers", "groundtruth", "ground_truth", "truth", "key"]


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(BENCH_ROOT)).replace("\\", "/")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 18.91 Manual evidence inbox audit update"
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

    inbox_rows = read_csv(INBOX_MANIFEST)
    post_dispatch = read_json(POST_DISPATCH)

    folder_rows: list[dict[str, object]] = []
    file_rows: list[dict[str, object]] = []
    sensitivity_rows: list[dict[str, object]] = []

    for inbox in inbox_rows:
        folder = BENCH_ROOT / inbox["inbox_folder"]
        files = [path for path in folder.rglob("*") if path.is_file()] if folder.exists() else []
        evidence_files = [path for path in files if path.name not in SCAFFOLD_FILES]
        folder_rows.append(
            {
                "dispatch_id": inbox["dispatch_id"],
                "linked_gate": inbox["linked_gate"],
                "inbox_folder": inbox["inbox_folder"],
                "folder_exists": folder.exists(),
                "total_files": len(files),
                "scaffold_files": len(files) - len(evidence_files),
                "candidate_evidence_files": len(evidence_files),
                "tracker_entry_allowed_now": "no",
                "reason": "No validated returned evidence has passed intake.",
            }
        )
        for path in evidence_files:
            lower_name = path.name.lower()
            markers = [marker for marker in SENSITIVE_NAME_MARKERS if marker in lower_name]
            file_rows.append(
                {
                    "dispatch_id": inbox["dispatch_id"],
                    "linked_gate": inbox["linked_gate"],
                    "file": rel(path),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                    "sensitive_name_marker": "; ".join(markers),
                    "safe_for_tracker_entry_now": "no",
                }
            )
            if markers:
                sensitivity_rows.append(
                    {
                        "dispatch_id": inbox["dispatch_id"],
                        "file": rel(path),
                        "marker": "; ".join(markers),
                        "risk": "Potential label/answer leakage; inspect before any analyst-visible use.",
                    }
                )

    qa_rows = [
        {
            "check": "six_inbox_folders_audited",
            "result": "PASS" if len(folder_rows) == 6 and all(row["folder_exists"] for row in folder_rows) else "FAIL",
            "detail": f"folder_rows={len(folder_rows)}",
        },
        {
            "check": "no_sensitive_return_files_present",
            "result": "PASS" if not sensitivity_rows else "FAIL",
            "detail": f"sensitive_rows={len(sensitivity_rows)}",
        },
        {
            "check": "empty_inbox_state_preserved",
            "result": "PASS" if sum(int(row["candidate_evidence_files"]) for row in folder_rows) == 0 else "FAIL",
            "detail": f"candidate_evidence_files={sum(int(row['candidate_evidence_files']) for row in folder_rows)}",
        },
        {
            "check": "no_validator_pass_claim",
            "result": "PASS" if post_dispatch.get("evidence_rows_passed") == 0 else "FAIL",
            "detail": f"evidence_rows_passed={post_dispatch.get('evidence_rows_passed')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "manual_evidence_inbox_folder_audit.csv",
        folder_rows,
        ["dispatch_id", "linked_gate", "inbox_folder", "folder_exists", "total_files", "scaffold_files", "candidate_evidence_files", "tracker_entry_allowed_now", "reason"],
    )
    write_csv(
        OUT_DIR / "manual_evidence_inbox_file_checksums.csv",
        file_rows,
        ["dispatch_id", "linked_gate", "file", "size_bytes", "sha256", "sensitive_name_marker", "safe_for_tracker_entry_now"],
    )
    write_csv(OUT_DIR / "manual_evidence_inbox_sensitive_name_scan.csv", sensitivity_rows, ["dispatch_id", "file", "marker", "risk"])
    write_csv(OUT_DIR / "manual_evidence_inbox_audit_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Manual evidence inbox audit report 2026-08-10",
        "",
        "Status: `manual_evidence_inbox_audit_ready_empty`",
        "",
        f"1. Inbox folders audited: {len(folder_rows)}",
        f"2. Candidate evidence files: {len(file_rows)}",
        f"3. Sensitive-name rows: {len(sensitivity_rows)}",
        f"4. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: inbox folders exist and currently contain no returned evidence files beyond scaffold README files.",
        "",
    ]
    write_text(OUT_DIR / "MANUAL_EVIDENCE_INBOX_AUDIT_README.md", "\n".join(report))
    write_text(OUT_DIR / "manual_evidence_inbox_audit_report.md", "\n".join(report))

    summary = {
        "package": "manual_evidence_inbox_audit_20260810",
        "inbox_folders_audited": len(folder_rows),
        "candidate_evidence_files": len(file_rows),
        "sensitive_name_rows": len(sensitivity_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "tracker_entry_allowed_now": False,
        "manual_evidence_written": False,
        "evidence_rows_passed": post_dispatch.get("evidence_rows_passed"),
        "submission_ready": False,
        "status": "manual_evidence_inbox_audit_ready_empty",
    }

    section = f"""### 18.91 Manual evidence inbox audit update

Added a manual evidence inbox audit that checks inbox folders, candidate returned files, SHA256 checksums and label/answer filename leakage before tracker entry.

New directory: `{OUT_DIR}`

New files:
1. `manual_evidence_inbox_folder_audit.csv`
2. `manual_evidence_inbox_file_checksums.csv`
3. `manual_evidence_inbox_sensitive_name_scan.csv`
4. `manual_evidence_inbox_audit_qa.csv`
5. `MANUAL_EVIDENCE_INBOX_AUDIT_README.md`
6. `manual_evidence_inbox_audit_report.md`
7. `manual_evidence_inbox_audit_summary.json`

Current result:
1. inbox_folders_audited = {summary['inbox_folders_audited']}
2. candidate_evidence_files = {summary['candidate_evidence_files']}
3. sensitive_name_rows = {summary['sensitive_name_rows']}
4. qa_pass = {str(qa_pass).lower()}
5. tracker_entry_allowed_now = false
6. manual_evidence_written = false
7. submission_ready = false

Boundary:
1. This step does not write tracker evidence.
2. This step does not validate external labels.
3. This step does not close gates or authorize upload."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "manual_evidence_inbox_audit_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Manual evidence inbox audit QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
