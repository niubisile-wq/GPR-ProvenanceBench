#!/usr/bin/env python3
"""Run a reproducible public-benchmark probe for IOAI 2025 Radar.

This script is intentionally scoped as a public benchmark evaluation route,
not blind external validation. It downloads the official IOAI Radar training
and public scoring assets from GitHub, trains the simple notebook baseline
model, and reports weighted pixel accuracy on the public validation/test
splits when their ground-truth CSV files are available.

The script supports a smoke-test mode with sample limits, plus a full-benchmark
mode that uses every available training and public evaluation sample.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import math
import os
import time
from pathlib import Path
from typing import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset


REPO = "IOAI-official/IOAI-2025"
BRANCH = "main"
RADAR_ROOT = "Individual-Contest/Radar"
TRAIN_TREE_SHA = "95e618513411404d62ef4b767b6da650cdd3a83f"
SOLUTION_TREE_SHA = "c6324ecd86002042abb031df6ac796518bedab54"
VAL_TREE_SHA = "2635d97f40fdb5987726ddca8f6429770c56b140"
TEST_TREE_SHA = "ec022deafa734a5f362a41c8fdb39fc2554f1680"

GITHUB_RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
GITHUB_API = f"https://api.github.com/repos/{REPO}"


def tree_paths(tree_sha: str) -> list[str]:
    url = f"{GITHUB_API}/git/trees/{tree_sha}?recursive=1"
    r = requests.get(url, headers={"User-Agent": "Codex"}, timeout=60)
    r.raise_for_status()
    data = r.json()
    return [item["path"] for item in data.get("tree", []) if item.get("type") == "blob"]


def list_sorted_pt_paths(root_tree_sha: str) -> list[str]:
    paths = [p for p in tree_paths(root_tree_sha) if p.endswith(".mat.pt")]

    def sort_key(path: str) -> tuple[int, str]:
        stem = Path(path).stem.split(".")[0]
        try:
            return int(stem), path
        except ValueError:
            return math.inf, path

    return sorted(paths, key=sort_key)


def download_file(url: str, path: Path, *, retries: int = 5) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    tmp = path.with_suffix(path.suffix + ".part")
    for attempt in range(1, retries + 1):
        try:
            if tmp.exists():
                tmp.unlink()
            with requests.get(url, headers={"User-Agent": "Codex"}, stream=True, timeout=120) as r:
                r.raise_for_status()
                with tmp.open("wb") as f:
                    for chunk in r.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            f.write(chunk)
            tmp.replace(path)
            return
        except Exception:
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    pass
            if attempt == retries:
                raise
            time.sleep(min(2 * attempt, 10))


def download_collection(
    remote_root: str,
    local_root: Path,
    paths: Iterable[str],
    limit: int | None = None,
    *,
    workers: int = 1,
) -> list[Path]:
    selected = []
    for i, rel in enumerate(paths):
        if limit is not None and i >= limit:
            break
        selected.append(rel)

    local_paths = [local_root / Path(rel).name for rel in selected]
    if workers <= 1 or len(selected) <= 1:
        for rel, local in zip(selected, local_paths):
            download_file(f"{GITHUB_RAW}/{remote_root}/{rel}", local)
        return local_paths

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(download_file, f"{GITHUB_RAW}/{remote_root}/{rel}", local): local
            for rel, local in zip(selected, local_paths)
        }
        for future in as_completed(futures):
            future.result()
    return local_paths


class RadarTrainDataset(Dataset):
    def __init__(self, files: list[Path]):
        self.files = files

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, idx: int):
        data = torch.load(self.files[idx], weights_only=True)
        x = data[:6].float()
        y = data[6].long() + 1
        return x, y, self.files[idx].name


class RadarInferDataset(Dataset):
    def __init__(self, files: list[Path], label_map: dict[str, list[int]] | None = None):
        self.files = files
        self.label_map = label_map or {}

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, idx: int):
        data = torch.load(self.files[idx], weights_only=True)
        x = data[:6].float()
        name = self.files[idx].name
        return x, name


class TinyRadarCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(6, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(32, 5, kernel_size=3, padding=1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        return self.conv3(x)


def load_gt_map(csv_path: Path) -> dict[str, list[int]]:
    df = pd.read_csv(csv_path)
    pixel_cols = [c for c in df.columns if c.startswith("pixel_")]
    return {str(row["filename"]): row[pixel_cols].astype(int).tolist() for _, row in df.iterrows()}


def weighted_score(pred: list[int], gt: list[int]) -> float:
    eq = [p == g for p, g in zip(pred, gt)]
    neg = [g == -1 for g in gt]
    num = sum(1 for e, n in zip(eq, neg) if e and n) * 1 + sum(1 for e, n in zip(eq, neg) if e and not n) * 50
    den = sum(1 for n in neg if n) * 1 + sum(1 for n in neg if not n) * 50
    return float(num) / float(den) if den else 0.0


def run_training(
    model: nn.Module,
    train_loader: DataLoader,
    epochs: int,
    device: torch.device,
) -> list[dict[str, float]]:
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    history: list[dict[str, float]] = []

    for epoch in range(epochs):
        model.train()
        total = 0.0
        count = 0
        for x, y, _ in train_loader:
            x = x.to(device)
            y = y.to(device)
            out = model(x)
            loss = criterion(out.view(out.size(0), out.size(1), -1), y.view(y.size(0), -1))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total += float(loss.item())
            count += 1
        history.append({"epoch": epoch + 1, "train_loss": total / max(count, 1)})
    return history


@dataclasses.dataclass
class EvalResult:
    split: str
    samples: int
    weighted_score: float
    preview: list[dict[str, object]]


def run_inference(
    model: nn.Module,
    loader: DataLoader,
    gt_map: dict[str, list[int]],
    device: torch.device,
    split: str,
) -> EvalResult:
    model.eval()
    preview = []
    weighted_sum = 0.0
    count = 0
    with torch.no_grad():
        for x, name in loader:
            x = x.to(device)
            out = model(x)
            pred = out.argmax(1).squeeze(0).cpu().numpy().reshape(-1).astype(int).tolist()
            gt = gt_map[name[0]]
            score = weighted_score(pred, gt)
            weighted_sum += score
            count += 1
            if len(preview) < 3:
                preview.append(
                    {
                        "filename": name[0],
                        "sample_score": score,
                        "pred_len": len(pred),
                        "gt_len": len(gt),
                    }
                )
    return EvalResult(split=split, samples=count, weighted_score=weighted_sum / max(count, 1), preview=preview)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a public Radar benchmark probe.")
    parser.add_argument("--workdir", type=Path, default=Path("reports") / "ioai_radar_public_benchmark_20260811")
    parser.add_argument("--download-dir", type=Path, default=Path("external_blind") / "ioai_radar_public_benchmark_cache")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-train", type=int, default=None)
    parser.add_argument("--max-val", type=int, default=None)
    parser.add_argument("--max-test", type=int, default=None)
    parser.add_argument("--download-workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    args.workdir.mkdir(parents=True, exist_ok=True)
    args.download_dir.mkdir(parents=True, exist_ok=True)

    train_paths = download_collection(
        f"{RADAR_ROOT}/training_set",
        args.download_dir / "training_set",
        list_sorted_pt_paths(TRAIN_TREE_SHA),
        limit=args.max_train,
        workers=args.download_workers,
    )
    val_paths = download_collection(
        f"{RADAR_ROOT}/Solution/validation_set",
        args.download_dir / "validation_set",
        list_sorted_pt_paths(VAL_TREE_SHA),
        limit=args.max_val,
        workers=args.download_workers,
    )
    test_paths = download_collection(
        f"{RADAR_ROOT}/Solution/test_set",
        args.download_dir / "test_set",
        list_sorted_pt_paths(TEST_TREE_SHA),
        limit=args.max_test,
        workers=args.download_workers,
    )

    gt_val_path = args.download_dir / "ground_truth_val.csv"
    gt_test_path = args.download_dir / "ground_truth_test.csv"
    download_file(f"{GITHUB_RAW}/{RADAR_ROOT}/Solution/Scoring/ground_truth_val.csv", gt_val_path)
    download_file(f"{GITHUB_RAW}/{RADAR_ROOT}/Solution/Scoring/ground_truth_test.csv", gt_test_path)
    gt_val = load_gt_map(gt_val_path)
    gt_test = load_gt_map(gt_test_path)

    train_loader = DataLoader(RadarTrainDataset(train_paths), batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(RadarInferDataset(val_paths), batch_size=1, shuffle=False)
    test_loader = DataLoader(RadarInferDataset(test_paths), batch_size=1, shuffle=False)

    model = TinyRadarCNN().to(device)
    history = run_training(model, train_loader, args.epochs, device)
    val_result = run_inference(model, val_loader, gt_val, device, "validation")
    test_result = run_inference(model, test_loader, gt_test, device, "test")

    result = {
        "route": "public_benchmark_evaluation",
        "blind_external_validation": False,
        "dataset": {
            "training_samples": len(train_paths),
            "validation_samples": len(val_paths),
            "test_samples": len(test_paths),
        },
        "training": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "history": history,
        },
        "evaluation": {
            "validation": dataclasses.asdict(val_result),
            "test": dataclasses.asdict(test_result),
        },
        "note": "This route is a public benchmark probe only. It does not satisfy blind external validation.",
    }

    (args.workdir / "ioai_radar_public_benchmark_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    report = [
        "# IOAI 2025 Radar public benchmark probe",
        "",
        f"- Route: `{result['route']}`",
        f"- Blind external validation: `{result['blind_external_validation']}`",
        f"- Training samples: `{len(train_paths)}`",
        f"- Validation samples: `{len(val_paths)}`",
        f"- Test samples: `{len(test_paths)}`",
        f"- Epochs: `{args.epochs}`",
        f"- Batch size: `{args.batch_size}`",
        "",
        "## Training history",
        "",
        "| epoch | train_loss |",
        "| ---: | ---: |",
    ]
    for row in history:
        report.append(f"| {row['epoch']} | {row['train_loss']:.4f} |")
    report.extend(
        [
            "",
            "## Evaluation",
            "",
            f"- Validation weighted score: `{val_result.weighted_score:.4f}`",
            f"- Test weighted score: `{test_result.weighted_score:.4f}`",
            "",
            "### Validation preview",
            "",
        ]
    )
    for item in val_result.preview:
        report.append(
            f"- `{item['filename']}`: score `{item['sample_score']:.4f}`, pred_len `{item['pred_len']}`, gt_len `{item['gt_len']}`"
        )
    report.extend(
        [
            "",
            "### Test preview",
            "",
        ]
    )
    for item in test_result.preview:
        report.append(
            f"- `{item['filename']}`: score `{item['sample_score']:.4f}`, pred_len `{item['pred_len']}`, gt_len `{item['gt_len']}`"
        )
    report.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a public benchmark evaluation route with public scoring assets. It can strengthen experiment closure, but it is not blind external validation.",
        ]
    )
    (args.workdir / "ioai_radar_public_benchmark_report.md").write_text(
        "\n".join(report),
        encoding="utf-8",
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
