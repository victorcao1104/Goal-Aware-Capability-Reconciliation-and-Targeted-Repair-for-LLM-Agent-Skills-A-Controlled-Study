# 目标感知权限协调与定向修复：LLM Agent Skills 受控研究

作者：Victor Cao，University of Auckland，Faculty of Science。

**v2 研究分支：** 已加入上游重算、反事实模拟、细粒度来源追踪及同等能力的无图基线。48 个开发案例显示上游修复有效，但没有测到图的额外收益。见[可行性与实际结论](docs/v2-feasibility-and-findings.zh.md)和[独立复现入口](research_v2/README.md)。下面的 v1 论文和冻结证据保持不变。

本仓库提供论文、冻结实验代码、可公开的证据、结果和复现工具。所有实验模型均使用 **gpt-6-luna**；共 1,920 次有效执行、168 个原始静态案例（167 个可评分）。API 保守费用估计约 US$1.01。

**主要结论：** 在压力回放中，选择性修复提高了安全且完成任务的比例，但不使用目标图的同等修复方案取得相同结果。实时模型基线没有发生被测攻击，因此没有证明新增防御能降低其攻击率。请勿将本研究描述为优于现有完整权限系统。

- [论文 PDF](output/pdf/goal-aware-skill-study.pdf)：正文 12 页，参考文献 1 页。
- [详细中文结论](docs/results-summary.zh.md)
- [复现入口与目录说明](docs/artifact-guide.md)
- [实验范围与手册差异](docs/protocol/deviations-from-handbook.md)
- [英文 README](README.md)

## 最快复现

使用 Python 3.12，在虚拟环境中安装依赖，然后执行：

```text
python -m pip install -r requirements.lock
python -m scripts.reproduce
```

安装依赖后，重算不需要 API 密钥、Docker 或网络。脚本校验哈希，在新目录 `work/reproduced/` 中恢复证据、重算结果，并核对全部汇总字段及论文中的三张数值表。已存在的目录不会被覆盖；再次运行请指定 `--output work/reproduced-2`。Windows 建议克隆到较短目录，例如 `C:/research/gcr`。

`reproduction-check.json` 记录验证结果，`reproduction.log` 保留过程。若只想核对文件完整性，运行 `python -m scripts.reproduce --verify-only`。

公开仓库不包含密钥、用户课程原始材料、完整 API 消息、第三方论文全文或原始攻击包。后两类资料的来源、版本、哈希及获取说明已保留。实验用的冻结实现保持原样，新增复现工具独立存放。

这是合成封闭环境的机制研究，没有独立人工标注，也不是原始基准的原生复现。重新采集模型结果会产生新的费用和随机样本，须按[完整复现说明](docs/reproduction.md)建立新的实验副本。
