#!/usr/bin/env python3
"""Audit whether current 4TU evidence can be upgraded into a model-family matrix."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "4tu_model_family_extension_audit_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"
MATERIAL_DELTA = 0.05


SOURCES = [
    {
        "layer_id": "4TU-L1",
        "evidence_layer": "summary_feature_fixed_split",
        "model_family": "summary_feature_classifiers",
        "source": REPORTS / "4tu_counterfactual_reliance_20260810" / "counterfactual_reliance_metrics.csv",
        "claim_use": "stress_test_only",
        "limitation": "Uses hand-engineered trace summary features under a fixed split.",
    },
    {
        "layer_id": "4TU-L2",
        "evidence_layer": "raw_pixel_fixed_split",
        "model_family": "rawtrace_pixel_classifiers",
        "source": REPORTS / "4tu_counterfactual_rawtrace_pixel_20260810" / "rawtrace_pixel_reliance_metrics.csv",
        "claim_use": "stress_test_only",
        "limitation": "Uses rendered raw-trace pixels under a fixed split.",
    },
    {
        "layer_id": "4TU-L3",
        "evidence_layer": "hog_seed_sweep_fixed_split",
        "model_family": "hog_image_classifiers",
        "source": REPORTS / "4tu_counterfactual_hog_seed_sweep_20260810" / "hog_seed_sweep_metrics.csv",
        "claim_use": "stress_test_only",
        "limitation": "Repeats model seeds but keeps the split fixed.",
    },
    {
        "layer_id": "4TU-L4",
        "evidence_layer": "small_cnn_seed_sweep_fixed_split",
        "model_family": "small_cnn",
        "source": REPORTS / "4tu_counterfactual_cnn_seed_sweep_20260810" / "cnn_seed_sweep_metrics.csv",
        "claim_use": "stress_test_only",
        "limitation": "CPU-scale CNN seed sweep; currently limited to Land type.",
    },
    {
        "layer_id": "4TU-L5",
        "evidence_layer": "hog_group_aware_repeated_split",
        "model_family": "hog_group_aware_classifiers",
        "source": REPORTS / "4tu_counterfactual_hog_group_splits_20260810" / "hog_group_split_metrics.csv",
        "claim_use": "feasibility_boundary",
        "limitation": "Group-aware repeated splits weaken the fixed-split effect and remain label-limited.",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def selected_counterfactual_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for row in rows:
        if row.get("variant") == "original":
            continue
        selected = row.get("selected_model", "")
        model = row.get("model", "")
        if selected and model != selected:
            continue
        if model == "dummy_majority":
            continue
        out.append(row)
    return out


def aggregate_source(source: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows = read_csv(source["source"])  # type: ignore[arg-type]
    selected = selected_counterfactual_rows(rows)
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in selected:
        groups[(row.get("target_field", ""), row.get("model", ""), row.get("variant", ""))].append(row)

    audit_rows = []
    for (target, model, variant), items in sorted(groups.items()):
        deltas = [float(item["balanced_accuracy_delta_vs_original"]) for item in items]
        flips = [float(item["prediction_flip_rate_vs_original"]) for item in items]
        test_ba = [float(item["test_balanced_accuracy"]) for item in items]
        audit_rows.append(
            {
                "layer_id": source["layer_id"],
                "evidence_layer": source["evidence_layer"],
                "model_family": source["model_family"],
                "target_field": target,
                "model": model,
                "variant": variant,
                "n_rows": len(items),
                "test_balanced_accuracy_mean": mean(test_ba),
                "balanced_accuracy_delta_mean": mean(deltas),
                "balanced_accuracy_delta_std": pstdev(deltas) if len(deltas) > 1 else 0.0,
                "prediction_flip_rate_mean": mean(flips),
                "directional_drop_support": mean(deltas) < 0,
                "material_drop_support": mean(deltas) <= -MATERIAL_DELTA,
                "claim_use": source["claim_use"],
                "limitation": source["limitation"],
                "source_file": str(Path(source["source"]).relative_to(BENCH_ROOT)),  # type: ignore[arg-type]
            }
        )

    strongest = sorted(audit_rows, key=lambda row: float(row["balanced_accuracy_delta_mean"]))[:1]
    source_summary = {
        "layer_id": source["layer_id"],
        "evidence_layer": source["evidence_layer"],
        "model_family": source["model_family"],
        "source_file": str(Path(source["source"]).relative_to(BENCH_ROOT)),  # type: ignore[arg-type]
        "input_rows": len(rows),
        "selected_counterfactual_rows": len(selected),
        "aggregate_rows": len(audit_rows),
        "strongest_target": strongest[0]["target_field"] if strongest else "",
        "strongest_variant": strongest[0]["variant"] if strongest else "",
        "strongest_delta_mean": strongest[0]["balanced_accuracy_delta_mean"] if strongest else "",
        "claim_use": source["claim_use"],
        "upgrade_to_main_confirmation": False,
        "reason": source["limitation"],
    }
    return audit_rows, source_summary


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.69 4TU model-family extension audit 更新"
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            text = text[:start].rstrip()
            updated = text + "\n\n" + section.strip() + "\n"
        else:
            text_before = text[:start].rstrip()
            text_after = text[next_start:].lstrip("\n")
            updated = text_before + "\n\n" + section.strip() + "\n\n" + text_after
    else:
        updated = text.rstrip() + "\n\n" + section.strip() + "\n"
    DESKTOP_PLAN.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    missing = [str(source["source"]) for source in SOURCES if not Path(source["source"]).exists()]
    if missing:
        raise SystemExit("Missing 4TU source files: " + "; ".join(missing))

    matrix_rows: list[dict[str, object]] = []
    layer_rows: list[dict[str, object]] = []
    for source in SOURCES:
        rows, summary = aggregate_source(source)
        matrix_rows.extend(rows)
        layer_rows.append(summary)

    decision_rows = [
        {
            "decision_id": "4TU-UPGRADE-001",
            "question": "Can 4TU be upgraded to a main five-model confirmation layer now?",
            "decision": "NO",
            "evidence": "Group-aware repeated splits weaken the fixed-split effect; metadata labels are project-limited; model layers are not the same claim unit as Mojahid/Res-SAM environment transfer.",
            "allowed_use": "Use 4TU as counterfactual stress-test and feasibility-boundary evidence.",
        },
        {
            "decision_id": "4TU-UPGRADE-002",
            "question": "Can 4TU strengthen the Discussion without overclaiming?",
            "decision": "YES",
            "evidence": "Five current evidence layers show where preprocessing/representation sensitivity appears and where grouped validation weakens it.",
            "allowed_use": "Report as a failure-mode/stress-test panel and as a reason to require asset-feasibility reporting.",
        },
        {
            "decision_id": "4TU-UPGRADE-003",
            "question": "Does this close the external validation gate?",
            "decision": "NO",
            "evidence": "4TU is already in the local evidence stack and no held-label blind external asset has been acquired.",
            "allowed_use": "Keep external validation readiness NO-GO.",
        },
    ]

    qa_rows = [
        {
            "check": "All source files exist",
            "result": "PASS" if not missing else "FAIL",
            "detail": f"sources={len(SOURCES)}",
        },
        {
            "check": "Five 4TU evidence layers audited",
            "result": "PASS" if len(layer_rows) == 5 else "FAIL",
            "detail": f"layers={len(layer_rows)}",
        },
        {
            "check": "Matrix rows generated",
            "result": "PASS" if len(matrix_rows) > 0 else "FAIL",
            "detail": f"rows={len(matrix_rows)}",
        },
        {
            "check": "No main confirmation upgrade asserted",
            "result": "PASS" if all(row["upgrade_to_main_confirmation"] is False for row in layer_rows) else "FAIL",
            "detail": "4TU remains stress-test/feasibility-boundary evidence.",
        },
        {
            "check": "Submission readiness remains false",
            "result": "PASS",
            "detail": "This audit does not close external validation, figures, DOI/rights or Reporting Summary gates.",
        },
    ]

    write_csv(
        OUT_DIR / "4tu_model_family_extension_matrix.csv",
        [
            "layer_id",
            "evidence_layer",
            "model_family",
            "target_field",
            "model",
            "variant",
            "n_rows",
            "test_balanced_accuracy_mean",
            "balanced_accuracy_delta_mean",
            "balanced_accuracy_delta_std",
            "prediction_flip_rate_mean",
            "directional_drop_support",
            "material_drop_support",
            "claim_use",
            "limitation",
            "source_file",
        ],
        matrix_rows,
    )
    write_csv(
        OUT_DIR / "4tu_evidence_layer_upgrade_decisions.csv",
        [
            "layer_id",
            "evidence_layer",
            "model_family",
            "source_file",
            "input_rows",
            "selected_counterfactual_rows",
            "aggregate_rows",
            "strongest_target",
            "strongest_variant",
            "strongest_delta_mean",
            "claim_use",
            "upgrade_to_main_confirmation",
            "reason",
        ],
        layer_rows,
    )
    write_csv(
        OUT_DIR / "4tu_claim_upgrade_decision.csv",
        ["decision_id", "question", "decision", "evidence", "allowed_use"],
        decision_rows,
    )
    write_csv(OUT_DIR / "4tu_model_family_extension_audit_qa.csv", ["check", "result", "detail"], qa_rows)

    top_rows = sorted(matrix_rows, key=lambda row: float(row["balanced_accuracy_delta_mean"]))[:10]
    md_lines = [
        "# 4TU Model-Family Extension Audit",
        "",
        "Status: `4tu_model_family_extension_audit_ready_stress_test_only`",
        "",
        "This audit asks whether current 4TU evidence can be upgraded into the same kind of five-model confirmation matrix used for Mojahid and Res-SAM. The answer is no. The current value of 4TU is stress-test and feasibility-boundary evidence.",
        "",
        "## Evidence Layers",
        "",
        "| layer | model family | aggregate rows | strongest target | strongest variant | strongest delta | allowed use |",
        "| --- | --- | ---: | --- | --- | ---: | --- |",
    ]
    for row in layer_rows:
        delta = row["strongest_delta_mean"]
        delta_text = f"{float(delta):.4f}" if delta != "" else ""
        md_lines.append(
            f"| {row['evidence_layer']} | {row['model_family']} | {row['aggregate_rows']} | "
            f"{row['strongest_target']} | {row['strongest_variant']} | {delta_text} | {row['claim_use']} |"
        )
    md_lines.extend(
        [
            "",
            "## Strongest Counterfactual Drops",
            "",
            "| layer | target | model | variant | delta_mean | flip_mean | material_drop |",
            "| --- | --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in top_rows:
        md_lines.append(
            f"| {row['evidence_layer']} | {row['target_field']} | {row['model']} | {row['variant']} | "
            f"{float(row['balanced_accuracy_delta_mean']):.4f} | {float(row['prediction_flip_rate_mean']):.4f} | {row['material_drop_support']} |"
        )
    md_lines.extend(
        [
            "",
            "## Boundary",
            "",
            "4TU should remain a counterfactual stress-test and failure-mode/feasibility-boundary layer. It must not be used as a main five-model confirmation layer or as blind external validation evidence until label structure, grouped split coverage and external held-label status are resolved.",
            "",
        ]
    )
    write_text(OUT_DIR / "4tu_model_family_extension_audit.md", "\n".join(md_lines))

    summary = {
        "package": "4tu_model_family_extension_audit_20260810",
        "evidence_layers": len(layer_rows),
        "matrix_rows": len(matrix_rows),
        "decision_rows": len(decision_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "upgrade_to_main_confirmation": False,
        "allowed_use": "stress_test_and_feasibility_boundary",
        "external_validation_closed": False,
        "submission_ready": False,
        "status": "4tu_model_family_extension_audit_ready_stress_test_only",
    }
    write_text(OUT_DIR / "4tu_model_family_extension_audit_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    desktop_section = f"""### 18.69 4TU model-family extension audit 更新

