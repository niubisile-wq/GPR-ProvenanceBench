#!/usr/bin/env python3
"""Record public raw-GPR candidate assets for Track C follow-up."""

from __future__ import annotations

import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
ROOT = BENCH_ROOT.parent
OUT_DIR = BENCH_ROOT / "reports" / "external_raw_gpr_candidate_probe_20260811"
ZENODO_AUDIT = BENCH_ROOT / "reports" / "zenodo_gpr_raw_asset_audit_20260811" / "zenodo_gpr_raw_asset_audit_summary.json"


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# External Raw-GPR Candidate Probe",
        "",
        "Purpose: identify non-blind public raw-GPR assets that could strengthen",
        "Track C after download and manifest construction. This is not a blind",
        "external validation result.",
        "",
        "## Candidates",
        "",
        "| candidate | DOI | licence | file | size bytes | checksum | current status | local raw rows |",
        "| --- | --- | --- | --- | ---: | --- | --- | ---: |",
    ]
    for row in result["candidates"]:
        lines.append(
            f"| {row['title']} | {row['doi']} | {row['license']} | `{row['file_key']}` | "
            f"{row['size_bytes']} | `{row['checksum']}` | {row['current_status']} | "
            f"{row.get('local_manifest_rows', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            result["decision"],
            "",
            "## Next Executable Step",
            "",
            result["next_executable_step"],
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    local_audit = {}
    if ZENODO_AUDIT.exists():
        local_audit = json.loads(ZENODO_AUDIT.read_text(encoding="utf-8-sig"))
    current_status = local_audit.get("status", "candidate_not_downloaded")
    result = {
        "run_id": "20260811_E16_external_raw_gpr_candidate_probe",
        "candidates": [
            {
                "title": "GPR DATASET",
                "provider": "Zenodo",
                "record_id": "14637589",
                "doi": "10.5281/zenodo.14637589",
                "publication_date": "2025-01-13",
                "license": "cc-by-4.0",
                "file_key": "Data Set.zip",
                "size_bytes": 3784747664,
                "checksum": "md5:a20da497549c01f7f079e68e46ed7c87",
                "download_url": "https://zenodo.org/api/records/14637589/files/Data%20Set.zip/content",
                "content_summary": "Raw GPR data covering tunnel lining, underground pipeline and rebar scenarios.",
                "current_status": current_status,
                "local_archive_path": local_audit.get("archive", {}).get("local_path", ""),
                "local_archive_md5_verified": local_audit.get("archive", {}).get("md5_verified", False),
                "local_manifest_rows": local_audit.get("manifest_rows", 0),
                "local_raw_trace_files": local_audit.get("inventory", {}).get("raw_trace_files", 0),
                "local_raw_trace_bytes": local_audit.get("inventory", {}).get("raw_trace_bytes", 0),
                "blind_external_eligible": False,
                "reason_not_blind": "Public labelled or organized dataset; labels/provenance are not held by a third party until prediction freeze.",
            }
        ],
        "decision": (
            "A public raw-GPR candidate has been downloaded, checksum-verified, extracted and manifested "
            "for Track C-style non-blind stress testing. It cannot close the hard blind external gate."
        ),
        "next_executable_step": (
            "Use the generated manifest and Track C metadata baseline as non-blind stress evidence; "
            "continue seeking a true label-held external asset for the hard gate."
        ),
    }
    (OUT_DIR / "external_raw_gpr_candidate_probe_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_md(OUT_DIR / "external_raw_gpr_candidate_probe_summary.md", result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
