# Narrative citation pass 20260810

Scope: local Nature Communications benchmark/supporting papers only.

This pass maps citable narrative claims to locally downloaded and extracted candidate papers. It does not replace final manual citation verification, and it does not convert internal project metrics into literature-supported claims.

## Outputs

1. `citation_need_segments.csv`
2. `citation_candidate_library.csv`
3. `narrative_citation_mapping.csv`
4. `references_narrative_citation_pass.ris`
5. `citation_pass_browser.html`
6. `citation_pass_summary.json`

## Candidate Library

- P1: Zhou et al. (2025), Reservoir-enhanced segment anything model for subsurface diagnosis, Nature Communications, DOI 10.1038/s41467-025-67382-4.
- P2: Zhou et al. (2025), Mitigating data bias and ensuring reliable evaluation of AI models with shortcut hull learning, Nature Communications, DOI 10.1038/s41467-025-60801-6.
- P3: Brown et al. (2023), Detecting shortcut learning for fair medical AI using shortcut testing, Nature Communications, DOI 10.1038/s41467-023-39902-7.
- P4: Rosenblatt et al. (2024), Data leakage inflates prediction performance in connectome-based machine learning models, Nature Communications, DOI 10.1038/s41467-024-46150-w.
- P5: Joeres et al. (2025), Data splitting to avoid information leakage with DataSAIL, Nature Communications, DOI 10.1038/s41467-025-58606-8.
- P6: Roschewitz et al. (2023), Automatic correction of performance drift under acquisition shift in medical image classification, Nature Communications, DOI 10.1038/s41467-023-42396-y.

## Conservative Interpretation

1. P1 is direct GPR/Res-SAM context, but the present benchmark deltas must cite internal figure/table source data.
2. P4 and P5 strongly support the general risk that leakage or weak splitting can inflate apparent performance.
3. P2 and P3 support shortcut-learning and evaluation logic, but they do not directly validate the present GPR metrics.
4. P6 supports acquisition-shift/performance-drift reasoning by analogy and should be labelled as non-GPR background.
5. Release/readiness claims require internal companion artifacts and repository records, not literature citations.

## Remaining Citation Gaps

- S002: P4/P5 support leakage and split design; P6 supports acquisition shift by analogy outside GPR.
- S004: External blind validation remains an internal protocol gate, not a completed cited result.
- S006: P3 is medical-AI context; use as conceptual support, not GPR-specific evidence.
- S007: P6 supports the acquisition-shift concept in medical imaging; P1 anchors the GPR setting.
- S008: Do not cite a literature paper as if the repository DOI or public release already exists.
- S009: Conclusion must retain the NO-GO boundary for external blind validation.

Boundary: citation mapping is ready for manuscript drafting, but final references still need manual placement after figure numbering and final prose are locked.
