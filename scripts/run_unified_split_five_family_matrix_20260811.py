#!/usr/bin/env python3
"""Run a five-family local model matrix over all unified split manifests."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

from run_unified_split_baseline_20260811 import BENCH_ROOT, DATASETS, PROTOCOLS, read_rows, simple_hog


OUT_DIR = BENCH_ROOT / "reports" / "unified_split_five_family_matrix_20260811"
SEED = 20260811

IMAGE_FAMILIES = [
    "hog_sgd_logistic",
    "hog_extra_trees",
    "pixel32_sgd_logistic",
    "pixel32_extra_trees",
    "image_metadata_extra_trees",
]
RAW_FAMILIES = [
    "byte_signature_sgd_logistic",
    "byte_signature_extra_trees",
    "head_hist_sgd_logistic",
    "tail_hist_extra_trees",
    "raw_file_metadata_extra_trees",
]


def load_gray(path: Path, size: int) -> np.ndarray:
    with Image.open(path) as image:
        image.load()
        arr = np.asarray(
            image.convert("L").resize((size, size), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
    return arr / 255.0


def image_path(row: dict[str, str]) -> Path:
    path = Path(row["abs_path"])
    if path.exists():
        return path
    rel_path = row.get("rel_path", "") or row.get("rel_path_from_cns1", "")
    if rel_path:
        for root in [BENCH_ROOT, BENCH_ROOT.parents[0]]:
            fallback = root / rel_path
            if fallback.exists():
                return fallback
    raise FileNotFoundError(row["sample_id"])


def raw_path(row: dict[str, str]) -> Path:
    path = Path(row["absolute_path"])
    if path.exists():
        return path
    raise FileNotFoundError(row["sample_id"])


def byte_hist(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    if arr.size == 0:
        return np.zeros(256, dtype=np.float32)
    hist = np.bincount(arr, minlength=256).astype(np.float32)
    hist /= hist.sum()
    return hist


def raw_byte_features(path: Path) -> dict[str, np.ndarray]:
    size = path.stat().st_size
    with path.open("rb") as handle:
        head = handle.read(4096)
        if size > 4096:
            handle.seek(max(0, size - 4096))
            tail = handle.read(4096)
        else:
            tail = b""
    combined = head + tail
    hist = byte_hist(combined)
    nonzero = hist[hist > 0]
    entropy = float(-(nonzero * np.log2(nonzero)).sum()) if nonzero.size else 0.0
    file_meta = np.asarray(
        [
            math.log1p(size),
            float(hist[0]),
            float(hist[32:127].sum()),
            float(hist[128:].sum()),
            entropy,
            float(len(path.name)),
        ],
        dtype=np.float32,
    )
    return {
        "byte_signature": np.asarray([*file_meta[:5], *hist], dtype=np.float32),
        "head_hist": byte_hist(head),
        "tail_hist": byte_hist(tail),
        "raw_file_metadata": file_meta,
    }


def image_metadata(row: dict[str, str], path: Path) -> np.ndarray:
    rel_name = row.get("rel_path", "") or row.get("rel_path_from_cns1", "") or path.name
    return np.asarray(
        [
            float(row.get("width_px") or 0),
            float(row.get("height_px") or 0),
            math.log1p(path.stat().st_size),
            float(len(Path(rel_name).name)),
            1.0 if row.get("augmentation_status") == "augmented" else float(row.get("is_augmented") or 0),
        ],
        dtype=np.float32,
    )


def build_family_features(dataset: str, rows: list[dict[str, str]]) -> tuple[dict[str, np.ndarray], dict[str, int]]:
    cache_path = OUT_DIR / f"{dataset}_five_family_features.npz"
    sample_ids = [row["sample_id"] for row in rows]
    sample_index = {sample_id: idx for idx, sample_id in enumerate(sample_ids)}
    if cache_path.exists():
        cached = np.load(cache_path, allow_pickle=False)
        if cached["sample_ids"].tolist() == sample_ids:
            return {family: cached[family] for family in cached["families"].tolist()}, sample_index

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    arrays: dict[str, list[np.ndarray]] = {}
    if dataset == "zenodo_14637589":
        for family in ["byte_signature", "head_hist", "tail_hist", "raw_file_metadata"]:
            arrays[family] = []
        for row in rows:
            feats = raw_byte_features(raw_path(row))
            for family, values in feats.items():
                arrays[family].append(values)
    else:
        for family in ["hog", "pixel32", "image_metadata"]:
            arrays[family] = []
        for row in rows:
            path = image_path(row)
            image64 = load_gray(path, 64)
            arrays["hog"].append(simple_hog(image64))
            arrays["pixel32"].append(load_gray(path, 32).ravel())
            arrays["image_metadata"].append(image_metadata(row, path))

    stacked = {family: np.stack(values).astype(np.float32) for family, values in arrays.items()}
    np.savez_compressed(
        cache_path,
        sample_ids=np.asarray(sample_ids),
        families=np.asarray(list(stacked)),
        **stacked,
    )
    return stacked, sample_index


def model_for_family(family: str):
    if family.endswith("extra_trees"):
        return ExtraTreesClassifier(
            n_estimators=160,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight="balanced",
            random_state=SEED,
            n_jobs=-1,
        )
    return make_pipeline(
        StandardScaler(),
        SGDClassifier(
            loss="log_loss",
            alpha=1e-4,
            max_iter=3000,
            tol=1e-4,
            class_weight="balanced",
            random_state=SEED,
        ),
    )


def feature_key_for_family(family: str) -> str:
    if family.startswith("hog"):
        return "hog"
    if family.startswith("pixel32"):
        return "pixel32"
    if family.startswith("image_metadata"):
        return "image_metadata"
    if family.startswith("byte_signature"):
        return "byte_signature"
    if family.startswith("head_hist"):
        return "head_hist"
    if family.startswith("tail_hist"):
        return "tail_hist"
    if family.startswith("raw_file_metadata"):
        return "raw_file_metadata"
    raise ValueError(family)


def evaluate_family(
    dataset: str,
    protocol: str,
    family: str,
    features_by_family: dict[str, np.ndarray],
    sample_index: dict[str, int],
    label_by_sample: dict[str, str],
) -> dict[str, object]:
    split_rows = read_rows(BENCH_ROOT / "splits" / dataset / f"{protocol}_split_manifest_20260811.csv")
    train_ids = [row["sample_id"] for row in split_rows if row["split_role"] == "train"]
    test_ids = [row["sample_id"] for row in split_rows if row["split_role"] == "test"]
    feature_key = feature_key_for_family(family)
    train_index = np.asarray([sample_index[sample_id] for sample_id in train_ids], dtype=np.int64)
    test_index = np.asarray([sample_index[sample_id] for sample_id in test_ids], dtype=np.int64)
    train_x = features_by_family[feature_key][train_index]
    test_x = features_by_family[feature_key][test_index]
    encoder = LabelEncoder()
    train_y = encoder.fit_transform([label_by_sample[sample_id] for sample_id in train_ids])
    test_y = encoder.transform([label_by_sample[sample_id] for sample_id in test_ids])
    model = model_for_family(family)
    model.fit(train_x, train_y)
    pred = model.predict(test_x)
    train_groups = {row["source_group"] for row in split_rows if row["split_role"] == "train"}
    test_groups = {row["source_group"] for row in split_rows if row["split_role"] == "test"}
    return {
        "dataset": dataset,
        "protocol": protocol,
        "model_family": family,
        "feature_family": feature_key,
        "train_n": len(train_ids),
        "test_n": len(test_ids),
        "shared_train_test_groups": len(train_groups.intersection(test_groups)),
        "test_label_counts": dict(Counter(label_by_sample[sample_id] for sample_id in test_ids)),
        "accuracy": float(accuracy_score(test_y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(test_y, pred)),
        "macro_f1": float(f1_score(test_y, pred, average="macro")),
    }


def rank(rows: list[dict[str, object]]) -> list[str]:
    return [
        row["model_family"]
        for row in sorted(
            rows,
            key=lambda row: (float(row["balanced_accuracy"]), float(row["macro_f1"]), str(row["model_family"])),
            reverse=True,
        )
    ]


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    summary: dict[str, object] = {}
    for dataset in DATASETS:
        dataset_rows = [row for row in rows if row["dataset"] == dataset]
        random_rows = [row for row in dataset_rows if row["protocol"] == "random_stratified_70_15_15"]
        random_rank = rank(random_rows)
        random_best = random_rank[0]
        protocol_items = {}
        for protocol in PROTOCOLS:
            current = [row for row in dataset_rows if row["protocol"] == protocol]
            current_rank = rank(current)
            protocol_items[protocol] = {
                "rank": current_rank,
                "top_model": current_rank[0],
                "random_top_model": random_best,
                "top_model_flip_vs_random": current_rank[0] != random_best,
                "balanced_accuracy_by_model": {
                    row["model_family"]: row["balanced_accuracy"] for row in current
                },
            }
        summary[dataset] = {
            "random_rank": random_rank,
            "protocols": protocol_items,
            "top_model_flip_count_vs_random": sum(
                1
                for protocol, item in protocol_items.items()
                if protocol != "random_stratified_70_15_15" and item["top_model_flip_vs_random"]
            ),
        }
    return summary


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
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
        "# Unified Split Five-Family Matrix",
        "",
        "Five lightweight model/feature families are evaluated for every unified split.",
        "",
        "| dataset | protocol | top model | random top | flip vs random |",
        "| --- | --- | --- | --- | --- |",
    ]
    for dataset, item in result["dataset_summaries"].items():
        for protocol, protocol_item in item["protocols"].items():
            lines.append(
                f"| {dataset} | {protocol} | {protocol_item['top_model']} | "
                f"{protocol_item['random_top_model']} | {protocol_item['top_model_flip_vs_random']} |"
            )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a local lightweight five-family matrix. It strengthens split",
            "and model-selection sensitivity evidence, but it is not a deep-backbone",
            "replacement for ResNet/DeiT training and does not close blind external",
            "validation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    runs: list[dict[str, object]] = []
    for dataset, manifest_path in DATASETS.items():
        manifest_rows = read_rows(manifest_path)
        labels = {row["sample_id"]: row["label"] for row in manifest_rows}
        features, sample_index = build_family_features(dataset, manifest_rows)
        families = RAW_FAMILIES if dataset == "zenodo_14637589" else IMAGE_FAMILIES
        for protocol in PROTOCOLS:
            for family in families:
                runs.append(evaluate_family(dataset, protocol, family, features, sample_index, labels))
    result = {
        "run_id": "20260811_E29_unified_split_five_family_matrix",
        "datasets": list(DATASETS),
        "protocols": PROTOCOLS,
        "image_model_families": IMAGE_FAMILIES,
        "raw_model_families": RAW_FAMILIES,
        "runs": runs,
        "dataset_summaries": summarize(runs),
        "blind_external_eligible": False,
        "status": "complete_local_unified_split_five_family_matrix",
    }
    (OUT_DIR / "unified_split_five_family_matrix_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(OUT_DIR / "unified_split_five_family_matrix_runs.csv", runs)
    write_md(OUT_DIR / "unified_split_five_family_matrix_summary.md", result)
    print(
        json.dumps(
            {
                "run_id": result["run_id"],
                "status": result["status"],
                "runs": len(runs),
                "datasets": result["datasets"],
                "blind_external_eligible": result["blind_external_eligible"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
