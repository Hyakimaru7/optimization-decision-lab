# 需求契约与反例

[English](../requirement-contract.md) | **简体中文**

用于订单规则容易遗漏、模型重构、多人交接或重要决策。目的：在“模型求解成功”之前检查是否回答了用户的问题。简单任务用需求表和反例即可，不默认要求机器可读清单。

## 先确认语义，再检查记录

逐条记录来源与版本、要求内容、硬/软属性、数学表达、代码位置、原业务量的独立验证及反例。独立验证尽量从订单/时序/资源等原始实体计算，不只是重复生成矩阵。

例如“B 产品至少交付 6 件”对应 `y >= 6`。反例 `(10,5)` 应被业务验证拒绝；若求解模型和验证器同时没有交付下限，两者都会误报成功。不要让工具自动把“建议多供货”升级为硬下限。

未知规则不能通过文字推理变成已确认事实。关键要求无法确认时给出条件性方案与具体缺项。登记表不可能自动发现所有未登记规则；必要时沿订单、物料、设备、时间与角色追踪一个实际执行过程。

## 可执行检查

```bash
python3 scripts/audit_requirement_contract.py assets/requirement-contract-example.json
```

输入字段均必填，未知字段报错：

- `model_revision`：本次验收快照的版本字符串，推荐内容哈希而非随意版本号；应覆盖模型、验证代码和测试相关输入。只给建模代码打版本不能捕获数据或验证器变化，脚本不能验证版本字符串的生成过程。
- `model_elements`、`validators`：当前模型元素 ID 与独立验证函数 ID 的不重复列表。
- `requirements`：非空数组；每条含 `id,text,kind,source,revision,model_elements,validator_ids,test_ids,semantic_review`。
- `kind` 为 `hard` 或 `soft`；`semantic_review` 含 `status`（`confirmed/pending`）和非空 `evidence`。确认记录由人或经过实际检查的代理填写，不是本脚本作出的语义判断。
- `tests`：数组；每条含 `id,requirement_id,requirement_revision,model_revision,validator_id,result,evidence`；`result` 为 `passed/failed/not_run`。版本须匹配当前模型和对应要求。

硬要求需要存在的模型映射、已记录的语义确认、存在的独立验证器、各验证器至少一个当前版本通过的测试。测试要检验业务语义和边界，不只是“程序没报错”。软要求的问题单独警示；未关联测试单列。此工具读取证据记录，不执行测试、不打开证据文件，不验证记录真实性；调用者必须真正运行相应测试并保留证据。

退出码：0 表示已登记硬要求的记录一致，仍需查看软要求警示；1 表示有硬要求待核查；2 表示输入无效。输出始终注明 `semantic_truth_verified:false` 和 `evidence_contents_verified:false`。

示例是合成演示记录，使用时替换真实要求与已执行证据。禁止通过补写 `passed` 来让未运行测试通过。

## 变更与无解

要求或模型版本改变后重跑受影响验证，不能继续沿用旧测试。IIS 仅给出不可约冲突子系统，一般不保证最少约束数量，也不代表所有独立冲突；计算若提前中止，还须核对是否真的达到不可约条件。把冲突映射回业务来源，并检查数据错误、单位错误和重复规则，再提出有范围的修复。[官方 computeIIS 说明](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html#Model.computeIIS)。

修复候选可比较“改几条规则”“改变多少”“实际执行成本”；每种度量可能产生不同方案。金额罚项不能代替不可妥协规则；在副本中试验，不以调大容差、软化硬约束或删除订单作为默认修复。
