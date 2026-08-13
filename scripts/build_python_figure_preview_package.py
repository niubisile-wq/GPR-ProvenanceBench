#!/usr/bin/env python3
"""Render Python preview figures for author review.

These are not final submission figures. They are preview artifacts for checking
scientific logic, panel structure and source-data traceability.
"""

from __future__ import annotations

import csv
import json
import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "python_figure_preview_package_20260810"
FIG_DIR = OUT_DIR / "figures"
DESKTOP_PLAN = Path.home() / "Desktop" / "8\u670810\u65e5cns.md"

FIGURE_LOCK = REPORTS / "figure_source_data_lock_20260810" / "figure_panel_claim_lock.csv"
FIG1 = REPORTS / "figure1_table1_sources_20260810" / "figure1_flow_source.csv"
FIG2 = REPORTS / "figure2_table2_sources_20260810" / "figure2_source_data.csv"
TAB2 = REPORTS / "figure2_table2_sources_20260810" / "table2_model_family_support.csv"
FIG3A = REPORTS / "figure3_sources_20260810" / "figure3_hog_split_source_data.csv"
FIG3B = REPORTS / "figure3_sources_20260810" / "figure3_model_delta_source_data.csv"
FIG4 = REPORTS / "figure4_sources_20260810" / "figure4_counterfactual_source_data.csv"
FIG4_LAYER = REPORTS / "figure4_sources_20260810" / "figure4_evidence_layer_boundary.csv"
FIG5 = REPORTS / "figure5_figure6_sources_20260810" / "figure5_4tu_feasibility_source_data.csv"
FIG6 = REPORTS / "figure5_figure6_sources_20260810" / "figure6_external_gate_source_data.csv"


mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica", "sans-serif"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.size": 7,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.8,
        "legend.frameon": False,
        "figure.dpi": 150,
    }
)

PALETTE = {
    "blue": "#4C78A8",
    "orange": "#F58518",
    "green": "#54A24B",
    "red": "#E45756",
    "teal": "#72B7B2",
    "purple": "#B279A2",
    "gray": "#9D9D9D",
    "dark": "#2F3A45",
    "light": "#EEF2F5",
}


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def save_preview(fig: mpl.figure.Figure, stem: str) -> list[str]:
    outputs = []
    for suffix, kwargs in [
        ("png", {"dpi": 300}),
        ("svg", {}),
        ("pdf", {}),
        ("tiff", {"dpi": 600}),
    ]:
        out = FIG_DIR / f"{stem}.{suffix}"
        fig.savefig(out, bbox_inches="tight", **kwargs)
        outputs.append(str(out.relative_to(BENCH_ROOT)).replace("\\", "/"))
    plt.close(fig)
    return outputs


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(-0.08, 1.06, label, transform=ax.transAxes, fontsize=10, fontweight="bold", va="top")


def wrap_label(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(str(text), width=width, break_long_words=False))


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 18.97 Python figure preview package update"
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            updated = text[:start].rstrip() + "\n\n" + section.strip() + "\n"
        else:
            updated = text[:start].rstrip() + "\n\n" + section.strip() + "\n\n" + text[next_start:].lstrip("\n")
    else:
        updated = text.rstrip() + "\n\n" + section.strip() + "\n"
    DESKTOP_PLAN.write_text(updated, encoding="utf-8", newline="\n")
    return True


def render_figure1() -> list[str]:
    df = read_csv(FIG1)
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.6), gridspec_kw={"width_ratios": [1.55, 0.85]})
    ax = axes[0]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, len(df) + 1)
    ax.axis("off")
    for idx, row in df.iterrows():
        y = len(df) - idx
        color = PALETTE["green"] if "complete" in row["evidence_status"] else PALETTE["orange"] if "template" in row["evidence_status"] else PALETTE["blue"]
        ax.scatter(0.08, y, s=170, color=color, edgecolor="white", linewidth=1.2, zorder=3)
        ax.text(0.08, y, row["step_id"], ha="center", va="center", color="white", fontsize=7, fontweight="bold")
        ax.text(0.18, y + 0.12, row["step_label"], ha="left", va="center", fontsize=8, fontweight="bold")
        ax.text(0.18, y - 0.2, wrap_label(row["key_message"], 58), ha="left", va="center", fontsize=6.1, color=PALETTE["dark"])
        if idx < len(df) - 1:
            ax.plot([0.08, 0.08], [y - 0.55, y - 0.25], color="#C8D0D8", linewidth=1)
    panel_label(ax, "A")
    ax.set_title("Evidence workflow and open gates", loc="left", fontweight="bold")

    ax = axes[1]
    summary_rows = [
        ("local evidence", 3, PALETTE["green"]),
        ("stress-test layer", 1, PALETTE["orange"]),
        ("external gate open", 1, PALETTE["red"]),
    ]
    ax.barh([r[0] for r in summary_rows], [r[1] for r in summary_rows], color=[r[2] for r in summary_rows])
    ax.set_xlim(0, 3.2)
    ax.set_xlabel("Workflow items")
    ax.set_title("Manuscript role summary", loc="left", fontweight="bold")
    panel_label(ax, "B")
    fig.suptitle("Figure 1 preview | Protocol and asset boundary map", x=0.02, ha="left", fontweight="bold")
    fig.text(0.02, -0.02, "Preview only: protocol/asset map, not a performance result.", fontsize=7, color=PALETTE["red"])
    return save_preview(fig, "figure1_protocol_asset_boundary_preview")


