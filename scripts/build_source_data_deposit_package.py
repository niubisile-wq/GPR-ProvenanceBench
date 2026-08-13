#!/usr/bin/env python3
"""Build a source-data deposit manifest with checksums and figure/table mapping."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "source_data_deposit_package_20260810"

FIGURE_PLAN = REPORTS / "manuscript_figure_table_plan_20260810" / "figure_table_claim_evidence_map.csv"

SOURCE_DIRS = [
    REPORTS / "figure1_table1_sources_20260810",
    REPORTS / "figure2_table2_sources_20260810",
    REPORTS / "figure3_sources_20260810",
    REPORTS / "figure4_sources_20260810",
    REPORTS / "figure5_figure6_sources_20260810",
    REPORTS / "manuscript_figure_table_plan_20260810",
    REPORTS / "results_section_skeleton_20260810",
    REPORTS / "methods_section_skeleton_20260810",
    REPORTS / "submission_package_skeleton_20260810",
    REPORTS / "companion_artifacts_skeleton_20260810",
]

EXTRA_SOURCE_FILES = [
    BENCH_ROOT / "data_manifests" / "mojahid_unified_samples_20260810.csv",
    BENCH_ROOT / "data_manifests" / "four_tu_unified_samples_20260810.csv",
    BENCH_ROOT / "data_manifests" / "res_sam_unified_samples_20260810.csv",
    BENCH_ROOT / "data_manifests" / "tigpr_unified_samples_20260810.csv",
    BENCH_ROOT / "data_manifests" / "unified_sample_schema_20260810.csv",
    BENCH_ROOT / "environment" / "pip_freeze_20260810.txt",
    BENCH_ROOT / "environment" / "python_environment_20260810.json",
    BENCH_ROOT / "environment" / "environment_audit_20260810.md",
    BENCH_ROOT / "protocols" / "blind_external_validation_protocol_20260810.md",
    BENCH_ROOT / "protocols" / "4tu_raw_trace_counterfactual_audit_20260810.md",
    BENCH_ROOT / "scripts" / "run_m0_m2_checks.ps1",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(BENCH_ROOT.resolve()).as_posix()


def classify(path: Path) -> str:
    rel_path = rel(path)
    if rel_path.startswith("reports/figure"):
        return "figure_table_source_data"
    if rel_path.startswith("reports/manuscript_figure_table_plan"):
        return "claim_evidence_plan"
    if rel_path.startswith("reports/results_section"):
        return "results_skeleton"
    if rel_path.startswith("reports/methods_section"):
        return "methods_skeleton"
    if rel_path.startswith("reports/submission_package"):
        return "submission_skeleton"
    if rel_path.startswith("reports/companion_artifacts"):
        return "companion_artifact_skeleton"
    if rel_path.startswith("data_manifests"):
        return "sample_manifest"
    if rel_path.startswith("environment"):
        return "environment_metadata"
    if rel_path.startswith("protocols"):
        return "protocol"
    if rel_path.startswith("scripts"):
        return "reproducibility_script"
    return "other"


def collect_files() -> list[Path]:
    files: set[Path] = set()
    for directory in SOURCE_DIRS:
        if directory.exists():
            for path in directory.rglob("*"):
                if path.is_file() and path.suffix.lower() in {".csv", ".json", ".md", ".txt", ".ps1"}:
                    files.add(path)
    for path in EXTRA_SOURCE_FILES:
        if path.exists():
            files.add(path)
    return sorted(files, key=lambda p: rel(p))


def build_file_manifest(files: list[Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in files:
        rows.append(
            {
                "relative_path": rel(path),
                "category": classify(path),
                "file_extension": path.suffix.lower(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "deposit_status": "ready_as_derived_artifact",
                "release_note": "Derived artifact or metadata only; third-party raw data are not redistributed here.",
            }
        )
    return rows


def source_files_for_item(item_id: str) -> list[str]:
    mapping = {
        "Figure 1": [
            "reports/figure1_table1_sources_20260810/table1_asset_audit.csv",
            "reports/figure1_table1_sources_20260810/figure1_flow_source.csv",
        ],
        "Table 1": [
            "reports/figure1_table1_sources_20260810/table1_asset_audit.csv",
            "data_manifests/mojahid_unified_samples_20260810.csv",
            "data_manifests/four_tu_unified_samples_20260810.csv",
            "data_manifests/res_sam_unified_samples_20260810.csv",
            "data_manifests/tigpr_unified_samples_20260810.csv",
        ],
        "Figure 2": [
            "reports/figure2_table2_sources_20260810/figure2_source_data.csv",
            "reports/figure2_table2_sources_20260810/table2_model_family_support.csv",
        ],
        "Table 2": [
            "reports/figure2_table2_sources_20260810/table2_model_family_support.csv",
            "reports/five_model_synthesis_20260810/five_model_synthesis_claim_summary.csv",
        ],
        "Figure 3": [
            "reports/figure3_sources_20260810/figure3_hog_split_source_data.csv",
            "reports/figure3_sources_20260810/figure3_model_delta_source_data.csv",
            "reports/figure3_sources_20260810/figure3_claim_boundary.csv",
        ],
        "Figure 4": [
            "reports/figure4_sources_20260810/figure4_counterfactual_source_data.csv",
            "reports/figure4_sources_20260810/figure4_evidence_layer_boundary.csv",
        ],
        "Figure 5": [
            "reports/figure5_figure6_sources_20260810/figure5_4tu_feasibility_source_data.csv",
        ],
        "Figure 6": [
            "reports/figure5_figure6_sources_20260810/figure6_external_gate_source_data.csv",
            "reports/external_validation_readiness_20260810/external_validation_readiness_tracks.csv",
        ],
        "Table 3": [
            "checkpoints/gate_status_20260810.md",
            "checkpoints/checkpoint_20260810.md",
        ],
    }
    return mapping.get(item_id, [])


def build_mapping_rows() -> list[dict[str, str]]:
    plan_rows = read_csv(FIGURE_PLAN)
    rows: list[dict[str, str]] = []
    for row in plan_rows:
        item_id = row["item_id"]
        sources = source_files_for_item(item_id)
        rows.append(
            {
                "item_id": item_id,
                "role": row["role"],
                "claim": row["claim"],
                "status": row["status"],
                "source_files": "; ".join(sources),
                "rendered_artifact_status": "not_rendered_yet" if item_id.startswith("Figure") else "table_source_ready",
                "boundary": row["boundary"],
            }
        )
    return rows


def write_readme(path: Path, file_rows: list[dict[str, object]], mapping_rows: list[dict[str, str]]) -> None:
    categories = sorted({str(row["category"]) for row in file_rows})
    lines = [
        "# GPR-ProvenanceBench Source Data Deposit Skeleton 2026-08-10",
        "",
        "This package describes derived source data and metadata that support the current manuscript skeleton. It is not a final public repository record and has no DOI or accession number yet.",
        "",
        "## Contents",
        "",
        f"- Files indexed: {len(file_rows)}",
        f"- Figure/table mapping rows: {len(mapping_rows)}",
        f"- Categories: {', '.join(categories)}",
        "",
        "## Files",
        "",
        "See `source_data_file_manifest.csv` for relative paths, file categories, sizes and SHA256 checksums.",
        "",
        "## Figure and Table Mapping",
        "",
        "See `figure_table_source_mapping.csv` for the mapping between planned display items and current source files. Figures are not rendered yet; the mapping points to source data only.",
        "",
        "## Variables and Units",
        "",
        "Column definitions remain file-specific and should be expanded before repository deposition. Current CSV headers are preserved in each source-data file.",
        "",
        "## Methods and Provenance",
        "",
        "The package is generated by `scripts/build_source_data_deposit_package.py` from dated source-data folders under `reports/`, unified manifests under `data_manifests/`, environment records under `environment/`, protocols under `protocols/` and the M0-M2 check script.",
        "",
        "## Access and Licence",
        "",
        "Derived artifacts are planned for public deposition, but no licence has been assigned yet. Third-party raw GPR datasets are not redistributed in this skeleton unless their original licences permit redistribution.",
        "",
        "## Citation",
        "",
        "[Dataset citation pending repository DOI/accession].",
        "",
        "## Blocking Items Before Public Deposit",
        "",
        "1. Choose repository and create persistent DOI/accession.",
        "2. Add licence after institutional and third-party data checks.",
        "3. Replace or sanitize local absolute paths where public release requires it.",
        "4. Add final rendered figures and panel-level source-data mapping after plotting backend is selected.",
        "5. Verify original dataset licences and official citations.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = collect_files()
    file_rows = build_file_manifest(files)
    mapping_rows = build_mapping_rows()
    write_csv(
        OUT_DIR / "source_data_file_manifest.csv",
        file_rows,
        [
            "relative_path",
            "category",
            "file_extension",
            "size_bytes",
            "sha256",
            "deposit_status",
            "release_note",
        ],
    )
    write_csv(
        OUT_DIR / "figure_table_source_mapping.csv",
        mapping_rows,
        [
            "item_id",
            "role",
            "claim",
            "status",
            "source_files",
            "rendered_artifact_status",
            "boundary",
        ],
    )
    write_readme(OUT_DIR / "SOURCE_DATA_README.md", file_rows, mapping_rows)
    result = {
        "run_id": "20260810_source_data_deposit_package",
        "indexed_files": len(file_rows),
        "mapping_rows": len(mapping_rows),
        "has_checksums": all(bool(row["sha256"]) for row in file_rows),
        "repository_identifier": None,
        "submission_ready": False,
        "boundary": "Derived source-data deposit skeleton only; final rendered figures, DOI/accession and licence are missing.",
    }
    (OUT_DIR / "source_data_deposit_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
