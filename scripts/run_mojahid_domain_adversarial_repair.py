#!/usr/bin/env python3
"""Train-only domain-adversarial repair on frozen Mojahid HOG features."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from torch import nn
from torch.autograd import Function
from torch.utils.data import DataLoader, TensorDataset


SEEDS = [20260810, 20260811, 20260812, 20260813, 20260814]
LAMBDAS = [0.0, 0.1, 0.5, 1.0]
PROTOCOLS = [
    ("current_fold0_test_fold1_val", 0, 1),
    ("task_aware_fold0_test_fold3_val", 0, 3),
]


class GradientReverse(Function):
    @staticmethod
    def forward(ctx, x: torch.Tensor, strength: float) -> torch.Tensor:
        ctx.strength = strength
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output: torch.Tensor) -> tuple[torch.Tensor, None]:
        return -ctx.strength * grad_output, None


class DomainAdversarialNet(nn.Module):
    def __init__(self, input_dim: int, n_targets: int) -> None:
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128), nn.ReLU(), nn.Dropout(0.1),
            nn.Linear(128, 64), nn.ReLU(),
        )
        self.target_head = nn.Linear(64, n_targets)
        self.domain_head = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 2))

    def forward(self, x: torch.Tensor, grl_lambda: float) -> tuple[torch.Tensor, torch.Tensor]:
        z = self.encoder(x)
        target_logits = self.target_head(z)
        domain_logits = self.domain_head(GradientReverse.apply(z, grl_lambda))
        return target_logits, domain_logits


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_aligned_features(manifest: Path, feature_cache: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rows = read_rows(manifest)
    cache = np.load(feature_cache, allow_pickle=False)
    index = {str(sample_id): i for i, sample_id in enumerate(cache["sample_ids"].tolist())}
    missing = [row["sample_id"] for row in rows if row["sample_id"] not in index]
    if missing:
        raise ValueError(f"Feature cache misses {len(missing)} manifest samples")
    order = np.asarray([index[row["sample_id"]] for row in rows], dtype=np.int64)
    x = cache["hog"][order].astype(np.float32)
    labels = np.asarray([row["label"] for row in rows])
    folds = np.asarray([int(row["fold_id"]) for row in rows], dtype=np.int64)
    domains = np.asarray([int(row["is_augmented"]) for row in rows], dtype=np.int64)
    return x, labels, folds, domains


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


def class_weights(y: np.ndarray, n_classes: int) -> torch.Tensor:
    counts = np.bincount(y, minlength=n_classes).astype(np.float64)
    weights = counts.sum() / np.maximum(counts, 1.0) / n_classes
    return torch.tensor(weights, dtype=torch.float32)


def predict(model: nn.Module, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    with torch.no_grad():
        target_logits, domain_logits = model(torch.tensor(x, dtype=torch.float32), 0.0)
    return target_logits.argmax(1).numpy(), domain_logits.argmax(1).numpy()


def evaluate(model: nn.Module, x: np.ndarray, y: np.ndarray, d: np.ndarray) -> dict[str, float]:
    target_pred, domain_pred = predict(model, x)
    return {
        "target_balanced_accuracy": float(balanced_accuracy_score(y, target_pred)),
        "target_macro_f1": float(f1_score(y, target_pred, average="macro")),
        "domain_balanced_accuracy": float(balanced_accuracy_score(d, domain_pred)),
    }


def train_one(
    x_train: np.ndarray,
    y_train: np.ndarray,
    d_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    d_val: np.ndarray,
    seed: int,
    grl_lambda: float,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> tuple[DomainAdversarialNet, dict[str, object]]:
    set_seed(seed)
    model = DomainAdversarialNet(x_train.shape[1], int(y_train.max()) + 1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    target_loss_fn = nn.CrossEntropyLoss(weight=class_weights(y_train, int(y_train.max()) + 1))
    domain_loss_fn = nn.CrossEntropyLoss(weight=class_weights(d_train, 2))
    generator = torch.Generator().manual_seed(seed)
    loader = DataLoader(
        TensorDataset(
            torch.tensor(x_train, dtype=torch.float32),
            torch.tensor(y_train, dtype=torch.long),
            torch.tensor(d_train, dtype=torch.long),
        ),
        batch_size=batch_size,
        shuffle=True,
        generator=generator,
    )
    best_state = None
    best_score = -float("inf")
    best_epoch = 0
    trace: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        model.train()
        target_loss_total = 0.0
        domain_loss_total = 0.0
        seen = 0
        for xb, yb, db in loader:
            optimizer.zero_grad(set_to_none=True)
            target_logits, domain_logits = model(xb, grl_lambda)
            target_loss = target_loss_fn(target_logits, yb)
            domain_loss = domain_loss_fn(domain_logits, db)
            loss = target_loss + domain_loss
            loss.backward()
            optimizer.step()
            target_loss_total += float(target_loss.detach()) * len(xb)
            domain_loss_total += float(domain_loss.detach()) * len(xb)
            seen += len(xb)
        val_metrics = evaluate(model, x_val, y_val, d_val)
        # Select on validation target performance only; source suppression is reported, not optimized post hoc.
        score = val_metrics["target_balanced_accuracy"]
        if score > best_score:
            best_score = score
            best_epoch = epoch
            best_state = {key: value.detach().clone() for key, value in model.state_dict().items()}
        if epoch in {1, epochs} or epoch % 25 == 0:
            trace.append({
                "epoch": epoch,
                "target_loss": target_loss_total / seen,
                "domain_loss": domain_loss_total / seen,
                **val_metrics,
            })
    if best_state is None:
        raise RuntimeError("No model checkpoint selected")
    model.load_state_dict(best_state)
    return model, {"best_epoch": best_epoch, "best_val_target_balanced_accuracy": best_score, "trace": trace}


def aggregate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, float], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["protocol"]), float(row["grl_lambda"]))].append(row)
    output = []
    for (protocol, grl_lambda), items in sorted(grouped.items()):
        target = np.asarray([float(row["test_target_balanced_accuracy"]) for row in items])
        domain = np.asarray([float(row["test_domain_balanced_accuracy"]) for row in items])
        output.append({
            "protocol": protocol,
            "grl_lambda": grl_lambda,
            "n_seeds": len(items),
            "test_target_ba_mean": float(target.mean()),
            "test_target_ba_std": float(target.std(ddof=0)),
            "test_domain_ba_mean": float(domain.mean()),
            "test_domain_ba_std": float(domain.std(ddof=0)),
        })
    baselines = {row["protocol"]: row for row in output if row["grl_lambda"] == 0.0}
    for row in output:
        base = baselines[row["protocol"]]
        row["target_ba_delta_vs_erm"] = row["test_target_ba_mean"] - base["test_target_ba_mean"]
        row["domain_ba_delta_vs_erm"] = row["test_domain_ba_mean"] - base["test_domain_ba_mean"]
    return output


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# Mojahid Train-Only Domain-Adversarial Repair",
        "",
        "A gradient-reversal network suppresses the binary original/augmented processing-role signal using training folds only. Checkpoint selection uses validation target balanced accuracy; test folds are never used for selection.",
        "",
        "| protocol | lambda | target BA | delta vs ERM | domain BA | delta vs ERM |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["aggregate_rows"]:
        lines.append(
            f"| {row['protocol']} | {row['grl_lambda']:.1f} | {row['test_target_ba_mean']:.4f} | "
            f"{row['target_ba_delta_vs_erm']:+.4f} | {row['test_domain_ba_mean']:.4f} | "
            f"{row['domain_ba_delta_vs_erm']:+.4f} |"
        )
    lines.extend([
        "", "## Boundary", "",
        "This is an internal train-only representation-invariance stress test over a processing-role proxy. It is not a real blind external repair result, and a lower domain probe is useful only if target generalization is retained.", "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--feature-cache", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(max(1, min(4, torch.get_num_threads())))

    x, label_text, folds, domains = load_aligned_features(args.manifest, args.feature_cache)
    encoder = LabelEncoder().fit(label_text)
    y = encoder.transform(label_text).astype(np.int64)
    detailed_rows: list[dict[str, object]] = []
    traces: list[dict[str, object]] = []
    for protocol, test_fold, val_fold in PROTOCOLS:
        train_idx = np.flatnonzero(~np.isin(folds, [test_fold, val_fold]))
        val_idx = np.flatnonzero(folds == val_fold)
        test_idx = np.flatnonzero(folds == test_fold)
        scaler = StandardScaler().fit(x[train_idx])
        x_scaled = scaler.transform(x).astype(np.float32)
        for seed in SEEDS:
            for grl_lambda in LAMBDAS:
                model, training = train_one(
                    x_scaled[train_idx], y[train_idx], domains[train_idx],
                    x_scaled[val_idx], y[val_idx], domains[val_idx],
                    seed, grl_lambda, args.epochs, args.batch_size, args.learning_rate,
                )
                val_metrics = evaluate(model, x_scaled[val_idx], y[val_idx], domains[val_idx])
                test_metrics = evaluate(model, x_scaled[test_idx], y[test_idx], domains[test_idx])
                detailed_rows.append({
                    "protocol": protocol, "seed": seed, "grl_lambda": grl_lambda,
                    "train_n": len(train_idx), "val_n": len(val_idx), "test_n": len(test_idx),
                    "best_epoch": training["best_epoch"],
                    **{f"val_{k}": v for k, v in val_metrics.items()},
                    **{f"test_{k}": v for k, v in test_metrics.items()},
                })
                traces.append({
                    "protocol": protocol, "seed": seed, "grl_lambda": grl_lambda,
                    "best_epoch": training["best_epoch"], "trace": training["trace"],
                })
    aggregate_rows = aggregate(detailed_rows)
    result = {
        "run_id": "20260811_E39_mojahid_train_only_domain_adversarial_repair",
        "status": "complete_internal_train_only_domain_adversarial_repair",
        "source_proxy": "is_augmented",
        "repair_uses_unlabeled_target_statistics": False,
        "repair_uses_test_fold_for_parameter_selection": False,
        "blind_external_eligible": False,
        "seeds": SEEDS,
        "grl_lambdas": LAMBDAS,
        "epochs": args.epochs,
        "sample_count": len(y),
        "aggregate_rows": aggregate_rows,
        "detailed_rows": detailed_rows,
        "training_traces": traces,
    }
    write_csv(args.output_dir / "domain_adversarial_repair_runs.csv", detailed_rows)
    (args.output_dir / "domain_adversarial_repair_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_md(args.output_dir / "domain_adversarial_repair_summary.md", result)
    print(json.dumps({"aggregate_rows": aggregate_rows}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
