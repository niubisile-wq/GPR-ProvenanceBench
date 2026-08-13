#!/usr/bin/env python3
"""Build repository metadata drafts for future data/code deposit."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "repository_metadata_package_20260810"
STAGING_MANIFEST = BENCH_ROOT / "reports" / "sanitized_release_staging_20260810" / "sanitized_release_manifest.csv"
RIGHTS_CHECKLIST = BENCH_ROOT / "reports" / "release_readiness_audit_20260810" / "licence_and_rights_checklist.csv"


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
    staging_rows = read_csv(STAGING_MANIFEST)
    rights_rows = read_csv(RIGHTS_CHECKLIST)
    category_counts = Counter(row["category"] for row in staging_rows)

    metadata_rows = [
        {"field": "title", "value": "GPR-ProvenanceBench: source-aware evaluation artifacts for ground-penetrating radar recognition", "status": "draft"},
        {"field": "creators", "value": "Liu, Zixuan; collaborators to be added before deposit", "status": "needs_confirmation"},
        {"field": "description", "value": "Derived manifests, source-data tables, protocol files and audit artifacts supporting a provenance-aware GPR recognition benchmark checkpoint.", "status": "draft"},
        {"field": "keywords", "value": "ground-penetrating radar; provenance-aware evaluation; environment transfer; data leakage; benchmark; source data", "status": "draft"},
        {"field": "version", "value": "2026-08-10-predeposit", "status": "draft"},
        {"field": "license", "value": "TBD; candidate permissive licence for code and CC-BY/CC0-compatible licence for derived metadata only after rights review", "status": "blocking"},
        {"field": "related_identifiers", "value": "Manuscript DOI/preprint DOI to be added after submission or preprint; data/code DOI missing", "status": "blocking"},
        {"field": "access_right", "value": "open for derived artifacts only after third-party rights review; restricted for raw third-party GPR files", "status": "blocking"},
    ]
    write_csv(OUT_DIR / "repository_metadata_fields.csv", metadata_rows, ["field", "value", "status"])

    inclusion_rows = []
    for category, count in sorted(category_counts.items()):
        inclusion_rows.append(
            {
                "category": category,
                "candidate_files": str(count),
                "release_decision": "include_after_licence_review",
                "reason": "Sanitized staging preview reports no local-path or placeholder markers for these candidate files.",
                "remaining_condition": "Licence selection and third-party rights review.",
            }
        )
    exclusion_rows = [
        {
            "category": "third_party_raw_gpr_files",
            "release_decision": "exclude_by_default",
            "reason": "Raw data redistribution requires original-provider permission.",
            "remaining_condition": "Use citations/access instructions rather than bundling raw files unless explicit rights are available.",
        },
        {
            "category": "filled_blind_label_files",
            "release_decision": "exclude_until_policy_set",
            "reason": "Blind external labels may be held, restricted, or delayed depending on data-holder agreement.",
            "remaining_condition": "Define release policy with data holder after main evaluation.",
        },
        {
            "category": "local_absolute_path_records",
            "release_decision": "exclude_or_sanitize",
            "reason": "Local machine paths are not reusable and can leak private filesystem details.",
            "remaining_condition": "Use relative paths or repository paths only.",
        },
        {
            "category": "final_rendered_figures",
            "release_decision": "include_after_creation",
            "reason": "Figures do not exist yet.",
            "remaining_condition": "Render figures, QA outputs and panel-level Source Data first.",
        },
    ]
    write_csv(OUT_DIR / "release_inclusion_plan.csv", inclusion_rows, ["category", "candidate_files", "release_decision", "reason", "remaining_condition"])
    write_csv(OUT_DIR / "release_exclusion_plan.csv", exclusion_rows, ["category", "release_decision", "reason", "remaining_condition"])

    licence_rows = [
        {
            "component": "Code/scripts",
            "candidate_licence": "MIT or BSD-3-Clause",
            "decision_status": "needs_author_confirmation",
            "risk": "Cannot archive code as reusable without an explicit software licence.",
        },
        {
            "component": "Derived source-data CSV/JSON/Markdown",
            "candidate_licence": "CC BY 4.0 or CC0 if permitted",
            "decision_status": "needs_rights_review",
            "risk": "Derived metadata may still reflect third-party data; redistribution boundaries must be checked.",
        },
        {
            "component": "Third-party raw GPR data",
            "candidate_licence": "provider licence only",
            "decision_status": "exclude_by_default",
            "risk": "Do not redistribute raw files without explicit provider permission.",
        },
        {
            "component": "Rendered figures",
            "candidate_licence": "same as article/source-data policy after journal decision",
            "decision_status": "not_created",
            "risk": "Figures cannot be deposited before rendering and panel-level source-data QA.",
        },
    ]
    write_csv(OUT_DIR / "licence_decision_matrix.csv", licence_rows, ["component", "candidate_licence", "decision_status", "risk"])

    citation_cff = """cff-version: 1.2.0
