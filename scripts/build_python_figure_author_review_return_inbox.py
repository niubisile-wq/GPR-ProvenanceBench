#!/usr/bin/env python3
"""Build and audit an inbox for returned Python figure author-review files."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "python_figure_author_review_return_inbox_20260810"
RETURN_DIR = OUT_DIR / "returned_author_review_files"
DESKTOP_PLAN = Path.home() / "Desktop" / "8\u670810\u65e5cns.md"

REVIEW_PACKET_SUMMARY = REPORTS / "python_figure_author_review_packet_20260810" / "python_figure_author_review_packet_summary.json"
INTAKE_SUMMARY = REPORTS / "python_figure_author_review_intake_validator_20260810" / "python_figure_author_review_intake_summary.json"
REVIEW_FORM = REPORTS / "python_figure_author_review_packet_20260810" / "python_figure_author_review_form.csv"


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.01 Python figure author review return inbox update"
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
    RETURN_DIR.mkdir(parents=True, exist_ok=True)

    packet_summary = read_json(REVIEW_PACKET_SUMMARY)
    intake_summary = read_json(INTAKE_SUMMARY)
    review_rows = read_csv(REVIEW_FORM)

    returned_files = [path for path in RETURN_DIR.iterdir() if path.is_file() and not path.name.startswith("README")]
    file_rows = []
    for path in returned_files:
        file_rows.append(
            {
                "file_name": path.name,
                "relative_path": str(path.relative_to(BENCH_ROOT)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "candidate_type": "author_review_return",
            }
        )

    inbox_rows = [
        {
            "inbox_id": "FIG-RETURN-001",
            "linked_dispatch": "MD-002_main_figure_rendering",
            "folder": str(RETURN_DIR.relative_to(BENCH_ROOT)).replace("\\", "/"),
            "expected_return_file": "filled python_figure_author_review_form.csv or equivalent author-marked review sheet",
            "allowed_next_validator": "py scripts\\build_python_figure_author_review_intake_validator.py",
            "writeback_allowed_now": "no",
        }
    ]

    stop_rows = [
        {"rule_id": "FIG-RETURN-STOP-001", "rule": "Do not edit the canonical review form from files placed in this inbox without explicit manual writeback."},
        {"rule_id": "FIG-RETURN-STOP-002", "rule": "Do not treat a returned file as approval until the intake validator passes allowed values."},
        {"rule_id": "FIG-RETURN-STOP-003", "rule": "Do not generate final candidates if any approval row is blank, revision or rejected."},
        {"rule_id": "FIG-RETURN-STOP-004", "rule": "Do not close final figure gate from inbox file presence alone."},
        {"rule_id": "FIG-RETURN-STOP-005", "rule": "Do not use Figure 6 approval as completed blind external validation."},
    ]

    readme = """# Python figure author-review return inbox

Place returned author-review files here only after the author has reviewed the figure packet.

Expected file:
1. Filled `python_figure_author_review_form.csv`, or
2. An equivalent author-marked sheet that can be manually transcribed into the canonical review form.

Do not edit tracker files inside this inbox. After manual transcription, rerun:

