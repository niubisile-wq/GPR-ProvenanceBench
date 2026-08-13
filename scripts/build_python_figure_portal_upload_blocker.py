#!/usr/bin/env python3
"""Build a portal-upload blocker overlay for Python figure artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "python_figure_portal_upload_blocker_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8\u670810\u65e5cns.md"

PORTAL_INVENTORY = REPORTS / "portal_submission_file_preflight_20260810" / "portal_submission_file_inventory.csv"
PORTAL_SUMMARY = REPORTS / "portal_submission_file_preflight_20260810" / "portal_submission_file_preflight_summary.json"
PREVIEW_SUMMARY = REPORTS / "python_figure_preview_package_20260810" / "python_figure_preview_summary.json"
VISUAL_QA_SUMMARY = REPORTS / "python_figure_preview_visual_qa_20260810" / "python_figure_preview_visual_qa_summary.json"
AUTHOR_PACKET_SUMMARY = REPORTS / "python_figure_author_review_packet_20260810" / "python_figure_author_review_packet_summary.json"
FINAL_PREFLIGHT_SUMMARY = REPORTS / "python_figure_final_candidate_preflight_20260810" / "python_figure_final_candidate_preflight_summary.json"
FINAL_EXPORT_SUMMARY = REPORTS / "python_figure_final_export_qa_template_20260810" / "python_figure_final_export_qa_template_summary.json"


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
    marker = "### 19.05 Python figure portal upload blocker update"
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

    portal_rows = read_csv(PORTAL_INVENTORY)
    portal_summary = read_json(PORTAL_SUMMARY)
    preview = read_json(PREVIEW_SUMMARY)
    visual = read_json(VISUAL_QA_SUMMARY)
    author_packet = read_json(AUTHOR_PACKET_SUMMARY)
    final_preflight = read_json(FINAL_PREFLIGHT_SUMMARY)
    final_export = read_json(FINAL_EXPORT_SUMMARY)

    affected = [row for row in portal_rows if row["portal_item"] in {"display_figures", "source_data_files", "main_manuscript_docx_or_pdf", "supplementary_information"}]
    overlay_rows = []
    for row in affected:
        if row["portal_item"] == "display_figures":
            current_figure_state = "preview_rendered_author_review_ready_not_final"
            blocker = "Final figure candidates, final export QA, final caption lock and final Source Data panel map are absent."
        elif row["portal_item"] == "source_data_files":
            current_figure_state = "source_data_manifest_exists_panel_map_not_final_locked"
            blocker = "Panel-level Source Data mapping is not locked to final rendered figures."
        elif row["portal_item"] == "main_manuscript_docx_or_pdf":
            current_figure_state = "manuscript_depends_on_final_figure_set"
            blocker = "Main manuscript cannot be final until final figure set, captions and figure references are locked."
        else:
            current_figure_state = "supplementary_split_depends_on_final_display_set"
            blocker = "Display-vs-SI figure split remains unresolved until final figure set is approved."
        overlay_rows.append(
            {
                "portal_item": row["portal_item"],
                "portal_current_state": row["current_state"],
                "figure_overlay_state": current_figure_state,
                "preview_figures_rendered": preview.get("rendered_figures_preview"),
                "author_review_ready_rows": visual.get("author_review_preview_ready_rows"),
                "author_approvals_recorded": author_packet.get("author_approvals_recorded"),
                "final_candidate_generation_allowed": final_preflight.get("final_candidate_generation_allowed"),
                "final_export_qa_allowed_rows": final_export.get("final_export_qa_allowed_rows"),
                "source_data_panel_map_locked": final_export.get("source_data_panel_map_locked"),
                "captions_locked_final": final_export.get("captions_locked_final"),
                "upload_allowed_now": "no",
                "figure_specific_blocker": blocker,
            }
        )

    no_upload_rows = [
        {"rule_id": "FIG-PORTAL-STOP-001", "rule": "Do not upload preview PNG/PDF/SVG files as final display figures."},
        {"rule_id": "FIG-PORTAL-STOP-002", "rule": "Do not upload final candidates without final export QA and full M0-M2 pass."},
        {"rule_id": "FIG-PORTAL-STOP-003", "rule": "Do not upload Source Data until panel maps match final rendered figures."},
        {"rule_id": "FIG-PORTAL-STOP-004", "rule": "Do not upload the main manuscript until figure captions and figure callouts are final."},
        {"rule_id": "FIG-PORTAL-STOP-005", "rule": "Do not let Figure 6 upload language imply completed blind external validation."},
    ]

    qa_rows = [
        {
            "check": "affected_portal_items_indexed",
            "result": "PASS" if len(overlay_rows) == 4 else "FAIL",
            "detail": f"overlay_rows={len(overlay_rows)}",
        },
        {
            "check": "preview_state_imported",
            "result": "PASS" if preview.get("rendered_figures_preview") == 6 and visual.get("author_review_preview_ready_rows") == 6 else "FAIL",
            "detail": f"preview={preview.get('rendered_figures_preview')}; review_ready={visual.get('author_review_preview_ready_rows')}",
        },
        {
            "check": "final_upload_blocked",
            "result": "PASS" if all(row["upload_allowed_now"] == "no" for row in overlay_rows) and final_export.get("final_figures_ready") is False else "FAIL",
            "detail": f"final_figures_ready={final_export.get('final_figures_ready')}",
        },
        {
            "check": "portal_upload_still_blocked",
            "result": "PASS" if portal_summary.get("portal_upload_ready") is False and portal_summary.get("submission_ready") is False else "FAIL",
            "detail": f"portal_upload_ready={portal_summary.get('portal_upload_ready')}; submission_ready={portal_summary.get('submission_ready')}",
        },
        {
            "check": "source_data_and_caption_locks_absent",
            "result": "PASS" if final_export.get("source_data_panel_map_locked") is False and final_export.get("captions_locked_final") is False else "FAIL",
            "detail": f"source_data_panel_map_locked={final_export.get('source_data_panel_map_locked')}; captions_locked_final={final_export.get('captions_locked_final')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "python_figure_portal_upload_blocker_overlay.csv",
        overlay_rows,
        ["portal_item", "portal_current_state", "figure_overlay_state", "preview_figures_rendered", "author_review_ready_rows", "author_approvals_recorded", "final_candidate_generation_allowed", "final_export_qa_allowed_rows", "source_data_panel_map_locked", "captions_locked_final", "upload_allowed_now", "figure_specific_blocker"],
    )
    write_csv(OUT_DIR / "python_figure_portal_no_upload_rules.csv", no_upload_rows, ["rule_id", "rule"])
    write_csv(OUT_DIR / "python_figure_portal_upload_blocker_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Python figure portal upload blocker report 2026-08-10",
        "",
        "Status: `python_figure_portal_upload_blocker_ready_upload_blocked`",
        "",
        f"1. Affected portal items: {len(overlay_rows)}",
        f"2. No-upload rules: {len(no_upload_rows)}",
        f"3. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: figure previews are ready for author review, but no figure-related portal item is upload-ready.",
        "",
    ]
    write_text(OUT_DIR / "PYTHON_FIGURE_PORTAL_UPLOAD_BLOCKER_README.md", "\n".join(report))
    write_text(OUT_DIR / "python_figure_portal_upload_blocker_report.md", "\n".join(report))

    summary = {
        "package": "python_figure_portal_upload_blocker_20260810",
        "affected_portal_items": len(overlay_rows),
        "no_upload_rules": len(no_upload_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "preview_figures_rendered": preview.get("rendered_figures_preview"),
        "author_review_ready_rows": visual.get("author_review_preview_ready_rows"),
        "author_approvals_recorded": author_packet.get("author_approvals_recorded"),
        "final_export_qa_allowed_rows": final_export.get("final_export_qa_allowed_rows"),
        "figure_portal_upload_allowed_rows": 0,
        "portal_upload_ready": False,
        "submission_ready": False,
        "status": "python_figure_portal_upload_blocker_ready_upload_blocked",
    }

    section = f"""### 19.05 Python figure portal upload blocker update

Added a figure-specific portal upload blocker overlay for display figures, Source Data, main manuscript and Supplementary Information.

New directory: `{OUT_DIR}`

New files:
1. `python_figure_portal_upload_blocker_overlay.csv`
2. `python_figure_portal_no_upload_rules.csv`
3. `python_figure_portal_upload_blocker_qa.csv`
4. `PYTHON_FIGURE_PORTAL_UPLOAD_BLOCKER_README.md`
5. `python_figure_portal_upload_blocker_report.md`
6. `python_figure_portal_upload_blocker_summary.json`

Current result:
1. affected_portal_items = {summary['affected_portal_items']}
2. preview_figures_rendered = {summary['preview_figures_rendered']}
3. author_review_ready_rows = {summary['author_review_ready_rows']}
4. author_approvals_recorded = {summary['author_approvals_recorded']}
5. figure_portal_upload_allowed_rows = 0
6. portal_upload_ready = false
7. submission_ready = false

Boundary:
1. This overlay prevents preview or candidate files from being treated as portal-ready final figures.
2. It does not upload files or close portal gates.
3. It does not claim final figures are ready."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "python_figure_portal_upload_blocker_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Python figure portal upload blocker QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
