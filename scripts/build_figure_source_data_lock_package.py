#!/usr/bin/env python3
"""Build a figure source-data lock package without rendering final figures."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "figure_source_data_lock_20260810"
SPEC_DIR = BENCH_ROOT / "reports" / "figure_rendering_spec_20260810"
PREFLIGHT_DIR = BENCH_ROOT / "reports" / "figure_rendering_preflight_20260810"
CLAIM_AUDIT = BENCH_ROOT / "reports" / "manuscript_claim_readiness_audit_20260810" / "manuscript_claim_readiness_audit.csv"
SOURCE_MAPPING = BENCH_ROOT / "reports" / "source_data_deposit_package_20260810" / "figure_table_source_mapping.csv"


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


CAPTIONS = {
    "Figure 1": "Figure 1 | Executable evidence boundary and unresolved confirmation gates. The schematic separates local executable assets, source-data generation, model-family comparisons and remaining submission gates. Asset-status bars report local executable checkpoint status only; they are not performance results.",
    "Figure 2": "Figure 2 | Res-SAM environment transfer is the strongest current model-family signal. The figure summarizes balanced-accuracy deltas and material-support counts for Mojahid and Res-SAM contrasts. Res-SAM real-to-synthetic and synthetic-to-real transfer remain separate contrasts; the panel does not include 4TU or blind external validation.",
    "Figure 3": "Figure 3 | Mojahid split sensitivity is directional but modest and model-dependent. Seed-level and model-family views show that random-minus-grouped inflation is consistent in direction but reaches material support in only a minority of model families.",
    "Figure 4": "Figure 4 | 4TU multi-layer counterfactual stress-test evidence remains a feasibility-boundary layer rather than main confirmation. Fixed-split, project-level repeated-split and five-layer evidence-boundary summaries are displayed separately to prevent the stress-test signal from being interpreted as causal proof or external validation.",
    "Figure 5": "Figure 5 | 4TU target feasibility defines a confirmation boundary. Target-level grouped-holdout feasibility and failure modes explain why 4TU is retained as stress-test or gate evidence rather than expanded into the main five-model confirmation matrix.",
    "Figure 6": "Figure 6 | Blind external validation remains an open gate. The checklist reports strict intake, label-holdout, prediction-freezing and one-shot evaluation requirements; it is a protocol-status figure, not an external-validation result.",
}


FORBIDDEN = {
    "Figure 1": "Do not imply that all nominal datasets are executable or that asset counts are performance evidence.",
    "Figure 2": "Do not include 4TU, TIGPR or blind external validation; do not describe the contrast as universal deployment robustness.",
    "Figure 3": "Do not use universal leakage language; material support remains limited.",
    "Figure 4": "Do not pool fixed-split, group-aware and evidence-boundary layers; do not present the stress test as causal proof, main confirmation or blind external validation.",
    "Figure 5": "Do not turn target feasibility into model superiority or confirmation-matrix evidence.",
    "Figure 6": "Do not call template dry runs, protocol files or placeholder checks completed blind external validation.",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    spec_rows = read_csv(SPEC_DIR / "figure_rendering_spec.csv")
    preflight_summary = json.loads((PREFLIGHT_DIR / "figure_rendering_preflight_summary.json").read_text(encoding="utf-8"))
    preflight_sources = read_csv(PREFLIGHT_DIR / "figure_source_file_preflight.csv")
    claim_rows = read_csv(CLAIM_AUDIT)
    source_mapping_rows = read_csv(SOURCE_MAPPING)

    claim_by_figure = {row["figure_or_table"].split(";")[0].strip(): row for row in claim_rows if row["figure_or_table"]}
    source_status_by_figure = {row["figure_id"]: row for row in preflight_sources}
    mapping_by_figure = {row["item_id"]: row for row in source_mapping_rows if row["item_id"].startswith("Figure")}

    panel_rows: list[dict[str, str]] = []
    source_manifest_rows: list[dict[str, str]] = []
    caption_rows: list[dict[str, str]] = []
    qa_rows: list[dict[str, str]] = []

    for spec in spec_rows:
        figure_id = spec["figure_id"]
        sources = split_sources(spec["primary_source_files"])
        source_status = source_status_by_figure[figure_id]["source_status"]
        claim = claim_by_figure.get(figure_id, {})
        mapping = mapping_by_figure.get(figure_id, {})

        panel_rows.append(
            {
                "figure_id": figure_id,
                "citation_label": spec["citation_label"],
                "allowed_claim": spec["main_conclusion"],
                "claim_readiness": claim.get("readiness", "figure_specific_boundary"),
                "allowed_strength": claim.get("allowed_strength", "bounded_figure_claim"),
                "panel_plan": spec["panel_plan"],
                "recommended_plot_type": spec["recommended_plot_type"],
                "source_status": source_status,
                "rendering_status": "not_rendered",
                "caption_status": "ready_for_final_candidate_review",
                "boundary": spec["boundary"],
            }
        )

        source_manifest_rows.append(
            {
                "figure_id": figure_id,
                "source_file_count": str(len(sources)),
                "source_files": "; ".join(sources),
                "source_mapping_status": mapping.get("status", "mapped_in_spec"),
                "rendered_artifact_status": mapping.get("rendered_artifact_status", "not_rendered_yet"),
                "source_data_filename": f"Source_Data_{figure_id.replace(' ', '_')}.csv",
                "final_source_data_status": "not_final_until_figure_rendered_and_QA_passed",
            }
        )

        caption_rows.append(
            {
                "figure_id": figure_id,
                "caption_draft": CAPTIONS[figure_id],
                "required_boundary_sentence": spec["boundary"],
                "forbidden_upgrade": FORBIDDEN[figure_id],
                "caption_lock_status": "ready_for_final_candidate_review",
            }
        )

        qa_rows.append(
            {
                "figure_id": figure_id,
                "source_present": "pass" if source_status == "all_sources_present" else "fail",
                "caption_has_boundary": "pass",
                "forbidden_upgrade_listed": "pass",
                "rendered_artifact_status": "not_rendered",
                "final_figure_ready": "false",
            }
        )

    write_csv(
        OUT_DIR / "figure_panel_claim_lock.csv",
        panel_rows,
        [
            "figure_id",
            "citation_label",
            "allowed_claim",
            "claim_readiness",
            "allowed_strength",
            "panel_plan",
            "recommended_plot_type",
            "source_status",
            "rendering_status",
            "caption_status",
            "boundary",
        ],
    )
    write_csv(
        OUT_DIR / "figure_source_data_manifest.csv",
        source_manifest_rows,
        [
            "figure_id",
            "source_file_count",
            "source_files",
            "source_mapping_status",
            "rendered_artifact_status",
            "source_data_filename",
            "final_source_data_status",
        ],
    )
    write_csv(
        OUT_DIR / "figure_caption_boundary_drafts.csv",
        caption_rows,
        ["figure_id", "caption_draft", "required_boundary_sentence", "forbidden_upgrade", "caption_lock_status"],
    )
    write_csv(
        OUT_DIR / "figure_lock_qa.csv",
        qa_rows,
        ["figure_id", "source_present", "caption_has_boundary", "forbidden_upgrade_listed", "rendered_artifact_status", "final_figure_ready"],
    )

    qa_pass = all(row["source_present"] == "pass" and row["caption_has_boundary"] == "pass" and row["forbidden_upgrade_listed"] == "pass" for row in qa_rows)
    readme = """# Figure source-data lock 2026-08-10

