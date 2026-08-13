#!/usr/bin/env python3
"""Evaluate one lightweight baseline over the unified split manifests."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "unified_split_baseline_20260811"
DATASETS = {
    "mojahid": BENCH_ROOT / "data_manifests" / "mojahid_unified_samples_20260810.csv",
    "tigpr": BENCH_ROOT / "data_manifests" / "tigpr_unified_samples_20260810.csv",
    "zenodo_14637589": BENCH_ROOT / "data_manifests" / "zenodo_gpr_14637589_raw_manifest_20260811.csv",
    "deepmask_gpr": BENCH_ROOT / "data_manifests" / "deepmask_gpr_unified_samples_20260811.csv",
}
PROTOCOLS = [
    "random_stratified_70_15_15",
    "existing_fold_p2",
    "source_group_holdout_70_15_15",
    "provenance_size_holdout_p4",
    "datasail_like_group_balance",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_gray(path: Path, size: int = 64) -> np.ndarray:
    with Image.open(path) as image:
        image.load()
        arr = np.asarray(
            image.convert("L").resize((size, size), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
    return arr / 255.0


def simple_hog(image: np.ndarray, cell_size: int = 8, bins: int = 9) -> np.ndarray:
    gy, gx = np.gradient(image)
    magnitude = np.sqrt(gx * gx + gy * gy)
    orientation = np.mod((np.arctan2(gy, gx) + np.pi) * (180.0 / np.pi), 180.0)
    bin_idx = np.minimum((orientation / (180.0 / bins)).astype(np.int32), bins - 1)
    cells_y = image.shape[0] // cell_size
    cells_x = image.shape[1] // cell_size
    features: list[float] = []
    for cy in range(cells_y):
        for cx in range(cells_x):
            y0 = cy * cell_size
            x0 = cx * cell_size
            cell_bins = bin_idx[y0 : y0 + cell_size, x0 : x0 + cell_size].ravel()
            cell_mag = magnitude[y0 : y0 + cell_size, x0 : x0 + cell_size].ravel()
            hist = np.bincount(cell_bins, weights=cell_mag, minlength=bins).astype(np.float32)
            features.extend((hist / (float(np.linalg.norm(hist)) + 1e-8)).tolist())
    return np.asarray(features, dtype=np.float32)


def byte_signature(path: Path) -> np.ndarray:
    size = path.stat().st_size
    with path.open("rb") as handle:
        head = handle.read(4096)
        if size > 4096:
            handle.seek(max(0, size - 4096))
            tail = handle.read(4096)
        else:
            tail = b""
    data = np.frombuffer(head + tail, dtype=np.uint8)
    if data.size:
        hist = np.bincount(data, minlength=256).astype(np.float32)
        hist /= hist.sum()
        zero_ratio = float(hist[0])
        printable_ratio = float(hist[32:127].sum())
        high_byte_ratio = float(hist[128:].sum())
        nonzero = hist[hist > 0]
        entropy = float(-(nonzero * np.log2(nonzero)).sum())
    else:
        hist = np.zeros(256, dtype=np.float32)
        zero_ratio = printable_ratio = high_byte_ratio = entropy = 0.0
    return np.asarray([math.log1p(size), zero_ratio, printable_ratio, high_byte_ratio, entropy, *hist], dtype=np.float32)


def build_feature_table(dataset: str, manifest_rows: list[dict[str, str]]) -> tuple[dict[str, np.ndarray], dict[str, str]]:
    features: dict[str, np.ndarray] = {}
    labels: dict[str, str] = {}
    for row in manifest_rows:
        sample_id = row["sample_id"]
        if dataset == "zenodo_14637589":
            path = Path(row["absolute_path"])
            features[sample_id] = byte_signature(path)
        else:
            path = Path(row["abs_path"])
            features[sample_id] = simple_hog(load_gray(path))
        labels[sample_id] = row["label"]
    return features, labels


def evaluate_protocol(
    dataset: str,
    protocol: str,
    features: dict[str, np.ndarray],
    label_by_sample: dict[str, str],
) -> dict[str, object]:
    split_path = BENCH_ROOT / "splits" / dataset / f"{protocol}_split_manifest_20260811.csv"
    split_rows = read_rows(split_path)
    train_ids = [row["sample_id"] for row in split_rows if row["split_role"] == "train"]
    test_ids = [row["sample_id"] for row in split_rows if row["split_role"] == "test"]
    train_x = np.stack([features[sample_id] for sample_id in train_ids])
    test_x = np.stack([features[sample_id] for sample_id in test_ids])
    encoder = LabelEncoder()
    train_y = encoder.fit_transform([label_by_sample[sample_id] for sample_id in train_ids])
    test_y = encoder.transform([label_by_sample[sample_id] for sample_id in test_ids])
    model = make_pipeline(
        StandardScaler(),
        SGDClassifier(loss="log_loss", alpha=1e-4, max_iter=3000, tol=1e-4, class_weight="balanced", random_state=20260811),
    )
    model.fit(train_x, train_y)
    pred = model.predict(test_x)
    train_groups = {row["source_group"] for row in split_rows if row["split_role"] == "train"}
    test_groups = {row["source_group"] for row in split_rows if row["split_role"] == "test"}
    return {
        "dataset": dataset,
        "protocol": protocol,
        "model": "hog_sgd_logistic" if dataset != "zenodo_14637589" else "byte_signature_sgd_logistic",
        "train_n": len(train_ids),
        "test_n": len(test_ids),
        "train_groups": len(train_groups),
        "test_groups": len(test_groups),
        "shared_train_test_groups": len(train_groups.intersection(test_groups)),
        "test_label_counts": dict(Counter(label_by_sample[sample_id] for sample_id in test_ids)),
        "accuracy": float(accuracy_score(test_y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(test_y, pred)),
        "macro_f1": float(f1_score(test_y, pred, average="macro")),
    }


def summarize_dataset(rows: list[dict[str, object]]) -> dict[str, object]:
    by_protocol = {row["protocol"]: row for row in rows}
    random_ba = float(by_protocol["random_stratified_70_15_15"]["balanced_accuracy"])
    contrasts = {}
    for protocol, row in by_protocol.items():
        contrasts[protocol] = {
            "balanced_accuracy": row["balanced_accuracy"],
            "random_minus_protocol_balanced_accuracy": float(random_ba - float(row["balanced_accuracy"])),
            "shared_train_test_groups": row["shared_train_test_groups"],
        }
    return {
        "protocols": contrasts,
        "largest_random_minus_protocol_ba": max(
            float(item["random_minus_protocol_balanced_accuracy"]) for item in contrasts.values()
        ),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
                    for key, value in row.items()
                }
            )


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# Unified Split Baseline",
        "",
        "One lightweight baseline is evaluated over every generated split manifest.",
        "",
        "| dataset | protocol | model | test n | shared groups | balanced accuracy | random - protocol BA |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in result["runs"]:
        random_delta = result["dataset_summaries"][row["dataset"]]["protocols"][row["protocol"]][
            "random_minus_protocol_balanced_accuracy"
        ]
        lines.append(
            f"| {row['dataset']} | {row['protocol']} | {row['model']} | {row['test_n']} | "
            f"{row['shared_train_test_groups']} | {row['balanced_accuracy']:.4f} | {random_delta:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "These are local split-protocol baselines. They quantify split sensitivity",
            "but do not create blind external validation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    runs: list[dict[str, object]] = []
    for dataset, manifest_path in DATASETS.items():
        manifest_rows = read_rows(manifest_path)
        features, labels = build_feature_table(dataset, manifest_rows)
        for protocol in PROTOCOLS:
            runs.append(evaluate_protocol(dataset, protocol, features, labels))
    dataset_summaries = {
        dataset: summarize_dataset([row for row in runs if row["dataset"] == dataset])
        for dataset in DATASETS
    }
    result = {
        "run_id": "20260811_E23_unified_split_baseline",
        "datasets": list(DATASETS),
        "protocols": PROTOCOLS,
        "runs": runs,
        "dataset_summaries": dataset_summaries,
        "blind_external_eligible": False,
        "status": "complete_local_unified_split_baseline",
    }
    (OUT_DIR / "unified_split_baseline_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(OUT_DIR / "unified_split_baseline_runs.csv", runs)
    write_md(OUT_DIR / "unified_split_baseline_summary.md", result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
