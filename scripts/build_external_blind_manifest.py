#!/usr/bin/env python3
"""Build an analyst-facing blind external manifest from an unlabeled file tree."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = BENCH_ROOT / "data_manifests" / "external_blind_manifest_filled_YYYYMMDD.csv"

ALLOWED_TRACKS = {
    "tigpr_restoration",
    "third_party_blind",
    "4tu_like_raw_trace",
    "other_external",
}
ALLOWED_MODALITIES = {"image", "raw_trace", "mixed"}
DEFAULT_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tif",
    ".tiff",
    ".npy",
    ".csv",
    ".txt",
}
FIELDNAMES = [
    "sample_id",
    "rel_path",
    "abs_path",
    "file_sha256",
    "label_placeholder",
    "source_group",
    "asset_track",
    "modality",
    "target_task",
    "notes",
]


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_extensions(raw: str) -> set[str]:
    extensions = set()
    for item in raw.split(","):
        suffix = item.strip().lower()
        if not suffix:
            continue
        if not suffix.startswith("."):
            suffix = "." + suffix
        extensions.add(suffix)
    return extensions


def source_group_for(path: Path, root: Path, mode: str, fixed_group: str) -> str:
    rel = path.relative_to(root)
    if mode == "fixed":
        return fixed_group
    if mode == "parent":
        return rel.parent.name if rel.parent.name else fixed_group
    if mode == "top_level":
        return rel.parts[0] if len(rel.parts) > 1 else fixed_group
    raise ValueError(f"unsupported source group mode: {mode}")


def iter_files(root: Path, extensions: set[str]) -> list[Path]:
    files = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in extensions
    ]
    return sorted(files, key=lambda item: item.relative_to(root).as_posix().lower())


def build_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    root = args.input_root.resolve()
    files = iter_files(root, args.extensions)
    rows: list[dict[str, str]] = []
    width = max(6, len(str(len(files))))
    for index, path in enumerate(files, start=1):
        rel_path = path.relative_to(root).as_posix()
        rows.append(
            {
                "sample_id": f"{args.sample_prefix}_{index:0{width}d}",
                "rel_path": rel_path,
                "abs_path": "" if args.omit_abs_path else str(path),
                "file_sha256": sha256_file(path),
                "label_placeholder": "HELD_OUT",
                "source_group": source_group_for(
                    path,
                    root,
                    args.source_group_mode,
                    args.fixed_source_group,
                ),
                "asset_track": args.asset_track,
                "modality": args.modality,
                "target_task": args.target_task,
                "notes": args.notes,
            }
        )
    return rows


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--sample-prefix", default="BLIND")
    parser.add_argument("--asset-track", choices=sorted(ALLOWED_TRACKS), required=True)
    parser.add_argument("--modality", choices=sorted(ALLOWED_MODALITIES), required=True)
    parser.add_argument("--target-task", required=True)
    parser.add_argument(
        "--source-group-mode",
        choices=["fixed", "parent", "top_level"],
        default="parent",
    )
    parser.add_argument("--fixed-source-group", default="external_group_001")
    parser.add_argument(
        "--extensions",
        type=parse_extensions,
        default=DEFAULT_EXTENSIONS,
        help="Comma-separated extensions. Default covers common image/raw-trace files.",
    )
    parser.add_argument("--notes", default="non_label_metadata_only")
    parser.add_argument("--omit-abs-path", action="store_true")
    args = parser.parse_args()

    if not args.input_root.exists():
        raise SystemExit(f"input root does not exist: {args.input_root}")
    if not args.input_root.is_dir():
        raise SystemExit(f"input root is not a directory: {args.input_root}")

    rows = build_rows(args)
    if not rows:
        raise SystemExit(
            f"no files found in {args.input_root} with extensions {sorted(args.extensions)}"
        )
    write_manifest(args.output_csv, rows)
    print(f"wrote {len(rows)} rows to {args.output_csv}")
    print("next: validate with validate_external_blind_intake.py --strict-sha")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
