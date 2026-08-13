#!/usr/bin/env python3
"""Build a conservative citation mapping pass for narrative section drafts."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BENCH_ROOT.parent
LIT_ROOT = PROJECT_ROOT / "literature" / "nature_communications_5paper_benchmark_20260810"
OUT_DIR = BENCH_ROOT / "reports" / "narrative_citation_pass_20260810"
DRAFT_DIR = BENCH_ROOT / "reports" / "narrative_section_drafts_20260810"


CANDIDATES = [
    {
        "candidate_id": "P1",
        "authors_short": "Zhou et al.",
        "year": "2025",
        "title": "Reservoir-enhanced segment anything model for subsurface diagnosis",
        "journal": "Nature Communications",
        "doi": "10.1038/s41467-025-67382-4",
        "article_url": "https://www.nature.com/articles/s41467-025-67382-4",
        "local_text": "extracted_text/Zhou_2025_NatCommun_Res-SAM-GPR.txt",
        "support_role": "Direct GPR and Res-SAM background; supports GPR task context, data scarcity and environment variability.",
    },
    {
        "candidate_id": "P2",
        "authors_short": "Zhou et al.",
        "year": "2025",
        "title": "Mitigating data bias and ensuring reliable evaluation of AI models with shortcut hull learning",
        "journal": "Nature Communications",
        "doi": "10.1038/s41467-025-60801-6",
        "article_url": "https://www.nature.com/articles/s41467-025-60801-6",
        "local_text": "extracted_text/Zhou_2025_NatCommun_shortcut-hull-learning.txt",
        "support_role": "Shortcut learning and data-bias evaluation context; supports model-family and overclaim guard logic.",
    },
    {
        "candidate_id": "P3",
        "authors_short": "Brown et al.",
        "year": "2023",
        "title": "Detecting shortcut learning for fair medical AI using shortcut testing",
        "journal": "Nature Communications",
        "doi": "10.1038/s41467-023-39902-7",
        "article_url": "https://www.nature.com/articles/s41467-023-39902-7",
        "local_text": "extracted_text/Brown_2023_NatCommun_shortcut-testing.txt",
        "support_role": "Shortcut testing context; supports the distinction between encoded attributes and actual model reliance.",
    },
    {
        "candidate_id": "P4",
        "authors_short": "Rosenblatt et al.",
        "year": "2024",
        "title": "Data leakage inflates prediction performance in connectome-based machine learning models",
        "journal": "Nature Communications",
        "doi": "10.1038/s41467-024-46150-w",
        "article_url": "https://www.nature.com/articles/s41467-024-46150-w",
        "local_text": "extracted_text/Rosenblatt_2024_NatCommun_data-leakage.txt",
        "support_role": "Data leakage and inflated performance context; supports the random-split inflation warning.",
    },
    {
        "candidate_id": "P5",
        "authors_short": "Joeres et al.",
        "year": "2025",
        "title": "Data splitting to avoid information leakage with DataSAIL",
        "journal": "Nature Communications",
        "doi": "10.1038/s41467-025-58606-8",
        "article_url": "https://www.nature.com/articles/s41467-025-58606-8",
        "local_text": "extracted_text/Joeres_2025_NatCommun_DataSAIL.txt",
        "support_role": "Leakage-aware data splitting context; supports split design and similarity/provenance separation logic.",
    },
    {
        "candidate_id": "P6",
        "authors_short": "Roschewitz et al.",
        "year": "2023",
        "title": "Automatic correction of performance drift under acquisition shift in medical image classification",
        "journal": "Nature Communications",
        "doi": "10.1038/s41467-023-42396-y",
        "article_url": "https://www.nature.com/articles/s41467-023-42396-y",
        "local_text": "screened_supporting/Glocker_2023_NatCommun_acquisition-shift.txt",
        "support_role": "Acquisition-shift and performance-drift background; not GPR-specific.",
    },
]


SEGMENTS = [
    {
        "segment_id": "S001",
        "source_section": "Introduction",
        "source_paragraphs": "I1",
        "core_claim": "GPR recognition is important for subsurface diagnosis, but B-scan interpretation is sensitive to site conditions and limited labels.",
        "claim_type": "background",
        "candidate_ids": "P1",
        "support_grade": "strong background support",
        "insert_after": "After the first GPR context sentence in Introduction paragraph 1.",
        "risk_note": "P1 supports GPR/Res-SAM context; broader application claims may need additional non-CNS domain citations.",
    },
    {
        "segment_id": "S002",
        "source_section": "Introduction",
        "source_paragraphs": "I1-I2",
        "core_claim": "Apparent model generalization can be reshaped by acquisition, provenance or split structure rather than target physics alone.",
        "claim_type": "review-context",
        "candidate_ids": "P4;P5;P6",
        "support_grade": "partial support",
        "insert_after": "After the evaluation-bottleneck sentence in Introduction paragraph 2.",
        "risk_note": "P4/P5 support leakage and split design; P6 supports acquisition shift by analogy outside GPR.",
    },
    {
        "segment_id": "S003",
        "source_section": "Introduction",
        "source_paragraphs": "I2",
        "core_claim": "Random or weak train-test splits can leak similarity information and inflate performance estimates.",
        "claim_type": "method",
        "candidate_ids": "P4;P5",
        "support_grade": "strong support",
        "insert_after": "After the sentence describing random/weak split leakage.",
        "risk_note": "Use these citations for leakage/split design, not as direct evidence for the present GPR results.",
    },
    {
        "segment_id": "S004",
        "source_section": "Introduction",
        "source_paragraphs": "I3-I4",
        "core_claim": "A defensible benchmark needs executable assets, split-aware evaluation, multiple model families and explicit open gates for external validation.",
        "claim_type": "method",
        "candidate_ids": "P2;P5",
        "support_grade": "partial support",
        "insert_after": "After the paragraph introducing the study design.",
        "risk_note": "External blind validation remains an internal protocol gate, not a completed cited result.",
    },
    {
        "segment_id": "S005",
        "source_section": "Discussion",
        "source_paragraphs": "D1",
        "core_claim": "The strongest current executable evidence is Res-SAM environment-transfer fragility across model families.",
        "claim_type": "association",
        "candidate_ids": "P1",
        "support_grade": "background support",
        "insert_after": "Do not cite P1 as evidence for our measured deltas; cite internal source data for those results.",
        "risk_note": "P1 is only the Res-SAM/GPR context paper; our derived metrics remain the primary evidence.",
    },
    {
        "segment_id": "S006",
        "source_section": "Discussion",
        "source_paragraphs": "D2-D3",
        "core_claim": "Shortcut sensitivity should be assessed with model-family and intervention-aware controls rather than one architecture or one split.",
        "claim_type": "method",
        "candidate_ids": "P2;P3;P5",
        "support_grade": "partial support",
        "insert_after": "After the sentence discussing rival explanations and model-family dependence.",
        "risk_note": "P3 is medical-AI context; use as conceptual support, not GPR-specific evidence.",
    },
    {
        "segment_id": "S007",
        "source_section": "Discussion",
        "source_paragraphs": "D3",
        "core_claim": "Acquisition or environment shift can cause performance drift, so environment transfer is an appropriate stress axis.",
        "claim_type": "review-context",
        "candidate_ids": "P1;P6",
        "support_grade": "partial support",
        "insert_after": "After the environment-transfer interpretation sentence.",
        "risk_note": "P6 supports the acquisition-shift concept in medical imaging; P1 anchors the GPR setting.",
    },
    {
        "segment_id": "S008",
        "source_section": "Discussion",
        "source_paragraphs": "D4-D5",
        "core_claim": "Release, source-data and reporting-summary readiness are necessary before submission-ready reproducibility claims.",
        "claim_type": "method",
        "candidate_ids": "internal_artifacts",
        "support_grade": "internal evidence needed",
        "insert_after": "Use companion-artifact and release-readiness reports, not external literature, for this claim.",
        "risk_note": "Do not cite a literature paper as if the repository DOI or public release already exists.",
    },
    {
        "segment_id": "S009",
        "source_section": "Conclusion",
        "source_paragraphs": "C1-C3",
        "core_claim": "The conclusion should state a bounded benchmark contribution, strongest current evidence and remaining external-validation gate.",
        "claim_type": "review-context",
        "candidate_ids": "P1;P4;P5",
        "support_grade": "partial support",
        "insert_after": "Use only where the conclusion restates background rationale; results should cite internal figures/source data.",
        "risk_note": "Conclusion must retain the NO-GO boundary for external blind validation.",
    },
]


RIS_AUTHORS = {
    "P1": [
        "Zhou, Xiren",
        "Liu, Shikang",
        "Yan, Xinyu",
        "Fan, Yizhan",
        "Wang, Xiangyu",
        "Kang, Yu",
        "Cheng, Jian",
        "Chen, Huanhuan",
    ],
    "P2": ["Zhou, Wenhao", "Liu, Faqiang", "Zheng, Hao", "Zhao, Rong"],
    "P3": ["Brown, Alexander", "Tomasev, Nenad", "Freyberg, Jan", "Liu, Yuan", "Karthikesalingam, Alan", "Schrouff, Jessica"],
    "P4": ["Rosenblatt, Matthew", "Tejavibulya, Link", "Jiang, Rongtao", "Noble, Stephanie", "Scheinost, Dustin"],
    "P5": ["Joeres, Roman", "Blumenthal, David B.", "Kalinina, Olga V."],
    "P6": ["Roschewitz, Melanie", "Khara, Galvin", "Yearsley, Joe", "Sharma, Nisha", "James, Jonathan J.", "Ambrozay, Eva", "Heroux, Adam", "Kecskemethy, Peter", "Rijken, Tobias", "Glocker, Ben"],
}


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def candidate_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for candidate in CANDIDATES:
        local_path = LIT_ROOT / candidate["local_text"]
        rows.append(
            {
                **candidate,
                "local_text_exists": str(local_path.exists()).lower(),
                "verification_basis": "local extracted full text" if local_path.exists() else "missing local text; do not use until checked",
                "use_boundary": "Do not cite as evidence for this project's derived metrics unless mapped to internal source data.",
            }
        )
    return rows


def write_ris(path: Path, candidates: list[dict[str, str]]) -> None:
    lines: list[str] = []
    for candidate in candidates:
        lines.append("TY  - JOUR")
        lines.append(f"TI  - {candidate['title']}")
        for author in RIS_AUTHORS.get(candidate["candidate_id"], []):
            lines.append(f"AU  - {author}")
        lines.append(f"T2  - {candidate['journal']}")
        lines.append(f"JO  - {candidate['journal']}")
        lines.append(f"PY  - {candidate['year']}")
        lines.append(f"DO  - {candidate['doi']}")
        lines.append(f"UR  - {candidate['article_url']}")
        lines.append(f"N1  - {candidate['support_role']}")
        lines.append("ER  -")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_html(path: Path, segments: list[dict[str, str]], candidates: list[dict[str, str]]) -> None:
    candidate_lookup = {row["candidate_id"]: row for row in candidates}
    rows = []
    for segment in segments:
        candidate_labels = []
        for candidate_id in segment["candidate_ids"].split(";"):
            candidate = candidate_lookup.get(candidate_id)
            if candidate:
                label = f"{candidate_id}: {candidate['authors_short']} {candidate['year']}"
            else:
                label = candidate_id
            candidate_labels.append(label)
        rows.append(
            "<tr>"
            f"<td>{html.escape(segment['segment_id'])}</td>"
            f"<td>{html.escape(segment['source_section'])}</td>"
            f"<td>{html.escape(segment['core_claim'])}</td>"
            f"<td>{html.escape('; '.join(candidate_labels))}</td>"
            f"<td>{html.escape(segment['support_grade'])}</td>"
            f"<td>{html.escape(segment['risk_note'])}</td>"
            "</tr>"
        )

    body = "\n".join(rows)
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Narrative citation pass 20260810</title>
  <style>
    body {{ font-family: Georgia, serif; margin: 32px; color: #172019; background: #f7f4ec; }}
    h1 {{ font-size: 28px; }}
    table {{ border-collapse: collapse; width: 100%; background: #fffdf7; }}
    th, td {{ border: 1px solid #c9c0ad; padding: 8px; vertical-align: top; }}
    th {{ background: #e7dec9; text-align: left; }}
    td:nth-child(3) {{ width: 34%; }}
  </style>
</head>
<body>
  <h1>Narrative citation pass 20260810</h1>
  <p>Scope: local Nature Communications benchmark/supporting papers only. This is a conservative mapping, not a final reference list.</p>
  <table>
    <thead><tr><th>ID</th><th>Section</th><th>Claim</th><th>Candidates</th><th>Support</th><th>Risk note</th></tr></thead>
    <tbody>
{body}
    </tbody>
  </table>
</body>
</html>
"""
    path.write_text(page, encoding="utf-8")


