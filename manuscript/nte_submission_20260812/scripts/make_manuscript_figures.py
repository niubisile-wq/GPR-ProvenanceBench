from pathlib import Path
import textwrap

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


ROOT = Path(__file__).resolve().parents[3]
MANUSCRIPT = Path(__file__).resolve().parents[1]
OUT = MANUSCRIPT / "figures"
REPORTS = ROOT / "reports"


mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "font.size": 7,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.7,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.frameon": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "figure.dpi": 150,
})

BLUE = "#4C78A8"
TEAL = "#59A14F"
ORANGE = "#F28E2B"
RED = "#E15759"
GRAY = "#6B7280"
LIGHT = "#EEF2F6"
DARK = "#1F2937"


def wrap_label(s, width=22):
    return "\n".join(textwrap.wrap(str(s), width=width, break_long_words=False))


def panel_label(ax, label):
    ax.text(-0.07, 1.04, label, transform=ax.transAxes, ha="left", va="bottom",
            fontsize=9, fontweight="bold")


def save(fig, name):
    for ext in ("pdf", "svg", "png"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight",
                    dpi=450 if ext == "png" else None)
    plt.close(fig)


def fig1_workflow():
    flow = pd.read_csv(REPORTS / "figure1_table1_sources_20260810" / "figure1_flow_source.csv")
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.axis("off")
    ys = np.linspace(0.86, 0.18, len(flow))
    colors = [BLUE, TEAL, ORANGE, "#9C755F", RED]
    for i, row in flow.iterrows():
        y = ys[i]
        box = FancyBboxPatch(
            (0.08, y - 0.062), 0.84, 0.118,
            boxstyle="round,pad=0.014,rounding_size=0.018",
            facecolor="white", edgecolor=colors[i], linewidth=1.4
        )
        ax.add_patch(box)
        ax.text(0.11, y, f"{i + 1}", ha="center", va="center", fontsize=9,
                color="white", fontweight="bold",
                bbox=dict(boxstyle="circle,pad=0.25", facecolor=colors[i], edgecolor="none"))
        ax.text(0.17, y + 0.026, row["step_label"], ha="left", va="center",
                fontsize=7.7, fontweight="bold", color=DARK)
        ax.text(0.17, y - 0.017, wrap_label(row["key_message"], 92),
                ha="left", va="center", fontsize=6.5, color=DARK)
        ax.text(0.91, y, wrap_label(row["evidence_status"].replace("_", " "), 20),
                ha="right", va="center", fontsize=6.2, color=colors[i])
        if i < len(flow) - 1:
            ax.add_patch(FancyArrowPatch((0.5, y - 0.078), (0.5, ys[i + 1] + 0.078),
                                         arrowstyle="-|>", mutation_scale=8,
                                         linewidth=1.0, color=GRAY))
    ax.text(0.02, 0.93, "a", transform=ax.transAxes, fontsize=9, fontweight="bold")
    ax.text(0.5, 0.05, "Evidence is interpreted only after the asset role and evaluation gate are fixed.",
            ha="center", va="center", fontsize=7.2, color=DARK)
    save(fig, "fig1_workflow")


def fig2_cross_model():
    data = pd.read_csv(REPORTS / "figure2_table2_sources_20260810" / "figure2_source_data.csv")
    order = [
        "HOG + RBF-SVM", "LBP + LinearSVM", "TinyCNN",
        "ResNet18 emb. + LinearSVM", "EfficientNetB0 emb. + LinearSVM"
    ]
    contrast_order = [
        "Mojahid: random - grouped",
        "Res-SAM: within synthetic - synthetic->real",
        "Res-SAM: within real - real->synthetic",
    ]
    pivot = data.pivot(index="model_label", columns="contrast_label",
                       values="delta_mean_balanced_accuracy").loc[order, contrast_order]

    fig, ax = plt.subplots(figsize=(7.2, 3.45))
    y = np.arange(len(order))
    height = 0.22
    colors = [GRAY, BLUE, TEAL]
    labels = ["Mojahid random - grouped", "Res-SAM synthetic to real", "Res-SAM real to synthetic"]
    for j, col in enumerate(contrast_order):
        vals = pivot[col].to_numpy()
        ax.barh(y + (j - 1) * height, vals, height=height,
                color=colors[j], edgecolor="white", linewidth=0.5, label=labels[j])
        for yy, val in zip(y + (j - 1) * height, vals):
            ax.text(val + (0.012 if val >= 0 else -0.012), yy, f"{val:.2f}",
                    va="center", ha="left" if val >= 0 else "right", fontsize=6.2)
    ax.axvline(0, color="#111827", lw=0.8)
    ax.axvline(0.05, color="#9CA3AF", lw=0.8, ls="--")
    ax.text(0.052, -0.65, "material threshold", fontsize=6.4, color=GRAY)
    ax.set_yticks(y)
    ax.set_yticklabels(order)
    ax.invert_yaxis()
    ax.set_xlabel("Balanced-accuracy delta")
    ax.set_xlim(-0.08, 0.70)
    ax.legend(loc="lower center", bbox_to_anchor=(0.55, -0.19), ncol=3, fontsize=6.4)
    panel_label(ax, "a")
    save(fig, "fig2_cross_model_transfer")


