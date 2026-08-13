#!/usr/bin/env python3
"""Evaluate a one-shot blind external prediction after labels are unlocked.

Default execution uses the template rows as a dry run. A real main-claim
evaluation must pass --manifest, --labels, --predictions and --main-claim.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import warnings
from collections import Counter, defaultdict
from pathlib import Path

from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score


BENCH_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = BENCH_ROOT / "data_manifests"
REPORT_DIR = BENCH_ROOT / "reports" / "external_blind_locked_evaluation_20260810"

DEFAULT_MANIFEST = DATA_DIR / "external_blind_manifest_template_20260810.csv"
DEFAULT_LABELS = DATA_DIR / "external_blind_label_holdout_template_20260810.csv"
DEFAULT_PREDICTIONS = DATA_DIR / "external_blind_prediction_submission_template_20260810.csv"

MANIFEST_COLUMNS = [
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
LABEL_COLUMNS = [
    "sample_id",
    "sealed_label",
    "label_space_version",
    "label_holder",
    "sealed_timestamp",
    "unlock_timestamp",
    "unlock_authorized_by",
]
PREDICTION_COLUMNS = [
    "sample_id",
    "predicted_label",
    "prediction_score",
    "model_family",
    "model_version",
    "preprocessing_version",
    "seed",
    "submission_id",
    "prediction_timestamp",
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def require_columns(path: Path, columns: list[str], required: list[str]) -> list[str]:
    missing = [column for column in required if column not in columns]
    extra = [column for column in columns if column not in required]
    issues: list[str] = []
    if missing:
        issues.append(f"{path.name}: missing columns: {', '.join(missing)}")
    if extra:
        issues.append(f"{path.name}: unexpected columns: {', '.join(extra)}")
    return issues


def index_by_sample_id(path: Path, rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], list[str]]:
    issues: list[str] = []
    indexed: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        sample_id = row.get("sample_id", "").strip()
        if not sample_id:
            issues.append(f"{path.name}:{row_number}: missing sample_id")
            continue
        if sample_id in indexed:
            issues.append(f"{path.name}:{row_number}: duplicate sample_id {sample_id}")
        indexed[sample_id] = row
    return indexed, issues


def parse_score(value: str) -> float | None:
    value = value.strip()
    if not value:
        return None
    try:
        score = float(value)
    except ValueError:
        return None
    if math.isnan(score) or math.isinf(score):
        return None
    return score


def validate_join(
    manifest: dict[str, dict[str, str]],
    labels: dict[str, dict[str, str]],
    predictions: dict[str, dict[str, str]],
    main_claim: bool,
) -> list[str]:
    issues: list[str] = []
    manifest_ids = set(manifest)
    label_ids = set(labels)
    prediction_ids = set(predictions)
    if manifest_ids != label_ids:
        issues.append(
            "manifest and label sample_id sets differ: "
            f"manifest_only={len(manifest_ids - label_ids)}, label_only={len(label_ids - manifest_ids)}"
        )
    if manifest_ids != prediction_ids:
        issues.append(
            "manifest and prediction sample_id sets differ: "
            f"manifest_only={len(manifest_ids - prediction_ids)}, prediction_only={len(prediction_ids - manifest_ids)}"
        )

    submission_ids = {
        row.get("submission_id", "").strip()
        for row in predictions.values()
        if row.get("submission_id", "").strip()
    }
    if len(submission_ids) != 1:
        issues.append(f"prediction file must contain exactly one submission_id, got {sorted(submission_ids)}")

    label_versions = {
        row.get("label_space_version", "").strip()
        for row in labels.values()
        if row.get("label_space_version", "").strip()
    }
    if len(label_versions) != 1:
        issues.append(f"label file must contain exactly one label_space_version, got {sorted(label_versions)}")

    for sample_id, row in labels.items():
        sealed_label = row.get("sealed_label", "").strip()
        if not sealed_label:
            issues.append(f"labels:{sample_id}: missing sealed_label")
        if main_claim:
            if not row.get("unlock_timestamp", "").strip():
                issues.append(f"labels:{sample_id}: missing unlock_timestamp for main-claim evaluation")
            if not row.get("unlock_authorized_by", "").strip():
                issues.append(f"labels:{sample_id}: missing unlock_authorized_by for main-claim evaluation")

    for sample_id, row in predictions.items():
        if not row.get("predicted_label", "").strip():
            issues.append(f"predictions:{sample_id}: missing predicted_label")
        if parse_score(row.get("prediction_score", "")) is None:
            issues.append(f"predictions:{sample_id}: invalid prediction_score")
        if main_claim and not row.get("prediction_timestamp", "").strip():
            issues.append(f"predictions:{sample_id}: missing prediction_timestamp for main-claim evaluation")
    return issues


def metric_block(y_true: list[str], y_pred: list[str]) -> dict[str, object]:
    labels = sorted(set(y_true) | set(y_pred))
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="y_pred contains classes not in y_true")
        balanced_accuracy = balanced_accuracy_score(y_true, y_pred) if y_true else None
    return {
        "n": len(y_true),
        "labels": labels,
        "accuracy": accuracy_score(y_true, y_pred) if y_true else None,
        "balanced_accuracy": balanced_accuracy,
        "macro_f1": f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0) if y_true else None,
        "confusion_matrix": matrix.tolist(),
    }


def compute_metrics(
    manifest: dict[str, dict[str, str]],
    labels: dict[str, dict[str, str]],
    predictions: dict[str, dict[str, str]],
) -> dict[str, object]:
    common_ids = sorted(set(manifest) & set(labels) & set(predictions))
    y_true = [labels[sample_id]["sealed_label"].strip() for sample_id in common_ids]
    y_pred = [predictions[sample_id]["predicted_label"].strip() for sample_id in common_ids]
    overall = metric_block(y_true, y_pred)

    by_group: dict[str, dict[str, object]] = {}
    grouped_ids: dict[str, list[str]] = defaultdict(list)
    for sample_id in common_ids:
        group = manifest[sample_id].get("source_group", "").strip() or "UNKNOWN"
        grouped_ids[group].append(sample_id)
    for group, ids in sorted(grouped_ids.items()):
        group_true = [labels[sample_id]["sealed_label"].strip() for sample_id in ids]
        group_pred = [predictions[sample_id]["predicted_label"].strip() for sample_id in ids]
        by_group[group] = metric_block(group_true, group_pred)

    return {
        "overall": overall,
        "by_source_group": by_group,
        "label_counts": dict(sorted(Counter(y_true).items())),
        "prediction_counts": dict(sorted(Counter(y_pred).items())),
    }


def write_reports(result: dict[str, object]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORT_DIR / "external_blind_locked_evaluation_summary.json"
    md_path = REPORT_DIR / "external_blind_locked_evaluation_summary.md"
    group_csv_path = REPORT_DIR / "external_blind_locked_evaluation_by_group.csv"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    metrics = result["metrics"]
    overall = metrics.get("overall", {})
    lines = [
        "# External Blind Locked Evaluation 2026-08-10",
        "",
        f"Status: **{result['status']}**",
        f"Evaluation mode: **{result['evaluation_mode']}**",
        "",
        "## Inputs",
        "",
        f"- manifest: `{result['inputs']['manifest']}`",
        f"- labels: `{result['inputs']['labels']}`",
        f"- predictions: `{result['inputs']['predictions']}`",
        "",
        "## Overall Metrics",
        "",
        f"- n: {overall.get('n')}",
        f"- accuracy: {overall.get('accuracy')}",
        f"- balanced_accuracy: {overall.get('balanced_accuracy')}",
        f"- macro_f1: {overall.get('macro_f1')}",
        f"- labels: {', '.join(overall.get('labels', []))}",
        "",
        "## Issues",
        "",
    ]
    if result["issues"]:
        lines.extend(f"- {issue}" for issue in result["issues"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            result["boundary"],
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    with group_csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["source_group", "n", "accuracy", "balanced_accuracy", "macro_f1"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for group, block in metrics.get("by_source_group", {}).items():
            writer.writerow(
                {
                    "source_group": group,
                    "n": block.get("n"),
                    "accuracy": block.get("accuracy"),
                    "balanced_accuracy": block.get("balanced_accuracy"),
                    "macro_f1": block.get("macro_f1"),
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument(
        "--main-claim",
        action="store_true",
        help="Require unlock metadata and timestamp completeness for a real main-claim evaluation.",
    )
    args = parser.parse_args()

    issues: list[str] = []
    for path in [args.manifest, args.labels, args.predictions]:
        if not path.exists():
            issues.append(f"missing input: {path}")

    if issues:
        result = {
            "status": "FAIL",
            "evaluation_mode": "main_claim" if args.main_claim else "template_dry_run",
            "inputs": {
                "manifest": str(args.manifest),
                "labels": str(args.labels),
                "predictions": str(args.predictions),
            },
            "issues": issues,
            "metrics": {"overall": {}, "by_source_group": {}},
            "boundary": "No evaluation was run because required inputs were missing.",
        }
        write_reports(result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1

    manifest_columns, manifest_rows = read_csv(args.manifest)
    label_columns, label_rows = read_csv(args.labels)
    prediction_columns, prediction_rows = read_csv(args.predictions)
    issues.extend(require_columns(args.manifest, manifest_columns, MANIFEST_COLUMNS))
    issues.extend(require_columns(args.labels, label_columns, LABEL_COLUMNS))
    issues.extend(require_columns(args.predictions, prediction_columns, PREDICTION_COLUMNS))

    manifest, manifest_issues = index_by_sample_id(args.manifest, manifest_rows)
    labels, label_issues = index_by_sample_id(args.labels, label_rows)
    predictions, prediction_issues = index_by_sample_id(args.predictions, prediction_rows)
    issues.extend(manifest_issues)
    issues.extend(label_issues)
    issues.extend(prediction_issues)
    issues.extend(validate_join(manifest, labels, predictions, args.main_claim))

    metrics = compute_metrics(manifest, labels, predictions) if not issues else {"overall": {}, "by_source_group": {}}
    mode = "main_claim" if args.main_claim else "template_dry_run"
    status = "PASS" if not issues else "FAIL"
    boundary = (
        "This is a template dry run only; it does not constitute blind external validation."
        if not args.main_claim
        else "This evaluation is eligible for main-claim reporting only if the prediction file was frozen before label unlock and the asset passed strict intake validation."
    )
    result = {
        "status": status,
        "evaluation_mode": mode,
        "inputs": {
            "manifest": str(args.manifest),
            "labels": str(args.labels),
            "predictions": str(args.predictions),
        },
        "issues": issues,
        "metrics": metrics,
        "boundary": boundary,
    }
    write_reports(result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