def write_report(path: Path, segments: list[dict[str, str]], candidates: list[dict[str, str]]) -> None:
    unresolved = [row for row in segments if "internal" in row["support_grade"] or "partial" in row["support_grade"]]
    lines = [
        "# Narrative citation pass 20260810",
        "",
        "Scope: local Nature Communications benchmark/supporting papers only.",
        "",
        "This pass maps citable narrative claims to locally downloaded and extracted candidate papers. It does not replace final manual citation verification, and it does not convert internal project metrics into literature-supported claims.",
        "",
        "## Outputs",
        "",
        "1. `citation_need_segments.csv`",
        "2. `citation_candidate_library.csv`",
        "3. `narrative_citation_mapping.csv`",
        "4. `references_narrative_citation_pass.ris`",
        "5. `citation_pass_browser.html`",
        "6. `citation_pass_summary.json`",
        "",
        "## Candidate Library",
        "",
    ]
    for candidate in candidates:
        lines.append(f"- {candidate['candidate_id']}: {candidate['authors_short']} ({candidate['year']}), {candidate['title']}, {candidate['journal']}, DOI {candidate['doi']}.")
    lines.extend(
        [
            "",
            "## Conservative Interpretation",
            "",
            "1. P1 is direct GPR/Res-SAM context, but the present benchmark deltas must cite internal figure/table source data.",
            "2. P4 and P5 strongly support the general risk that leakage or weak splitting can inflate apparent performance.",
            "3. P2 and P3 support shortcut-learning and evaluation logic, but they do not directly validate the present GPR metrics.",
            "4. P6 supports acquisition-shift/performance-drift reasoning by analogy and should be labelled as non-GPR background.",
            "5. Release/readiness claims require internal companion artifacts and repository records, not literature citations.",
            "",
            "## Remaining Citation Gaps",
            "",
        ]
    )
    for row in unresolved:
        lines.append(f"- {row['segment_id']}: {row['risk_note']}")
    lines.extend(
        [
            "",
            "Boundary: citation mapping is ready for manuscript drafting, but final references still need manual placement after figure numbering and final prose are locked.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidate_library = candidate_rows()

    missing = [row for row in candidate_library if row["local_text_exists"] != "true"]
    if missing:
        missing_ids = ", ".join(row["candidate_id"] for row in missing)
        raise FileNotFoundError(f"Missing local citation text for: {missing_ids}")

    segment_fields = [
        "segment_id",
        "source_section",
        "source_paragraphs",
        "core_claim",
        "claim_type",
        "candidate_ids",
        "support_grade",
        "insert_after",
        "risk_note",
    ]
    candidate_fields = [
        "candidate_id",
        "authors_short",
        "year",
        "title",
        "journal",
        "doi",
        "article_url",
        "local_text",
        "support_role",
        "local_text_exists",
        "verification_basis",
        "use_boundary",
    ]
    write_csv(OUT_DIR / "citation_need_segments.csv", SEGMENTS, segment_fields)
    write_csv(OUT_DIR / "narrative_citation_mapping.csv", SEGMENTS, segment_fields)
    write_csv(OUT_DIR / "citation_candidate_library.csv", candidate_library, candidate_fields)
    write_ris(OUT_DIR / "references_narrative_citation_pass.ris", candidate_library)
    write_html(OUT_DIR / "citation_pass_browser.html", SEGMENTS, candidate_library)
    write_report(OUT_DIR / "citation_pass_report.md", SEGMENTS, candidate_library)

    summary = {
        "run_id": "20260810_narrative_citation_pass",
        "scope": "local Nature Communications candidates",
        "candidate_count": len(candidate_library),
        "segment_count": len(SEGMENTS),
        "strong_or_strong_background_segments": sum("strong" in row["support_grade"] for row in SEGMENTS),
        "partial_or_internal_segments": sum(("partial" in row["support_grade"]) or ("internal" in row["support_grade"]) for row in SEGMENTS),
        "reference_export": str((OUT_DIR / "references_narrative_citation_pass.ris").relative_to(BENCH_ROOT)),
        "browser": str((OUT_DIR / "citation_pass_browser.html").relative_to(BENCH_ROOT)),
        "status": "citation_mapping_ready_not_final_references",
        "boundary": "Use as a conservative citation placement guide; final prose, figure numbering and repository identifiers remain open.",
    }
    (OUT_DIR / "citation_pass_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
