#!/usr/bin/env python3
"""Audit release-readiness risks for a future public code/data repository."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "release_readiness_audit_20260810"

SOURCE_MANIFEST = REPORTS / "source_data_deposit_package_20260810" / "source_data_file_manifest.csv"

TEXT_EXTENSIONS = {".csv", ".json", ".md", ".txt", ".ps1", ".py", ".yaml", ".yml"}
LOCAL_PATH_PATTERNS = [
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"D:/"),
    re.compile(r"C:/Users/"),
    re.compile(r"百度网盘"),
    re.compile(r"刘子轩"),
]
PLACEHOLDER_PATTERNS = [
    re.compile(r"\[[A-Z0-9_ /.-]+\]"),
    re.compile(r"\bDOI/accession\b"),
    re.compile(r"\bREPOSITORY\b"),
    re.compile(r"\bCODE_REPOSITORY_URL\b"),
    re.compile(r"\bZENODO_OR_OTHER_ARCHIVE_DOI\b"),
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


def scan_text(path: Path) -> tuple[list[str], list[str]]:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return [], []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ["non_utf8_text"], []
    local_hits = sorted({pattern.pattern for pattern in LOCAL_PATH_PATTERNS if pattern.search(text)})
    placeholder_hits = sorted({pattern.pattern for pattern in PLACEHOLDER_PATTERNS if pattern.search(text)})
    return local_hits, placeholder_hits


def build_audit_rows() -> list[dict[str, object]]:
    manifest_rows = read_csv(SOURCE_MANIFEST)
    rows: list[dict[str, object]] = []
    for row in manifest_rows:
        rel_path = row["relative_path"]
        path = BENCH_ROOT / rel_path
        local_hits, placeholder_hits = scan_text(path)
        category = row["category"]
        rights_status = (
            "third_party_rights_review_required"
            if category in {"sample_manifest", "protocol"}
            else "derived_artifact_review_required"
        )
        release_status = "needs_review"
        if not local_hits and not placeholder_hits and category not in {"sample_manifest", "protocol"}:
            release_status = "candidate_after_licence"
        rows.append(
            {
                "relative_path": rel_path,
                "category": category,
                "size_bytes": row["size_bytes"],
                "sha256": row["sha256"],
                "local_path_markers": "; ".join(local_hits),
                "placeholder_markers": "; ".join(placeholder_hits),
                "rights_status": rights_status,
                "release_status": release_status,
                "required_action": action_for(category, local_hits, placeholder_hits),
            }
        )
    return rows


def action_for(category: str, local_hits: list[str], placeholder_hits: list[str]) -> str:
    actions: list[str] = []
    if local_hits:
        actions.append("sanitize local paths or replace with repository-relative paths")
    if placeholder_hits:
        actions.append("resolve placeholders after repository DOI/licence decisions")
    if category == "sample_manifest":
        actions.append("verify third-party dataset licence and remove nonredistributable raw-file paths if needed")
    if category == "protocol":
        actions.append("verify protocols do not include restricted data owner details")
    if not actions:
        actions.append("review licence and include in release manifest")
    return "; ".join(actions)


def build_rights_checklist() -> list[dict[str, str]]:
    return [
        {
            "item": "Derived source-data CSV/JSON/Markdown files",
            "current_status": "candidate_after_review",
            "required_action": "Assign repository licence and verify no local absolute paths remain.",
            "release_blocker": "licence_missing",
        },
        {
            "item": "Unified sample manifests",
            "current_status": "needs_review",
            "required_action": "Sanitize local paths and verify each third-party dataset permits redistribution of derived metadata.",
            "release_blocker": "third_party_rights_and_path_sanitization",
        },
        {
            "item": "Code and scripts",
            "current_status": "local_only",
            "required_action": "Create public repository, add software licence, release tag and archive DOI.",
            "release_blocker": "code_release_missing",
        },
        {
            "item": "Third-party raw GPR files",
            "current_status": "not_in_release",
            "required_action": "Do not redistribute unless original licences permit; cite providers instead.",
            "release_blocker": "licence_verification_required",
        },
        {
            "item": "Final rendered figures",
            "current_status": "not_created",
            "required_action": "Render after plotting backend is selected and add panel-level source-data mapping.",
            "release_blocker": "final_figures_missing",
        },
        {
            "item": "Repository metadata",
            "current_status": "missing",
            "required_action": "Create DOI/accession, title, creators, description, keywords, version, licence and related identifiers.",
            "release_blocker": "repository_record_missing",
        },
    ]


def write_readme(path: Path, audit_rows: list[dict[str, object]], rights_rows: list[dict[str, str]]) -> None:
    local_path_count = sum(1 for row in audit_rows if row["local_path_markers"])
    placeholder_count = sum(1 for row in audit_rows if row["placeholder_markers"])
    candidate_count = sum(1 for row in audit_rows if row["release_status"] == "candidate_after_licence")
    lines = [
        "# Release Readiness Audit 2026-08-10",
        "",
        "Purpose: identify what must be cleaned before a public code/data release. This audit does not create a DOI, repository, licence or public deposit.",
        "",
        "## Summary",
        "",
        f"- Files audited: {len(audit_rows)}",
        f"- Candidate files after licence review: {candidate_count}",
        f"- Files with local path markers: {local_path_count}",
        f"- Files with unresolved placeholders: {placeholder_count}",
        f"- Rights checklist rows: {len(rights_rows)}",
        "",
        "## Blocking Release Items",
        "",
        "1. Repository DOI/accession is missing.",
        "2. Code release DOI and software licence are missing.",
        "3. Third-party dataset rights and redistribution conditions are not verified.",
        "4. Some files may contain local paths or submission placeholders that must be resolved before public release.",
        "5. Final rendered figures and panel-level source-data mapping are missing.",
        "",
        "## Files",
        "",
        "1. `release_file_audit.csv`: per-file local-path, placeholder, rights and release-status audit.",
        "2. `licence_and_rights_checklist.csv`: non-file release blockers and required actions.",
        "3. `PUBLIC_RELEASE_README_SKELETON.md`: repository README draft for future public release.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_public_readme(path: Path) -> None:
    lines = [
        "# GPR-ProvenanceBench",
        "",
        "This repository will contain the code, derived source data and reproducibility metadata for a provenance-aware evaluation of ground-penetrating radar recognition.",
        "",
        "## Status",
        "",
        "This is a release skeleton. A public DOI, final licence, final rendered figures and verified third-party data citations are still pending.",
        "",
        "## Reproducing Current M0-M2 Artifacts",
        "",
        "```powershell",
        "& .\\scripts\\run_m0_m2_checks.ps1",
        "```",
        "",
        "Use the Python launcher `py` on Windows. Current checked environment metadata are stored under `environment/`.",
        "",
        "## Data",
        "",
        "Derived manifests, source-data tables and report artifacts are planned for public deposition. Third-party raw GPR datasets are not redistributed unless their original licences permit redistribution.",
        "",
        "## Source Data",
        "",
        "The source-data deposit package should include `source_data_file_manifest.csv`, `figure_table_source_mapping.csv`, `SOURCE_DATA_README.md` and SHA256 checksums.",
        "",
        "## Licence",
        "",
        "[LICENCE PENDING: choose after institutional and third-party rights review].",
        "",
        "## Citation",
        "",
        "[CITATION PENDING: add repository DOI/accession after release].",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audit_rows = build_audit_rows()
    rights_rows = build_rights_checklist()
    write_csv(
        OUT_DIR / "release_file_audit.csv",
        audit_rows,
        [
            "relative_path",
            "category",
            "size_bytes",
            "sha256",
            "local_path_markers",
            "placeholder_markers",
            "rights_status",
            "release_status",
            "required_action",
        ],
    )
    write_csv(
        OUT_DIR / "licence_and_rights_checklist.csv",
        rights_rows,
        ["item", "current_status", "required_action", "release_blocker"],
    )
    write_readme(OUT_DIR / "RELEASE_READINESS_README.md", audit_rows, rights_rows)
    write_public_readme(OUT_DIR / "PUBLIC_RELEASE_README_SKELETON.md")
    result = {
        "run_id": "20260810_release_readiness_audit",
        "files_audited": len(audit_rows),
        "files_with_local_path_markers": sum(1 for row in audit_rows if row["local_path_markers"]),
        "files_with_placeholder_markers": sum(1 for row in audit_rows if row["placeholder_markers"]),
        "candidate_files_after_licence_review": sum(
            1 for row in audit_rows if row["release_status"] == "candidate_after_licence"
        ),
        "rights_rows": len(rights_rows),
        "release_ready": False,
        "boundary": "Release readiness audit only; public repository, DOI, licence and third-party rights verification are still missing.",
    }
    (OUT_DIR / "release_readiness_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
