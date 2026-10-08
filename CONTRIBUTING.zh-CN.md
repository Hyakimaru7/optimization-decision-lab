# 贡献指南

[English](CONTRIBUTING.md) | **简体中文**

说明修改解决的建模或决策失败、受影响的假设及预期可观测行为。数值问题请提供最小可复现输入和实际输出；欢迎明确标注的合成输入。

保持[英文 Skill](skills/optimization-modeling-experiments/SKILL.md)与[中文 Skill](skills/optimization-modeling-experiments/SKILL.zh-CN.md)语义一致。能力、格式、限制和命令改变时，同步参考文档与 README；两种语言共用数值脚本。

采用最小充分修改。保留失败记录、原目标、硬约束及真实保证边界。不要为标准库工具引入强制求解器依赖。

提交 PR 前，在仓库根目录运行：

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 examples/run_demo.py
```

说明改动、实际执行的检查、结果与局限。新数值逻辑需要有意义的边界或不变量测试。不从单个例子推导通用组织规则，不用合成数据声称现场收益。贡献遵循仓库的 [MIT 许可证](LICENSE)。