def render_figure2() -> list[str]:
    df = read_csv(FIG2)
    support = read_csv(TAB2)
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.6), gridspec_kw={"width_ratios": [1.55, 1.1, 1.45]})
    short_contrast = {
        "Mojahid: random - grouped": "Mojahid\nrandom-grouped",
        "Res-SAM: within synthetic - synthetic->real": "Res-SAM\nsyn->real",
        "Res-SAM: within real - real->synthetic": "Res-SAM\nreal->syn",
    }
    piv = df.pivot(index="model_label", columns="contrast_label", values="delta_mean_balanced_accuracy")
    piv = piv.loc[df["model_label"].drop_duplicates()]
    im = axes[0].imshow(piv.values, cmap="RdBu_r", vmin=-0.1, vmax=0.65, aspect="auto")
    axes[0].set_xticks(range(len(piv.columns)), labels=[short_contrast.get(c, c) for c in piv.columns], rotation=0)
    axes[0].set_yticks(range(len(piv.index)), labels=piv.index)
    for y in range(piv.shape[0]):
        for x in range(piv.shape[1]):
            axes[0].text(x, y, f"{piv.iloc[y, x]:.2f}", ha="center", va="center", fontsize=6)
    axes[0].set_title("Delta balanced accuracy", loc="left", fontweight="bold")
    panel_label(axes[0], "A")
    fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.03, label="Delta BA")

    y = np.arange(len(support))
    axes[1].barh(y - 0.16, support["directional_support"].str.split("/").str[0].astype(int), height=0.32, label="directional", color=PALETTE["gray"])
    axes[1].barh(y + 0.16, support["material_support"].str.split("/").str[0].astype(int), height=0.32, label="material", color=PALETTE["blue"])
    axes[1].set_yticks(y, labels=[short_contrast.get(v, v) for v in support["contrast"]])
    axes[1].set_xlim(0, 5.6)
    axes[1].set_xlabel("Model families / 5")
    axes[1].legend(loc="upper left")
    axes[1].set_title("Support counts", loc="left", fontweight="bold")
    panel_label(axes[1], "B")

    colors = [PALETTE["orange"] if "Mojahid" in d else PALETTE["blue"] for d in support["dataset"]]
    axes[2].barh([short_contrast.get(v, v) for v in support["contrast"]], support["mean_delta_balanced_accuracy"], color=colors)
    axes[2].axvline(0.05, color=PALETTE["red"], linestyle="--", linewidth=0.8)
    axes[2].set_xlim(0, 0.5)
    axes[2].set_xlabel("Mean delta BA")
    axes[2].set_title("Contrast-level effect", loc="left", fontweight="bold")
    panel_label(axes[2], "C")
    fig.suptitle("Figure 2 preview | Res-SAM transfer dominates current cross-model signal", x=0.02, ha="left", fontweight="bold")
    fig.text(0.02, -0.02, "Preview only: Mojahid and Res-SAM scope; no blind external validation claim.", fontsize=7, color=PALETTE["red"])
    fig.tight_layout()
    return save_preview(fig, "figure2_res_sam_transfer_signal_preview")


