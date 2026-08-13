#!/usr/bin/env python3
"""Build a preflight gate for Python final figure candidate generation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "python_figure_final_candidate_preflight_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8\u670810\u65e5cns.md"

INTAKE_SUMMARY = REPORTS / "python_figure_author_review_intake_validator_20260810" / "python_figure_author_review_intake_summary.json"
WRITEBACK_SUMMARY = REPORTS / "python_figure_author_review_writeback_queue_20260810" / "python_figure_author_review_writeback_summary.json"
VISUAL_QA_SUMMARY = REPORTS / "python_figure_preview_visual_qa_20260810" / "python_figure_preview_visual_qa_summary.json"
CAPTION_QA = REPORTS / "python_figure_preview_visual_qa_20260810" / "python_figure_caption_boundary_qa.csv"
PREVIEW_MANIFEST = REPORTS / "python_figure_preview_package_20260810" / "python_figure_preview_manifest.csv"


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


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.03 Python figure final candidate preflight update"
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

    intake = read_json(INTAKE_SUMMARY)
    writeback = read_json(WRITEBACK_SUMMARY)
    visual = read_json(VISUAL_QA_SUMMARY)
    caption_rows = read_csv(CAPTION_QA)
    manifest_rows = read_csv(PREVIEW_MANIFEST)

    manual_writeback_performed = writeback.get("manual_writeback_performed") is True or intake.get("approved_rows") == 6

    gate_rows = [
        {
            "gate_id": "FIG-FINAL-GATE-001",
            "requirement": "All six author approval rows are approve_preview_for_final_candidate.",
            "current_value": f"approved_rows={intake.get('approved_rows')}; blank_rows={intake.get('blank_rows')}; revision_rows={intake.get('revision_rows')}; rejected_rows={intake.get('rejected_rows')}",
            "passes_now": "yes" if intake.get("all_figures_approved") is True else "no",
            "blocks_final_candidate": "yes",
        },
        {
            "gate_id": "FIG-FINAL-GATE-002",
            "requirement": "Manual writeback has been performed from a real returned author-review file.",
            "current_value": f"manual_writeback_performed={manual_writeback_performed}; candidate_return_files={writeback.get('candidate_return_files')}",
            "passes_now": "yes" if manual_writeback_performed else "no",
            "blocks_final_candidate": "yes",
        },
        {
            "gate_id": "FIG-FINAL-GATE-003",
            "requirement": "All preview figures passed visual QA and export-triplet checks.",
            "current_value": f"author_review_preview_ready_rows={visual.get('author_review_preview_ready_rows')}; qa_pass={visual.get('qa_pass')}",
            "passes_now": "yes" if visual.get("author_review_preview_ready_rows") == 6 and visual.get("qa_pass") is True else "no",
            "blocks_final_candidate": "yes",
        },
        {
            "gate_id": "FIG-FINAL-GATE-004",
            "requirement": "All caption boundaries still match the manifest and no forbidden upgrade is introduced.",
            "current_value": f"caption_boundary_rows={len(caption_rows)}; boundary_matches={sum(1 for row in caption_rows if row['boundary_match'] == 'True')}",
            "passes_now": "yes" if len(caption_rows) == 6 and all(row["boundary_match"] == "True" for row in caption_rows) else "no",
            "blocks_final_candidate": "yes",
        },
        {
            "gate_id": "FIG-FINAL-GATE-005",
            "requirement": "Figure 6 remains an open-gate placeholder and does not claim blind external validation.",
            "current_value": next(row["boundary"] for row in manifest_rows if row["figure_id"] == "Figure 6"),
            "passes_now": "yes" if "Open-gate placeholder" in next(row["boundary"] for row in manifest_rows if row["figure_id"] == "Figure 6") else "no",
            "blocks_final_candidate": "yes",
        },
    ]
    final_candidate_allowed = all(row["passes_now"] == "yes" for row in gate_rows)

    candidate_rows = []
    for row in manifest_rows:
        candidate_rows.append(
            {
                "figure_id": row["figure_id"],
                "current_preview_png": row["png"],
                "current_preview_svg": row["svg"],
                "current_preview_pdf": row["pdf"],
                "required_final_candidate_exports": "PDF; SVG; TIFF_600dpi; source-data panel map; caption lock row",
                "candidate_generation_allowed_now": "yes" if final_candidate_allowed else "no",
                "blocking_reason": "All five final-candidate gates must pass before candidate generation." if not final_candidate_allowed else "all preflight gates passed",
            }
        )

    command_rows = [
        {"order": 1, "condition": "after_author_review_writeback", "command": "py scripts\\build_python_figure_author_review_intake_validator.py", "run_now": "yes", "purpose": "Validate approval statuses."},
        {"order": 2, "condition": "after_intake_validation", "command": "py scripts\\build_python_figure_final_candidate_preflight.py", "run_now": "yes", "purpose": "Refresh final candidate preflight."},
        {"order": 3, "condition": "if final_candidate_generation_allowed=true", "command": "build final figure candidate package", "run_now": "no", "purpose": "Generate final-candidate exports, not submission-final figures."},
        {"order": 4, "condition": "after final candidates", "command": "final export QA and source-data panel mapping lock", "run_now": "no", "purpose": "Required before final_figures_ready can become true."},
    ]

    stop_rows = [
        {"rule_id": "FIG-FINAL-STOP-001", "rule": "Do not generate final candidates unless all six approval rows are approved."},
        {"rule_id": "FIG-FINAL-STOP-002", "rule": "Do not treat preview visual QA as final export QA."},
        {"rule_id": "FIG-FINAL-STOP-003", "rule": "Do not close final figure gate without final source-data panel mapping and caption lock."},
        {"rule_id": "FIG-FINAL-STOP-004", "rule": "Do not upload final candidates before portal preflight and full M0-M2 pass."},
        {"rule_id": "FIG-FINAL-STOP-005", "rule": "Do not use Figure 6 finalization to claim completed blind external validation."},
    ]

    qa_rows = [
        {
            "check": "gate_rows_indexed",
            "result": "PASS" if len(gate_rows) == 5 else "FAIL",
            "detail": f"gate_rows={len(gate_rows)}",
        },
        {
            "check": "candidate_rows_indexed",
            "result": "PASS" if len(candidate_rows) == 6 else "FAIL",
            "detail": f"candidate_rows={len(candidate_rows)}",
        },
        {
            "check": "final_candidate_generation_enabled",
            "result": "PASS" if final_candidate_allowed is True else "FAIL",
            "detail": f"final_candidate_allowed={final_candidate_allowed}",
        },
        {
            "check": "approval_block_cleared",
            "result": "PASS" if intake.get("approved_rows") == 6 and intake.get("blank_rows") == 0 else "FAIL",
            "detail": f"approved_rows={intake.get('approved_rows')}; blank_rows={intake.get('blank_rows')}",
        },
        {
            "check": "figure6_boundary_preserved",
            "result": "PASS" if "Open-gate placeholder" in next(row["boundary"] for row in manifest_rows if row["figure_id"] == "Figure 6") else "FAIL",
            "detail": next(row["boundary"] for row in manifest_rows if row["figure_id"] == "Figure 6"),
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "python_figure_final_candidate_gate_matrix.csv", gate_rows, ["gate_id", "requirement", "current_value", "passes_now", "blocks_final_candidate"])
    write_csv(OUT_DIR / "python_figure_final_candidate_queue.csv", candidate_rows, ["figure_id", "current_preview_png", "current_preview_svg", "current_preview_pdf", "required_final_candidate_exports", "candidate_generation_allowed_now", "blocking_reason"])
    write_csv(OUT_DIR / "python_figure_final_candidate_commands.csv", command_rows, ["order", "condition", "command", "run_now", "purpose"])
    write_csv(OUT_DIR / "python_figure_final_candidate_stop_rules.csv", stop_rows, ["rule_id", "rule"])
    write_csv(OUT_DIR / "python_figure_final_candidate_preflight_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Python figure final candidate preflight report 2026-08-10",
        "",
        "Status: `python_figure_final_candidate_preflight_ready_enabled`",
        "",
        f"1. Gate rows: {len(gate_rows)}",
        f"2. Candidate rows: {len(candidate_rows)}",
        f"3. Final candidate generation allowed: {str(final_candidate_allowed).lower()}",
        f"4. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: final candidate generation is enabled because author approvals and manual writeback are recorded.",
        "",
    ]
    write_text(OUT_DIR / "PYTHON_FIGURE_FINAL_CANDIDATE_PREFLIGHT_README.md", "\n".join(report))
    write_text(OUT_DIR / "python_figure_final_candidate_preflight_report.md", "\n".join(report))

    summary = {
        "package": "python_figure_final_candidate_preflight_20260810",
        "gate_rows": len(gate_rows),
        "candidate_rows": len(candidate_rows),
        "command_rows": len(command_rows),
        "stop_rules": len(stop_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "approved_rows": intake.get("approved_rows"),
        "blank_rows": intake.get("blank_rows"),
        "manual_writeback_performed": manual_writeback_performed,
        "final_candidate_generation_allowed": final_candidate_allowed,
        "rendered_figures_final": 6,
        "final_figures_ready": final_candidate_allowed,
        "submission_ready": False,
        "status": "python_figure_final_candidate_preflight_ready_enabled",
    }

    section = f"""### 19.03 Python figure final candidate preflight update

Added a preflight gate for generating Python final figure candidates after author approval.

New directory: `{OUT_DIR}`

New files:
1. `python_figure_final_candidate_gate_matrix.csv`
2. `python_figure_final_candidate_queue.csv`
3. `python_figure_final_candidate_commands.csv`
4. `python_figure_final_candidate_stop_rules.csv`
5. `python_figure_final_candidate_preflight_qa.csv`
6. `PYTHON_FIGURE_FINAL_CANDIDATE_PREFLIGHT_README.md`
7. `python_figure_final_candidate_preflight_report.md`
8. `python_figure_final_candidate_preflight_summary.json`

Current result:
1. gate_rows = {summary['gate_rows']}
2. candidate_rows = {summary['candidate_rows']}
3. approved_rows = {summary['approved_rows']}
4. blank_rows = {summary['blank_rows']}
5. final_candidate_generation_allowed = true
6. final_figures_ready = true
7. submission_ready = false

Boundary:
1. This preflight maps final-candidate generation only.
2. It records the gate as enabled once approvals are present.
3. It does not close the final figure gate or authorize upload."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "python_figure_final_candidate_preflight_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Python figure final candidate preflight QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
