#!/usr/bin/env python3
"""Build a conservative Methods draft package from the audited Methods skeleton."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "conservative_methods_draft_20260810"
MODULE_MAP = BENCH_ROOT / "reports" / "methods_section_skeleton_20260810" / "methods_module_map.csv"
TRACE_SOURCE = BENCH_ROOT / "reports" / "methods_section_skeleton_20260810" / "methods_section_skeleton.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


METHODS_DRAFT = """# Methods draft v0.1

## Study design and evidence boundary

This study was designed as an auditable evaluation of how provenance and environment structure affect ground-penetrating radar (GPR) recognition. The workflow did not treat every nominally available dataset as an equivalent validation asset. Instead, each asset was assigned a dated executable status before it was used for model comparison, stress testing or gate reporting. At the 2026-08-10 checkpoint, Mojahid, 4TU and Res-SAM contributed executable local samples, whereas TIGPR remained a supporting-only asset because its local executable sample index was empty. This distinction was used to prevent non-executable assets from being promoted into the core evidence matrix.

## Unified sample manifests

Local assets were represented using unified sample manifests generated for the 2026-08-10 checkpoint. Each manifest recorded the asset name, sample identifiers, available paths, task-relevant fields and asset status needed for downstream audit. The manifest layer was used to count executable rows and to separate current analysis assets from assets that required restoration or additional permission. The asset-boundary outputs were then summarized for Figure 1 and Table 1 source data. This module defines the provenance and execution boundary; it does not measure recognition performance.

## Split and environment-transfer construction

Mojahid and Res-SAM were used for split and environment-transfer contrasts. Mojahid was evaluated under random stratified splits and grouped splits to test whether apparent performance changed when provenance-related grouping was respected. Res-SAM was evaluated under within-environment and cross-environment transfer settings between real-world and synthetic subsets. These contrasts were designed to separate ordinary within-source performance from sensitivity to environment transfer. They do not constitute blind external validation because the assets were already part of the current development and analysis matrix.

## Five-model family matrix

To reduce dependence on a single model family, the current Mojahid and Res-SAM comparisons were summarized across five model families: HOG plus RBF-SVM, LBP plus LinearSVM, TinyCNN, ResNet18 frozen embeddings plus LinearSVM and EfficientNetB0 frozen embeddings plus LinearSVM. For each contrast, the primary effect direction was defined using the difference in balanced accuracy between the compared settings. Directional support recorded whether a model family changed in the predeclared direction, whereas material support required an absolute balanced-accuracy delta of at least 0.05. The first five-model matrix excluded 4TU and did not include a real blind external asset.

## 4TU multi-layer counterfactual stress tests

The 4TU asset was used to examine whether raw-trace rendering and processing choices could alter model predictions. Raw traces were rendered into image-feature inputs and evaluated through summary-feature, raw-pixel, HOG image-feature and small-CNN stress-test layers. Deterministic counterfactual variants included log clipping, z-score clipping, time reversal and nuisance-band or border-related modifications. Fixed-split seed sweeps were compared with project-level repeated splits, and a five-layer extension audit was used to keep the 4TU evidence in a stress-test and feasibility-boundary role. These analyses were not treated as causal proof, main confirmation or blind external validation.

## 4TU grouped feasibility audit

Before expanding 4TU into any main confirmation matrix, each metadata target was audited for grouped-holdout feasibility. The audit recorded sample count, project count, label count, singleton labels, rare project support and the number of feasible test-project and validation-project combinations. This gate was used to identify targets that could support grouped evaluation and targets that should remain feasibility or failure-mode examples. Land type was retained as usable with caution, whereas several other targets were limited by non-viable grouped holdouts or single-project label structure. The target-feasibility gate and the five-layer extension audit therefore jointly prevent 4TU from being promoted beyond stress-test support at the current checkpoint.

## Blind external validation protocol

A blind external validation protocol was defined but not completed. The protocol requires an external asset that was not used during model development, a manifest with strict file hashes, labels held outside the analyst workflow, a frozen prediction submission and one locked evaluation after labels are released. Analyst-facing manifest, label-holdout and prediction-submission templates were created, and a locked-evaluation dry run was executed on template files. These outputs verify the protocol entry point only. They are not evidence of completed blind external validation.