def fig3_split_sensitivity():
    split = pd.read_csv(REPORTS / "figure3_sources_20260810" / "figure3_hog_split_source_data.csv")
    delta = pd.read_csv(REPORTS / "figure3_sources_20260810" / "figure3_model_delta_source_data.csv")
    split = split[split["metric"].eq("balanced_accuracy")].copy()
    split["split_label"] = split["split"].map({
        "random_stratified_80_20": "Random",
        "grouped_fold_0_test_fold_1_val": "Grouped"
    })
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.85), gridspec_kw={"width_ratios": [0.95, 1.55]})

    ax = axes[0]
    xpos = np.arange(len(split))
    ax.bar(xpos, split["mean"], yerr=split["std"], capsize=3,
           color=[BLUE if x == "Random" else ORANGE for x in split["split_label"]],
           edgecolor="white", linewidth=0.5)
    for x, (_, row) in zip(xpos, split.iterrows()):
        ax.text(x, row["mean"] + 0.018, f"{row['mean']:.3f}", ha="center", fontsize=6.5)
    ax.set_xticks(xpos)
    ax.set_xticklabels(split["split_label"])
    ax.set_ylim(0.78, 0.99)
    ax.set_ylabel("Balanced accuracy")
    ax.set_title("HOG + RBF-SVM on Mojahid", fontsize=7.5)
    panel_label(ax, "a")

    ax = axes[1]
    delta = delta.sort_values("delta_mean_balanced_accuracy")
    colors = [BLUE if m else "#B8C2CC" for m in delta["material_support"]]
    ax.barh(np.arange(len(delta)), delta["delta_mean_balanced_accuracy"], color=colors,
            edgecolor="white", linewidth=0.5)
    ax.axvline(0.05, color="#9CA3AF", lw=0.8, ls="--")
    ax.set_yticks(np.arange(len(delta)))
    ax.set_yticklabels([wrap_label(x, 22) for x in delta["model_label"]])
    ax.set_xlabel("Random - grouped balanced accuracy")
    ax.set_xlim(0, 0.115)
    for i, v in enumerate(delta["delta_mean_balanced_accuracy"]):
        ax.text(v + 0.003, i, f"{v:.3f}", va="center", fontsize=6.3)
    ax.set_title("Five-family split contrast", fontsize=7.5)
    panel_label(ax, "b")
    fig.tight_layout(w_pad=2.0)
    save(fig, "fig3_mojahid_split")


