# 作者最终确认材料发送稿

# 给作者/通讯作者的一次性最终确认邮件草稿

各位老师/合作者好，

当前 Nature Communications 方向仍处于 submission-prelock 状态，不能视为已可投稿。为避免后续反复返工，需要一次性确认以下事项：

1. 作者顺序、单位、通讯作者、ORCID、Author Contributions、Competing Interests、Funding 和 Acknowledgements。
2. 当前是否确认走 Track B：benchmark/resource + evidence-boundary；若有真实盲外部验证数据持有人，请提供数据持有人、机构、时间线和标签托管方式。
3. 正式出图后端请选择 Python 或 R；当前自动化链路推荐 Python。
4. 代码、派生 Source Data、第三方数据和仓库 DOI 的 licence/rights 路线。
5. suggested reviewers、excluded reviewers、preprint/prior posting、previous editor discussion 和 transparent peer review 选择。
6. Reporting Summary 中 blinding、randomization、sample size、data exclusion 和 availability 相关答案。

请直接填写 `author_finalization_reply_form_cn.csv` 及配套表格中的 author_reply 列。所有空白项在确认前均视为 open gate，不会写入最终投稿文件。

边界说明：这封邮件和表格只是收集最终确认，不代表作者已经同意投稿，也不代表 figures、DOI、Reporting Summary、references 或 portal upload 已完成。


## 附件清单

- reports\natcomms_author_finalization_reply_packet_20260810\author_finalization_reply_form_cn.csv: Core 12-field author finalization replies.
- reports\natcomms_author_finalization_reply_packet_20260810\corresponding_author_metadata_form.csv: Title page and corresponding-author metadata.
- reports\natcomms_author_finalization_reply_packet_20260810\reviewer_and_policy_reply_sheet.csv: Suggested/excluded reviewers and editorial policy choices.
- reports\natcomms_author_finalization_reply_packet_20260810\track_branch_and_external_validation_reply.csv: Track B confirmation or real external blind validation route.
- reports\natcomms_author_finalization_reply_packet_20260810\figure_backend_decision_ticket.csv: Single formal figure backend decision.
- reports\natcomms_author_finalization_reply_packet_20260810\licence_rights_reply_sheet.csv: Licence, rights and repository release route.
- reports\natcomms_author_finalization_reply_packet_20260810\reporting_summary_author_reply_sheet.csv: Reporting Summary author confirmations.
- reports\natcomms_author_finalization_reply_packet_20260810\coauthor_finalization_email_cn.md: Chinese email body for collecting finalization replies.

## 回复后验收

收到回复后，先运行 author reply ingestion validator，再运行 gate closure evidence binder 和 finalization command dashboard v3。任何空白回复、未选择 backend、未完成 DOI/rights 或未完成 Reporting Summary/reference/final-file 证据，都继续视为 open gate。
