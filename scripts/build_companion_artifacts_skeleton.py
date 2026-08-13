#!/usr/bin/env python3
"""Build Nature Communications companion-artifact skeletons without inventing identifiers."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "companion_artifacts_skeleton_20260810"


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_data_inventory() -> list[dict[str, str]]:
    return [
        {
            "dataset_id": "D1",
            "dataset": "Unified sample manifests",
            "supports": "Figure 1; Table 1; asset boundary",
            "current_location": "data_manifests/*_unified_samples_20260810.csv; data_manifests/unified_sample_schema_20260810.csv",
            "access_route": "public repository planned",
            "recommended_repository": "Zenodo, Figshare, OSF, Dryad or institutional DOI repository",
            "identifier_status": "missing_persistent_identifier",
            "restriction_or_note": "Contains derived sample metadata and local paths; local absolute paths should be sanitized or replaced with relative/deposit paths before public release.",
        },
        {
            "dataset_id": "D2",
            "dataset": "Figure and table source data",
            "supports": "Figures 1-6; Tables 1-3",
            "current_location": "reports/figure*_sources_20260810; reports/manuscript_figure_table_plan_20260810",
            "access_route": "public repository planned",
            "recommended_repository": "Same DOI record as benchmark source data, with panel-level source-data mapping",
            "identifier_status": "missing_persistent_identifier",
            "restriction_or_note": "Ready as derived source data; final rendered figure source files still depend on plotting backend selection.",
        },
        {
            "dataset_id": "D3",
            "dataset": "Reused public or third-party GPR datasets",
            "supports": "Mojahid, 4TU, Res-SAM and TIGPR asset context",
            "current_location": "local copies and manifests only",
            "access_route": "reused public source or third-party restricted",
            "recommended_repository": "Cite original dataset providers; do not redistribute third-party files unless licence permits",
            "identifier_status": "source_identifiers_need_verification",
            "restriction_or_note": "Dataset-specific licences, official URLs, versions and redistribution rights must be verified before submission.",
        },
        {
            "dataset_id": "D4",
            "dataset": "External blind validation asset",
            "supports": "Future Figure 6 or main external validation claim",
            "current_location": "not available",
            "access_route": "not applicable yet",
            "recommended_repository": "To be determined after acquisition; strict-SHA manifest required before prediction",
            "identifier_status": "not_started",
            "restriction_or_note": "Current gate is NO-GO; no statement may claim completed blind external validation.",
        },
        {
            "dataset_id": "D5",
            "dataset": "Environment and reproducibility metadata",
            "supports": "Reproducibility checks; Methods M7",
            "current_location": "environment/pip_freeze_20260810.txt; environment/python_environment_20260810.json; checkpoints/*.md",
            "access_route": "public repository planned",
            "recommended_repository": "Archive with code release DOI",
            "identifier_status": "missing_persistent_identifier",
            "restriction_or_note": "Current environment is CPU/Python 3.12 for M0-M2 checks; not a full final training environment.",
        },
    ]


def build_reporting_rows() -> list[dict[str, str]]:
    return [
        {
            "item": "Study design",
            "current_status": "partial",
            "evidence": "Results/Methods skeletons define asset audit, split/transfer contrasts and gates.",
            "missing_before_submission": "Final manuscript framing and exact article type.",
            "risk": "medium",
        },
        {
            "item": "Sample size and exclusions",
            "current_status": "partial",
            "evidence": "Unified manifests record executable rows: Mojahid 2524, 4TU 99, Res-SAM 1050, TIGPR 0.",
            "missing_before_submission": "Final inclusion/exclusion criteria and dataset licence constraints for each source.",
            "risk": "medium",
        },
        {
            "item": "Randomization and split strategy",
            "current_status": "partial",
            "evidence": "Current Results skeleton distinguishes random, grouped and environment-transfer contrasts.",
            "missing_before_submission": "Frozen split manifests for every final figure and exact seed table.",
            "risk": "medium",
        },
        {
            "item": "Blinding",
            "current_status": "protocol_only",
            "evidence": "Blind external validation protocol, templates and locked evaluator dry run exist.",
            "missing_before_submission": "Real external asset with label holdout, strict-SHA manifest and one-shot prediction submission.",
            "risk": "high",
        },
        {
            "item": "Statistical analysis",
            "current_status": "partial",
            "evidence": "Current source packages report balanced accuracy deltas, support counts and feasibility status.",
            "missing_before_submission": "Final statistical test plan, uncertainty intervals and multiple-comparison policy where applicable.",
            "risk": "medium",
        },
        {
            "item": "Software and code availability",
            "current_status": "local_only",
            "evidence": "Scripts and run_m0_m2_checks.ps1 regenerate current M0-M2 artifacts.",
            "missing_before_submission": "Public repository URL, release tag, archive DOI, licence and README.",
            "risk": "high",
        },
        {
            "item": "Data availability",
            "current_status": "local_only",
            "evidence": "Derived manifests and figure/table source data exist locally.",
            "missing_before_submission": "Repository DOI/accession, dataset README, licence, source-data mapping and third-party data source citations.",
            "risk": "high",
        },
        {
            "item": "External validation",
            "current_status": "not_ready",
            "evidence": "External validation readiness gate is NO-GO.",
            "missing_before_submission": "Acquire or restore external asset and run the locked evaluation after label unlock.",
            "risk": "high",
        },
    ]


def write_data_availability(path: Path, inventory: list[dict[str, str]]) -> None:
    lines = [
        "# Data Availability Skeleton 2026-08-10",
        "",
        "Ready-to-paste status: not ready. Persistent repository identifiers are missing.",
        "",
        "## Draft Statement",
        "",
        "The derived sample manifests, figure source data, table source data, external-validation templates and reproducibility metadata generated for this study will be deposited in [REPOSITORY] under [DOI/accession] before submission. The deposited record should include the unified sample manifests, figure/table source-data files, benchmark reports, protocol files, environment metadata and a README mapping each file to the corresponding manuscript figure, table or Methods module. Public or third-party GPR datasets reused in the analysis, including Mojahid, 4TU, Res-SAM and TIGPR-related records, should be accessed from their original providers under their respective licences and cited with verified dataset identifiers. The current external blind-validation asset is not yet available; no data supporting a completed blind external-validation claim exist at this checkpoint.",
        "",
        "## Repository and Citation Actions",
        "",
        "1. Create a durable repository record for derived benchmark artifacts and source data.",
        "2. Add a dataset README with file descriptions, columns, units, checksums where relevant and figure/table mapping.",
        "3. Verify original source identifiers, licences and redistribution rights for Mojahid, 4TU, Res-SAM and TIGPR before final wording.",
        "4. Add formal DataCite-style dataset citations after repository records are created.",
        "5. Do not use temporary cloud links or local Baidu/desktop paths as the only availability route.",
        "",
        "## Inventory",
        "",
        "| id | dataset | supports | route | identifier status | note |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in inventory:
        lines.append(
            f"| {row['dataset_id']} | {row['dataset']} | {row['supports']} | {row['access_route']} | {row['identifier_status']} | {row['restriction_or_note']} |"
        )
    lines.extend(
        [
            "",
            "## Chinese Author Check",
            "",
            "1. 不能写“数据可向通讯作者索取”作为主要方案，除非有明确限制原因和机构化申请流程。",
            "2. 不能写“所有数据都在文中”，因为当前还需要 figure/table source data 和代码仓库记录。",
            "3. 不能伪造 DOI、accession number、仓库名或 licence。",
            "4. 当前只能写 derived artifacts will be deposited，不应写 have been deposited，除非真实仓库记录已经创建。",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_code_availability(path: Path) -> None:
    lines = [
        "# Code Availability Skeleton 2026-08-10",
        "",
        "Ready-to-paste status: not ready. Public repository URL, release tag, archive DOI and licence are missing.",
        "",
        "## Draft Statement",
        "",
        "The analysis code and reproducibility scripts used to generate the current benchmark manifests, source-data packages, Results/Methods skeletons and submission-package skeleton will be made available in [CODE_REPOSITORY_URL] and archived at [ZENODO_OR_OTHER_ARCHIVE_DOI] before submission. The archived release should include the PowerShell runbook, Python scripts, environment files, protocol templates and instructions needed to reproduce the M0-M2 artifacts from locally available or properly obtained input data. Third-party datasets are not redistributed with the code unless their licences permit redistribution.",
        "",
        "## Required Actions",
        "",
        "1. Create a clean public repository or release branch.",
        "2. Add a software licence after institutional approval.",
        "3. Add a README with setup, `py` launcher usage, expected input locations and `run_m0_m2_checks.ps1` instructions.",
        "4. Archive a release in Zenodo, Figshare, OSF or an institutional repository to obtain a DOI.",
        "5. Remove or parameterize local absolute paths before public release.",
        "6. Add checksums or manifest hashes for critical input and output files where appropriate.",
        "",
        "## Boundary",
        "",
        "The current code availability statement covers M0-M2 artifacts only. It does not cover future final figures, real blind external validation, full Res-SAM model replication or any GPU training environment that has not yet been frozen.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_reporting_summary(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Reporting Summary Checklist Skeleton 2026-08-10",
        "",
        "Purpose: identify Nature-style reporting fields that must be resolved before submission.",
        "",
        "| item | current status | evidence | missing before submission | risk |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['item']} | {row['current_status']} | {row['evidence']} | {row['missing_before_submission']} | {row['risk']} |"
        )
    lines.extend(
        [
            "",
            "## Blocking Items",
            "",
            "1. Data Availability is not submission-ready because no persistent repository identifier exists.",
            "2. Code Availability is not submission-ready because no public release DOI exists.",
            "3. Blinding is protocol-ready only; no real blind external validation asset has passed strict-SHA intake.",
            "4. Final figure files and source-data panel mapping are not complete.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data_inventory = build_data_inventory()
    reporting_rows = build_reporting_rows()
    write_csv(
        OUT_DIR / "data_repository_plan.csv",
        data_inventory,
        [
            "dataset_id",
            "dataset",
            "supports",
            "current_location",
            "access_route",
            "recommended_repository",
            "identifier_status",
            "restriction_or_note",
        ],
    )
    write_csv(
        OUT_DIR / "reporting_summary_checklist.csv",
        reporting_rows,
        ["item", "current_status", "evidence", "missing_before_submission", "risk"],
    )
    write_data_availability(OUT_DIR / "data_availability_skeleton.md", data_inventory)
    write_code_availability(OUT_DIR / "code_availability_skeleton.md")
    write_reporting_summary(OUT_DIR / "reporting_summary_checklist.md", reporting_rows)
    result = {
        "run_id": "20260810_companion_artifacts_skeleton",
        "data_inventory_rows": len(data_inventory),
        "reporting_checklist_rows": len(reporting_rows),
        "blocking_items": [
            "missing data repository DOI/accession",
            "missing code repository release DOI",
            "missing reporting summary final answers",
            "missing final figures/source-data panel mapping",
            "blind external validation remains NO-GO",
        ],
        "submission_ready": False,
        "boundary": "Companion artifact skeleton only; no persistent identifiers have been created.",
    }
    (OUT_DIR / "companion_artifacts_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