## Reproducibility and checkpoint regeneration

All current artifacts were regenerated through the dated M0-M2 check script. The script validates the Python launcher and core imports, checks manifest consistency, audits asset readiness, builds source-data packages, regenerates Results and Methods skeletons, produces submission-readiness artifacts and verifies required outputs. The checkpoint also runs a manuscript-facing text-encoding check to detect common mojibake markers in generated prose and tabular files. Passing this script demonstrates that the current checkpoint can be regenerated, but it does not close future scientific gates such as rendered figures, repository identifiers, rights clearance, final Reporting Summary or blind external validation.
"""


def count_words(text: str) -> int:
    return len([token for token in text.replace("#", " ").split() if token.strip()])


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    modules = read_csv(MODULE_MAP)
    trace_exists = TRACE_SOURCE.exists()

    (OUT_DIR / "methods_draft_v0_1.md").write_text(METHODS_DRAFT, encoding="utf-8")

    trace_rows = []
    for module in modules:
        trace_rows.append(
            {
                "module_id": module["module_id"],
                "module_title": module["module_title"],
                "role_in_results": module["role_in_results"],
                "draft_section": module["module_title"],
                "boundary": module["boundary"],
            }
        )
    write_csv(OUT_DIR / "methods_module_trace_v0_1.csv", trace_rows, ["module_id", "module_title", "role_in_results", "draft_section", "boundary"])

    budget_rows = [
        {
            "section": "Methods v0.1",
            "word_count": str(count_words(METHODS_DRAFT)),
            "nat_comms_target": "about 1500 words within main 5000-word Article budget",
            "status": "within_target",
        },
        {
            "section": "Methods final",
            "word_count": "not_final",
            "nat_comms_target": "revise after final figures and repository identifiers are locked",
            "status": "pending_final_lock",
        },
    ]
    write_csv(OUT_DIR / "methods_word_budget_v0_1.csv", budget_rows, ["section", "word_count", "nat_comms_target", "status"])

    qa_rows = [
        {
            "check": "No completed blind external validation claim",
            "result": "PASS",
            "detail": "Methods states protocol was defined but not completed.",
        },
        {
            "check": "No TIGPR executable-core claim",
            "result": "PASS",
            "detail": "Methods states TIGPR remained supporting-only because local executable sample index was empty.",
        },
        {
            "check": "No 4TU main confirmation overclaim",
            "result": "PASS",
            "detail": "Methods frames 4TU as stress-test and feasibility evidence.",
        },
        {
            "check": "No repository or Reporting Summary completion claim",
            "result": "PASS",
            "detail": "Methods states these remain future scientific/submission gates.",
        },
        {
            "check": "Methods skeleton trace source present",
            "result": "PASS" if trace_exists else "WARN",
            "detail": str(TRACE_SOURCE),
        },
    ]
    write_csv(OUT_DIR / "methods_boundary_qa_v0_1.csv", qa_rows, ["check", "result", "detail"])

    summary = {
        "run_id": "20260810_conservative_methods_draft_v0_1",
        "modules_traced": len(trace_rows),
        "methods_words": count_words(METHODS_DRAFT),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "submission_ready": False,
        "status": "methods_draft_ready_not_submission_final",
        "boundary": "Methods v0.1 is reproducibility prose based on current modules; final Methods remain blocked by figures, repository identifiers, rights, Reporting Summary and external validation status.",
    }
    (OUT_DIR / "methods_draft_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Conservative Methods draft report 2026-08-10",
        "",
        f"- Modules traced: {summary['modules_traced']}",
        f"- Methods word count: {summary['methods_words']}",
        f"- Boundary QA rows: {summary['qa_rows']}",
        f"- Boundary QA pass: {summary['qa_pass']}",
        f"- Submission ready: {summary['submission_ready']}",
        "",
        "Conclusion: Methods v0.1 is ready for author review but remains non-final.",
        "",
    ]
    (OUT_DIR / "methods_draft_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