已新增 4TU model-family extension audit 包。这个包把 4TU 当前已经完成的五类证据层统一审计：summary-feature fixed split、raw-pixel fixed split、HOG seed sweep、small-CNN seed sweep 和 HOG group-aware repeated split。

新增目录：
`{OUT_DIR}`

新增材料：
1. `4tu_model_family_extension_matrix.csv`
2. `4tu_evidence_layer_upgrade_decisions.csv`
3. `4tu_claim_upgrade_decision.csv`
4. `4tu_model_family_extension_audit_qa.csv`
5. `4tu_model_family_extension_audit.md`
6. `4tu_model_family_extension_audit_summary.json`

当前结果：
1. evidence_layers = {len(layer_rows)}
2. matrix_rows = {len(matrix_rows)}
3. decision_rows = {len(decision_rows)}
4. qa_pass = {str(summary['qa_pass']).lower()}
5. upgrade_to_main_confirmation = false
6. external_validation_closed = false
7. submission_ready = false
8. 当前状态：`4tu_model_family_extension_audit_ready_stress_test_only`

结论边界：
1. 4TU 可以强化 stress-test / failure-mode / feasibility-boundary 论证。
2. 4TU 现在不能升级为与 Mojahid/Res-SAM 同口径的主五模型确认层。
3. 4TU 不能替代 held-label blind external validation。
4. 论文中仍应把 4TU 放在 Figure 4/Figure 5 或讨论边界，而不是主结论确认。
"""
    desktop_plan_updated = update_desktop_plan(desktop_section)
    summary["desktop_plan_updated"] = desktop_plan_updated
    write_text(OUT_DIR / "4tu_model_family_extension_audit_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not summary["qa_pass"]:
        raise SystemExit("4TU model-family extension audit QA failed")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
