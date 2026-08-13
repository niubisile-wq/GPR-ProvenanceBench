#!/usr/bin/env python3
"""Run multi-seed stability audit for unified split baselines."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
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


OUT_DIR = BENCH_ROOT / "reports" / "unified_split_seed_stability_20260811"
SEEDS = [20260811, 20260812, 20260813, 20260814, 20260815]


def evaluate(
    dataset: str,
    protocol: str,
    seed: int,
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
        SGDClassifier(
            loss="log_loss",
            alpha=1e-4,
            max_iter=3000,
            tol=1e-4,
            class_weight="balanced",
            random_state=seed,
        ),
    )
    model.fit(train_x, train_y)
    pred = model.predict(test_x)
    train_groups = {row["source_group"] for row in split_rows if row["split_role"] == "train"}
    test_groups = {row["source_group"] for row in split_rows if row["split_role"] == "test"}
    return {
        "dataset": dataset,
        "protocol": protocol,
        "seed": seed,
        "model": "hog_sgd_logistic" if dataset != "zenodo_14637589" else "byte_signature_sgd_logistic",
        "train_n": len(train_ids),
        "test_n": len(test_ids),
        "shared_train_test_groups": len(train_groups.intersection(test_groups)),
        "accuracy": float(accuracy_score(test_y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(test_y, pred)),
        "macro_f1": float(f1_score(test_y, pred, average="macro")),
    }


def summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def dataset_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    by_protocol = {
        protocol: [row for row in rows if row["protocol"] == protocol]
        for protocol in PROTOCOLS
    }
    random_by_seed = {
        int(row["seed"]): float(row["balanced_accuracy"])
        for row in by_protocol["random_stratified_70_15_15"]
    }
    protocol_summary = {}
    for protocol, protocol_rows in by_protocol.items():
        ba_values = [float(row["balanced_accuracy"]) for row in protocol_rows]
        deltas = [
            random_by_seed[int(row["seed"])] - float(row["balanced_accuracy"])
            for row in protocol_rows
        ]
        protocol_summary[protocol] = {
            "balanced_accuracy": summarize(ba_values),
            "random_minus_protocol_balanced_accuracy": summarize(deltas),
            "shared_train_test_groups": int(protocol_rows[0]["shared_train_test_groups"]) if protocol_rows else 0,
        }
    strict_protocols = [protocol for protocol in PROTOCOLS if protocol != "random_stratified_70_15_15"]
    largest = max(
        protocol_summary[protocol]["random_minus_protocol_balanced_accuracy"]["mean"]
        for protocol in strict_protocols
    )
    return {
        "protocols": protocol_summary,
        "largest_mean_random_minus_protocol_ba": float(largest),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# Unified Split Seed Stability",
        "",
        "Five SGD-logistic seeds are evaluated for every unified split.",
        "",
        "| dataset | protocol | BA mean | BA std | random - protocol BA mean | delta min | delta max |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for dataset, item in result["dataset_summaries"].items():
        for protocol, protocol_item in item["protocols"].items():
            ba = protocol_item["balanced_accuracy"]
            delta = protocol_item["random_minus_protocol_balanced_accuracy"]
            lines.append(
                f"| {dataset} | {protocol} | {ba['mean']:.4f} | {ba['std']:.4f} | "
                f"{delta['mean']:+.4f} | {delta['min']:+.4f} | {delta['max']:+.4f} |"
            )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is local seed stability for a lightweight baseline. It does not",
            "replace full deep-model seed sweeps or blind external validation.",
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
            for seed in SEEDS:
                runs.append(evaluate(dataset, protocol, seed, features, labels))
    summaries = {
        dataset: dataset_summary([row for row in runs if row["dataset"] == dataset])
        for dataset in DATASETS
    }
    result = {
        "run_id": "20260811_E26_unified_split_seed_stability",
        "datasets": list(DATASETS),
        "protocols": PROTOCOLS,
        "seeds": SEEDS,
        "runs": runs,
        "dataset_summaries": summaries,
        "blind_external_eligible": False,
        "status": "complete_local_unified_split_seed_stability",
    }
    (OUT_DIR / "unified_split_seed_stability_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(OUT_DIR / "unified_split_seed_stability_runs.csv", runs)
    write_md(OUT_DIR / "unified_split_seed_stability_summary.md", result)
    print(
        json.dumps(
            {
                "run_id": result["run_id"],
                "status": result["status"],
                "datasets": result["datasets"],
                "protocols": len(result["protocols"]),
                "seeds": len(result["seeds"]),
                "runs": len(result["runs"]),
                "largest_mean_random_minus_protocol_ba": {
                    dataset: summary["largest_mean_random_minus_protocol_ba"]
                    for dataset, summary in result["dataset_summaries"].items()
                },
                "blind_external_eligible": result["blind_external_eligible"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