def fig4_stress_repair():
    cf = pd.read_csv(REPORTS / "figure4_sources_20260810" / "figure4_counterfactual_source_data.csv")
    boundary = pd.read_csv(REPORTS / "figure4_sources_20260810" / "figure4_evidence_layer_boundary.csv")
    key = cf[cf["variant"].isin(["log_clip", "zscore_clip", "time_reverse", "remove_top_band"])]
    key = key.copy()
    key["layer_label"] = key["layer"].map({
        "fixed_split_seed_sweep": "Fixed split",
        "group_aware_repeated_split": "Project-aware"
    })
    variants = ["log_clip", "zscore_clip", "time_reverse", "remove_top_band"]
    layer_order = ["Fixed split", "Project-aware"]

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={"width_ratios": [1.25, 1.10]})
    ax = axes[0]
    x = np.arange(len(variants))
    width = 0.34
    for j, layer in enumerate(layer_order):
        sub = key[key["layer_label"].eq(layer)].set_index("variant").loc[variants]
        vals = sub["delta_balanced_accuracy_mean"].to_numpy()
        errs = sub["delta_balanced_accuracy_std"].to_numpy()
        ax.bar(x + (j - 0.5) * width, vals, yerr=errs, width=width, capsize=2.5,
               color=BLUE if layer == "Fixed split" else ORANGE,
               edgecolor="white", linewidth=0.5, label=layer)
    ax.axhline(0, color="#111827", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([v.replace("_", "\n") for v in variants])
    ax.set_ylabel("Delta balanced accuracy")
    ax.set_title("4TU perturbation response", fontsize=7.5)
    ax.legend(loc="lower right", fontsize=6.5)
    panel_label(ax, "a")

    ax = axes[1]
    boundary = boundary.copy()
    boundary["strongest_delta_mean"] = boundary["strongest_delta_mean"].astype(float)
    boundary = boundary.sort_values("strongest_delta_mean")
    short_labels = {
        "summary_feature_fixed_split": "summary features\nfixed split",
        "raw_pixel_fixed_split": "raw pixels\nfixed split",
        "hog_seed_sweep_fixed_split": "HOG seed sweep\nfixed split",
        "small_cnn_seed_sweep_fixed_split": "small CNN\nfixed split",
        "hog_group_aware_repeated_split": "HOG group-aware\nrepeats",
    }
    y = np.arange(len(boundary))
    ax.barh(y, boundary["strongest_delta_mean"],
            color=[RED if v < -0.1 else ORANGE for v in boundary["strongest_delta_mean"]],
            edgecolor="white", linewidth=0.5)
    ax.axvline(0, color="#111827", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([short_labels.get(x, wrap_label(x.replace("_", " "), 18)) for x in boundary["evidence_layer"]])
    ax.set_xlabel("Strongest delta")
    ax.set_title("Evidence-layer boundary", fontsize=7.5)
    for i, v in enumerate(boundary["strongest_delta_mean"]):
        x_text = max(v + 0.018, -0.375) if v < -0.08 else v - 0.014
        ax.text(x_text, i, f"{v:.2f}", ha="left" if v < -0.08 else "right", va="center", fontsize=6.3)
    panel_label(ax, "b")
    fig.tight_layout(w_pad=2.0)
    save(fig, "fig4_4tu_stress")


def fig5_feasibility():
    data = pd.read_csv(REPORTS / "figure5_figure6_sources_20260810" / "figure5_4tu_feasibility_source_data.csv")
    data = data.sort_values("test2_val2_feasible_fraction")
    status_color = {
        "usable_with_caution": TEAL,
        "weak_due_to_single_project_labels": ORANGE,
        "not_viable_for_group_holdout": RED,
    }
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    y = np.arange(len(data))
    colors = [status_color[s] for s in data["status"]]
    ax.barh(y, data["test2_val2_feasible_fraction"], color=colors,
            edgecolor="white", linewidth=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels([wrap_label(t, 26) for t in data["target"]])
    ax.set_xlabel("Feasible two-test/two-validation project splits")
    ax.set_xlim(0, 1.02)
    ax.set_xticks(np.linspace(0, 1, 6))
    for i, row in data.iterrows():
        idx = list(data.index).index(i)
        val = row["test2_val2_feasible_fraction"]
        ax.text(val + 0.015, idx, f"{val:.2f}", va="center", fontsize=6.5)
        if val > 0.18:
            ax.text(0.02, idx, f"n={int(row['sample_count'])}, projects={int(row['project_count'])}",
                    va="center", fontsize=6.1, color="white")
        else:
            ax.text(0.23, idx, f"n={int(row['sample_count'])}, projects={int(row['project_count'])}",
                    va="center", fontsize=6.1, color=DARK)
    handles = [
        plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=TEAL, label="usable with caution"),
        plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=ORANGE, label="weak label/project support"),
        plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=RED, label="not viable for group holdout"),
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=6.5)
    panel_label(ax, "a")
    save(fig, "fig5_4tu_feasibility")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fig1_workflow()
    fig2_cross_model()
    fig3_split_sensitivity()
    fig4_stress_repair()
    fig5_feasibility()


if __name__ == "__main__":
    main()
