#!/usr/bin/env python3
"""Build request and handoff package for acquiring a real blind external asset."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "blind_external_acquisition_package_20260810"


REQUEST_ROWS = [
    {
        "request_item": "Unlabeled GPR samples",
        "required": "yes",
        "provided_to_analyst": "yes",
        "allowed_content": "Raw files or exported images without labels or label hints.",
        "not_allowed": "Class names in folder names, filename label hints, notes that reveal outcome.",
    },
    {
        "request_item": "Analyst-facing manifest",
        "required": "yes",
        "provided_to_analyst": "yes",
        "allowed_content": "sample_id, rel_path or abs_path, file_sha256, label_placeholder, source_group, asset_track, modality, target_task, notes.",
        "not_allowed": "Any real class label, diagnostic label, target-derived split, or label hint.",
    },
    {
        "request_item": "Sealed label file",
        "required": "yes",
        "provided_to_analyst": "no_until_unlock",
        "allowed_content": "sample_id, sealed_label, label_space_version, label_holder, sealed_timestamp.",
        "not_allowed": "Transfer to analyst before prediction package is frozen and hashed.",
    },
    {
        "request_item": "Source-group metadata",
        "required": "yes",
        "provided_to_analyst": "yes",
        "allowed_content": "Project/site/device/collection group IDs that do not reveal labels.",
        "not_allowed": "Grouping variables derived from the hidden outcome.",
    },
    {
        "request_item": "Rights statement",
        "required": "yes",
        "provided_to_analyst": "yes",
        "allowed_content": "Whether files can be used for validation, figures, derived metrics and public release.",
        "not_allowed": "Assuming redistribution is allowed without written permission.",
    },
]


HANDOFF_CHECKLIST = [
    {
        "step": "1",
        "owner": "Data holder",
        "action": "Prepare unlabeled files in a dated folder and remove label-bearing folder names or filenames.",
        "evidence": "Folder listing and file hashes.",
        "go_no_go": "NO-GO if filenames or folders reveal labels.",
    },
    {
        "step": "2",
        "owner": "Data holder",
        "action": "Create the analyst-facing manifest using the required external_blind columns.",
        "evidence": "CSV manifest with stable sample_id and file_sha256.",
        "go_no_go": "NO-GO if sample IDs are duplicated or SHA256 values are missing.",
    },
    {
        "step": "3",
        "owner": "Label holder",
        "action": "Create and store the sealed label file outside the analyst workflow.",
        "evidence": "Hash of sealed label file, but no label values sent to analyst.",
        "go_no_go": "NO-GO if labels are opened before prediction freeze.",
    },
    {
        "step": "4",
        "owner": "Analyst",
        "action": "Run strict intake validation before model prediction.",
        "evidence": "PASS report from validate_external_blind_intake.py --strict-sha.",
        "go_no_go": "NO-GO if validator reports label leakage or hash problems.",
    },
    {
        "step": "5",
        "owner": "Analyst and auditor",
        "action": "Freeze preprocessing, model family, seeds, thresholds, scripts and one prediction submission.",
        "evidence": "Frozen prediction CSV and hash record.",
        "go_no_go": "NO-GO if any model choice is made after labels are seen.",
    },
    {
        "step": "6",
        "owner": "Unlocker",
        "action": "Release labels only after prediction freeze and authorization.",
        "evidence": "unlock_timestamp and unlock_authorized_by fields.",
        "go_no_go": "NO-GO if unlock precedes prediction freeze.",
    },
    {
        "step": "7",
        "owner": "Analyst",
        "action": "Run locked evaluation once for the main claim.",
        "evidence": "evaluate_external_blind_submission.py --main-claim output.",
        "go_no_go": "Later reruns are exploratory only.",
    },
]


RIGHTS_ROWS = [
    {
        "rights_item": "Use for model evaluation",
        "minimum_answer": "explicit yes",
        "reason": "Blind external validation cannot proceed without permission to compute and report metrics.",
        "if_not_available": "Use only for internal dry run or exclude from manuscript claims.",
    },
    {
        "rights_item": "Use in manuscript figures/tables",
        "minimum_answer": "yes or derived-summary-only",
        "reason": "Main text may need aggregate metrics, confusion matrices or example images.",
        "if_not_available": "Report only allowed aggregate metrics or omit examples.",
    },
    {
        "rights_item": "Public redistribution of raw files",
        "minimum_answer": "explicit licence or no",
        "reason": "Data Availability wording depends on redistribution permission.",
        "if_not_available": "State restricted access and provide contact/access procedure if allowed.",
    },
    {
        "rights_item": "Public release of derived metrics",
        "minimum_answer": "explicit yes",
        "reason": "Source Data deposit can usually include derived aggregate metrics if permitted.",
        "if_not_available": "Exclude derived rows from public deposit until cleared.",
    },
    {
        "rights_item": "Commercial or journal-publication use",
        "minimum_answer": "compatible with journal publication",
        "reason": "Nature Communications publication requires rights to publish the reported evidence.",
        "if_not_available": "Do not use asset in main submission.",
    },
]


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(
        OUT_DIR / "external_asset_request_items.csv",
        REQUEST_ROWS,
        ["request_item", "required", "provided_to_analyst", "allowed_content", "not_allowed"],
    )
    write_csv(
        OUT_DIR / "blind_handoff_checklist.csv",
        HANDOFF_CHECKLIST,
        ["step", "owner", "action", "evidence", "go_no_go"],
    )
    write_csv(
        OUT_DIR / "external_asset_rights_checklist.csv",
        RIGHTS_ROWS,
        ["rights_item", "minimum_answer", "reason", "if_not_available"],
    )

    request_letter = """# External blind GPR validation asset request