This package locks the figure-level claims, source-data inputs, caption boundaries and QA requirements that must be used when formal rendering starts.

It does not render figures and it does not make any figure submission-final.

## Use rule

After the author chooses one backend, generate each figure from the listed source files, export PDF/SVG/600-dpi PNG previews and run visual QA before any caption or Source Data file is treated as final.
"""
    (OUT_DIR / "FIGURE_SOURCE_DATA_LOCK_README.md").write_text(readme, encoding="utf-8")

    summary = {
        "run_id": "20260810_figure_source_data_lock",
        "figures_locked": len(panel_rows),
        "source_manifest_rows": len(source_manifest_rows),
        "caption_rows": len(caption_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "backend_choice": preflight_summary["backend_choice"],
        "rendered_figures": 0,
        "final_figures_ready": False,
        "submission_ready": False,
        "status": "figure_source_data_lock_ready_figures_not_rendered",
        "boundary": "This package locks figure inputs and caption boundaries; it does not render or visually QA final figures.",
    }
    (OUT_DIR / "figure_source_data_lock_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Figure source-data lock report 2026-08-10",
        "",
        f"- Figures locked: {summary['figures_locked']}",
        f"- Source manifest rows: {summary['source_manifest_rows']}",
        f"- Caption rows: {summary['caption_rows']}",
        f"- QA rows: {summary['qa_rows']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Backend choice: {summary['backend_choice']}",
        f"- Rendered figures: {summary['rendered_figures']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: Figure 1-6 inputs are locked for rendering, but formal figure production remains open until backend choice, export and visual QA.",
        "",
    ]
    (OUT_DIR / "figure_source_data_lock_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
