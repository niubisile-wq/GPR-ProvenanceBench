#!/usr/bin/env python3
"""Assemble a local figure final-candidate review packet without unlocking submission."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "figure_final_candidate_review_packet_20260811"
PACKAGE_DIR = OUT_DIR / "candidate_files"
DESKTOP_REPORT = Path.home() / "Desktop" / "NatComms_20260811_figure_final_candidate_review_packet.md"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"

PREVIEW_MANIFEST = BENCH_ROOT / "reports" / "python_figure_preview_package_20260810" / "python_figure_preview_manifest.csv"


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


def copy_rel(rel_path: str, target_dir: Path) -> str:
    source = BENCH_ROOT / rel_path
    target = target_dir / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.exists():
        shutil.copy2(source, target)
        return str(target.relative_to(BENCH_ROOT))
    return ""


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 20.04 Figure final-candidate review packet update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/figure_final_candidate_review_packet_20260811/` and Desktop report `NatComms_20260811_figure_final_candidate_review_packet.md`.
- Current final-candidate review packet state: `figures_packaged={summary["figures_packaged"]}`, `preview_exports_packaged={summary["preview_exports_packaged"]}`, `review_packet_ready={str(summary["review_packet_ready"]).lower()}`.
- Final figure state remains guarded: `final_figures_ready=false`, `source_data_panel_map_locked=false`, `figure_portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: this is a review packet only; it does not record author approval, create final exports, lock Source Data or permit portal upload.
"""
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        text = text[:start].rstrip() if next_start == -1 else text[:start].rstrip() + "\n\n" + text[next_start:].lstrip("\n")
    DESKTOP_PLAN.write_text(text.rstrip() + block + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)

    preview_rows = read_csv(PREVIEW_MANIFEST)
    caption_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "python_figure_final_export_qa_template_20260810"
        / "python_figure_caption_lock_queue.csv"
    )
    source_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "python_figure_final_export_qa_template_20260810"
        / "python_figure_source_data_panel_map_lock_queue.csv"
    )
    export_qa_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "python_figure_final_export_qa_template_20260810"
        / "python_figure_final_export_qa_checklist.csv"
    )
    stop_rule_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "python_figure_final_export_qa_template_20260810"
        / "python_figure_final_export_stop_rules.csv"
    )

    bridge = read_json(
        BENCH_ROOT
        / "reports"
        / "figure_preview_completion_bridge_20260811"
        / "figure_preview_completion_bridge_summary.json"
    )
    final_template = read_json(
        BENCH_ROOT
        / "reports"
        / "python_figure_final_export_qa_template_20260810"
        / "python_figure_final_export_qa_template_summary.json"
    )

    packaged_rows: list[dict[str, object]] = []
    for row in preview_rows:
        figure_dir = PACKAGE_DIR / row["figure_id"].lower().replace(" ", "_")
        copied = []
        for key in ["png", "svg", "pdf", "tiff"]:
            copied_path = copy_rel(row[key], figure_dir)
            if copied_path:
                copied.append(copied_path)
        packaged_rows.append(
            {
                "figure_id": row["figure_id"],
                "core_conclusion": row["core_conclusion"],
                "archetype": row["archetype"],
                "copied_preview_exports": len(copied),
                "copied_files": "; ".join(copied),
                "candidate_review_status": "ready_for_final_candidate_review",
                "finalization_status": "blocked_pending_author_approval_final_export_qa_source_data_lock",
                "boundary": row["boundary"],
            }
        )

    copied_support_rows = [
        {
            "support_item": "caption lock queue",
            "copied_file": copy_rel(
                "reports/python_figure_final_export_qa_template_20260810/python_figure_caption_lock_queue.csv",
                PACKAGE_DIR / "review_controls",
            ),
        },
        {
            "support_item": "source data panel-map lock queue",
            "copied_file": copy_rel(
                "reports/python_figure_final_export_qa_template_20260810/python_figure_source_data_panel_map_lock_queue.csv",
                PACKAGE_DIR / "review_controls",
            ),
        },
        {
            "support_item": "final export QA checklist",
            "copied_file": copy_rel(
                "reports/python_figure_final_export_qa_template_20260810/python_figure_final_export_qa_checklist.csv",
                PACKAGE_DIR / "review_controls",
            ),
        },
        {
            "support_item": "final export stop rules",
            "copied_file": copy_rel(
                "reports/python_figure_final_export_qa_template_20260810/python_figure_final_export_stop_rules.csv",
                PACKAGE_DIR / "review_controls",
            ),
        },
    ]

    gate_rows = [
        {
            "gate": "preview files available",
            "current_state": f"preview_complete_figures={bridge.get('preview_complete_figures')}; preview_export_files={bridge.get('preview_export_files')}",
            "passes_for_review_packet": "yes",
            "passes_for_final_submission": "no",
        },
        {
            "gate": "preview visual QA",
            "current_state": f"visual_qa_pass={bridge.get('visual_qa_pass')}",
            "passes_for_review_packet": "yes",
            "passes_for_final_submission": "no",
        },
        {
            "gate": "caption lock",
            "current_state": f"caption_lock_rows={len(caption_rows)}; captions_locked_final={final_template.get('captions_locked_final')}",
            "passes_for_review_packet": "yes",
            "passes_for_final_submission": "no",
        },
        {
            "gate": "source data panel map",
            "current_state": f"source_data_panel_map_rows={len(source_rows)}; source_data_panel_map_locked={final_template.get('source_data_panel_map_locked')}",
            "passes_for_review_packet": "yes",
            "passes_for_final_submission": "no",
        },
        {
            "gate": "final export QA",
            "current_state": f"export_qa_rows={len(export_qa_rows)}; final_export_qa_allowed_rows={final_template.get('final_export_qa_allowed_rows')}",
            "passes_for_review_packet": "yes",
            "passes_for_final_submission": "no",
        },
        {
            "gate": "stop rules",
            "current_state": f"stop_rules={len(stop_rule_rows)}",
            "passes_for_review_packet": "yes",
            "passes_for_final_submission": "yes_as_guardrail_only",
        },
    ]

    qa_rows = [
        {
            "check": "six figures packaged",
            "result": "PASS" if len(packaged_rows) == 6 else "FAIL",
            "detail": f"figures_packaged={len(packaged_rows)}",
        },
        {
            "check": "all preview exports copied",
            "result": "PASS" if sum(int(row["copied_preview_exports"]) for row in packaged_rows) == 24 else "FAIL",
            "detail": f"preview_exports_packaged={sum(int(row['copied_preview_exports']) for row in packaged_rows)}",
        },
        {
            "check": "support controls copied",
            "result": "PASS" if all(row["copied_file"] for row in copied_support_rows) else "FAIL",
            "detail": f"support_controls={len(copied_support_rows)}",
        },
        {
            "check": "final submission remains blocked",
            "result": "PASS" if final_template.get("final_figures_ready") is False else "FAIL",
            "detail": f"final_figures_ready={final_template.get('final_figures_ready')}",
        },
    ]

    preview_exports_packaged = sum(int(row["copied_preview_exports"]) for row in packaged_rows)
    summary = {
        "package": "figure_final_candidate_review_packet_20260811",
        "figures_packaged": len(packaged_rows),
        "preview_exports_packaged": preview_exports_packaged,
        "support_controls_packaged": len(copied_support_rows),
        "gate_rows": len(gate_rows),
        "review_packet_ready": len(packaged_rows) == 6 and preview_exports_packaged == 24,
        "caption_lock_rows": len(caption_rows),
        "source_data_panel_map_rows": len(source_rows),
        "export_qa_rows": len(export_qa_rows),
        "stop_rules": len(stop_rule_rows),
        "captions_locked_final": False,
        "source_data_panel_map_locked": False,
        "final_figures_ready": False,
        "figure_portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "desktop_report": str(DESKTOP_REPORT),
        "status": "figure_final_candidate_review_packet_ready_final_blocked",
    }

    report = f"""# Figure Final-candidate Review Packet

This packet consolidates the six Python preview figures and the final-candidate
review controls needed before final export QA can be considered.

Current state:

1. `figures_packaged={summary["figures_packaged"]}`.
2. `preview_exports_packaged={summary["preview_exports_packaged"]}`.
3. `support_controls_packaged={summary["support_controls_packaged"]}`.
4. `review_packet_ready={str(summary["review_packet_ready"]).lower()}`.
5. `captions_locked_final=false`.
6. `source_data_panel_map_locked=false`.
7. `final_figures_ready=false`.
8. `figure_portal_upload_allowed=false`.
9. `submission_ready=false`.

Use: review final-candidate layout, caption boundary language, source-data
crosswalk requirements and stop rules.

Boundary: this is a local review packet only. It does not record author
approval, generate final submission figures, lock Source Data, clear portal
upload or submit the manuscript.
"""

    write_csv(
        OUT_DIR / "figure_final_candidate_review_manifest.csv",
        [
            "figure_id",
            "core_conclusion",
            "archetype",
            "copied_preview_exports",
            "copied_files",
            "candidate_review_status",
            "finalization_status",
            "boundary",
        ],
        packaged_rows,
    )
    write_csv(OUT_DIR / "figure_final_candidate_support_controls.csv", ["support_item", "copied_file"], copied_support_rows)
    write_csv(OUT_DIR / "figure_final_candidate_gate_matrix.csv", ["gate", "current_state", "passes_for_review_packet", "passes_for_final_submission"], gate_rows)
    write_csv(OUT_DIR / "figure_final_candidate_review_packet_qa.csv", ["check", "result", "detail"], qa_rows)
    write_text(OUT_DIR / "FIGURE_FINAL_CANDIDATE_REVIEW_PACKET_README.md", report)
    write_text(OUT_DIR / "figure_final_candidate_review_packet_report.md", report)
    write_text(DESKTOP_REPORT, report)
    summary["desktop_plan_updated"] = update_desktop_plan(summary)
    write_text(OUT_DIR / "figure_final_candidate_review_packet_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
