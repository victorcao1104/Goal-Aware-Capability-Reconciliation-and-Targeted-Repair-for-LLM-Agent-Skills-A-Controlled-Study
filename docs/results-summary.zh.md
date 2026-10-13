# 实验结论与交付说明

研究题目：Goal-Aware Capability Reconciliation and Targeted Repair for LLM Agent Skills: A Controlled Study。

作者：Victor Cao，University of Auckland，Faculty of Science。

## 实际完成的研究

- 所有实验模型角色均使用 gpt-6-luna；共 1,362 次 API 调用。
- 完成 1,920 次有效执行：主实验实时模型执行 1,152 次、确定性压力回放 624 次、迁移攻击文本执行 144 次。没有缺失、重复或意外执行记录。
- 原始静态数据共 168 个配对案例，其中 167 个可评分；一个模型输出不完整案例保留为未解决，不计为安全。
- 总费用保守估计 US$1.013328125，未结算预留为零。此数来自使用量和保守单价，并非账单；授权上限为 US$20。

## 核心发现

实时模型条件下，无额外权限网关的 B0 没有发生被测攻击，任务成功率为 99.3%；B5 为 92.4%。因此，本实验无法证明新增防御降低了实时模型攻击率，反而观测到任务功能损失。

压力回放强制请求攻击效果。B5 的攻击成功率从 B0 的 100% 降至零；同时安全且完成被攻击任务的比例为 83.3%，高于仅拒绝的来源权限网关 B2P 的 33.3%。但采用同等选择性过滤、不使用目标图的 B2R 与 B5 取得相同结果。结论是：在本封闭环境中，选择性修复有效，但没有证明目标图带来额外收益。论文保留了这一负面结论。

## 适用范围

这是一项受控机制研究，并非原始 Skill-Inject 的原生代理复现。执行使用合成结构化文件和模拟发送箱；命名家庭不跨数据分区，但宽泛模板仍重复。没有独立人工标注，AI 复核不等于人工标注。数据集标签、确定性验收、代码复核各自支持的结论已在论文中区分。

与手册的范围差异见 docs/protocol/deviations-from-handbook.md。13 篇论文和 4 个代码仓库保留在本地研究目录；公开准备包不包含原论文、用户课程材料、完整原始攻击包或密钥。

## 文件入口

- output/pdf/goal-aware-skill-study.pdf：IEEE 双栏论文，正文 12 页，参考文献 1 页、14 条；摘要 173 词。
- paper/：可编辑 LaTeX、BibTeX、图和表。
- results/summary/：测量结果、配对区间、失败案例和费用。
- results/evidence/：可用于离线重算的审阅后证据。
- docs/reproduction.md：复现步骤。
- release/goal-aware-skill-study.zip：本地交付包；2026-10-14 作者另行授权将审阅后内容发布至指定 GitHub 仓库。

本地完整过程资料另保留于忽略的 work/、results/raw_runs/、results/preformal/、literature/ 和 third_party/ 中。请在遵守课程 AI 使用规定的前提下审阅并使用论文；本文和 NOTICE.md 已披露 AI 辅助。