```powershell
py scripts\\build_python_figure_author_review_intake_validator.py
```
"""
    write_text(RETURN_DIR / "README_DO_NOT_EDIT_TRACKERS_HERE.md", readme)

    qa_rows = [
        {
            "check": "packet_ready_imported",
            "result": "PASS" if packet_summary.get("figures_included") == 6 and packet_summary.get("qa_pass") is True else "FAIL",
            "detail": f"figures_included={packet_summary.get('figures_included')}; packet_qa={packet_summary.get('qa_pass')}",
        },
        {
            "check": "intake_waiting_approvals",
            "result": "PASS" if intake_summary.get("blank_rows") == 6 and intake_summary.get("approved_rows") == 0 else "FAIL",
            "detail": f"blank_rows={intake_summary.get('blank_rows')}; approved_rows={intake_summary.get('approved_rows')}",
        },
        {
            "check": "canonical_review_form_blank",
            "result": "PASS" if len(review_rows) == 6 and all(row["author_approval_status"] == "blank" for row in review_rows) else "FAIL",
            "detail": f"review_rows={len(review_rows)}",
        },
        {
            "check": "return_inbox_empty",
            "result": "PASS" if len(file_rows) == 0 else "FAIL",
            "detail": f"candidate_return_files={len(file_rows)}",
        },
        {
            "check": "final_gate_not_closed",
            "result": "PASS" if intake_summary.get("final_candidate_generation_allowed") is False else "FAIL",
            "detail": f"final_candidate_generation_allowed={intake_summary.get('final_candidate_generation_allowed')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "python_figure_author_review_return_inbox_manifest.csv", inbox_rows, ["inbox_id", "linked_dispatch", "folder", "expected_return_file", "allowed_next_validator", "writeback_allowed_now"])
    write_csv(OUT_DIR / "python_figure_author_review_return_file_audit.csv", file_rows, ["file_name", "relative_path", "bytes", "sha256", "candidate_type"])
    write_csv(OUT_DIR / "python_figure_author_review_return_stop_rules.csv", stop_rows, ["rule_id", "rule"])
    write_csv(OUT_DIR / "python_figure_author_review_return_inbox_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Python figure author-review return inbox report 2026-08-10",
        "",
        "Status: `python_figure_author_review_return_inbox_ready_empty`",
        "",
        f"1. Inbox folders: {len(inbox_rows)}",
        f"2. Candidate returned files: {len(file_rows)}",
        f"3. Stop rules: {len(stop_rows)}",
        f"4. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: the return inbox is ready, but no author-review return file is present and final figure generation remains blocked.",
        "",
    ]
    write_text(OUT_DIR / "PYTHON_FIGURE_AUTHOR_REVIEW_RETURN_INBOX_README.md", "\n".join(report))
    write_text(OUT_DIR / "python_figure_author_review_return_inbox_report.md", "\n".join(report))

    summary = {
        "package": "python_figure_author_review_return_inbox_20260810",
        "inbox_rows": len(inbox_rows),
        "candidate_return_files": len(file_rows),
        "stop_rules": len(stop_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "author_return_file_present": len(file_rows) > 0,
        "writeback_allowed_now": False,
        "approved_rows": intake_summary.get("approved_rows"),
        "blank_rows": intake_summary.get("blank_rows"),
        "final_candidate_generation_allowed": False,
        "final_figures_ready": False,
        "submission_ready": False,
        "status": "python_figure_author_review_return_inbox_ready_empty",
    }

    section = f"""### 19.01 Python figure author review return inbox update

Added a dedicated return inbox and audit layer for filled figure author-review forms.

New directory: `{OUT_DIR}`

New files:
1. `returned_author_review_files/README_DO_NOT_EDIT_TRACKERS_HERE.md`
2. `python_figure_author_review_return_inbox_manifest.csv`
3. `python_figure_author_review_return_file_audit.csv`
4. `python_figure_author_review_return_stop_rules.csv`
5. `python_figure_author_review_return_inbox_qa.csv`
6. `PYTHON_FIGURE_AUTHOR_REVIEW_RETURN_INBOX_README.md`
7. `python_figure_author_review_return_inbox_report.md`
8. `python_figure_author_review_return_inbox_summary.json`

Current result:
1. inbox_rows = {summary['inbox_rows']}
2. candidate_return_files = {summary['candidate_return_files']}
3. author_return_file_present = false
4. writeback_allowed_now = false
5. qa_pass = {str(qa_pass).lower()}
6. final_candidate_generation_allowed = false
7. final_figures_ready = false

Boundary:
1. This inbox receives returned author-review files only.
2. It does not write approvals into the canonical review form.
3. It does not generate final figures or close the figure gate."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "python_figure_author_review_return_inbox_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Python figure author-review return inbox QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
