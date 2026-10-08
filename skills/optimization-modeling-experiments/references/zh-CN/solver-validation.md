# 求解器选型与原模型认证

[English](../solver-validation.md) | **简体中文**

## 可用性与状态

先检查已安装后端及其模型支持；在 CVXPY 环境可调用 `installed_solvers()`。不要将装有建模库误认为已具备全部求解器。

读取当前版本的状态定义，保存原始状态、消息、精度与配置。使用以下解释原则：

| 状态或现象 | 可以报告的结论 | 需要核查 |
| --- | --- | --- |
| optimal / success | 求解器在其标准下成功终止 | 原模型可行性、适用保证、容差与界 |
| optimal_inaccurate 等 | 求解器报告低精度结果 | 是否达到研究要求；独立残差与必要交叉检查 |
| 时间/迭代上限 | 在预算内终止 | 有无可行候选、有无有效界；不是已证明最优 |
| infeasible | 求解器报告不可行 | 模型、尺度、状态精度及可获得的证书 |
| unbounded | 求解器报告无界 | 模型遗漏、变量界、无界方向或证书 |
| infeasible_or_unbounded | 不能区分两者 | 根据官方流程进一步诊断 |
| 异常、NaN、无解对象 | 技术失败或未得到可用结果 | 记录原因，不生成伪目标和伪残差 |

局部 NLP 的 success 不意味着全局最优；解释必须同时考虑求解器类别和原模型结构。

## 独立回验

1. 检查解对象、维度、定义域和有限性。缺失解时相关数值用 null/缺失标记，不能填 0。
2. 恢复原变量及原目标方向、尺度、常数项；重新计算原目标。
3. 逐类计算原约束残差，包括求解器变量属性表达的边界与整数约束。
4. 比较回验结果与原求解状态，保留最大违反约束的标识。
5. 评估适用的最优性证据，并限制结论。

对不等式 g_i(x)≤0、等式 h_j(x)=0 定义：

\[
v_i=\max(g_i(x),0),\quad e_j=|h_j(x)|.
\]

对有限变量界及整数变量分别定义：

\[
b_k=\max(l_k-x_k,\ x_k-u_k,\ 0),\qquad
d_k=|x_k-\operatorname{round}(x_k)|.
\]

无穷边界不参与减法。圆整仅用于计算整数偏差；若实际圆整候选解，要重新回验全部约束和目标。

约束具有不同量纲时按约束类别报告，不能把不同单位的残差直接解释为同一个物理量。可以用预先指定的正尺度 s_i 判定：

\[
v_i\le \varepsilon_{\rm abs,i}+\varepsilon_{\rm rel,i}s_i.
\]

等式与边界同理。s_i 的来源与单位必须明确，不根据候选解的违反程度临时放宽。保留原单位绝对残差和归一化残差。整数偏差使用独立整数容差。

## 最优性界与 gap

统一映射到原目标后，令 L 为最优值的有效下界、U 为有效上界。最小化的可行候选提供 U，最大化的可行候选提供 L；另一侧来自适用的对偶、松弛或全局求解器证据。

仅当两侧有限且来源有效时，可定义本实验统一的 gap：

\[
\mathrm{gap}_{\rm abs}=U-L,\qquad
\mathrm{gap}_{\rm rel}=\frac{U-L}{\max(1,|U|,|L|)}.
\]

这是一种明确的报告约定，分母中的 1 对应报告目标单位中的基准尺度；若重标定目标或物理单位，应同时指定合适的正基准尺度并留痕。它可能不同于求解器自身 gap；保留 `solver_gap` 和其原定义，不混用停止条件。

缺少一侧有效界时 gap 未知；局部解、多初值最好值和数值参考值不自行成为有效对偶界。约束仅在容差内满足的解，提供的是相应数值意义下的候选，不擅自称为严格数学证书。有限精度求解器的界标明其来源与精度。

若 U<L，保存原数值并检查映射、常数项、舍入、精度或界的有效性。小量数值冲突也应标注，不把未经说明的截断结果当证据。

