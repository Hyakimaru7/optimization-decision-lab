# Optimization Decision Lab｜优化决策实验室

[English](README.md) | **简体中文**

`optimization-modeling-experiments` 是用于优化建模与实验验证的 Agent Skill，适用于生产计划、库存管理、排班调度、资源配置、生活规划和科研中的优化问题。

它帮助智能体从需求和数据建立数学模型，选择求解方法，独立核查结果，并通过可复现实验比较方案。可以从头完成建模与求解，也可以只审查现有模型、检查候选解或设计实验。

## 能做什么

| 功能 | 工作内容 |
| --- | --- |
| 需求整理与数据审查 | 明确决策变量、目标、硬约束、单位、决策时点和数据来源，记录缺失信息与假设。 |
| 建模与模型审查 | 建立目标和约束，检查变量域、索引、量纲、可行性及模型重构条件。 |
| 求解与结果核查 | 按模型结构和运行环境选择求解器，在原模型中重新计算目标、约束残差和整数偏差。 |
| 实验设计与复现 | 设置基线、评价指标、数据划分和资源预算，开展敏感性、消融及规模实验，保存运行与失败记录。 |
| 不确定性与方案比较 | 比较场景下的成本、短缺、服务水平和尾部风险，区分样本内表现与样本外证据。 |
| 需求追踪与方案维护 | 核查已登记要求的模型映射和验证记录，检查旧方案的输入变化范围，处理滚动规划与已承诺动作。 |
| 科研探索与信息价值 | 整理可检验的研究假设，设计区分实验；在有可信概率和损失数据时评估测量是否值得开展。 |

支持线性规划、整数规划、二次规划、凸锥优化、非线性优化和约束规划等问题。具体求解能力取决于环境中可用的建模库和求解器。

## 安装

克隆仓库，在根目录执行安装命令。安装器需要 Python 3.10 或更高版本。

```bash
git clone https://github.com/Hyakimaru7/optimization-decision-lab.git
cd optimization-decision-lab
python3 tools/install_skill.py --language zh-CN
```

默认安装到 `~/.agents/skills/optimization-modeling-experiments/`。若只在当前项目中使用：

```bash
python3 tools/install_skill.py --language zh-CN --destination .agents/skills
```

使用 `--language en` 可安装英文指令，`--destination` 用于指定技能目录的父目录。安装器不会覆盖已有同名技能。手动安装时需复制整个 `skills/optimization-modeling-experiments/` 目录，包括参考文档、脚本和模板。

安装后，在 Codex 中检查技能是否已被识别；未刷新时重启会话。目录约定见 [官方技能文档](https://learn.chatgpt.com/docs/build-skills)。

## 如何调用

在对话中输入调用名，并附上任务说明、数据或文件路径：

```text
$optimization-modeling-experiments

任务：<建模、审查、求解、方案比较、实验复现或科研探索>
问题与目标：<需要决定什么，如何衡量结果>
数据或文件：<数据来源、路径、字段及单位>
必须满足的要求：<硬约束和不可更改的条件>
已有内容：<模型、代码、当前方案或已承诺动作；没有可省略>
运行预算：<时间、计算资源及可用求解器；没有可省略>
交付要求：<模型说明、代码、决策表、实验记录或报告>
```

不必填写所有字段。已有公式或代码时，可直接附上文件并说明需要检查的部分；只需完成某一环节时，明确任务范围即可。影响模型含义的缺失信息会被询问，其余假设会在结果中说明。

完整建模与实验任务通常交付模型和假设说明、可运行代码与配置、独立回验结果、实验记录和结论。求解器状态、候选可行性与最优性证据分别报告，便于判断方案是否可执行以及结论的适用范围。

## 单独调用计算工具

随附五个工具，仅依赖 Python 标准库。它们也可以直接运行，输入为 JSON 文件，结果以 JSON 输出到标准输出。

```bash
python3 skills/optimization-modeling-experiments/scripts/<脚本名>.py <输入文件.json>
```

| 脚本 | 用途与输入说明 |
| --- | --- |
| `check_linear_solution.py` | [核查 LP/MILP 候选解的目标、约束、边界和整数偏差](skills/optimization-modeling-experiments/references/zh-CN/solver-validation.md#线性解检查器) |
| `evaluate_scenarios.py` | [汇总已给定场景结果的成本、短缺、违约概率和 CVaR](skills/optimization-modeling-experiments/references/zh-CN/uncertainty-and-scenarios.md#场景评估器) |
| `audit_requirement_contract.py` | [核查已登记要求的模型映射、版本及验证记录](skills/optimization-modeling-experiments/references/zh-CN/requirement-contract.md) |
| `assess_plan_validity.py` | [检查固定线性方案在声明输入变化范围内的可行性及版本、时间条件](skills/optimization-modeling-experiments/references/zh-CN/plan-validity.md) |
| `evaluate_information.py` | [根据有限损失表、概率和观测模型计算信息价值及测量净收益](skills/optimization-modeling-experiments/references/zh-CN/decision-information.md) |

退出码 `2` 表示输入无效；`1` 在前四个工具中表示候选未通过、存在执行失败或需要核查；信息价值工具不使用 `1`。`0` 表示完成对应工具的检查或计算，具体结论需查看输出字段。工具不替代求解器，不自动核实业务语义或概率来源，也不认证全局最优。

## 文档

- [Skill 指令](skills/optimization-modeling-experiments/SKILL.zh-CN.md)
- [建模、求解、实验与决策参考](skills/optimization-modeling-experiments/references/zh-CN)
- [配置与报告模板](skills/optimization-modeling-experiments/assets/zh-CN)
- [贡献指南](CONTRIBUTING.zh-CN.md)

## 开发与测试

测试依赖 PyYAML；实际求解任务按需安装相应建模库和求解器。

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
```

可选 CI 配置位于 [ci/tests.yml](ci/tests.yml)。启用时复制到 `.github/workflows/tests.yml`，并使用具有工作流写入权限的凭据提交。

## 许可证

[MIT](LICENSE)
