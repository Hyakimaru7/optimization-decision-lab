# Optimization Decision Lab｜优化决策实验室

[English](README.md) | **简体中文**

**建立优化模型、核查可执行方案，并开展可复现的决策实验。**

本项目将 `optimization-modeling-experiments` Agent Skill、五个仅依赖 Python 标准库的计算工具、完整双语说明及可运行合成案例整理为开源仓库，适用于生产与库存、排班、资源分配、生活规划和科研探索。

项目名体现决策与实验的范围，Skill 调用名继续保持 **`$optimization-modeling-experiments`**。技能版本 **3.0.0**，许可证 **MIT**。

## 功能

| 能力 | 解决的问题 |
| --- | --- |
| 优化建模与模型审查 | 决策、单位、目标、变量域和业务规则是否表达正确？ |
| 独立方案回验 | 候选解是否在给定容差下满足原线性模型？ |
| 可复现实验 | 数据、预算、评价指标及失败记录是否使比较公平可追溯？ |
| 场景与尾部风险评估 | 给定方案的成本、短缺、硬违约与离散 CVaR 如何比较？ |
| 需求覆盖与证据追踪 | 已登记硬要求是否进入模型，验证记录是否对应当前版本？ |
| 固定方案有效范围 | 方案能承受多少声明的输入变化，其快照是否仍适用？ |
| 测量与实验信息价值 | 决策前的含噪观测能否改善决策并覆盖成本？ |
| 操作与科研流程 | 如何处理承诺、滚动状态、模型失配与可证伪假设？ |

Skill 的指导流程支持非线性、约束规划等多类问题，需要实际可用且适配的后端。随附数值工具有更窄的明确范围，不能替代通用求解器或自动证明全局最优。

## 快速开始：不依赖智能体也能运行

克隆仓库并进入根目录。使用 **Python 3.10 或更高版本**。五个计算工具、案例和安装器均不需要第三方包。

```bash
git clone https://github.com/Hyakimaru7/optimization-decision-lab.git
cd optimization-decision-lab
python3 examples/run_demo.py
```

案例在每个有界生产模型上完整检查 273 个候选，验证遗漏订单、资源缓冲与含噪/完美测量。结果写入被 Git 忽略的 `results/demo/`。

预期主要结果：

| 合成案例 | 结果 |
| --- | --- |
| 漏掉最低交付约束 | 利润 1050，但 B 产品交付不足 |
| 补齐订单的名义最优 | 利润 1040，固定方案容量变化半径 0 |
| 缓冲后的最优 | 利润 990，声明容量变化半径 1 |
| 成本 5 的含噪检测 | EVSI 10，净价值 5 |
| 成本 25 的完美检测 | EVPI 20，净价值 -5 |

详见[完整案例说明](docs/EXAMPLES.zh-CN.md)。全部示例参数均为**合成或假设数据**，不能作为已实现工业收益的证据。

## 安装为 Codex Skill

当前 [OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills)说明了项目级 `.agents/skills/` 与用户级 `~/.agents/skills/` 发现位置。安装器复制整个技能目录，遇到已有同名安装时拒绝覆盖。

中文版安装：

```bash
python3 tools/install_skill.py --language zh-CN
```

英文版安装：

```bash
python3 tools/install_skill.py --language en
```

同一位置选择一种主语言。项目级安装可在本仓库根目录执行：

```bash
python3 tools/install_skill.py --language zh-CN --destination .agents/skills
```

其他已配置技能目录通过 `--destination` 指定其**父目录**。若已有同名技能，先审查并自行移走旧安装，或选择新位置；安装器不合并、不覆盖。必须保留 references、scripts、assets 和 agents。如果宿主未刷新技能发现，可重启后检查。

默认主文件 `SKILL.md` 为英文。中文安装将完整中文指令与界面元数据设为主版本，同时将英文指令保留为 `SKILL.en.md`。两种安装使用同一套计算脚本。README 顶部语言链接仅切换说明页面，不改变数值行为。

## 调用 Skill

```text
$optimization-modeling-experiments

请依据订单和产能数据建立整数生产模型。
检查最低交付和资源规则是否完整进入模型，
构造应被拒绝的业务反例，独立回验方案。
比较名义与缓冲方案；若缺少重要输入，
提出在决策前可获得的测量，并评估其决策价值。

问题与数据：……
必须满足的要求：……
当前方案或已承诺动作：……
时间与计算预算：……
```

可以用中文或英文提问，必要时指定输出语言。简单任务只启用相关模块。提供真实单位、决策时序、规则、数据来源和预算；会改变答案的缺失语义需要澄清或明确标注分支。

## 单独运行工具

以下命令在仓库根目录执行，结果以 JSON 输出到标准输出；需要保留时可重定向到文件。