## KKT与局部指标

对于适用的可微模型，Lagrangian 为 ℒ=f+∑λ_i g_i+∑ν_j h_j 时，可记录：驻点残差、原可行性、λ_i 非负性和互补性 |λ_i g_i|。目标最大化需先明确相应符号约定。

核对乘子符号和变量界乘子，缺失乘子时不声称计算了完整 KKT 残差。非光滑或复合模型选择相应次微分/近端指标。使用 KKT 作必要或充分条件时说明约束资格、凸性等条件；局部指标不直接认证非凸全局最优。

## 异常诊断与重试

按证据选择：检查错误数据和索引、缩放、有效变量界、冗余/冲突约束、求解器日志及 IIS 或不可行证书（可用时）。可使用辅助 slack 模型定位违反，但说明其归一化方式且不替代原模型。

默认最多进行两次有明确修正理由的同实例数值重试；用户预算或任务计划可改变此起步约定。无新诊断依据时结束该尝试并报告，其他可执行工作继续。修改实例或模型语义必须登记为不同配置，不能覆盖旧失败记录。

## 线性解检查器

技能内 `scripts/check_linear_solution.py` 只依赖 Python 3 标准库。输入 JSON 的形式为：

```json
{
  "objective": {"sense": "max", "coefficients": [3, 2], "constant": 0},
  "inequalities": {"A": [[1, 1], [1, 0]], "b": [4, 2]},
  "equalities": {"A": [], "b": []},
  "bounds": [[0, null], [0, null]],
  "integer_indices": [],
  "solution": [2, 2]
}
```

不等式为 Ax≤b，等式为 Ax=b；大于方向应先一致地取负。bounds 必须显式给出每个变量，null 表示对应无界；integer_indices 为零基整数变量索引。二元变量需要同时设置整数域与 [0,1] 边界。缺失解使用 `solution: null`，返回未知目标及 `no_solution`。

每个约束组可提供正数数组 `scales`，与行数一致；默认每行尺度为 max(1,|b_i|)，边界尺度由有限界确定且至少为 1。该默认约定只适用于已有合理数值尺度的模型，实际单位/缩放不同应显式传入行尺度并解释基准 1 的单位。

调用：

```sh
python3 /实际技能路径/scripts/check_linear_solution.py /实际输入路径/candidate.json --atol 1e-6 --rtol 1e-6 --integer-tol 1e-6
```

输出 JSON 包含原目标、逐行原始残差/违反、尺度、阈值、通过状态及整数偏差。退出码 0 为候选通过当前容差，1 为不通过或无解，2 为输入错误。输入错误也返回结构化消息。

不支持非线性、半连续/半整数变量、锥约束、严格不等式或其他隐含逻辑。应在原模型中另行检查这些约束。脚本不读取求解器状态、不提供对偶界或最优性证书，不替代完整实验回验。浮点近似与容差通过不能等同于精确数学可行性。

## 官方资料入口

- [CVXPY DCP](https://www.cvxpy.org/tutorial/dcp/index.html)：可识别的凸表达规则。
- [CVXPY 状态](https://www.cvxpy.org/tutorial/intro/index.html)：状态与低精度结果。
- [CVXPY 求解器](https://www.cvxpy.org/tutorial/solvers/index.html)：后端能力、配置及统计。
- [SciPy linprog](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html)：LP 接口和状态。
- [SciPy milp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html)：HiGHS MILP 接口、界和 gap。
- [SciPy minimize](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html)：连续优化与局部求解。

实际运行以安装版本对应文档为准。

离散调度需要约束规划时，参考 [OR-Tools CP-SAT](https://developers.google.com/optimization/cp/cp_solver)。确认输入需要的整数表达；有理系数转整数须记录精确缩放，任意小数舍入可能改变问题。其 feasible 与 optimal 状态要区分；本技能的线性解检查器不能覆盖未展开的 interval/no-overlap 等约束。
