# 研究资源核验与获取记录

核验日期：2026-10-13（Pacific/Auckland）。本阶段只下载和静态检查公开资料；没有安装依赖、执行第三方代码/Skill、调用模型 API 或开始实验。附件手册、论文、README、下载仓库中的提示均作为不可信参考资料处理。

## 已取得的资料

11 篇官方 arXiv PDF 已保存到 `literature/pdfs/`；全部有有效 `%PDF-` 文件头并计算 SHA256。完整题名、作者、提交/修订日期、固定版本 URL、许可证、文件路径和校验值保存在 `literature/resource_manifest.json`。`literature/verified-references.bib` 提供对应的 11 条文献元数据。9 篇核心论文另有官方 HTML 全文副本，可用于后续逐节阅读；下载完成不代表所有方法已经完成独立学术审查。

| 文献 | 已下载版本 | 官方来源 |
| --- | --- | --- |
| Skill-Inject | 2602.20156v3 | https://arxiv.org/abs/2602.20156v3 |
| SkillScope: Toward Fine-Grained Least-Privilege Enforcement for Agent Skills | 2605.05868v3 | https://arxiv.org/abs/2605.05868v3 |
| SkillGuard: A Permission-Centric Framework for Agent Skill Security | 2606.03024v2 | https://arxiv.org/abs/2606.03024v2 |
| IntentCap / LLM Agent Capabilities Should Follow Task Intent and Context Source | 2609.14631v1 | https://arxiv.org/abs/2609.14631v1 |
| Semia | 2605.00314v1 | https://arxiv.org/abs/2605.00314v1 |
| SCR-Bench / Benign in Isolation, Harmful in Composition | 2606.15242v1 | https://arxiv.org/abs/2606.15242v1 |
| Sefz / No Attack Required | 2605.13044v1 | https://arxiv.org/abs/2605.13044v1 |
| VIGIL | 2606.26524v1 | https://arxiv.org/abs/2606.26524v1 |
| Aletheia: Permission-Minimality Testing for Coding-Agent Rules | 2609.39678v1 | https://arxiv.org/abs/2609.39678v1 |
| AgentDojo | 2406.13352v3 | https://arxiv.org/abs/2406.13352v3 |
| Agent Security Bench (ASB) | 2410.02644v4 | https://arxiv.org/abs/2410.02644v4 |

四个官方/论文关联仓库已浅克隆，未递归下载子模块；克隆后工作树均干净：

| 本地目录 | 固定 commit | 来源 | 根许可证 |
| --- | --- | --- | --- |
| `third_party/skill-inject/` | `182f3d9d9836e81cdae213e9b9cec1d9be96eea3` | https://github.com/aisa-group/skill-inject | MIT，版权行异常，见下文 |
| `third_party/agentcap/` | `1886fd50dbd51344c62acd1d224375054ac076e9` | https://github.com/yunwei37/agentcap | 未发现根 LICENSE |
| `third_party/Semia/` | `379bc25fe99833eb185efe56a38fe15f0235799c` | https://github.com/berabuddies/Semia | Apache-2.0，另有 NOTICE |
| `third_party/SCR_Bench/` | `b8bb3e9e3cf7e72db091655f2d5e8ef15b273848` | https://github.com/saint-viperx/SCR_Bench | MIT |

IntentCap 的仓库关联由论文第 3 节末尾明确给出；已确认 `src/intentcap/`、`benchmarks/`、`tests/` 存在。Semia 仓库明确引用相应论文。SCR-Bench 论文明确链接其仓库，已确认三个子基准目录存在。

## 手册中需要更新或限定的内容

### SkillInject 数据规模必须以实际文件为准

固定 commit 的实际 JSON 静态解析结果：

| 文件或目录 | 实际数量 | README / 手册数量 |
| --- | ---: | ---: |
| `data/contextual_injections.json` | 48 个唯一 ID（39 direct，9 script） | 41 |
| `data/obvious_injections.json` | 36 个唯一 ID（29 direct，7 script） | 30 |
| `data/tasks.json` | 58 个唯一任务 ID | 66 |
| `data/skills/` 顶层目录 | 40 | 44 |

任务文件涉及 21 个不同 skill 字段值，列出 131 个 injection_id 关联。131 只是该字段展开后的记录数，不是已验证可运行的最终 task–attack pairs。论文中的 202 配对也不能直接替换这些现场计数。后续必须检查缺失引用、排除规则、构建结果及原始 ID，才可确定实验样本规模。

