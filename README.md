# Optimization Decision Lab

**English** | [简体中文](README.zh-CN.md)

**Build optimization models, validate executable plans, and run reproducible decision experiments.**

Optimization Decision Lab packages the `optimization-modeling-experiments` agent skill with five standard-library Python utilities, bilingual instructions, and runnable synthetic examples. It supports production and inventory, scheduling, resource allocation, daily planning, and research exploration.

The repository name describes its wider decision/experiment focus; the stable skill invocation remains **`$optimization-modeling-experiments`**. Skill version: **3.0.0**. License: **MIT**.

## What you get

| Capability | What it helps answer |
| --- | --- |
| Formulation and model audit | Are decisions, units, objectives, domains, and rules modeled correctly? |
| Independent solution checking | Does a candidate satisfy the original linear model within stated tolerances? |
| Reproducible experiments | Are methods compared with consistent data, budgets, metrics, and failure records? |
| Scenario and tail-risk evaluation | How do supplied policies differ in cost, shortages, violations, and discrete CVaR? |
| Requirement traceability | Are declared hard requirements mapped and backed by current validation records? |
| Fixed-plan validity | How much declared input variation can a plan tolerate, and is its snapshot current? |
| Information value | Can a timely noisy observation improve decisions enough to cover its cost? |
| Operational/research workflows | How should commitments, rolling states, model discrepancy, and hypotheses be tested? |

The instruction workflow can handle broad optimization classes, including nonlinear and constraint-programming models, with suitable available backends. The bundled numerical utilities have narrower documented scopes. They do not replace an optimization solver or automatically prove global optimality.

## Quick start: run without an agent

Clone the repository and enter its root directory. Use **Python 3.10 or later**. The five decision utilities, demo, and installer need no third-party package.

```bash
git clone https://github.com/Hyakimaru7/optimization-decision-lab.git
cd optimization-decision-lab
python3 examples/run_demo.py
```

The demo exhaustively checks 273 candidates per bounded production model, validates an omitted order rule, compares a buffered plan, and evaluates noisy versus perfect measurements. Results are written to `results/demo/`, excluded from Git.

Expected key values:

| Synthetic case | Result |
| --- | --- |
| Order minimum omitted | Profit 1050, but B delivery is too small |
| Corrected nominal optimum | Profit 1040, fixed-plan capacity radius 0 |
| Buffered optimum | Profit 990, declared capacity radius 1 |
| Noisy test, cost 5 | EVSI 10, net value 5 |
| Perfect test, cost 25 | EVPI 20, net value -5 |

See the full [worked examples](docs/EXAMPLES.md). All example parameters are **synthetic/hypothetical**, not evidence of realized industrial gains.

## Install as a Codex skill