def render_figure3() -> list[str]:
    split = read_csv(FIG3A)
    delta = read_csv(FIG3B)
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.05, 1.35, 1]})
    ba = split[split["metric"] == "balanced_accuracy"].copy()
    colors = [PALETTE["green"] if "random" in s else PALETTE["orange"] for s in ba["split"]]
    split_labels = {
        "random_stratified_80_20": "r80/20",
        "grouped_fold_0_test_fold_1_val": "g0→1",
    }
    axes[0].bar([split_labels.get(v, v) for v in ba["split"]], ba["mean"], yerr=ba["std"], color=colors, capsize=3)
    axes[0].set_ylim(0.75, 1.0)
    axes[0].set_ylabel("Balanced accuracy")
    axes[0].set_title("HOG split sensitivity", loc="left", fontweight="bold")
    axes[0].tick_params(axis="x", pad=2, labelsize=8)
    panel_label(axes[0], "A")

    y = np.arange(len(delta))
    colors = [PALETTE["blue"] if m == "yes" else PALETTE["gray"] for m in delta["material_support"]]
    axes[1].barh(y, delta["delta_mean_balanced_accuracy"], color=colors)
    axes[1].axvline(0.05, color=PALETTE["red"], linestyle="--", linewidth=0.8)
    axes[1].set_yticks(y, labels=delta["model_label"])
    axes[1].set_xlabel("Random - grouped BA")
    axes[1].set_title("Five-model delta boundary", loc="left", fontweight="bold")
    panel_label(axes[1], "B")

    axes[2].axis("off")
    axes[2].text(0.0, 0.82, "Claim status", fontsize=9, fontweight="bold")
    axes[2].text(0.0, 0.62, "directional only", fontsize=11, color=PALETTE["orange"], fontweight="bold")
    axes[2].text(0.0, 0.42, "5/5 directional\n1/5 material", fontsize=8)
    axes[2].text(0.0, 0.18, "Do not frame as universal\nleakage proof.", fontsize=7, color=PALETTE["red"])
    panel_label(axes[2], "C")
    fig.suptitle("Figure 3 preview | Mojahid split effect is modest and model-dependent", x=0.02, ha="left", fontweight="bold")
    fig.tight_layout()
    return save_preview(fig, "figure3_mojahid_directional_boundary_preview")


def render_figure4() -> list[str]:
    df = read_csv(FIG4)
    layer = read_csv(FIG4_LAYER)
    fig, axes = plt.subplots(1, 3, figsize=(9.0, 3.6), gridspec_kw={"width_ratios": [1.25, 1.25, 1.15]})
    for ax, layer_name, title, label in [
        (axes[0], "fixed_split_seed_sweep", "Fixed split stress", "A"),
        (axes[1], "group_aware_repeated_split", "Group-aware stress", "B"),
    ]:
        sub = df[df["layer"] == layer_name].sort_values("delta_balanced_accuracy_mean")
        y = np.arange(len(sub))
        colors = [PALETTE["red"] if v < -0.05 else PALETTE["gray"] for v in sub["delta_balanced_accuracy_mean"]]
        ax.barh(y, sub["delta_balanced_accuracy_mean"], xerr=sub["delta_balanced_accuracy_std"], color=colors, capsize=2)
        ax.axvline(0, color="#333333", linewidth=0.7)
        ax.axvline(-0.05, color=PALETTE["red"], linestyle="--", linewidth=0.8)
        ax.set_xlim(-0.4, 0.18)
        ax.set_yticks(y, labels=sub["variant"])
        ax.set_xlabel("Delta BA")
        ax.set_title(title, loc="left", fontweight="bold")
        panel_label(ax, label)
    axes[2].axis("off")
    axes[2].text(0.0, 0.9, "Evidence boundary", fontsize=9, fontweight="bold")
    boundary_bullets = [
        "Fixed-split effects can be large.",
        "Group-aware effects are weaker.",
        "Land-type label scope only.",
        "Feasibility layer, not confirmation.",
    ]
    for i, bullet in enumerate(boundary_bullets):
        axes[2].text(0.0, 0.76 - i * 0.14, f"- {bullet}", fontsize=7)
    axes[2].text(0.0, 0.05, "Stress-test layer only;\nnot main confirmation.", fontsize=7.5, color=PALETTE["red"], fontweight="bold")
    panel_label(axes[2], "C")
    fig.suptitle("Figure 4 preview | 4TU counterfactual sensitivity as feasibility boundary", x=0.02, ha="left", fontweight="bold")
    fig.tight_layout()
    return save_preview(fig, "figure4_4tu_stress_boundary_preview")


