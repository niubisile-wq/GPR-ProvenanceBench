#!/usr/bin/env python3
"""Audit model-ranking sensitivity across unified split manifests."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

from run_unified_split_baseline_20260811 import (
    BENCH_ROOT,
    DATASETS,
    PROTOCOLS,
    build_feature_table,
    read_rows,
)


OUT_DIR = BENCH_ROOT / "reports" / "unified_split_model_ranking_audit_20260811"
MODEL_NAMES = ["sgd_logistic", "extra_trees"]


def make_model(name: str, seed: int):
    if name == "sgd_logistic":
        return make_pipeline(
            StandardScaler(),
            SGDClassifier(
                loss="log_loss",
                alpha=1e-4,
                max_iter=3000,
                tol=1e-4,
                class_weight="balanced",
                random_state=seed,
            ),
        )
    if name == "extra_trees":
        return ExtraTreesClassifier(
            n_estimators=160,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=seed,
            n_jobs=-1,
        )
    raise ValueError(name)


def evaluate_model(
    dataset: str,
    protocol: str,
    model_name: str,
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
    model = make_model(model_name, 20260811)
    model.fit(train_x, train_y)
    pred = model.predict(test_x)
    train_groups = {row["source_group"] for row in split_rows if row["split_role"] == "train"}
    test_groups = {row["source_group"] for row in split_rows if row["split_role"] == "test"}
    feature_family = "hog" if dataset != "zenodo_14637589" else "byte_signature"
    return {
        "dataset": dataset,
        "protocol": protocol,
        "model": model_name,
        "feature_family": feature_family,
        "train_n": len(train_ids),
        "test_n": len(test_ids),
        "shared_train_test_groups": len(train_groups.intersection(test_groups)),
        "test_label_counts": dict(Counter(label_by_sample[sample_id] for sample_id in test_ids)),
        "accuracy": float(accuracy_score(test_y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(test_y, pred)),
        "macro_f1": float(f1_score(test_y, pred, average="macro")),
    }


def rank_models(rows: list[dict[str, object]]) -> list[str]:
    return [
        row["model"]
        for row in sorted(
            rows,
            key=lambda row: (float(row["balanced_accuracy"]), float(row["macro_f1"]), row["model"]),
            reverse=True,
        )
    ]


def ranking_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    summary: dict[str, object] = {}
    for dataset in DATASETS:
        dataset_rows = [row for row in rows if row["dataset"] == dataset]
        random_rank = rank_models([row for row in dataset_rows if row["protocol"] == "random_stratified_70_15_15"])
        protocol_rows = {}
        for protocol in PROTOCOLS:
            current = [row for row in dataset_rows if row["protocol"] == protocol]
            rank = rank_models(current)
            protocol_rows[protocol] = {
                "rank": rank,
                "top_model": rank[0],
                "random_top_model": random_rank[0],
                "top_model_flip_vs_random": rank[0] != random_rank[0],
                "balanced_accuracy_by_model": {
                    row["model"]: row["balanced_accuracy"]
                    for row in current
                },
            }
        summary[dataset] = {
            "random_rank": random_rank,
            "protocols": protocol_rows,
            "top_model_flip_count_vs_random": sum(
                1
                for protocol, item in protocol_rows.items()
                if protocol != "random_stratified_70_15_15" and item["top_model_flip_vs_random"]
            ),
        }
    return summary


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
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
        "# Unified Split Model-Ranking Audit",
        "",
        "Two lightweight model families are evaluated on every unified split.",
        "",
        "| dataset | protocol | top model | random top | flip vs random | SGD BA | ExtraTrees BA |",
        "| --- | --- | --- | --- | --- | ---: | ---: |",
    ]
    for dataset, item in result["dataset_summaries"].items():
        for protocol, protocol_item in item["protocols"].items():
            ba = protocol_item["balanced_accuracy_by_model"]
            lines.append(
                f"| {dataset} | {protocol} | {protocol_item['top_model']} | "
                f"{protocol_item['random_top_model']} | {protocol_item['top_model_flip_vs_random']} | "
                f"{ba['sgd_logistic']:.4f} | {ba['extra_trees']:.4f} |"
            )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a local model-ranking sensitivity audit. It does not replace the",
            "larger five-model synthesis or blind external validation.",
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
            for model_name in MODEL_NAMES:
                runs.append(evaluate_model(dataset, protocol, model_name, features, labels))
    result = {
        "run_id": "20260811_E24_unified_split_model_ranking_audit",
        "datasets": list(DATASETS),
        "protocols": PROTOCOLS,
        "models": MODEL_NAMES,
        "runs": runs,
        "dataset_summaries": ranking_summary(runs),
        "blind_external_eligible": False,
        "status": "complete_local_unified_split_model_ranking_audit",
    }
    (OUT_DIR / "unified_split_model_ranking_audit_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(OUT_DIR / "unified_split_model_ranking_audit_runs.csv", runs)
    write_md(OUT_DIR / "unified_split_model_ranking_audit_summary.md", result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
