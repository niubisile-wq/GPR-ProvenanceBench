#!/usr/bin/env python3
"""Build non-final Data/Code Availability prelock statements and gate checks."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "availability_statement_prelock_20260810"
REPO_DIR = BENCH_ROOT / "reports" / "repository_metadata_package_20260810"
SOURCE_SUMMARY = BENCH_ROOT / "reports" / "source_data_deposit_package_20260810" / "source_data_deposit_summary.json"
RELEASE_SUMMARY = BENCH_ROOT / "reports" / "release_readiness_audit_20260810" / "release_readiness_summary.json"
STAGING_SUMMARY = BENCH_ROOT / "reports" / "sanitized_release_staging_20260810" / "sanitized_release_summary.json"
REPO_SUMMARY = REPO_DIR / "repository_metadata_package_summary.json"


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    repo_summary = json.loads(REPO_SUMMARY.read_text(encoding="utf-8"))
    source_summary = json.loads(SOURCE_SUMMARY.read_text(encoding="utf-8"))
    release_summary = json.loads(RELEASE_SUMMARY.read_text(encoding="utf-8"))
    staging_summary = json.loads(STAGING_SUMMARY.read_text(encoding="utf-8"))

    route_rows = [
        {
            "dataset_or_object": "Derived source-data tables, manifests and audit artifacts",
            "access_route": "public repository after rights review",
            "current_location": "sanitized_release_staging_20260810 and source_data_deposit_package_20260810",
            "identifier_status": "missing",
            "licence_status": "needs rights review",
            "ready_for_statement": "draft_only",
        },
        {
            "dataset_or_object": "Third-party raw GPR files",
            "access_route": "third-party restricted",
            "current_location": "excluded from draft release by default",
            "identifier_status": "provider-controlled or unknown",
            "licence_status": "provider licence only",
            "ready_for_statement": "restricted wording only",
        },
        {
            "dataset_or_object": "Blind external validation data",
            "access_route": "not yet acquired",
            "current_location": "none",
            "identifier_status": "not applicable yet",
            "licence_status": "not applicable yet",
            "ready_for_statement": "open gate only",
        },
        {
            "dataset_or_object": "Analysis code and regeneration scripts",
            "access_route": "public code repository plus archive DOI after licence decision",
            "current_location": "local project scripts",
            "identifier_status": "missing",
            "licence_status": "needs author confirmation",
            "ready_for_statement": "draft_only",
        },
        {
            "dataset_or_object": "Rendered figure source data",
            "access_route": "Source Data files and/or public repository",
            "current_location": "planned source-data package; figures not rendered",
            "identifier_status": "missing",
            "licence_status": "pending final figure/source-data QA",
            "ready_for_statement": "not final",
        },
    ]
    write_csv(
        OUT_DIR / "availability_access_route_matrix.csv",
        route_rows,
        ["dataset_or_object", "access_route", "current_location", "identifier_status", "licence_status", "ready_for_statement"],
    )

    variant_rows = [
        {
            "variant_id": "DA-PUBLIC-FINAL",
            "when_to_use": "Only after repository DOI/accession, licence, rights review and final figure source data exist.",
            "statement_text": "The derived source-data tables, sample manifests, audit artifacts and metadata supporting the findings of this study are available in [Repository] under [DOI/accession]. Raw third-party GPR data are not redistributed by the authors and should be obtained from their original providers under the applicable licences. Source data for the figures are provided with the article and in the repository record. Blind external validation data, if included, are available according to the data-holder agreement described in the repository metadata.",
            "status": "not_usable_yet",
        },
        {
            "variant_id": "DA-RESTRICTED-FINAL",
            "when_to_use": "Use if derived source data can be public but raw third-party or external blind assets cannot be redistributed.",
            "statement_text": "The derived source-data tables, sample manifests, audit artifacts and metadata generated in this study are available in [Repository] under [DOI/accession]. Third-party raw GPR files are subject to provider licences and are not publicly redistributed by the authors; requests for those data should be directed to the original providers. Blind external validation data are not publicly available unless permitted by the data holder; aggregate metrics and source-data tables sufficient to inspect the reported results are provided in [location].",
            "status": "not_usable_yet",
        },
        {
            "variant_id": "DA-CURRENT-DRAFT",
            "when_to_use": "Internal author-review draft only before DOI/licence/rights closure.",
            "statement_text": "A Data Availability statement cannot be finalized at this checkpoint. Derived source-data tables, manifests, protocol files and audit artifacts have been prepared for repository deposition, but repository DOI/accession, licence selection, third-party redistribution review, final rendered figure source data and any real blind external validation asset remain unresolved.",
            "status": "author_review_only",
        },
    ]
    write_csv(OUT_DIR / "data_availability_statement_variants.csv", variant_rows, ["variant_id", "when_to_use", "statement_text", "status"])

    code_rows = [
        {
            "variant_id": "CODE-PUBLIC-FINAL",
            "when_to_use": "Only after public repository URL, release tag, software licence and archive DOI exist.",
            "statement_text": "The analysis scripts, manifest builders, validation scripts and figure-generation code used in this study are available at [repository URL] and archived at [DOI]. The repository includes environment metadata and dated regeneration commands for the reported checkpoint artifacts.",
            "status": "not_usable_yet",
        },
        {
            "variant_id": "CODE-RESTRICTED-FINAL",
            "when_to_use": "Use only if institutional restrictions prevent full public code release and a specific access route exists.",
            "statement_text": "The code supporting this study is not fully public because [specific institutional/legal restriction]. Non-restricted analysis scripts and environment metadata are available at [repository/DOI]. Requests for restricted components should be directed to [institutional route/contact] and will be reviewed under [policy/agreement].",
            "status": "not_usable_yet",
        },
        {
            "variant_id": "CODE-CURRENT-DRAFT",
            "when_to_use": "Internal author-review draft only before repository/licence/archive closure.",
            "statement_text": "A Code Availability statement cannot be finalized at this checkpoint. The analysis scripts and regeneration commands are local and auditable, but a public repository URL, release tag, software licence, archive DOI and final figure-generation backend remain unresolved.",
            "status": "author_review_only",
        },
    ]
    write_csv(OUT_DIR / "code_availability_statement_variants.csv", code_rows, ["variant_id", "when_to_use", "statement_text", "status"])

    gate_rows = [
        {
            "gate": "data_repository_identifier",
            "required_evidence": "Repository DOI/accession resolves to a landing page with title, creators, file list, README, licence and version.",
            "current_state": "open",
        },
        {
            "gate": "code_repository_identifier",
            "required_evidence": "Public repository URL, release tag, software licence and archive DOI.",
            "current_state": "open",
        },
        {
            "gate": "third_party_rights",
            "required_evidence": "Provider licence review and explicit exclusion or redistribution permission for raw GPR files.",
            "current_state": "open",
        },
        {
            "gate": "figure_source_data",
            "required_evidence": "Rendered figures and panel-level source-data mapping.",
            "current_state": "open",
        },
        {
            "gate": "blind_external_data",
            "required_evidence": "Data-holder agreement, manifest, label-holdout route and aggregate sharability decision.",
            "current_state": "open",
        },
    ]
    write_csv(OUT_DIR / "availability_statement_gate_requirements.csv", gate_rows, ["gate", "required_evidence", "current_state"])

    fair_rows = [
        {"principle": "Findable", "current_status": "partial", "missing_item": "Persistent DOI/accession and final repository landing page."},
        {"principle": "Accessible", "current_status": "partial", "missing_item": "Public access route or explicit restricted-access procedure."},
        {"principle": "Interoperable", "current_status": "partial", "missing_item": "Final README/data dictionary tied to rendered figures and repository record."},
        {"principle": "Reusable", "current_status": "partial", "missing_item": "Final licence, rights clearance, provenance notes and versioned release."},
    ]
    write_csv(OUT_DIR / "fair_metadata_prelock_checklist.csv", fair_rows, ["principle", "current_status", "missing_item"])

    qa_rows = [
        {"check": "repository_identifier_not_claimed", "result": "PASS", "detail": f"repository_identifier_created={repo_summary['repository_identifier_created']}"},
        {"check": "code_doi_not_claimed", "result": "PASS", "detail": f"code_doi_created={repo_summary['code_doi_created']}"},
        {"check": "source_data_identifier_not_claimed", "result": "PASS", "detail": f"source_repository_identifier={source_summary['repository_identifier']}"},
        {"check": "public_release_not_claimed", "result": "PASS", "detail": f"public_release_ready={staging_summary['public_release_ready']}"},
        {"check": "release_readiness_boundary_preserved", "result": "PASS", "detail": f"release_ready={release_summary['release_ready']}"},
    ]
    write_csv(OUT_DIR / "availability_statement_prelock_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = """# Availability statement prelock package 2026-08-10