Current [official skill documentation](https://learn.chatgpt.com/docs/build-skills) describes repository-local `.agents/skills/` and user-level `~/.agents/skills/` discovery. The installer copies the complete folder and refuses to replace an existing installation.

English installation:

```bash
python3 tools/install_skill.py --language en
```

Chinese installation:

```bash
python3 tools/install_skill.py --language zh-CN
```

Choose one language per destination. For a repository-local installation, run from this repository root:

```bash
python3 tools/install_skill.py --language en --destination .agents/skills
```

To target another configured skills directory, pass its **parent directory** with `--destination`. If a same-name skill already exists, review/move the old installation or choose a fresh destination; the installer will not merge/overwrite it. Keep references, scripts, assets, and agents together. If the host does not refresh discovery, restart it.

The default installed `SKILL.md` is English. Chinese installation uses the full Chinese instructions and UI metadata while keeping English instructions accessible as `SKILL.en.md`. Both use identical calculation scripts. README language links only change documentation; they do not change numerical behavior.

## Invoke the skill

```text
$optimization-modeling-experiments

Build an integer production model from my orders and capacity data.
Check that mandatory delivery and resource rules are represented,
construct a rejected business counterexample, and independently validate the plan.
Compare nominal and buffered plans. If important inputs are missing,
identify a measurement available before the decision and evaluate its value.

Problem and data: ...
Hard requirements: ...
Current plan / committed actions: ...
Time and computation budget: ...
```

Ask in English or Chinese; specify the output language when needed. Simple tasks use only relevant modules. Supply real units, decision timing, rules, data provenance, and budgets; missing semantics affecting the answer require clarification or clearly labeled branches.

## Use individual tools

Commands below run from the repository root. Each emits JSON to stdout. Redirect output when you want to retain it.

```bash
# LP/MILP candidate validation: replace the example with your original model.
python3 skills/optimization-modeling-experiments/scripts/check_linear_solution.py skills/optimization-modeling-experiments/assets/linear-candidate-example.json

# Supplied outcomes on shared scenarios.
python3 skills/optimization-modeling-experiments/scripts/evaluate_scenarios.py skills/optimization-modeling-experiments/assets/scenario-example.json

# Declared requirements, model mappings, and current evidence records.
python3 skills/optimization-modeling-experiments/scripts/audit_requirement_contract.py skills/optimization-modeling-experiments/assets/requirement-contract-example.json

# Fixed linear plan under declared simultaneous box changes and snapshot checks.
python3 skills/optimization-modeling-experiments/scripts/assess_plan_validity.py skills/optimization-modeling-experiments/assets/plan-validity-example.json

# Finite losses, probabilities, noisy signals, and measurement costs.
python3 skills/optimization-modeling-experiments/scripts/evaluate_information.py skills/optimization-modeling-experiments/assets/information-example.json
```

| Tool | Input/details | Exit 0 | Exit 1 | Exit 2 |
| --- | --- | --- | --- | --- |
| Linear checker | [Schema](skills/optimization-modeling-experiments/references/solver-validation.md#linear-solution-checker) | Tolerance-feasible candidate | Invalid candidate/no solution | Invalid input |
| Scenario evaluator | [Schema](skills/optimization-modeling-experiments/references/uncertainty-and-scenarios.md#scenario-evaluator) | Complete outcome coverage | Explicit failed outcomes | Invalid input |
| Contract auditor | [Schema](skills/optimization-modeling-experiments/references/requirement-contract.md) | Consistent declared hard-rule records | Hard rules need review | Invalid input |
| Validity assessor | [Schema](skills/optimization-modeling-experiments/references/plan-validity.md) | Current snapshot within declared envelope | Review required | Invalid input |
| Information evaluator | [Schema](skills/optimization-modeling-experiments/references/decision-information.md) | Complete table evaluated | Not used | Invalid input |

Successful exit codes have tool-specific meaning. Complete scenario evaluation can contain hard violations; consistent records do not verify business truth; envelope checks do not prove optimality. Inspect the JSON and its scope, not only the exit code. Example expiry/`as_of` values are supplied synthetic conditions, not a live clock monitor.

## Documentation and layout

| Document | English | 中文 |
| --- | --- | --- |
| Agent instructions | [SKILL.md](skills/optimization-modeling-experiments/SKILL.md) | [SKILL.zh-CN.md](skills/optimization-modeling-experiments/SKILL.zh-CN.md) |
| Worked examples | [Examples](docs/EXAMPLES.md) | [案例](docs/EXAMPLES.zh-CN.md) |
| Contributions | [Guide](CONTRIBUTING.md) | [指南](CONTRIBUTING.zh-CN.md) |
| Modeling, experiments, operations, and research references | [Reference directory](skills/optimization-modeling-experiments/references) | [参考目录](skills/optimization-modeling-experiments/references/zh-CN) |

```text
optimization-decision-lab/
├── README.md / README.zh-CN.md
├── LICENSE / CONTRIBUTING.md / CONTRIBUTING.zh-CN.md
├── skills/optimization-modeling-experiments/
│   ├── SKILL.md / SKILL.zh-CN.md
│   ├── agents/                 English and Chinese UI metadata
│   ├── references/             English references and zh-CN translations
│   ├── assets/                 JSON examples and bilingual templates
│   └── scripts/                Five tools and one internal shared helper
├── examples/run_demo.py
├── tools/install_skill.py
├── tests/
└── ci/tests.yml
```

## Testing and dependencies

PyYAML is required only for tests checking metadata and workflow configuration. Optional solving tasks may require user-selected packages/backends such as SciPy/HiGHS, CVXPY, or OR-Tools; none is a mandatory dependency of the bundled decision utilities.

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 examples/run_demo.py --output results/my-demo
```

The baseline includes 51 tests for linear checking, scenario metrics, contract records, validity envelopes, and information value, plus repository/localization/installation checks. An optional CI template is provided in `ci/tests.yml` for Python 3.10, 3.12, and 3.13. To enable it, copy it to `.github/workflows/tests.yml` and commit using GitHub credentials with workflow-write permission. It is a template, not an active or remotely verified workflow.

## Evidence and limitations

- Candidate feasibility, solver claims, and optimality evidence are separate. The linear checker never certifies optimality.
- The contract auditor checks declared metadata, not hidden requirements, formula equivalence, or evidence-file truth.
- Plan validity covers fixed linear actions, independent simultaneous parameter boxes, supplied revisions/times, and numerical tolerances; not unmodeled physics, nonlinear rules, recourse, or indefinite validity.
- Scenario weights and observation likelihoods need real provenance. Tools do not calibrate them or establish population guarantees. Information value uses a complete finite, risk-neutral loss table; all actions must be feasible in all declared states.
- No production system is connected and no real operation is triggered by these tools. Field efficacy requires task-specific data and evaluation; software tests and synthetic examples do not establish it.
- The project integrates established modeling/decision methods. It makes no claim of universal industry-first novelty or independent agent benchmark certification.

## License and contributions

Released under the [MIT license](LICENSE). See the [contribution guide](CONTRIBUTING.md) for bilingual maintenance and validation expectations. External linked papers/docs retain their own rights; they are references, not bundled licensed content.
