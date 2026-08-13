#!/usr/bin/env python3
"""Build figure rendering specifications and QA checklist without rendering figures."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "figure_rendering_spec_20260810"
ANCHOR_MAP = BENCH_ROOT / "reports" / "figure_table_anchor_lock_20260810" / "source_data_anchor_map.csv"


FIGURE_SPECS = [
    {
        "figure_id": "Figure 1",
        "citation_label": "Fig. 1",
        "main_conclusion": "The study separates executable local evidence from unresolved confirmation gates.",
        "layout": "two-column schematic plus compact asset-status strip",
        "panel_plan": "A: workflow from assets to evidence gates; B: executable row counts and GO/NO-GO asset status.",
        "recommended_plot_type": "flow schematic plus horizontal status bars",
        "primary_source_files": "reports/figure1_table1_sources_20260810/figure1_flow_source.csv; reports/figure1_table1_sources_20260810/table1_asset_audit.csv",
        "visual_encoding": "Use neutral slate for protocol steps, green/amber/red for GO/caution/NO-GO status, and avoid performance-colored semantics.",
        "required_exports": "PDF; SVG; 600-dpi PNG preview",
        "qa_checks": "All asset counts match Table 1; TIGPR shown as 0 local executable rows; Fig. 1 not presented as performance evidence.",
        "render_priority": "2",
        "boundary": "Protocol/asset map only, not a performance result.",
    },
    {
        "figure_id": "Figure 2",
        "citation_label": "Fig. 2",
        "main_conclusion": "Res-SAM environment transfer is the strongest current cross-model signal.",
        "layout": "main multi-panel result figure",
        "panel_plan": "A: model-family delta matrix by dataset/contrast; B: material-support counts; C: contrast-level mean delta with boundary labels.",
        "recommended_plot_type": "dot/interval matrix plus compact support-count bars",
        "primary_source_files": "reports/figure2_table2_sources_20260810/figure2_source_data.csv; reports/figure2_table2_sources_20260810/table2_model_family_support.csv",
        "visual_encoding": "Use one hue family for Res-SAM transfer, muted grey for Mojahid directional-only contrast, and explicit material-support threshold markers.",
        "required_exports": "PDF; SVG; 600-dpi PNG preview; Source Data mapping",
        "qa_checks": "No 4TU or blind external rows; Mojahid labelled directional_only; Res-SAM real-to-synthetic and synthetic-to-real kept separate.",
        "render_priority": "1",
        "boundary": "Scope is Mojahid and Res-SAM only; no blind external validation claim.",
    },
    {
        "figure_id": "Figure 3",
        "citation_label": "Fig. 3",
        "main_conclusion": "Mojahid split sensitivity is directionally consistent but modest and model-dependent.",
        "layout": "secondary evidence figure or extended-data candidate",
        "panel_plan": "A: HOG random vs grouped balanced accuracy by seed; B: five-model delta distribution; C: claim-boundary badge.",
        "recommended_plot_type": "paired seed lines plus dot strip for model-family deltas",
        "primary_source_files": "reports/figure3_sources_20260810/figure3_hog_split_source_data.csv; reports/figure3_sources_20260810/figure3_model_delta_source_data.csv; reports/figure3_sources_20260810/figure3_claim_boundary.csv",
        "visual_encoding": "Use restrained contrast and label as secondary/directional-only; avoid red-alert leakage framing.",
        "required_exports": "PDF; SVG; 600-dpi PNG preview; Source Data mapping",
        "qa_checks": "Material support count remains 1/5; do not use universal leakage wording; paired seeds remain identifiable.",
        "render_priority": "3",
        "boundary": "Directional but modest/model-dependent split effect; not universal leakage proof.",
    },
    {
        "figure_id": "Figure 4",
        "citation_label": "Fig. 4",
        "main_conclusion": "4TU multi-layer counterfactual stress-test evidence remains a feasibility-boundary layer rather than main confirmation.",
        "layout": "stress-test comparison figure",
        "panel_plan": "A: fixed-split counterfactual BA/drop/flip summary; B: group-aware repeated-split sensitivity; C: five-layer evidence-boundary inset.",
        "recommended_plot_type": "side-by-side dot/interval plots with separate fixed and grouped strata",
        "primary_source_files": "reports/figure4_sources_20260810/figure4_counterfactual_source_data.csv; reports/figure4_sources_20260810/figure4_evidence_layer_boundary.csv",
        "visual_encoding": "Use two distinct strata labels rather than a continuous narrative; emphasize weakening under group-aware validation.",
        "required_exports": "PDF; SVG; 600-dpi PNG preview; Source Data mapping",
        "qa_checks": "Fixed-split and group-aware results not pooled; five-layer inset labelled stress-test only; no causal-proof, main-confirmation or blind-external wording.",
        "render_priority": "4",
        "boundary": "Stress-test evidence, not final causal proof or main confirmation.",
    },
    {
        "figure_id": "Figure 5",
        "citation_label": "Fig. 5",
        "main_conclusion": "Current 4TU labels are insufficient for the main cross-model confirmation layer.",
        "layout": "feasibility/failure-mode map",
        "panel_plan": "A: six target feasibility states; B: grouped-holdout feasibility counts; C: recommended manuscript role.",
        "recommended_plot_type": "status heatmap plus compact count bars",
        "primary_source_files": "reports/figure5_figure6_sources_20260810/figure5_4tu_feasibility_source_data.csv",
        "visual_encoding": "Use status colors for usable_with_caution, weak, not_viable; no accuracy axis.",
        "required_exports": "PDF; SVG; 600-dpi PNG preview; Source Data mapping",
        "qa_checks": "Land type and Utility crossing shown as caution, not confirmed; not_viable targets remain explicit.",
        "render_priority": "5",
        "boundary": "Gate/failure-mode result; supports study design decisions, not model superiority.",
    },
    {
        "figure_id": "Figure 6",
        "citation_label": "Fig. 6",
        "main_conclusion": "Blind external validation remains unavailable under the frozen protocol.",
        "layout": "open-gate placeholder figure or supplement",
        "panel_plan": "A: external validation tracks A-D status; B: hard requirements checklist; C: one-shot evaluation rule.",
        "recommended_plot_type": "gate matrix/checklist, not performance plot",
        "primary_source_files": "reports/figure5_figure6_sources_20260810/figure6_external_gate_source_data.csv; reports/external_validation_readiness_20260810/external_validation_readiness_tracks.csv",
        "visual_encoding": "Use open-gate styling; no performance metrics except template-dry-run label if shown.",
        "required_exports": "PDF; SVG; 600-dpi PNG preview; Source Data mapping",
        "qa_checks": "Must say NO-GO; template dry run never shown as external validation; Res-SAM not relabelled blind external.",
        "render_priority": "6",
        "boundary": "Open-gate placeholder only; no completed blind external validation.",
    },
]


QA_ROWS = [
    {
        "qa_id": "QA001",
        "category": "Evidence boundary",
        "check": "Every panel title matches the current claim status and boundary.",
        "failure_condition": "Any panel upgrades directional_only, stress-test, or NO-GO evidence into a completed main result.",
    },
    {
        "qa_id": "QA002",
        "category": "Source data",
        "check": "Every plotted number exists in the listed source-data CSV and has a panel-level mapping.",
        "failure_condition": "Any plotted value cannot be traced to a dated source-data file.",
    },
    {
        "qa_id": "QA003",
        "category": "Visual hierarchy",
        "check": "Figure 2 is visually dominant as the main result; Figures 3-6 are secondary, stress-test or gate figures.",
        "failure_condition": "A secondary/gate figure appears to carry the main claim.",
    },
    {
        "qa_id": "QA004",
        "category": "Accessibility",
        "check": "Color choices are colorblind-safe and remain interpretable in greyscale.",
        "failure_condition": "Status or result meaning is encoded by color alone.",
    },
    {
        "qa_id": "QA005",
        "category": "Export",
        "check": "Each rendered figure has PDF, SVG and 600-dpi PNG preview outputs.",
        "failure_condition": "Any final figure lacks vector export or preview QA file.",
    },
    {
        "qa_id": "QA006",
        "category": "Text safety",
        "check": "No figure caption states that blind external validation, public release, DOI or full Res-SAM replication is complete.",
        "failure_condition": "Caption language contradicts current gate status.",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    anchors = {row["item_id"]: row for row in read_csv(ANCHOR_MAP)}
    for spec in FIGURE_SPECS:
        anchor = anchors.get(spec["figure_id"])
        if anchor is None:
            raise KeyError(f"Missing anchor for {spec['figure_id']}")
        if anchor["rendered_artifact_status"] != "not_rendered_yet":
            raise ValueError(f"Unexpected rendered status for {spec['figure_id']}: {anchor['rendered_artifact_status']}")

    spec_fields = [
        "figure_id",
        "citation_label",
        "main_conclusion",
        "layout",
        "panel_plan",
        "recommended_plot_type",
        "primary_source_files",
        "visual_encoding",
        "required_exports",
        "qa_checks",
        "render_priority",
        "boundary",
    ]
    qa_fields = ["qa_id", "category", "check", "failure_condition"]
    write_csv(OUT_DIR / "figure_rendering_spec.csv", FIGURE_SPECS, spec_fields)
    write_csv(OUT_DIR / "figure_rendering_qa_checklist.csv", QA_ROWS, qa_fields)

    priority_rows = sorted(
        [
            {
                "render_priority": spec["render_priority"],
                "figure_id": spec["figure_id"],
                "citation_label": spec["citation_label"],
                "reason": "Lead result" if spec["figure_id"] == "Figure 2" else spec["main_conclusion"],
                "requires_user_backend_choice": "yes",
                "ready_to_render_after_backend_choice": "yes",
            }
            for spec in FIGURE_SPECS
        ],
        key=lambda row: int(row["render_priority"]),
    )
    write_csv(
        OUT_DIR / "figure_rendering_priority_queue.csv",
        priority_rows,
        ["render_priority", "figure_id", "citation_label", "reason", "requires_user_backend_choice", "ready_to_render_after_backend_choice"],
    )

    md_lines = [
        "# Figure rendering specification 2026-08-10",
        "",
        "This specification locks the intended conclusion, panel logic, source files, export requirements and QA risks for planned figures. It does not render figures.",
        "",
        "## Rendering Priority",
        "",
        "| Priority | Figure | Main conclusion | Boundary |",
        "| --- | --- | --- | --- |",
    ]
    for spec in sorted(FIGURE_SPECS, key=lambda row: int(row["render_priority"])):
        md_lines.append(f"| {spec['render_priority']} | {spec['citation_label']} | {spec['main_conclusion']} | {spec['boundary']} |")
    md_lines.extend(
        [
            "",
            "## Backend Decision",
            "",
            "Formal rendering is intentionally not started here. The next figure step requires choosing Python or R so the Nature figure workflow can run under one backend.",
            "",
            "## QA Gate",
            "",
            "Rendered figures must pass source-data traceability, boundary-language, visual hierarchy, accessibility and export checks before manuscript use.",
            "",
        ]
    )
    (OUT_DIR / "figure_rendering_spec.md").write_text("\n".join(md_lines), encoding="utf-8")

    summary = {
        "run_id": "20260810_figure_rendering_spec",
        "figures_specified": len(FIGURE_SPECS),
        "qa_checks": len(QA_ROWS),
        "rendered_figures": 0,
        "ready_to_render_after_backend_choice": True,
        "backend_choice_required": "Python_or_R",
        "status": "rendering_spec_ready_figures_not_rendered",
        "manuscript_ready": False,
        "boundary": "Figure specifications are ready, but no figure has been rendered or visually QAed.",
    }
    (OUT_DIR / "figure_rendering_spec_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