```bash
# LP/MILP 候选解：实际使用时替换为自己的原模型。
python3 skills/optimization-modeling-experiments/scripts/check_linear_solution.py skills/optimization-modeling-experiments/assets/linear-candidate-example.json

# 同一组场景下已经获得的方案结果。
python3 skills/optimization-modeling-experiments/scripts/evaluate_scenarios.py skills/optimization-modeling-experiments/assets/scenario-example.json

# 已登记要求、模型映射与当前验证记录。
python3 skills/optimization-modeling-experiments/scripts/audit_requirement_contract.py skills/optimization-modeling-experiments/assets/zh-CN/requirement-contract-example.json

# 固定线性方案的同时变化包络与快照检查。
python3 skills/optimization-modeling-experiments/scripts/assess_plan_validity.py skills/optimization-modeling-experiments/assets/plan-validity-example.json

# 有限损失表、概率、含噪信号与测量成本。
python3 skills/optimization-modeling-experiments/scripts/evaluate_information.py skills/optimization-modeling-experiments/assets/information-example.json
```

| 工具 | 输入说明 | 退出码 0 | 退出码 1 | 退出码 2 |
| --- | --- | --- | --- | --- |
| 线性解检查器 | [格式](skills/optimization-modeling-experiments/references/zh-CN/solver-validation.md#线性解检查器) | 候选在容差内通过 | 未通过或无解 | 输入无效 |
| 场景评估器 | [格式](skills/optimization-modeling-experiments/references/zh-CN/uncertainty-and-scenarios.md#场景评估器) | 情景评估完整 | 有显式执行失败 | 输入无效 |
| 需求审查器 | [格式](skills/optimization-modeling-experiments/references/zh-CN/requirement-contract.md) | 已登记硬规则的记录一致 | 硬规则需要核查 | 输入无效 |
| 有效范围检查器 | [格式](skills/optimization-modeling-experiments/references/zh-CN/plan-validity.md) | 当前快照在声明包络内 | 需要核查 | 输入无效 |
| 信息价值评估器 | [格式](skills/optimization-modeling-experiments/references/zh-CN/decision-information.md) | 损失表完成计算 | 不使用 | 输入无效 |

成功退出码的含义因工具而异。完整场景评估可以包含硬违约；记录一致不证明业务语义正确；包络通过不证明最优性。必须查看 JSON 及适用范围，不能只看退出码。示例的到期时间和 `as_of` 是声明的合成条件，并非实时监控时钟。

## 双语文档与结构

| 文档 | English | 中文 |
| --- | --- | --- |
| 智能体指令 | [SKILL.md](skills/optimization-modeling-experiments/SKILL.md) | [SKILL.zh-CN.md](skills/optimization-modeling-experiments/SKILL.zh-CN.md) |
| 完整案例 | [Examples](docs/EXAMPLES.md) | [案例](docs/EXAMPLES.zh-CN.md) |
| 贡献指南 | [Guide](CONTRIBUTING.md) | [指南](CONTRIBUTING.zh-CN.md) |
| 建模、实验、操作与科研参考 | [References](skills/optimization-modeling-experiments/references) | [参考目录](skills/optimization-modeling-experiments/references/zh-CN) |

```text
optimization-decision-lab/
├── README.md / README.zh-CN.md
├── LICENSE / CONTRIBUTING.md / CONTRIBUTING.zh-CN.md
├── skills/optimization-modeling-experiments/
│   ├── SKILL.md / SKILL.zh-CN.md
│   ├── agents/                 双语界面元数据
│   ├── references/             英文参考与 zh-CN 中文译本
│   ├── assets/                 JSON 案例与双语模板
│   └── scripts/                五个工具与一个内部共享模块
├── examples/run_demo.py
├── tools/install_skill.py
├── tests/
└── ci/tests.yml
```

## 测试与依赖

PyYAML 仅用于测试元数据与工作流配置。实际求解任务按模型选择 SciPy/HiGHS、CVXPY、OR-Tools 等后端；这些都不是随附计算工具的强制依赖。

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 examples/run_demo.py --output results/my-demo
```

原有基线包含线性检查、场景指标、需求记录、有效范围和信息价值等 51 项测试，另增项目结构、语言链接和安装检查。可选 CI 模板位于 `ci/tests.yml`，包含 Python 3.10、3.12、3.13。启用时将其复制到 `.github/workflows/tests.yml`，并使用具有工作流写入权限的 GitHub 凭据提交；当前它是模板，未启用或验证远程运行。

## 证据与限制

- 候选可行性、求解器状态和最优性证据分开；线性检查器不认证最优性。
- 需求审查器检查已登记记录，不自动发现隐藏规则、证明公式等价或核验证据文件真实性。
- 有效范围限于固定线性动作、独立同时变化盒、传入版本/时间与数值容差，不覆盖未建模物理过程、非线性规则、补救决策或永久适用性。
- 情景权重和观测似然需要真实依据。工具不校准它们、不认证总体保证；信息价值使用完整有限表和风险中性损失，所有动作须在各声明状态下可行。
- 工具不连接生产系统、不自动执行真实动作。现场效果需要目标任务的数据和评估，软件测试与合成案例不能替代。
- 项目整合已有建模与决策方法，不声称全球工业首创或已通过独立智能体行为评测。

## 许可证与贡献

项目采用 [MIT 许可证](LICENSE)。双语维护与验证要求见[贡献指南](CONTRIBUTING.zh-CN.md)。外链论文和官方文档保留各自权利，属于引用资料，不是随项目重新授权的内容。
