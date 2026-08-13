#!/usr/bin/env python3
"""Build a figure-rendering preflight package without rendering final figures."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "figure_rendering_preflight_20260810"
SPEC_DIR = BENCH_ROOT / "reports" / "figure_rendering_spec_20260810"
SOURCE_MAPPING = BENCH_ROOT / "reports" / "source_data_deposit_package_20260810" / "figure_table_source_mapping.csv"
DASHBOARD_DECISIONS = BENCH_ROOT / "reports" / "submission_command_dashboard_v2_20260810" / "current_branch_and_decision_register.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def split_sources(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    spec_summary = json.loads((SPEC_DIR / "figure_rendering_spec_summary.json").read_text(encoding="utf-8"))
    spec_rows = read_csv(SPEC_DIR / "figure_rendering_spec.csv")
    priority_rows = read_csv(SPEC_DIR / "figure_rendering_priority_queue.csv")
    qa_rows = read_csv(SPEC_DIR / "figure_rendering_qa_checklist.csv")
    mapping_rows = read_csv(SOURCE_MAPPING)
    decisions = read_csv(DASHBOARD_DECISIONS)
    backend_decision = next(row for row in decisions if row["decision"] == "current_figure_backend")

    source_rows: list[dict[str, str]] = []
    for row in spec_rows:
        sources = split_sources(row["primary_source_files"])
        missing = [source for source in sources if not (BENCH_ROOT / source).exists()]
        source_rows.append(
            {
                "figure_id": row["figure_id"],
                "source_file_count": str(len(sources)),
                "missing_source_files": ";".join(missing),
                "source_status": "all_sources_present" if not missing else "missing_sources",
                "boundary": row["boundary"],
            }
        )
    write_csv(OUT_DIR / "figure_source_file_preflight.csv", source_rows, ["figure_id", "source_file_count", "missing_source_files", "source_status", "boundary"])

    render_rows: list[dict[str, str]] = []
    priority_by_figure = {row["figure_id"]: row for row in priority_rows}
    mapping_by_item = {row["item_id"]: row for row in mapping_rows}
    for row in spec_rows:
        priority = priority_by_figure[row["figure_id"]]
        source_status = next(item for item in source_rows if item["figure_id"] == row["figure_id"])["source_status"]
        mapping = mapping_by_item.get(row["figure_id"], {})
        render_rows.append(
            {
                "render_order": priority["render_priority"],
                "figure_id": row["figure_id"],
                "claim": row["main_conclusion"],
                "recommended_plot_type": row["recommended_plot_type"],
                "source_status": source_status,
                "rendered_artifact_status": mapping.get("rendered_artifact_status", "not_rendered_yet"),
                "backend_blocker": backend_decision["selected_value"],
                "ready_after_backend_choice": priority["ready_to_render_after_backend_choice"],
                "first_allowed_action_after_backend_choice": f"Render {row['figure_id']} using the selected backend, then export PDF, SVG and 600-dpi PNG preview.",
                "must_preserve_boundary": row["boundary"],
            }
        )
    write_csv(
        OUT_DIR / "figure_rendering_kickoff_queue.csv",
        render_rows,
        [
            "render_order",
            "figure_id",
            "claim",
            "recommended_plot_type",
            "source_status",
            "rendered_artifact_status",
            "backend_blocker",
            "ready_after_backend_choice",
            "first_allowed_action_after_backend_choice",
            "must_preserve_boundary",
        ],
    )

    backend_rows = [
        {
            "backend_option": "Python",
            "fit_to_current_project": "recommended_default",
            "reason": "Current evidence pipeline, scripts and source data are already Python-based.",
            "post_decision_action": "Use Python for generation, preview, export and QA; do not mix with R in the final figure set.",
        },
        {
            "backend_option": "R",
            "fit_to_current_project": "allowed_if_author_prefers",
            "reason": "Allowed only if the author wants ggplot2/patchwork/ComplexHeatmap-style production and accepts conversion effort.",
            "post_decision_action": "Use R consistently for generation, preview, export and QA.",
        },
    ]
    write_csv(OUT_DIR / "figure_backend_decision_sheet.csv", backend_rows, ["backend_option", "fit_to_current_project", "reason", "post_decision_action"])

    qa_import_rows = [
        {
            "qa_id": row["qa_id"],
            "category": row["category"],
            "check": row["check"],
            "preflight_status": "must_apply_after_render",
            "failure_condition": row["failure_condition"],
        }
        for row in qa_rows
    ]
    write_csv(OUT_DIR / "figure_visual_qa_import.csv", qa_import_rows, ["qa_id", "category", "check", "preflight_status", "failure_condition"])

    stop_rows = [
        {"stop_rule": "Do not render formal figures before a single backend is selected.", "current_status": "active"},
        {"stop_rule": "Do not call Figure 6 an external validation result; it remains an open-gate figure.", "current_status": "active"},
        {"stop_rule": "Do not include 4TU or blind external rows in Figure 2.", "current_status": "active"},
        {"stop_rule": "Do not treat generated previews as final figures until vector exports and visual QA pass.", "current_status": "active"},
        {"stop_rule": "Do not lock figure captions before manuscript branch, references and Source Data are locked.", "current_status": "active"},
    ]
    write_csv(OUT_DIR / "figure_rendering_stop_rules.csv", stop_rows, ["stop_rule", "current_status"])

    readme = """# Figure rendering preflight 2026-08-10

This package checks whether the planned figure set can move into formal rendering after the author chooses one backend.

Current state: no final figures are rendered.

## Required author decision

Choose exactly one backend: Python or R. The current default recommendation is Python because the analysis pipeline and source-data files are already Python-oriented.

## Stop rules

1. Do not start formal figure rendering before backend choice.
2. Do not treat any planned figure as final without PDF, SVG, 600-dpi PNG preview and visual QA.
3. Do not upgrade Figure 6 into an external-validation result.
4. Do not use final figure captions until references, manuscript branch and Source Data are locked.
"""
    (OUT_DIR / "FIGURE_RENDERING_PREFLIGHT_README.md").write_text(readme, encoding="utf-8")

    summary = {
        "run_id": "20260810_figure_rendering_preflight",
        "figures_checked": len(spec_rows),
        "source_rows": len(source_rows),
        "figures_with_missing_sources": sum(1 for row in source_rows if row["source_status"] != "all_sources_present"),
        "render_queue_rows": len(render_rows),
        "backend_choice": backend_decision["selected_value"],
        "rendered_figures": spec_summary["rendered_figures"],
        "ready_to_render_after_backend_choice": spec_summary["ready_to_render_after_backend_choice"],
        "qa_import_rows": len(qa_import_rows),
        "submission_ready": False,
        "status": "figure_rendering_preflight_ready_figures_not_rendered",
        "boundary": "This package verifies figure rendering readiness inputs; it does not render or visually QA final figures.",
    }
    (OUT_DIR / "figure_rendering_preflight_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Figure rendering preflight report 2026-08-10",
        "",
        f"- Figures checked: {summary['figures_checked']}",
        f"- Figures with missing sources: {summary['figures_with_missing_sources']}",
        f"- Render queue rows: {summary['render_queue_rows']}",
        f"- Backend choice: {summary['backend_choice']}",
        f"- Rendered figures: {summary['rendered_figures']}",
        f"- Ready after backend choice: {summary['ready_to_render_after_backend_choice']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: figure sources are preflighted, but formal rendering remains blocked until backend choice.",
        "",
    ]
    (OUT_DIR / "figure_rendering_preflight_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
