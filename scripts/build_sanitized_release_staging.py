#!/usr/bin/env python3
"""Build a sanitized release-staging preview from candidate derived artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "sanitized_release_staging_20260810"
STAGED_FILES_DIR = OUT_DIR / "files"

RELEASE_AUDIT = REPORTS / "release_readiness_audit_20260810" / "release_file_audit.csv"
PUBLIC_README = REPORTS / "release_readiness_audit_20260810" / "PUBLIC_RELEASE_README_SKELETON.md"

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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_markers(path: Path) -> tuple[list[str], list[str]]:
    if path.suffix.lower() not in {".csv", ".json", ".md", ".txt", ".ps1", ".py", ".yaml", ".yml"}:
        return [], []
    text = path.read_text(encoding="utf-8")
    local_hits = sorted({pattern.pattern for pattern in LOCAL_PATH_PATTERNS if pattern.search(text)})
    placeholder_hits = sorted({pattern.pattern for pattern in PLACEHOLDER_PATTERNS if pattern.search(text)})
    return local_hits, placeholder_hits


def stage_rel_path(source_rel_path: str) -> Path:
    return STAGED_FILES_DIR / source_rel_path


def build_staging() -> list[dict[str, object]]:
    STAGED_FILES_DIR.mkdir(parents=True, exist_ok=True)
    audit_rows = read_csv(RELEASE_AUDIT)
    staged_rows: list[dict[str, object]] = []
    for row in audit_rows:
        if row["release_status"] != "candidate_after_licence":
            continue
        source_rel = row["relative_path"]
        source_path = BENCH_ROOT / source_rel
        target_path = stage_rel_path(source_rel)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        local_hits, placeholder_hits = scan_markers(target_path)
        staged_rows.append(
            {
                "source_relative_path": source_rel,
                "staged_relative_path": target_path.relative_to(OUT_DIR).as_posix(),
                "category": row["category"],
                "size_bytes": target_path.stat().st_size,
                "sha256": sha256_file(target_path),
                "local_path_markers_after_staging": "; ".join(local_hits),
                "placeholder_markers_after_staging": "; ".join(placeholder_hits),
                "staging_status": "candidate_after_licence" if not local_hits and not placeholder_hits else "needs_review",
            }
        )
    return staged_rows


def write_staging_readme(path: Path, staged_rows: list[dict[str, object]]) -> None:
    categories = sorted({str(row["category"]) for row in staged_rows})
    lines = [
        "# Sanitized Release Staging Preview 2026-08-10",
        "",
        "This directory is a local preview of derived artifacts that passed the release-readiness audit's `candidate_after_licence` filter.",
        "",
        "It is not a public release. It has no DOI, no selected licence and no verified third-party rights record.",
        "",
        "## Scope",
        "",
        f"- Staged files: {len(staged_rows)}",
        f"- Categories: {', '.join(categories)}",
        "- Excluded by design: unified sample manifests, protocols, files containing local path markers, files containing repository/DOI placeholders and third-party raw data.",
        "",
        "## Files",
        "",
        "See `sanitized_release_manifest.csv` for staged paths, SHA256 checksums and marker scan results.",
        "",
        "## Required Before Public Release",
        "",
        "1. Choose and apply a licence after institutional review.",
        "2. Create public repository metadata and DOI/accession.",
        "3. Verify third-party data rights and official citations.",
        "4. Add final rendered figures and panel-level source-data mapping.",
        "5. Re-run `run_m0_m2_checks.ps1` after any source-data change.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    staged_rows = build_staging()
    shutil.copy2(PUBLIC_README, OUT_DIR / "PUBLIC_RELEASE_README_SKELETON.md")
    write_csv(
        OUT_DIR / "sanitized_release_manifest.csv",
        staged_rows,
        [
            "source_relative_path",
            "staged_relative_path",
            "category",
            "size_bytes",
            "sha256",
            "local_path_markers_after_staging",
            "placeholder_markers_after_staging",
            "staging_status",
        ],
    )
    write_staging_readme(OUT_DIR / "SANITIZED_RELEASE_README.md", staged_rows)
    result = {
        "run_id": "20260810_sanitized_release_staging",
        "staged_files": len(staged_rows),
        "files_with_local_path_markers_after_staging": sum(
            1 for row in staged_rows if row["local_path_markers_after_staging"]
        ),
        "files_with_placeholder_markers_after_staging": sum(
            1 for row in staged_rows if row["placeholder_markers_after_staging"]
        ),
        "staging_ready_after_licence": all(row["staging_status"] == "candidate_after_licence" for row in staged_rows),
        "public_release_ready": False,
        "boundary": "Sanitized staging preview only; licence, DOI, final figures and third-party rights review are still missing.",
    }
    (OUT_DIR / "sanitized_release_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
