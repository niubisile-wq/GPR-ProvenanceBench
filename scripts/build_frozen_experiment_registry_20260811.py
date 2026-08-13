#!/usr/bin/env python3
"""Build a machine-readable frozen registry for current experiment artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "frozen_experiment_registry_20260811"
PROGRESS_DIR = BENCH_ROOT / "reports" / "experiment_only_progress_20260811"

CORE_FREEZE_FILES = [
    "configs/master_protocol_20260810.yaml",
    "environment/python_environment_20260810.json",
    "environment/pip_freeze_20260810.txt",
    "checkpoints/checkpoint_20260810.md",
    "checkpoints/gate_status_20260810.md",
    "reports/experiment_only_progress_20260811/experiment_only_progress_summary.json",
    "reports/experiment_only_progress_20260811/experiment_only_module_scores.csv",
    "reports/experiment_only_progress_20260811/experiment_only_qa.csv",
]


def rel(path: Path) -> str:
    return path.relative_to(BENCH_ROOT).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def module_evidence_paths() -> list[str]:
    rows = read_csv(PROGRESS_DIR / "experiment_only_module_scores.csv")
    paths: list[str] = []
    for row in rows:
        for part in row["evidence"].split(";"):
            item = part.strip()
            if item:
                paths.append(item)
    return paths


def experiment_entrypoints() -> list[str]:
    return sorted(rel(path) for path in (BENCH_ROOT / "experiments").glob("*.ps1"))


def script_sources() -> list[str]:
    keep_prefixes = (
        "run_",
        "build_experiment_only_progress",
        "build_unified_split",
        "build_zenodo_gpr_raw_manifest",
        "build_external_raw_gpr_candidate_probe",
        "build_external_validation_readiness",
        "validate_external_blind_intake",
        "evaluate_external_blind_submission",
        "build_frozen_experiment_registry",
    )
    paths = []
    for path in (BENCH_ROOT / "scripts").glob("*.py"):
        if path.name.startswith(keep_prefixes):
            paths.append(rel(path))
    return sorted(paths)


def registry_row(category: str, path_text: str, required: bool = True) -> dict[str, object]:
    path = BENCH_ROOT / path_text
    exists = path.exists()
    return {
        "category": category,
        "path": path_text,
        "required": required,
        "exists": exists,
        "is_file": path.is_file() if exists else False,
        "is_dir": path.is_dir() if exists else False,
        "size_bytes": path.stat().st_size if exists and path.is_file() else "",
        "sha256": sha256_file(path) if exists and path.is_file() else "",
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = ["category", "path", "required", "exists", "is_file", "is_dir", "size_bytes", "sha256"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# Frozen Experiment Registry",
        "",
        "Machine-readable freeze registry for current experiment artifacts.",
        "",
        f"- registry rows: {result['registry_rows']}",
        f"- missing required rows: {result['missing_required_rows']}",
        f"- hashed file rows: {result['hashed_file_rows']}",
        f"- experiment entrypoints: {result['experiment_entrypoint_rows']}",
        f"- script source rows: {result['script_source_rows']}",
        f"- status: {result['status']}",
        "",
        "## Boundary",
        "",
        "This freezes reproducibility metadata for local experiment artifacts. It",
        "does not execute a real blind external validation or create missing labels.",
        "",
    ]
    if result["missing_required"]:
        lines.extend(["## Missing Required", ""])
        lines.extend(f"- {item}" for item in result["missing_required"])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for category, paths in [
        ("core_freeze_file", CORE_FREEZE_FILES),
        ("module_evidence", module_evidence_paths()),
        ("experiment_entrypoint", experiment_entrypoints()),
        ("script_source", script_sources()),
    ]:
        for path_text in paths:
            key = (category, path_text)
            if key in seen:
                continue
            seen.add(key)
            rows.append(registry_row(category, path_text))
    missing_required = [
        str(row["path"])
        for row in rows
        if row["required"] and not row["exists"]
    ]
    result = {
        "run_id": "20260811_E32_frozen_experiment_registry",
        "registry_rows": len(rows),
        "missing_required_rows": len(missing_required),
        "missing_required": missing_required,
        "hashed_file_rows": sum(1 for row in rows if row["sha256"]),
        "experiment_entrypoint_rows": sum(1 for row in rows if row["category"] == "experiment_entrypoint"),
        "script_source_rows": sum(1 for row in rows if row["category"] == "script_source"),
        "blind_external_eligible": False,
        "status": "complete_local_frozen_experiment_registry" if not missing_required else "incomplete_local_frozen_experiment_registry",
    }
    write_csv(OUT_DIR / "frozen_experiment_registry_rows.csv", rows)
    (OUT_DIR / "frozen_experiment_registry_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_md(OUT_DIR / "frozen_experiment_registry_summary.md", result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