message: "If you use these derived artifacts, please cite the associated manuscript and repository DOI once available."
title: "GPR-ProvenanceBench: source-aware evaluation artifacts for ground-penetrating radar recognition"
version: "2026-08-10-predeposit"
date-released: "2026-08-10"
authors:
  - family-names: "Liu"
    given-names: "Zixuan"
keywords:
  - "ground-penetrating radar"
  - "provenance-aware evaluation"
  - "environment transfer"
  - "data leakage"
  - "benchmark"
license: "TBD"
repository-code: "TBD"
doi: "TBD"
"""
    (OUT_DIR / "CITATION.cff.draft").write_text(citation_cff, encoding="utf-8")

    zenodo_json = {
        "title": "GPR-ProvenanceBench: source-aware evaluation artifacts for ground-penetrating radar recognition",
        "upload_type": "dataset",
        "description": "Derived manifests, source-data tables, protocol files and audit artifacts for a provenance-aware GPR recognition benchmark checkpoint. Raw third-party GPR data are not redistributed in this draft package.",
        "creators": [{"name": "Liu, Zixuan", "affiliation": "TBD", "orcid": "TBD"}],
        "keywords": ["ground-penetrating radar", "provenance-aware evaluation", "environment transfer", "data leakage", "benchmark"],
        "license": "TBD",
        "version": "2026-08-10-predeposit",
        "access_right": "open-after-rights-review",
        "related_identifiers": [],
        "notes": "Draft metadata only. Repository DOI/accession, code DOI, final figures, licence and third-party rights remain unresolved.",
    }
    (OUT_DIR / "zenodo_metadata_draft.json").write_text(json.dumps(zenodo_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    data_availability = """# Data Availability update draft

Draft only. Do not paste into a manuscript until repository identifiers, rights review and figure-source locking are complete.

For this checkpoint, the derived source-data tables, manifests, protocol files and audit artifacts are prepared for repository deposition and can be cited through the associated checkpoint package. Raw third-party GPR files are not redistributed by the authors and should be obtained from their original providers under the applicable provider licences. Final figure Source Data and any blind external validation asset remain gated until the corresponding file-level locks and permissions are complete.

Current missing items: data repository DOI/accession, final figure Source Data, final licence decision, third-party redistribution clearance and real blind external validation asset.
"""
    (OUT_DIR / "data_availability_update_draft.md").write_text(data_availability, encoding="utf-8")

    code_availability = """# Code Availability update draft

Draft only. Do not paste into a manuscript until a public code repository, release tag, software licence and archival DOI exist.

For this checkpoint, the analysis scripts, manifest builders, validation scripts and figure-generation code are locally auditable and can be regenerated from the dated checkpoint artifacts. The code package is not yet publicly released; a public repository URL, release tag, archive DOI and final software licence remain unresolved.

Current missing items: public repository URL, release tag, archive DOI and software licence.
"""
    (OUT_DIR / "code_availability_update_draft.md").write_text(code_availability, encoding="utf-8")

    readme = [
        "# Repository metadata package 2026-08-10",
        "",
        "This package prepares repository metadata and release decisions before DOI creation. It does not create a repository or DOI.",
        "",
        "## Candidate release inventory",
        "",
        f"- Sanitized staged files: {len(staging_rows)}",
        f"- Categories: {len(category_counts)}",
        "",
        "## Remaining blockers",
        "",
        "1. Repository DOI/accession is missing.",
        "2. Code release DOI is missing.",
        "3. Licence is not selected.",
        "4. Third-party rights are not cleared.",
        "5. Final rendered figures and panel-level Source Data are missing.",
        "",
    ]
    (OUT_DIR / "REPOSITORY_METADATA_README.md").write_text("\n".join(readme), encoding="utf-8")

    summary = {
        "run_id": "20260810_repository_metadata_package",
        "sanitized_staged_files": len(staging_rows),
        "release_categories": len(category_counts),
        "metadata_fields": len(metadata_rows),
        "licence_rows": len(licence_rows),
        "rights_rows_from_audit": len(rights_rows),
        "repository_identifier_created": False,
        "code_doi_created": False,
        "package_ready_for_deposit_after_rights_review": False,
        "status": "metadata_draft_ready_no_doi",
        "boundary": "Metadata drafts and release decisions are prepared, but no public repository, DOI, licence or rights clearance has been created.",
    }
    (OUT_DIR / "repository_metadata_package_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