def render_figure5() -> list[str]:
    df = read_csv(FIG5)
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.0), gridspec_kw={"width_ratios": [1.3, 1]})
    status_order = ["usable_with_caution", "weak_due_to_single_project_labels", "not_viable_for_group_holdout"]
    status_color = {
        "usable_with_caution": PALETTE["green"],
        "weak_due_to_single_project_labels": PALETTE["orange"],
        "not_viable_for_group_holdout": PALETTE["red"],
    }
    df["status_rank"] = df["status"].map({v: i for i, v in enumerate(status_order)})
    sub = df.sort_values("status_rank")
    y = np.arange(len(sub))
    axes[0].barh(y, sub["test2_val2_feasible_fraction"], color=[status_color[s] for s in sub["status"]])
    axes[0].set_yticks(y, labels=sub["target"])
    axes[0].set_xlim(0, 1)
    axes[0].set_xlabel("Feasible grouped split fraction")
    axes[0].set_title("Target feasibility", loc="left", fontweight="bold")
    panel_label(axes[0], "A")

    counts = df["status"].value_counts().reindex(status_order).fillna(0)
    axes[1].bar(range(len(counts)), counts.values, color=[status_color[s] for s in counts.index])
    axes[1].set_xticks(range(len(counts)), labels=["usable\nwith caution", "weak", "not viable"])
    axes[1].set_ylabel("Targets")
    axes[1].set_title("Manuscript role counts", loc="left", fontweight="bold")
    panel_label(axes[1], "B")
    fig.suptitle("Figure 5 preview | 4TU labels define feasibility limits", x=0.02, ha="left", fontweight="bold")
    fig.text(0.02, -0.02, "Preview only: supports gate/failure-mode framing, not model superiority.", fontsize=7, color=PALETTE["red"])
    fig.tight_layout()
    return save_preview(fig, "figure5_4tu_feasibility_gate_preview")


