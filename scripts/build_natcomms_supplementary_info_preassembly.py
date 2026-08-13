#!/usr/bin/env python3
"""Build a bounded Nature Communications Supplementary Information preassembly."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_supplementary_info_preassembly_20260810"

METHODS_MAP = (
    BENCH_ROOT
    / "reports"
    / "methods_section_skeleton_20260810"
    / "methods_module_map.csv"
)
RESULTS_MAP = (
    BENCH_ROOT
    / "reports"
    / "results_section_skeleton_20260810"
    / "results_paragraph_claim_evidence_map.csv"
)
FIGURE_LOCK = (
    BENCH_ROOT
    / "reports"
    / "figure_source_data_lock_20260810"
    / "figure_panel_claim_lock.csv"
)
SOURCE_MAP = (
    BENCH_ROOT
    / "reports"
    / "source_data_deposit_package_20260810"
    / "figure_table_source_mapping.csv"
)
TABLE_DRAFTS = (
    BENCH_ROOT
    / "reports"
    / "manuscript_table_drafts_20260810"
    / "manuscript_table_drafts.md"
)
UNRESOLVED = (
    BENCH_ROOT
    / "reports"
    / "reporting_summary_draft_20260810"
    / "reporting_summary_unresolved_items.csv"
)
TEXT_PREASSEMBLY = (
    BENCH_ROOT
    / "reports"
    / "natcomms_initial_submission_text_preassembly_20260810"
    / "natcomms_initial_submission_text_preassembly.md"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def safe_get(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        if key in row and row[key]:
            return row[key]
    return ""


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    method_rows = read_csv(METHODS_MAP)
    result_rows = read_csv(RESULTS_MAP)
    figure_rows = read_csv(FIGURE_LOCK)
    source_rows = read_csv(SOURCE_MAP)
    unresolved_rows = read_csv(UNRESOLVED)
    table_text = TABLE_DRAFTS.read_text(encoding="utf-8")
    text_preassembly = TEXT_PREASSEMBLY.read_text(encoding="utf-8")

    toc_rows = [
        {
            "si_item": "Supplementary Methods 1",
            "title": "Asset intake, unified manifests and evidence-boundary policy",
            "source_anchor": "methods_section_skeleton_20260810/methods_module_map.csv",
            "status": "preassembled_not_final",
        },
        {
            "si_item": "Supplementary Methods 2",
            "title": "Split construction, environment-transfer contrasts and five-model matrix",
            "source_anchor": "methods_section_skeleton_20260810/methods_module_map.csv",
            "status": "preassembled_not_final",
        },
        {
            "si_item": "Supplementary Methods 3",
            "title": "4TU raw-trace counterfactual and grouped-feasibility stress tests",
            "source_anchor": "methods_section_skeleton_20260810/methods_module_map.csv",
            "status": "preassembled_not_final",
        },
        {
            "si_item": "Supplementary Table 1",
            "title": "Executable local asset audit",
            "source_anchor": "manuscript_table_drafts_20260810/manuscript_table_drafts.md",
            "status": "table_draft_not_typeset",
        },
        {
            "si_item": "Supplementary Table 2",
            "title": "Model-family support and open-gate summary",
            "source_anchor": "manuscript_table_drafts_20260810/manuscript_table_drafts.md",
            "status": "table_draft_not_typeset",
        },
        {
            "si_item": "Supplementary Note 1",
            "title": "Open submission gates and forbidden claim upgrades",
            "source_anchor": "reporting_summary_draft_20260810/reporting_summary_unresolved_items.csv",
            "status": "preassembled_not_final",
        },
        {
            "si_item": "Supplementary Data Guide",
            "title": "Source-data file mapping and release boundary",
            "source_anchor": "source_data_deposit_package_20260810/figure_table_source_mapping.csv",
            "status": "source_mapping_ready_figures_not_rendered",
        },
    ]
    write_csv(
        OUT_DIR / "supplementary_information_toc.csv",
        toc_rows,
        ["si_item", "title", "source_anchor", "status"],
    )

    method_modules = []
    for row in method_rows:
        module = safe_get(row, "module", "methods_module", "section", "method_module")
        evidence_role = safe_get(row, "evidence_role", "role", "claim", "purpose")
        output_anchor = safe_get(row, "output_anchor", "source", "evidence_anchor", "artifact")
        status = safe_get(row, "status", "readiness", "current_status")
        method_modules.append(
            {
                "supplementary_method": f"SM-{len(method_modules)+1:02d}",
                "module": module or f"method_module_{len(method_modules)+1}",
                "evidence_role": evidence_role or "method detail preassembled from current skeleton",
                "source_anchor": output_anchor or "methods_section_skeleton_20260810",
                "status": status or "preassembled_not_final",
                "boundary": "Supplementary Methods detail; not a substitute for final repository identifiers, rendered figures or blind external validation.",
            }
        )
    write_csv(
        OUT_DIR / "supplementary_methods_module_map.csv",
        method_modules,
        ["supplementary_method", "module", "evidence_role", "source_anchor", "status", "boundary"],
    )

    result_links = []
    for row in result_rows:
        claim = safe_get(row, "claim", "paragraph_claim", "allowed_claim")
        evidence = safe_get(row, "evidence", "source", "evidence_anchor")
        figure = safe_get(row, "figure", "figure_table", "display_item", "planned_display")
        result_links.append(
            {
                "main_text_result_anchor": safe_get(row, "paragraph_id", "result_id", "section") or f"result_{len(result_links)+1}",
                "planned_main_display": figure or "pending_final_figure_call",
                "supplementary_support_role": "methods_or_source_context",
                "claim": claim,
                "evidence_anchor": evidence,
                "boundary": "Do not use supplementary support to upgrade an open gate into a completed result.",
            }
        )
    write_csv(
        OUT_DIR / "main_text_to_supplement_crosswalk.csv",
        result_links,
        [
            "main_text_result_anchor",
            "planned_main_display",
            "supplementary_support_role",
            "claim",
            "evidence_anchor",
            "boundary",
        ],
    )

    figure_si_rows = []
    for row in figure_rows:
        role = "Supplementary source-data guide only"
        if row["figure_id"] in {"Figure 5", "Figure 6"}:
            role = "Potential supplementary gate/failure-mode material if main figure set is reduced"
        figure_si_rows.append(
            {
                "display_item": row["figure_id"],
                "allowed_claim": row["allowed_claim"],
                "recommended_si_role": role,
                "rendering_status": row["rendering_status"],
                "caption_status": row["caption_status"],
                "boundary": row["boundary"],
            }
        )
    write_csv(
        OUT_DIR / "figure_to_supplement_role_map.csv",
        figure_si_rows,
        [
            "display_item",
            "allowed_claim",
            "recommended_si_role",
            "rendering_status",
            "caption_status",
            "boundary",
        ],
    )

    source_si_rows = []
    for row in source_rows:
        source_si_rows.append(
            {
                "item_id": row["item_id"],
                "role": row["role"],
                "source_files": row["source_files"],
                "rendered_artifact_status": row["rendered_artifact_status"],
                "supplementary_or_source_data_role": "candidate_source_data_or_si_anchor",
                "boundary": row["boundary"],
            }
        )
    write_csv(
        OUT_DIR / "supplementary_source_data_boundary_map.csv",
        source_si_rows,
        [
            "item_id",
            "role",
            "source_files",
            "rendered_artifact_status",
            "supplementary_or_source_data_role",
            "boundary",
        ],
    )

    open_gate_rows = []
    for row in unresolved_rows:
        open_gate_rows.append(
            {
                "supplementary_note": "Supplementary Note 1",
                "unresolved_item": row["unresolved_item"],
                "status": row["status"],
                "required_evidence": row["required_evidence"],
                "allowed_si_wording": "Report as an open gate or boundary only.",
                "forbidden_si_wording": "Do not describe as completed, final, deposited or externally validated.",
            }
        )
    write_csv(
        OUT_DIR / "supplementary_open_gate_ledger.csv",
        open_gate_rows,
        [
            "supplementary_note",
            "unresolved_item",
            "status",
            "required_evidence",
            "allowed_si_wording",
            "forbidden_si_wording",
        ],
    )

    si_markdown = [
        "# Supplementary Information preassembly",
        "",
        "Boundary: this is a Nature Communications Supplementary Information preassembly for Track B author review. It is not a final Supplementary Information PDF, does not include rendered Supplementary Figures, does not finalize Source Data, and does not close repository, rights, Reporting Summary, reference or blind external-validation gates.",
        "",
        "## Table of contents",
        "",
    ]
    for row in toc_rows:
        si_markdown.append(f"- {row['si_item']}. {row['title']} ({row['status']})")
    si_markdown.extend(
        [
            "",
            "## Supplementary Methods preassembly",
            "",
            "The Supplementary Methods should expand reproducibility details that are too granular for the main 5000-word Article budget: asset intake, manifest fields, split construction, model-family settings, 4TU counterfactual variants and regeneration checks.",
            "",
            "## Supplementary Tables preassembly",
            "",
            table_text,
            "",
            "## Supplementary Note 1. Open gates",
            "",
            "The current Track B manuscript route must keep unresolved gates visible. Supplementary text may explain why figures, Source Data, repository identifiers, rights, Reporting Summary, references and blind external validation are not final, but it must not convert these gaps into claims of completion.",
            "",
            "## Supplementary Data guide",
            "",
            "The current source-data mapping identifies candidate files for future Source Data and Supplementary Data organization. Final public release still requires rendered figure panel mapping, repository identifiers, licence selection and third-party rights review.",
            "",
        ]
    )
    (OUT_DIR / "supplementary_information_preassembly.md").write_text(
        "\n".join(si_markdown), encoding="utf-8"
    )

    qa_rows = [
        {
            "check": "TOC exists",
            "result": "PASS" if len(toc_rows) >= 6 else "FAIL",
            "detail": f"{len(toc_rows)} SI items preassembled.",
        },
        {
            "check": "Methods modules mapped",
            "result": "PASS" if len(method_modules) > 0 else "FAIL",
            "detail": f"{len(method_modules)} method rows mapped.",
        },
        {
            "check": "Main-text crosswalk exists",
            "result": "PASS" if len(result_links) > 0 else "FAIL",
            "detail": f"{len(result_links)} result rows linked.",
        },
        {
            "check": "Figure rendering not upgraded",
            "result": "PASS" if all(row["rendering_status"] == "not_rendered" for row in figure_si_rows) else "FAIL",
            "detail": "Every figure remains marked not_rendered.",
        },
        {
            "check": "Open gates preserved",
            "result": "PASS" if len(open_gate_rows) >= 6 and "not a final submission package" in text_preassembly else "FAIL",
            "detail": f"{len(open_gate_rows)} unresolved Reporting Summary/open-gate rows preserved.",
        },
        {
            "check": "Final SI not claimed",
            "result": "PASS" if "not a final Supplementary Information PDF" in "\n".join(si_markdown) else "FAIL",
            "detail": "Boundary wording prevents final-SI claim.",
        },
    ]
    write_csv(
        OUT_DIR / "supplementary_info_preassembly_qa.csv",
        qa_rows,
        ["check", "result", "detail"],
    )

    readme = [
        "# Nat Comms Supplementary Information preassembly",
        "",
        "This package converts current methods, results, figure/source-data and open-gate artifacts into a Supplementary Information preassembly.",
        "",
        "It is not a final Supplementary Information PDF. It does not render figures, finalize Source Data, create DOI identifiers, clear rights, finalize Reporting Summary fields or complete blind external validation.",
        "",
    ]
    (OUT_DIR / "NATCOMMS_SUPPLEMENTARY_INFO_PREASSEMBLY_README.md").write_text(
        "\n".join(readme), encoding="utf-8"
    )

    report = [
        "# Nat Comms Supplementary Information preassembly report",
        "",
        f"- SI TOC rows: {len(toc_rows)}",
        f"- Supplementary Methods module rows: {len(method_modules)}",
        f"- Main-text crosswalk rows: {len(result_links)}",
        f"- Figure/SI role rows: {len(figure_si_rows)}",
        f"- Source-data boundary rows: {len(source_si_rows)}",
        f"- Open-gate rows: {len(open_gate_rows)}",
        f"- QA failures: {sum(1 for row in qa_rows if row['result'] == 'FAIL')}",
        "- Status: natcomms_supplementary_info_preassembly_ready_not_final",
        "",
        "Boundary: this package organizes SI material only; it does not create a final SI file or close scientific, repository, rights, reference or validation gates.",
        "",
    ]
    (OUT_DIR / "supplementary_info_preassembly_report.md").write_text(
        "\n".join(report), encoding="utf-8"
    )

    summary = {
        "run_id": "20260810_natcomms_supplementary_info_preassembly",
        "toc_rows": len(toc_rows),
        "supplementary_methods_rows": len(method_modules),
        "main_text_crosswalk_rows": len(result_links),
        "figure_role_rows": len(figure_si_rows),
        "source_data_boundary_rows": len(source_si_rows),
        "open_gate_rows": len(open_gate_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "current_applicable_branch": "TRACK-B",
        "supplementary_info_final": False,
        "submission_ready": False,
        "status": "natcomms_supplementary_info_preassembly_ready_not_final",
        "boundary": "SI is preassembled for author review only; final SI remains blocked by figures, Source Data, repository identifiers, rights, Reporting Summary, references and blind external validation.",
    }
    (OUT_DIR / "supplementary_info_preassembly_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
