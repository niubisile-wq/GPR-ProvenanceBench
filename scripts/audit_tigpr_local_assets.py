#!/usr/bin/env python3
"""Audit whether TIGPR is locally executable for the 2026-08-10 protocol."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = BENCH_ROOT / "reports"
DATE = "2026-08-10"

TIGPR_CLASSES = {
    "Crack",
    "Interlayer_bonding_deficiency",
    "Loose",
    "No_damage",
    "Void",
}

EXPECTED_CLASS_COUNTS = {
    "Crack": 1224,
    "Interlayer_bonding_deficiency": 2020,
    "Loose": 2100,
    "No_damage": 1520,
    "Void": 305,
}

MENDELEY_TIGPR_SHA256 = "f609c9e29cdb76f83c13d6d7f9986250842e03836b75acb567c48753d34a8c9a"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def count_csv_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def find_class_dirs() -> list[dict[str, str]]:
    found = []
    for class_name in sorted(TIGPR_CLASSES):
        for path in ROOT.rglob(class_name):
            if path.is_dir():
                found.append(
                    {
                        "class_name": class_name,
                        "path": str(path),
                        "relative_path": str(path.relative_to(ROOT)),
                    }
                )
    return found


def find_candidate_roots(class_dirs: list[dict[str, str]]) -> list[dict[str, object]]:
    parent_to_classes: dict[str, set[str]] = {}
    for item in class_dirs:
        path = Path(item["path"])
        if "res_sam_data" in path.parts:
            continue
        parent = str(path.parent)
        parent_to_classes.setdefault(parent, set()).add(item["class_name"])
    candidates = []
    for parent, classes in sorted(parent_to_classes.items()):
        candidates.append(
            {
                "path": parent,
                "relative_path": str(Path(parent).relative_to(ROOT)),
                "classes_found": sorted(classes),
                "missing_classes": sorted(TIGPR_CLASSES - classes),
                "complete": classes == TIGPR_CLASSES,
            }
        )
    return candidates


def list_archive_members(path: Path, limit: int = 60) -> list[str]:
    if not path.exists():
        return []
    seven_zip = shutil.which("7z") or r"C:\Program Files\7-Zip\7z.exe"
    if Path(seven_zip).exists():
        completed = subprocess.run(
            [seven_zip, "l", "-ba", str(path)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        members = []
        for line in completed.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 6:
                member = " ".join(parts[5:]).strip()
                if member:
                    members.append(member)
        if members:
            return members[:limit]
    try:
        completed = subprocess.run(
            ["tar", "-tf", str(path)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        return []
    members = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    return members[:limit]


def infer_archive_identity(members: list[str]) -> str:
    joined = "\n".join(members).lower()
    if "augmented_cavities" in joined or "augmented_intact" in joined:
        return "mojahid_gpr_data"
    if all(class_name.lower() in joined for class_name in TIGPR_CLASSES):
        return "possible_tigpr"
    if not members:
        return "unknown_or_unreadable"
    return "not_tigpr_by_visible_members"


def summarize_go_no_go(
    sample_rows: int | None,
    candidate_roots: list[dict[str, object]],
    archive_identity: str,
    archive_path: Path,
) -> tuple[str, list[str]]:
    blockers = []
    if sample_rows != 7169:
        blockers.append(
            f"local TIGPR sample index has {sample_rows if sample_rows is not None else 'missing'} rows, not 7169"
        )
    if not any(item["complete"] for item in candidate_roots):
        blockers.append("no local root contains the complete TIGPR five-class directory layout")
    if archive_identity != "possible_tigpr":
        blockers.append(f"available {archive_path.name} identity is {archive_identity}, not verified TIGPR")
    status = "NO-GO" if blockers else "GO"
    return status, blockers


def write_report(audit: dict) -> Path:
    path = REPORT_DIR / "tigpr_local_asset_audit_20260810.md"
    if audit["status"] == "GO":
        decision_text = (
            "TIGPR is locally executable for sample-level audit use: the restored source image tree, "
            "7169-row sample index, expected five-class layout and verified archive identity are present."
        )
        consequence = (
            "TIGPR can now be counted as a restored local sample-level asset. This does not by itself "
            "close blind external validation, because the labels and media are now available locally."
        )
    else:
        decision_text = (
            "TIGPR is currently valid only as bibliographic/prior-audit supporting evidence. It must not be counted as a core executable dataset until the source image tree is restored locally and the sample index is rebuilt to 7169 rows."
        )
        consequence = (
            "Until recovery succeeds, the M0-M2 core local asset set remains Mojahid, 4TU and Res-SAM. TIGPR remains supporting evidence only."
        )
    lines = [
        "# TIGPR Local Asset Audit 2026-08-10",
        "",
        "## Decision",
        "",
        f"Status: **{audit['status']}** for core executable asset use.",
        "",
        decision_text,
        "",
        "## Local Evidence",
        "",
        f"- Manifest path: `{audit['paths']['manifest_rel']}`; exists: `{audit['manifest_exists']}`.",
        f"- Sample index path: `{audit['paths']['sample_index_rel']}`; data rows: `{audit['sample_index_rows']}`.",
        f"- Prior provenance gate JSON: `{audit['paths']['prior_gate_rel']}`; exists: `{audit['prior_gate_exists']}`.",
        f"- Candidate archive: `{audit['paths']['candidate_archive_rel']}`; exists: `{audit['candidate_archive_exists']}`.",
        f"- Candidate archive identity: `{audit['candidate_archive_identity']}`.",
        f"- Candidate archive SHA256: `{audit['candidate_archive_sha256']}`.",
        "",
        "## Expected TIGPR Counts",
        "",
        "| Class | Expected images |",
        "| --- | ---: |",
    ]
    for class_name, count in EXPECTED_CLASS_COUNTS.items():
        lines.append(f"| {class_name} | {count} |")
    lines.extend(
        [
            f"| **Total** | **{sum(EXPECTED_CLASS_COUNTS.values())}** |",
            "",
            "## Local TIGPR Root Search",
            "",
        ]
    )
    if audit["candidate_roots"]:
        lines.extend(["| Candidate root | Classes found | Missing classes | Complete |", "| --- | --- | --- | --- |"])
        for item in audit["candidate_roots"]:
            lines.append(
                f"| `{item['relative_path']}` | {', '.join(item['classes_found'])} | {', '.join(item['missing_classes'])} | {item['complete']} |"
            )
    else:
        lines.append("No non-Res-SAM TIGPR candidate root was found under the CNS1 root.")
    if audit["non_tigpr_class_dir_hits"]:
        lines.extend(
            [
                "",
                "Non-TIGPR same-name class hits were found and intentionally excluded from GO/NO-GO logic:",
                "",
                "| Class | Relative path |",
                "| --- | --- |",
            ]
        )
        for item in audit["non_tigpr_class_dir_hits"]:
            lines.append(f"| {item['class_name']} | `{item['relative_path']}` |")
    lines.extend(
        [
            "",
            "## Prior Audit Evidence",
            "",
            f"- Prior audit image count: `{audit['prior_gate_summary'].get('n_images', '')}`.",
            f"- Prior audit exact duplicate groups: `{audit['prior_gate_summary'].get('exact_duplicate_group_count', '')}`.",
            f"- Prior audit exact duplicate images: `{audit['prior_gate_summary'].get('exact_duplicate_image_count', '')}`.",
            f"- Prior audit cross-label duplicate groups: `{audit['prior_gate_summary'].get('cross_label_exact_duplicate_group_count', '')}`.",
            f"- Prior audit geometry/filesize/JPEG provenance BA: `{audit['prior_gate_summary'].get('geometry_filesize_jpeg_quantization_balanced_accuracy', '')}`.",
            "",
            "This prior audit is useful for risk framing, but it points to a non-local historical path and cannot substitute for executable local media.",
            "",
            "## Blockers",
            "",
        ]
    )
    if audit["blockers"]:
        for blocker in audit["blockers"]:
            lines.append(f"- {blocker}.")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Required Recovery Steps",
            "",
            "1. Download TIGPR from the Mendeley dataset page with authorized access.",
            "2. Place the archive under `external_assets/tigpr/`.",
            "3. Extract to a layout equivalent to `TIGPR/Damage Classification/{Crack,Interlayer_bonding_deficiency,Loose,No_damage,Void}`.",
            "4. Rebuild `manifest/tigpr_sample_index_v1.csv` from local files.",
            "5. Verify 7169 rows, class counts, exact duplicate groups and cross-label conflicts before enabling TIGPR as a core asset.",
            "",
            "## Protocol Consequence",
            "",
            consequence,
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / "manifest" / "tigpr_manifest_v1.yaml"
    sample_index_path = ROOT / "manifest" / "tigpr_sample_index_v1.csv"
    prior_gate_path = ROOT / "gpr_leakage_research" / "tigpr_provenance_gate_v1.json"
    restored_archive_path = ROOT / "external_assets" / "tigpr" / "TIGPR.rar"
    legacy_archive_path = ROOT / "gpr_leakage_research" / "GPR_data.rar"
    archive_path = restored_archive_path if restored_archive_path.exists() else legacy_archive_path

    manifest = load_yaml(manifest_path)
    prior_gate = load_json(prior_gate_path)
    class_dirs = find_class_dirs()
    candidate_roots = find_candidate_roots(class_dirs)
    non_tigpr_hits = [item for item in class_dirs if "res_sam_data" in Path(item["path"]).parts]
    archive_members = list_archive_members(archive_path)
    archive_hash = sha256(archive_path) if archive_path.exists() else ""
    archive_identity = (
        "possible_tigpr"
        if archive_hash == MENDELEY_TIGPR_SHA256
        else infer_archive_identity(archive_members)
    )
    sample_rows = count_csv_rows(sample_index_path)
    status, blockers = summarize_go_no_go(sample_rows, candidate_roots, archive_identity, archive_path)

    prior_summary_keys = [
        "n_images",
        "exact_duplicate_group_count",
        "exact_duplicate_image_count",
        "cross_label_exact_duplicate_group_count",
        "geometry_filesize_jpeg_quantization_balanced_accuracy",
    ]
    prior_summary = {key: prior_gate.get(key, manifest.get("evidence", {}).get(key, "")) for key in prior_summary_keys}

    audit = {
        "audit": "tigpr_local_asset_audit",
        "date": DATE,
        "status": status,
        "blockers": blockers,
        "manifest_exists": manifest_path.exists(),
        "sample_index_rows": sample_rows,
        "prior_gate_exists": prior_gate_path.exists(),
        "candidate_archive_exists": archive_path.exists(),
        "candidate_archive_identity": archive_identity,
        "candidate_archive_sha256": archive_hash,
        "candidate_archive_expected_sha256": MENDELEY_TIGPR_SHA256,
        "candidate_archive_visible_members": archive_members,
        "candidate_roots": candidate_roots,
        "non_tigpr_class_dir_hits": non_tigpr_hits,
        "expected_class_counts": EXPECTED_CLASS_COUNTS,
        "prior_gate_summary": prior_summary,
        "paths": {
            "manifest": str(manifest_path),
            "manifest_rel": str(manifest_path.relative_to(ROOT)),
            "sample_index": str(sample_index_path),
            "sample_index_rel": str(sample_index_path.relative_to(ROOT)),
            "prior_gate": str(prior_gate_path),
            "prior_gate_rel": str(prior_gate_path.relative_to(ROOT)),
            "candidate_archive": str(archive_path),
            "candidate_archive_rel": str(archive_path.relative_to(ROOT)),
        },
        "protocol_consequence": "TIGPR local sample-level asset is restored; blind external validation remains a separate gate."
        if status == "GO"
        else "TIGPR remains supporting evidence only until local media are recovered and sample index has 7169 rows.",
    }

    json_path = REPORT_DIR / "tigpr_local_asset_audit_20260810.json"
    json_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path = write_report(audit)
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    print(f"status={status}")


if __name__ == "__main__":
    main()