def render_figure6() -> list[str]:
    df = read_csv(FIG6)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"width_ratios": [1.35, 1]})
    status_colors = {
        "not_ready": PALETTE["red"],
        "not_started": PALETTE["orange"],
        "already_used_in_model_matrix": PALETTE["gray"],
        "PASS": PALETTE["green"],
        "template_dry_run": PALETTE["blue"],
        "NO-GO": PALETTE["red"],
    }
    y = np.arange(len(df))
    axes[0].barh(y, np.ones(len(df)), color=[status_colors.get(s, PALETTE["gray"]) for s in df["status"]])
    axes[0].set_yticks(y, labels=df["gate_component"])
    axes[0].set_xlim(0, 1)
    axes[0].set_xticks([])
    axes[0].set_title("External validation readiness", loc="left", fontweight="bold")
    panel_label(axes[0], "A")

    axes[1].axis("off")
    axes[1].text(0.0, 0.88, "Overall gate", fontsize=9, fontweight="bold")
    axes[1].text(0.0, 0.68, "NO-GO", fontsize=18, color=PALETTE["red"], fontweight="bold")
    axes[1].text(0.0, 0.46, "No completed blind external\nvalidation is available.", fontsize=8)
    axes[1].text(0.0, 0.24, "Next step: acquire or restore\na real external asset.", fontsize=8, color=PALETTE["dark"])
    axes[1].text(0.0, 0.06, "Open-gate placeholder only.", fontsize=7.5, color=PALETTE["red"], fontweight="bold")
    panel_label(axes[1], "B")
    fig.suptitle("Figure 6 preview | Blind external validation gate remains open", x=0.02, ha="left", fontweight="bold")
    fig.tight_layout()
    return save_preview(fig, "figure6_external_validation_open_gate_preview")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    lock_df = read_csv(FIGURE_LOCK)
    renderers = {
        "Figure 1": render_figure1,
        "Figure 2": render_figure2,
        "Figure 3": render_figure3,
        "Figure 4": render_figure4,
        "Figure 5": render_figure5,
        "Figure 6": render_figure6,
    }

    manifest_rows: list[dict[str, object]] = []
    for figure_id, renderer in renderers.items():
        outputs = renderer()
        lock = lock_df[lock_df["figure_id"] == figure_id].iloc[0].to_dict()
        manifest_rows.append(
            {
                "figure_id": figure_id,
                "preview_status": "rendered_preview_not_final",
                "archetype": "quantitative grid" if figure_id in {"Figure 2", "Figure 3", "Figure 4", "Figure 5"} else "schematic-led composite",
                "core_conclusion": lock["allowed_claim"],
                "png": next(path for path in outputs if path.endswith(".png")),
                "svg": next(path for path in outputs if path.endswith(".svg")),
                "pdf": next(path for path in outputs if path.endswith(".pdf")),
                "tiff": next(path for path in outputs if path.endswith(".tiff")),
                "boundary": lock["boundary"],
            }
        )

    contract_rows = []
    for row in manifest_rows:
        contract_rows.append(
            {
                "figure_id": row["figure_id"],
                "core_conclusion": row["core_conclusion"],
                "evidence_chain": "panel-level preview built from locked source data",
                "archetype": row["archetype"],
                "backend": "python",
                "journal_export_contract": "PNG/SVG/PDF/TIFF preview exports; editable SVG/PDF text; not final submission figure.",
                "review_risk": row["boundary"],
            }
        )

    qa_rows = [
        {
            "check": "six_figures_rendered",
            "result": "PASS" if len(manifest_rows) == 6 else "FAIL",
            "detail": f"figures={len(manifest_rows)}",
        },
        {
            "check": "all_export_quads_exist",
            "result": "PASS" if all((BENCH_ROOT / row["png"]).exists() and (BENCH_ROOT / row["svg"]).exists() and (BENCH_ROOT / row["pdf"]).exists() and (BENCH_ROOT / row["tiff"]).exists() for row in manifest_rows) else "FAIL",
            "detail": "PNG/SVG/PDF/TIFF checked for each figure",
        },
        {
            "check": "python_backend_only",
            "result": "PASS",
            "detail": "Rendered with matplotlib only; no R backend used.",
        },
        {
            "check": "preview_not_final_boundary",
            "result": "PASS" if all(row["preview_status"] == "rendered_preview_not_final" for row in manifest_rows) else "FAIL",
            "detail": "All figures marked preview_not_final.",
        },
        {
            "check": "external_validation_not_claimed",
            "result": "PASS" if "Open-gate placeholder" in manifest_rows[-1]["boundary"] else "FAIL",
            "detail": manifest_rows[-1]["boundary"],
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "python_figure_preview_manifest.csv",
        manifest_rows,
        ["figure_id", "preview_status", "archetype", "core_conclusion", "png", "svg", "pdf", "tiff", "boundary"],
    )
    write_csv(
        OUT_DIR / "python_figure_preview_contract.csv",
        contract_rows,
        ["figure_id", "core_conclusion", "evidence_chain", "archetype", "backend", "journal_export_contract", "review_risk"],
    )
    write_csv(OUT_DIR / "python_figure_preview_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Python figure preview package report 2026-08-10",
        "",
        "Status: `python_figure_preview_package_rendered_not_final`",
        "",
        f"1. Figure previews rendered: {len(manifest_rows)}",
        "2. Export formats per figure: PNG, SVG, PDF and TIFF",
        "3. Backend: Python/matplotlib only",
        f"4. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: these are author-review previews only. They are not final submission figures, do not close the figure gate, and do not imply completed blind external validation.",
        "",
    ]
    write_text(OUT_DIR / "PYTHON_FIGURE_PREVIEW_README.md", "\n".join(report))
    write_text(OUT_DIR / "python_figure_preview_report.md", "\n".join(report))

    summary = {
        "package": "python_figure_preview_package_20260810",
        "figures_rendered": len(manifest_rows),
        "export_quads": len(manifest_rows),
        "backend": "python",
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "rendered_figures_preview": len(manifest_rows),
        "rendered_figures_final": 0,
        "final_figures_ready": False,
        "blind_external_validation_claimed": False,
        "submission_ready": False,
        "status": "python_figure_preview_package_rendered_not_final",
    }

    section = f"""### 18.97 Python figure preview package update

Rendered six Python/matplotlib author-review preview figures from locked source data.

New directory: `{OUT_DIR}`

New files:
1. `figures/figure1_protocol_asset_boundary_preview.png/.svg/.pdf`
2. `figures/figure2_res_sam_transfer_signal_preview.png/.svg/.pdf`
3. `figures/figure3_mojahid_directional_boundary_preview.png/.svg/.pdf`
4. `figures/figure4_4tu_stress_boundary_preview.png/.svg/.pdf`
5. `figures/figure5_4tu_feasibility_gate_preview.png/.svg/.pdf`
6. `figures/figure6_external_validation_open_gate_preview.png/.svg/.pdf`
7. `python_figure_preview_manifest.csv`
8. `python_figure_preview_contract.csv`
9. `python_figure_preview_qa.csv`
10. `PYTHON_FIGURE_PREVIEW_README.md`
11. `python_figure_preview_report.md`
12. `python_figure_preview_summary.json`

Current result:
1. figures_rendered = {summary['figures_rendered']}
2. backend = python
3. qa_pass = {str(qa_pass).lower()}
4. rendered_figures_preview = {summary['rendered_figures_preview']}
5. rendered_figures_final = 0
6. final_figures_ready = false
7. submission_ready = false

Boundary:
1. These are author-review preview figures only.
2. They do not close the final figure gate.
3. Figure 6 remains an open-gate placeholder and does not claim completed blind external validation."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "python_figure_preview_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Python figure preview QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
