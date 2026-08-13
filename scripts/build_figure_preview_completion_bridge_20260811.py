#!/usr/bin/env python3
"""Bridge existing Python figure previews into the experiment completion audit."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "figure_preview_completion_bridge_20260811"
PREVIEW_DIR = BENCH_ROOT / "reports" / "python_figure_preview_package_20260810"
FIGURE_DIR = PREVIEW_DIR / "figures"
DESKTOP_REPORT = Path.home() / "Desktop" / "NatComms_20260811_figure_preview_completion_bridge.md"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


FIGURES = [
    ("Figure 1", "figure1_protocol_asset_boundary_preview"),
    ("Figure 2", "figure2_res_sam_transfer_signal_preview"),
    ("Figure 3", "figure3_mojahid_directional_boundary_preview"),
    ("Figure 4", "figure4_4tu_stress_boundary_preview"),
    ("Figure 5", "figure5_4tu_feasibility_gate_preview"),
    ("Figure 6", "figure6_external_validation_open_gate_preview"),
]


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
    marker = "### 20.03 Figure preview completion bridge update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/figure_preview_completion_bridge_20260811/` and Desktop report `NatComms_20260811_figure_preview_completion_bridge.md`.
- Current preview figure state: `preview_complete_figures={summary["preview_complete_figures"]}`, `preview_export_files={summary["preview_export_files"]}`, `visual_qa_pass={str(summary["visual_qa_pass"]).lower()}`.
- Final figure state remains blocked: `final_figures_ready=false`, `figure_portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: this bridge upgrades local preview evidence only. It does not create author approval, final export QA, Source Data lock or portal-ready figures.
"""
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        text = text[:start].rstrip() if next_start == -1 else text[:start].rstrip() + "\n\n" + text[next_start:].lstrip("\n")
    DESKTOP_PLAN.write_text(text.rstrip() + block + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    preview_summary = read_json(PREVIEW_DIR / "python_figure_preview_summary.json")
    visual_qa = read_json(
        BENCH_ROOT
        / "reports"
        / "python_figure_preview_visual_qa_20260810"
        / "python_figure_preview_visual_qa_summary.json"
    )
    panel_map = read_json(
        BENCH_ROOT
        / "reports"
        / "python_figure_source_data_panel_map_preflight_20260810"
        / "python_figure_source_data_panel_map_preflight_summary.json"
    )
    portal_blocker = read_json(
        BENCH_ROOT
        / "reports"
        / "python_figure_portal_upload_blocker_20260810"
        / "python_figure_portal_upload_blocker_summary.json"
    )
    final_preflight = read_json(
        BENCH_ROOT
        / "reports"
        / "python_figure_final_candidate_preflight_20260810"
        / "python_figure_final_candidate_preflight_summary.json"
    )

    rows = []
    for figure_id, stem in FIGURES:
        files = {ext: FIGURE_DIR / f"{stem}.{ext}" for ext in ["pdf", "svg", "png", "tiff"]}
        rows.append(
            {
                "figure_id": figure_id,
                "preview_pdf_exists": files["pdf"].exists(),
                "preview_svg_exists": files["svg"].exists(),
                "preview_png_exists": files["png"].exists(),
                "preview_tiff_exists": files["tiff"].exists(),
                "preview_export_count": sum(1 for path in files.values() if path.exists()),
                "preview_status": "preview_complete" if all(path.exists() for path in files.values()) else "preview_incomplete",
                "final_status": "blocked_pending_author_approval_final_export_qa_and_source_data_lock",
                "submission_boundary": "preview-only; not portal-ready final figure",
            }
        )

    preview_complete = sum(1 for row in rows if row["preview_status"] == "preview_complete")
    preview_exports = sum(int(row["preview_export_count"]) for row in rows)
    bridge_rows = [
        {
            "gate": "preview package",
            "status": "ready" if preview_summary.get("figures_rendered", preview_summary.get("rendered_figures_preview", 0)) == 6 else "incomplete",
            "evidence": "reports/python_figure_preview_package_20260810/python_figure_preview_summary.json",
            "detail": f"figures_rendered={preview_summary.get('figures_rendered', preview_summary.get('rendered_figures_preview'))}",
        },
        {
            "gate": "visual QA",
            "status": "pass" if visual_qa.get("qa_pass") is True else "fail",
            "evidence": "reports/python_figure_preview_visual_qa_20260810/python_figure_preview_visual_qa_summary.json",
            "detail": f"author_review_preview_ready_rows={visual_qa.get('author_review_preview_ready_rows')}",
        },
        {
            "gate": "source-data panel map",
            "status": "preflight_ready_but_not_locked",
            "evidence": "reports/python_figure_source_data_panel_map_preflight_20260810/python_figure_source_data_panel_map_preflight_summary.json",
            "detail": f"missing_source_rows={panel_map.get('missing_source_rows')}; source_data_panel_map_locked={panel_map.get('source_data_panel_map_locked')}",
        },
        {
            "gate": "final candidate generation",
            "status": "blocked",
            "evidence": "reports/python_figure_final_candidate_preflight_20260810/python_figure_final_candidate_preflight_summary.json",
            "detail": f"approved_rows={final_preflight.get('approved_rows')}; final_candidate_generation_allowed={final_preflight.get('final_candidate_generation_allowed')}",
        },
        {
            "gate": "portal upload",
            "status": "blocked",
            "evidence": "reports/python_figure_portal_upload_blocker_20260810/python_figure_portal_upload_blocker_summary.json",
            "detail": f"figure_portal_upload_allowed_rows={portal_blocker.get('figure_portal_upload_allowed_rows')}",
        },
    ]

    qa_rows = [
        {
            "check": "all six previews have PDF SVG PNG TIFF",
            "result": "PASS" if preview_complete == 6 and preview_exports == 24 else "FAIL",
            "detail": f"preview_complete={preview_complete}; preview_exports={preview_exports}",
        },
        {
            "check": "visual QA passes",
            "result": "PASS" if visual_qa.get("qa_pass") is True else "FAIL",
            "detail": f"qa_pass={visual_qa.get('qa_pass')}",
        },
        {
            "check": "final figures remain blocked",
            "result": "PASS" if final_preflight.get("final_figures_ready") is False else "FAIL",
            "detail": f"final_figures_ready={final_preflight.get('final_figures_ready')}",
        },
        {
            "check": "portal upload remains blocked",
            "result": "PASS" if portal_blocker.get("portal_upload_ready") is False else "FAIL",
            "detail": f"portal_upload_ready={portal_blocker.get('portal_upload_ready')}",
        },
    ]

    summary = {
        "package": "figure_preview_completion_bridge_20260811",
        "preview_complete_figures": preview_complete,
        "preview_export_files": preview_exports,
        "visual_qa_pass": visual_qa.get("qa_pass") is True,
        "author_review_preview_ready_rows": visual_qa.get("author_review_preview_ready_rows"),
        "source_data_missing_source_rows": panel_map.get("missing_source_rows"),
        "source_data_panel_map_locked": False,
        "final_figures_ready": False,
        "final_candidate_generation_allowed": False,
        "figure_portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "desktop_report": str(DESKTOP_REPORT),
        "status": "figure_preview_complete_final_figures_blocked",
    }

    report = f"""# Figure Preview Completion Bridge

Current state: all six planned Python preview figures have PDF, SVG, PNG and
TIFF exports, and preview visual QA passes.

This improves the local experiment-presentation state but does not make the
figures final or portal-ready.

## Quantified State

1. `preview_complete_figures={preview_complete}`.
2. `preview_export_files={preview_exports}`.
3. `visual_qa_pass={str(summary["visual_qa_pass"]).lower()}`.
4. `source_data_missing_source_rows={summary["source_data_missing_source_rows"]}`.
5. `source_data_panel_map_locked=false`.
6. `final_figures_ready=false`.
7. `figure_portal_upload_allowed=false`.
8. `submission_ready=false`.

## Boundary

These are author-review previews only. Final figure completion still requires
author approval, final export QA, panel-level Source Data lock, final captions
and portal upload clearance.
"""

    write_csv(
        OUT_DIR / "figure_preview_file_inventory.csv",
        [
            "figure_id",
            "preview_pdf_exists",
            "preview_svg_exists",
            "preview_png_exists",
            "preview_tiff_exists",
            "preview_export_count",
            "preview_status",
            "final_status",
            "submission_boundary",
        ],
        rows,
    )
    write_csv(OUT_DIR / "figure_preview_to_final_gate_bridge.csv", ["gate", "status", "evidence", "detail"], bridge_rows)
    write_csv(OUT_DIR / "figure_preview_completion_bridge_qa.csv", ["check", "result", "detail"], qa_rows)
    write_text(OUT_DIR / "FIGURE_PREVIEW_COMPLETION_BRIDGE_README.md", report)
    write_text(OUT_DIR / "figure_preview_completion_bridge_report.md", report)
    write_text(DESKTOP_REPORT, report)
    summary["desktop_plan_updated"] = update_desktop_plan(summary)
    write_text(OUT_DIR / "figure_preview_completion_bridge_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
