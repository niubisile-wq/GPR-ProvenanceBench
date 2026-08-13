# Results Section Skeleton 2026-08-10

Purpose: convert frozen figure/table source data into a Results-section paragraph map without inventing new claims.

One-sentence argument: current evidence indicates that GPR recognition performance is sensitive to source and environment transfer, led by Res-SAM cross-environment fragility, with Mojahid and 4TU providing secondary split/stress-test support and blind external validation still open.

## Results Paragraph Map

| paragraph | role | figure/table | claim status | topic sentence | boundary |
| --- | --- | --- | --- | --- | --- |
| R1 | system/workflow validation | Figure 1; Table 1 | supported_for_checkpoint | We first froze the executable evidence boundary rather than treating all nominal datasets as equivalent validation assets. | This establishes asset/protocol status, not model performance. |
| R2 | main result | Figure 2; Table 2 | supported_current_main | Across five model families, Res-SAM environment transfer produced the strongest and most reproducible performance drop. | Scope is Mojahid and Res-SAM only; not blind external validation. |
| R3 | baseline comparison | Figure 3; Table 2 | directional_only | Mojahid random-minus-grouped inflation was directionally consistent but too modest to serve as the lead claim. | Do not frame as universal leakage; only 1/5 model families reaches material support. |
| R4 | stress test / failure mode | Figure 4 | stress_test_supported | 4TU multi-layer counterfactual stress tests defined a feasibility-boundary layer rather than a main confirmation result. | Stress-test and feasibility-boundary evidence only; not final causal proof, main 4TU confirmation or blind external validation. |
| R5 | failure-mode gate | Figure 5 | gate_supported | A target-level feasibility audit explained why 4TU should not yet be expanded into the main cross-model confirmation matrix. | Feasibility/gate result, not model superiority. |
| R6 | external validation boundary | Figure 6 | not_yet_supported | The blind external validation gate remains open despite having protocol templates and dry-run evaluators. | No completed blind external validation; protocol readiness is not a positive result. |

## Chinese Draft Paragraphs

### R1: system/workflow validation

我们首先冻结当前可执行证据边界，而不是把所有名义数据集都等同为可用验证资产。按本地 unified manifest 口径，Mojahid、4TU 和 Res-SAM 分别提供 2524、99 和 1050 个可执行样本；TIGPR 当前本地可执行样本数为 0，因此只能作为 supporting evidence，不能进入当前核心模型矩阵或外部盲评结论。

Evidence: Table 1 local executable rows: Mojahid=2524, 4TU=99, Res-SAM=1050, TIGPR=0. TIGPR local rows are 0 and remain supporting-only.

Boundary: This establishes asset/protocol status, not model performance.

### R2: main result

在五类模型家族中，Res-SAM 的环境迁移落差构成当前最强且最一致的主结果。real-to-synthetic 方向达到 5/5 directional support 和 5/5 material support，平均 balanced accuracy delta 为 0.4239；synthetic-to-real 方向达到 4/5 directional support 和 4/5 material support，平均 delta 为 0.3743。这说明当前最稳健的信号不是单一模型现象，而是跨模型家族可重复的环境迁移脆弱性。

Evidence: real-to-synthetic: directional=5/5, material=5/5, mean_delta=0.4239; synthetic-to-real: directional=4/5, material=4/5, mean_delta=0.3743.

Boundary: Scope is Mojahid and Res-SAM only; not blind external validation.

### R3: baseline comparison

Mojahid 的 random-minus-grouped 差异支持同一方向，但证据强度不足以作为主结论。HOG+RBF-SVM 五种子实验中，random split balanced accuracy mean 为 0.9543，grouped split 为 0.8566，delta 为 0.0976；但在五模型综合层面，该差异虽为 5/5 directional support，却只有 1/5 material support，平均 delta 仅为 0.0406。因此 Mojahid 应作为 split-sensitivity 的次级支撑，而不是 universal leakage 的主证据。

Evidence: directional=5/5, material=1/5, mean_delta=0.0406; Table 2 status=directional_only.

Boundary: Do not frame as universal leakage; only 1/5 model families reaches material support.

### R4: stress test / failure mode

4TU 的多层 counterfactual stress-test 结果表明，该资产目前应被定位为 feasibility-boundary 层，而不是主确认结果。Land type ExtraTrees 在 fixed-split seed sweep 中，log_clip 后 BA_mean 为 0.0905，delta_mean 为 -0.3429，flip_mean 为 0.8583；而在 group-aware repeated split 中，同一方向 delta_mean 降至 -0.0422，flip_mean 为 0.4693。进一步的五层扩展审计把 summary-feature、raw-pixel、HOG、small-CNN 和 group-aware HOG 证据统一限定为 stress-test 或 feasibility-boundary evidence。因此 4TU 不能写成 causal proof、blind external validation 或主确认层。

