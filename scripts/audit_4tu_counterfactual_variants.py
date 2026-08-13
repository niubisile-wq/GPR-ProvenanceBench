#!/usr/bin/env python3
"""Render and quantify 4TU counterfactual variants for frozen package rows."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image


VARIANT_ORDER = [
    "original",
    "log_clip",
    "zscore_clip",
    "amplitude_jitter",
    "remove_top_band",
    "remove_bottom_band",
    "remove_border",
    "time_reverse",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_matrix(path: Path) -> np.ndarray:
    return np.asarray(np.load(path), dtype=np.float32)


def normalize(array: np.ndarray) -> np.ndarray:
    arr = np.asarray(array, dtype=np.float32)
    finite = np.isfinite(arr)
    if not np.any(finite):
        return np.zeros_like(arr, dtype=np.float32)
    clean = arr.copy()
    clean[~finite] = 0.0
    minimum = float(np.min(clean))
    maximum = float(np.max(clean))
    if maximum <= minimum:
        return np.zeros_like(clean, dtype=np.float32)
    return (clean - minimum) / (maximum - minimum)


def variant(array: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(array, dtype=np.float32)
    if name == "original":
        return arr.copy()
    if name == "log_clip":
        return np.sign(arr) * np.log1p(np.abs(arr))
    if name == "zscore_clip":
        std = float(np.std(arr))
        if std <= 1e-8:
            return np.zeros_like(arr, dtype=np.float32)
        return np.clip((arr - float(np.mean(arr))) / std, -3.0, 3.0)
    if name == "amplitude_jitter":
        offset = float(np.median(arr))
        return (arr - offset) * 0.85 + offset
    if name == "remove_top_band":
        out = arr.copy()
        rows = min(24, max(1, out.shape[0] // 10))
        out[:rows, :] = np.median(out[rows : rows * 2, :], axis=0, keepdims=True)
        return out
    if name == "remove_bottom_band":
        out = arr.copy()
        rows = min(24, max(1, out.shape[0] // 10))
        out[-rows:, :] = np.median(out[-rows * 2 : -rows, :], axis=0, keepdims=True)
        return out
    if name == "remove_border":
        out = arr.copy()
        border = min(24, max(1, min(out.shape) // 10))
        if out.shape[0] <= border * 2 or out.shape[1] <= border * 2:
            return out
        fill = float(np.median(out[border:-border, border:-border]))
        out[:border, :] = fill
        out[-border:, :] = fill
        out[:, :border] = fill
        out[:, -border:] = fill
        return out
    if name == "time_reverse":
        return arr[::-1, :]
    raise ValueError(f"unknown variant: {name}")


def to_png(array: np.ndarray, path: Path) -> None:
    img = Image.fromarray(np.uint8(np.clip(normalize(array) * 255.0, 0, 255)), mode="L").convert("RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def region_metrics(base: np.ndarray, changed: np.ndarray) -> dict[str, float]:
    base_n = normalize(base)
    changed_n = normalize(changed)
    delta = np.abs(base_n - changed_n)
    h, w = delta.shape
    band = min(24, max(1, h // 10))
    border = min(24, max(1, min(h, w) // 10))
    center = delta[border : h - border, border : w - border]
    if center.size == 0:
        center = delta
    if np.std(base_n) <= 1e-12 or np.std(changed_n) <= 1e-12:
        corr = 0.0
    else:
        corr = float(np.corrcoef(base_n.ravel(), changed_n.ravel())[0, 1])
    return {
        "pearson_r": corr,
        "mae": float(delta.mean()),
        "rmse": float(np.sqrt(np.mean((base_n - changed_n) ** 2))),
        "top_band_mae": float(delta[:band, :].mean()),
        "bottom_band_mae": float(delta[-band:, :].mean()),
        "border_mae": float(
            np.concatenate(
                [
                    delta[:border, :].ravel(),
                    delta[-border:, :].ravel(),
                    delta[:, :border].ravel(),
                    delta[:, -border:].ravel(),
                ]
            ).mean()
        ),
        "center_mae": float(center.mean()),
    }


def select_rows(rows: list[dict[str, str]], per_split: int) -> list[dict[str, str]]:
    by_split: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_split[row["split_role"]].append(row)
    selected: list[dict[str, str]] = []
    for split in ("train", "val", "test"):
        selected.extend(by_split.get(split, [])[:per_split])
    return selected


def sample_tag(row: dict[str, str]) -> str:
    return f"{row['split_role']}__{row['project_id']}__{row['activity_id']}__{Path(row['member']).stem}".replace(".", "_")


def write_md(path: Path, result: dict) -> None:
    lines = [
        "# 4TU Counterfactual Variant Audit 2026-08-10",
        "",
        f"Samples: {result['n_samples']}",
        f"Variants: {', '.join(result['variants'])}",
        "",
        "## Aggregate Metrics",
        "",
        "| variant | pearson_r_mean | mae_mean | rmse_mean | border_mae_mean | center_mae_mean |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["aggregate"]:
        lines.append(
            f"| {row['variant']} | {row['pearson_r_mean']:.4f} | {row['mae_mean']:.4f} | "
            f"{row['rmse_mean']:.4f} | {row['border_mae_mean']:.4f} | {row['center_mae_mean']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This audit verifies deterministic counterfactual generation and",
            "measurable variant deltas on the selected frozen package rows. It is",
            "not yet a classifier-level causal reliance test.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--per-split", type=int, default=3)
    args = parser.parse_args()

    rows = select_rows(read_csv(args.package_manifest), args.per_split)
    metrics: list[dict[str, object]] = []
    for row in rows:
        tag = sample_tag(row)
        matrix = load_matrix(Path(row["package_npy_path"]))
        for name in VARIANT_ORDER:
            transformed = variant(matrix, name)
            png_path = args.output_dir / "rendered" / name / f"{tag}__{name}.png"
            to_png(transformed, png_path)
            item = {
                "sample_tag": tag,
                "split_role": row["split_role"],
                "project_id": row["project_id"],
                "activity_id": row["activity_id"],
                "member": row["member"],
                "variant": name,
                "png_path": str(png_path.relative_to(args.output_dir)).replace("\\", "/"),
                **region_metrics(matrix, transformed),
            }
            metrics.append(item)

    csv_path = args.output_dir / "counterfactual_metrics.csv"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(metrics[0].keys())
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics)

    aggregate = []
    for name in VARIANT_ORDER:
        subset = [row for row in metrics if row["variant"] == name]
        aggregate.append(
            {
                "variant": name,
                "pearson_r_mean": float(np.mean([row["pearson_r"] for row in subset])),
                "mae_mean": float(np.mean([row["mae"] for row in subset])),
                "rmse_mean": float(np.mean([row["rmse"] for row in subset])),
                "border_mae_mean": float(np.mean([row["border_mae"] for row in subset])),
                "center_mae_mean": float(np.mean([row["center_mae"] for row in subset])),
            }
        )

    result = {
        "package_manifest": args.package_manifest.name,
        "n_samples": len(rows),
        "per_split": args.per_split,
        "variants": VARIANT_ORDER,
        "aggregate": aggregate,
        "metrics_csv": csv_path.name,
    }
    json_path = args.output_dir / "counterfactual_audit_summary.json"
    md_path = args.output_dir / "counterfactual_audit_summary.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_md(md_path, result)
    print(json.dumps(result["aggregate"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