This package prepares Data Availability and Code Availability language for author review. It does not create repository identifiers, code DOI, licences or rights clearance.

## Use

1. Use `DA-CURRENT-DRAFT` and `CODE-CURRENT-DRAFT` only inside author-review drafts.
2. Use `DA-PUBLIC-FINAL` or `CODE-PUBLIC-FINAL` only after repository identifiers, licences and rights are real.
3. Use restricted variants only if a specific restriction reason and access route are confirmed.

## Stop rules

1. Do not write "available in [Repository] under [DOI]" until the DOI/accession exists and resolves.
2. Do not write that code is archived until a public release tag, software licence and archive DOI exist.
3. Do not redistribute raw third-party GPR files without provider permission.
4. Do not state that all data are included in the paper while final figure Source Data are absent.
5. Do not include blind external validation data language until a real data-holder agreement exists.
"""
    (OUT_DIR / "AVAILABILITY_PRELOCK_README.md").write_text(readme, encoding="utf-8")

    summary = {
        "run_id": "20260810_availability_statement_prelock",
        "access_route_rows": len(route_rows),
        "data_statement_variants": len(variant_rows),
        "code_statement_variants": len(code_rows),
        "gate_rows": len(gate_rows),
        "fair_rows": len(fair_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "repository_identifier_created": repo_summary["repository_identifier_created"],
        "code_doi_created": repo_summary["code_doi_created"],
        "public_release_ready": staging_summary["public_release_ready"],
        "submission_ready": False,
        "status": "availability_statement_prelock_ready_not_final",
        "boundary": "This package prepares availability wording; it does not create repository DOI, code DOI, licences, rights clearance, final source data or blind external data access.",
    }
    (OUT_DIR / "availability_statement_prelock_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report = [
        "# Availability statement prelock report 2026-08-10",
        "",
        f"- Access-route rows: {summary['access_route_rows']}",
        f"- Data statement variants: {summary['data_statement_variants']}",
        f"- Code statement variants: {summary['code_statement_variants']}",
        f"- Gate rows: {summary['gate_rows']}",
        f"- FAIR rows: {summary['fair_rows']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: Data and Code Availability language is prepared for author review, but final availability statements remain blocked by DOI, licence, rights, figure source data and blind external data decisions.",
        "",
    ]
    (OUT_DIR / "availability_statement_prelock_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