Evidence: fixed log_clip delta=-0.3429, flip=0.8583; group log_clip delta=-0.0422, flip=0.4693; evidence boundary layers=5.

Boundary: Stress-test and feasibility-boundary evidence only; not final causal proof, main 4TU confirmation or blind external validation.

### R5: failure-mode gate

4TU 的 target-level feasibility audit 解释了为什么当前不应强行扩展 4TU 五模型主确认矩阵。Land type 虽为 usable_with_caution，test2/val2 feasible fraction 为 0.9365，但 Land use 和 Construction workers 不适合 grouped holdout，Land cover 和 Relative groundwater level 受 single-project label 限制。因此，4TU 的合理定位是 counterfactual 和 stress-test，而不是当前主确认矩阵。

Evidence: Land type status=usable_with_caution, feasible_fraction=0.9365; Land use and Construction workers are not viable; Land cover and groundwater are weak.

Boundary: Feasibility/gate result, not model superiority.

### R6: external validation boundary

尽管项目已经具备 blind intake 模板、prediction submission 模板和 locked-evaluation dry run，真实 blind external validation 仍未完成。当前 external validation readiness gate 为 NO-GO；TIGPR restoration、第三方 blind GPR set 和 4TU-like raw-trace external asset 均未 ready，Res-SAM 也已进入当前模型矩阵，不能再作为独立盲评资产。因此，所有关于外部盲评的表述必须写成 open gate，而不是正结果。

Evidence: External gate status=NO-GO; boundary=No current track satisfies blind external validation readiness. The next concrete step is acquisition or restoration, not additional internal modeling.

Boundary: No completed blind external validation; protocol readiness is not a positive result.

## Claim-Evidence Map

- Claim: We first froze the executable evidence boundary rather than treating all nominal datasets as equivalent validation assets. | Evidence: Table 1 local executable rows: Mojahid=2524, 4TU=99, Res-SAM=1050, TIGPR=0. TIGPR local rows are 0 and remain supporting-only. | Status: supported_for_checkpoint | Boundary: This establishes asset/protocol status, not model performance.
- Claim: Across five model families, Res-SAM environment transfer produced the strongest and most reproducible performance drop. | Evidence: real-to-synthetic: directional=5/5, material=5/5, mean_delta=0.4239; synthetic-to-real: directional=4/5, material=4/5, mean_delta=0.3743. | Status: supported_current_main | Boundary: Scope is Mojahid and Res-SAM only; not blind external validation.
- Claim: Mojahid random-minus-grouped inflation was directionally consistent but too modest to serve as the lead claim. | Evidence: directional=5/5, material=1/5, mean_delta=0.0406; Table 2 status=directional_only. | Status: directional_only | Boundary: Do not frame as universal leakage; only 1/5 model families reaches material support.
- Claim: 4TU multi-layer counterfactual stress tests defined a feasibility-boundary layer rather than a main confirmation result. | Evidence: fixed log_clip delta=-0.3429, flip=0.8583; group log_clip delta=-0.0422, flip=0.4693; evidence boundary layers=5. | Status: stress_test_supported | Boundary: Stress-test and feasibility-boundary evidence only; not final causal proof, main 4TU confirmation or blind external validation.
- Claim: A target-level feasibility audit explained why 4TU should not yet be expanded into the main cross-model confirmation matrix. | Evidence: Land type status=usable_with_caution, feasible_fraction=0.9365; Land use and Construction workers are not viable; Land cover and groundwater are weak. | Status: gate_supported | Boundary: Feasibility/gate result, not model superiority.
- Claim: The blind external validation gate remains open despite having protocol templates and dry-run evaluators. | Evidence: External gate status=NO-GO; boundary=No current track satisfies blind external validation readiness. The next concrete step is acquisition or restoration, not additional internal modeling. | Status: not_yet_supported | Boundary: No completed blind external validation; protocol readiness is not a positive result.

## Manuscript Guardrails

1. Do not claim completed blind external validation.
2. Do not lead with Mojahid split inflation because it is directional_only at five-model level.
3. Do not present 4TU as main confirmation; keep it as stress-test/failure-mode evidence.
4. Lead Results with Res-SAM environment-transfer fragility.