We are preparing a provenance-aware GPR recognition benchmark and need one genuinely blind external validation asset. The asset must not have been used for model development, model selection, threshold tuning or figure selection.

Please provide only unlabeled files or images plus an analyst-facing manifest. Labels should be held by an advisor, collaborator or third-party label holder until the prediction submission is frozen and hashed.

## What the analyst can receive before prediction

1. Unlabeled GPR files or exported B-scan images.
2. A manifest with stable sample IDs, file paths, SHA256 hashes, source group, modality and predeclared target task.
3. Non-label metadata needed for grouped error analysis.
4. A rights statement describing what can be used in manuscript figures, aggregate metrics, Source Data and public release.

## What must not be sent before prediction

1. Class labels or diagnostic labels.
2. Folder names, filenames or notes that reveal labels.
3. Label-derived train/test split information.
4. Any informal hint about expected class balance or sample difficulty if it reveals outcome information.

## Required sequence

The analyst validates the unlabeled manifest with strict SHA checks, freezes models and predictions, stores one prediction submission, and only then receives the sealed label file for a single locked evaluation.

Current project status: blind external validation is NO-GO until this sequence is completed with a real asset.
"""
    (OUT_DIR / "external_blind_asset_request_letter.md").write_text(request_letter, encoding="utf-8")

    label_holder_sop = """# Label-holder SOP for blind external validation

## Role

The label holder protects the true labels until the analyst freezes the prediction submission.

## Before prediction

1. Assign stable sample IDs.
2. Prepare the sealed label file with `sample_id`, `sealed_label`, `label_space_version`, `label_holder` and `sealed_timestamp`.
3. Store the label file outside the analyst workflow.
4. Optionally provide a hash of the sealed label file, but do not provide labels.

## After prediction freeze

1. Verify that the analyst has produced a frozen prediction file and hash record.
2. Record `unlock_timestamp` and `unlock_authorized_by`.
3. Release the label file.
4. Do not allow model changes before the locked main-claim evaluation.

## Non-negotiable rule

Any evaluation after labels have been seen and after model or threshold changes is exploratory only. It cannot replace the main blind external validation result.
"""
    (OUT_DIR / "label_holder_sop.md").write_text(label_holder_sop, encoding="utf-8")

    intake_readme = """# Blind external acquisition package 2026-08-10

This package prepares the communication and handoff materials needed to acquire a real advisor-held or third-party-held GPR blind external validation asset.

Files:

1. `external_blind_asset_request_letter.md`
2. `label_holder_sop.md`
3. `external_asset_request_items.csv`
4. `blind_handoff_checklist.csv`
5. `external_asset_rights_checklist.csv`
6. `blind_external_acquisition_package_summary.json`

Boundary: this package does not create a blind external result. It only reduces acquisition and label-leakage risk before a real asset arrives.
"""
    (OUT_DIR / "BLIND_EXTERNAL_ACQUISITION_README.md").write_text(intake_readme, encoding="utf-8")

    summary = {
        "run_id": "20260810_blind_external_acquisition_package",
        "request_items": len(REQUEST_ROWS),
        "handoff_steps": len(HANDOFF_CHECKLIST),
        "rights_items": len(RIGHTS_ROWS),
        "blind_external_gate_status": "NO-GO",
        "package_ready_for_data_holder": True,
        "creates_real_external_result": False,
        "status": "acquisition_package_ready_no_external_asset",
        "boundary": "Request and handoff materials are ready, but no real blind external asset has been acquired or evaluated.",
    }
    (OUT_DIR / "blind_external_acquisition_package_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