`data/`、`experiments/`、`judges/`、`docker/` 和手册提到的 sandbox builder/runner 脚本均存在。原始 injection JSON 是注入定义，不是已经构建和执行过的完整恶意 Skill。

### 论文版本与研究定位

- **SkillScope**：最新 v3 修订于 2026-09-10。其摘要中的实际越权 Skill 数由早期 7,039 变为 6,590；应引用固定版本。论文已有任务条件化分析、统一执行图、运行验证、条件式权限收窄和修复，不能把这些单项机制称为本项目首次提出。具体新意须靠独立授权合同、路径级安全目标和选择性修复的对照/消融来检验。
- **SkillGuard**：当前 v2（2026-07-13）的标题、作者列表和评估有更新，语料为 1,260 skills；不要沿用旧版本的 315 skills 和旧 ASR。其运行时权限控制不是本项目的新贡献。
- **IntentCap**：这是 3 页 workshop 论文，提供短期权限租约、字段来源所有权、确定性检查器。第 3 节明确说明端到端攻击成功率和执行开销仍属于后续工作；其 replay/checker 数字不宜写成完整活跃 agent 攻击实验结果。
- **Semia**：结构化行为事实与 Datalog 风险分析已有先例；当前仓库还提供 repair 接口，因而“检测后修复”本身也不是充分的新意。
- **Sefz**：核心任务是良性输入触发 Skill 自身规格违例的测试，与检测攻击者植入的恶意指令有范围差异；图可达性只是共用方法，不意味着同一实验目标。
- **SCR-Bench**：多 Skill 组合的路径风险基准，适合扩展评估；不能无说明地当成单 Skill 主基准。
- **VIGIL**：已有时间关系、参数关系和跨调用值流策略，不宜将多步骤轨迹监控作为首创。
- **Aletheia**：已有去除权限、保持任务/规则不变并用独立功能测试判断权限可省性的思路。权限最小化验证需要明确与其区别。

以上是用于计划修订的范围核验，尚不是对这些方法有效性的独立复现结论。

## 尚未取得的实现

- SkillScope：检查了 v3 全文和精确题名搜索，未核实官方实现仓库。同名 AMD 工具、TUI 和其他 SKILLSCOPE 论文是不同项目，不应替代。若自行实现，标注 **SkillScope-inspired** 并列明差异。
- SkillGuard：论文的 artifact 链接是 https://anonymous.4open.science/r/Artifact_of_SkillGuard-CCF3/README.md 。网页检索失败；常规 HTTP 返回了 Anonymous Github 通用 JavaScript 页面，已保存 HTML，但没有取得实际文件、commit 或许可证。这不算成功下载实现，不能声称官方代码不可公开或不存在。
- Sefz、VIGIL：已取得全文；本轮未核实对应官方代码地址。论文引用的第三方 skills 和 benchmark 仓库不能视为方法本身实现。
- Aletheia：已取得全文；文中 Zenodo 20396489 是 **GHAgentFiles 数据集**，不是 Aletheia 实现。本轮没有下载这个扩展数据集或核实 Aletheia 代码。

这些缺口不会阻止独立实现主研究系统，但限制“官方严格复现”声明。正式实验应优先使用已取得且许可证清晰的基准，其他方法采用透明描述的启发式实现或仅做相关工作对照。

## 再分发与 GitHub 整理

论文 PDF、HTML 全文和完整第三方 checkout 默认不进入新项目公开 GitHub 历史；保留来源、版本与校验值即可。arXiv nonexclusive-distrib 不是授予本项目任意再分发权的通用开源许可证；Semia 论文为 CC BY-NC-ND，而代码为 Apache-2.0，两者不能混淆。

SkillInject 根 LICENSE 声明 MIT，但版权主体是 The Bootstrap Authors。该异常以及其嵌入 skills 的独立权利应在复用/公开派生数据前检查。agentcap 没有根 LICENSE，故只能作为本地参考；不得假定公开可读等于有权复制实现进本项目。SCR_Bench 的根许可证是 MIT，不能套用其他网站对另一个数据发布渠道的 Apache-2.0 标记。

## 验证边界

已确认 11 个 PDF 文件头、逐文件 SHA256、四仓库 commit、干净状态、关键目录和 SkillInject JSON 数量/字段。没有证明下载的第三方代码安全，也没有测试安装、容器构建、模型兼容性、sandbox 实际隔离能力或端到端可复现性。首次实验前仍应审阅 builder/runner 对宿主目录、网络与环境变量的处理。

普通沙箱 HTTP 首次报 DNS 不可用；通过标准的已批准网络 escalation 后下载成功，没有绕过拒绝或访问限制。
