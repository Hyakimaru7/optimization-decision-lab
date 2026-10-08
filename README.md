# Optimization Decision Lab

**English** | [简体中文](README.zh-CN.md)

`optimization-modeling-experiments` is an agent skill for optimization modeling and experimental validation. It supports production planning, inventory management, scheduling, resource allocation, daily planning, and optimization research.

The skill guides an agent through turning requirements and data into a mathematical model, choosing a solution method, independently checking results, and comparing plans through reproducible experiments. It can handle a complete modeling task or focus on reviewing a model, checking a candidate solution, or designing an experiment.

## What it does

| Capability | Work covered |
| --- | --- |
| Requirements and data review | Identify decisions, objectives, hard constraints, units, decision timing, and data sources; record missing information and assumptions. |
| Formulation and model audit | Define objectives and constraints; check domains, indices, units, feasibility, and reformulation conditions. |
| Solving and result validation | Select a solver for the model and available environment; recompute objectives, constraint residuals, and integrality errors in the original model. |
| Experiment design and reproduction | Set baselines, metrics, data splits, and resource budgets; run sensitivity, ablation, and scaling experiments; retain run and failure records. |
| Uncertainty and plan comparison | Compare costs, shortages, service levels, and tail risk across scenarios; distinguish training performance from evaluation evidence. |
| Requirement tracking and plan maintenance | Check declared requirement mappings and validation records, assess input changes for existing plans, and handle rolling planning and committed actions. |
| Research and information value | Develop testable hypotheses and discriminating experiments; assess whether measurements are worthwhile when credible probabilities and losses are available. |

The workflow covers linear, integer, quadratic, conic, nonlinear, and constraint-programming models. Actual solving capabilities depend on the modeling libraries and solvers available in the environment.

## Installation

Clone the repository and run the installer from its root. The installer requires Python 3.10 or later.

```bash
git clone https://github.com/Hyakimaru7/optimization-decision-lab.git
cd optimization-decision-lab
python3 tools/install_skill.py --language en
```

The default destination is `~/.agents/skills/optimization-modeling-experiments/`. To use the skill only within the current project:

```bash
python3 tools/install_skill.py --language en --destination .agents/skills
```

Use `--language zh-CN` for Chinese instructions. `--destination` specifies the parent skills directory. The installer refuses to overwrite an existing skill with the same name. For manual installation, copy the entire `skills/optimization-modeling-experiments/` directory, including references, scripts, and templates.

Check that Codex recognizes the installed skill; restart the session if discovery has not refreshed. See the [official skill documentation](https://learn.chatgpt.com/docs/build-skills) for directory conventions.

## Invocation

Enter the invocation name in a conversation, followed by your task, data, or file paths:

```text
$optimization-modeling-experiments

Task: <formulation, review, solving, plan comparison, reproduction, or research>
Problem and objective: <what must be decided and how results are measured>
Data or files: <sources, paths, fields, and units>
Mandatory requirements: <hard constraints and conditions that cannot change>
Existing work: <model, code, current plan, or committed actions; optional>
Run budget: <time, computing resources, and available solvers; optional>
Deliverables: <model description, code, decision table, experiment records, or report>
```

You do not need to fill every field. Attach existing formulas or code and identify the parts to review. Specify the scope when you need only one stage of the workflow. Missing information that changes the model's meaning will prompt clarification; other assumptions will be stated with the results.

A complete modeling and experimental task typically delivers a model and assumptions, runnable code and configuration, independent validation, experiment records, and findings. Solver status, candidate feasibility, and optimality evidence are reported separately so you can assess whether a plan is executable and where the conclusions apply.

## Calling the calculation tools directly

The five included tools use only the Python standard library. They can also run independently, reading a JSON file and writing JSON to stdout.

```bash
python3 skills/optimization-modeling-experiments/scripts/<script_name>.py <input.json>
```

| Script | Purpose and input documentation |
| --- | --- |
| `check_linear_solution.py` | [Check an LP/MILP candidate's objective, constraints, bounds, and integrality](skills/optimization-modeling-experiments/references/solver-validation.md#linear-solution-checker) |
| `evaluate_scenarios.py` | [Summarize supplied scenario outcomes: costs, shortages, violations, and CVaR](skills/optimization-modeling-experiments/references/uncertainty-and-scenarios.md#scenario-evaluator) |
| `audit_requirement_contract.py` | [Check declared requirement mappings, revisions, and validation records](skills/optimization-modeling-experiments/references/requirement-contract.md) |
| `assess_plan_validity.py` | [Assess a fixed linear plan under declared input changes, revision checks, and time conditions](skills/optimization-modeling-experiments/references/plan-validity.md) |
| `evaluate_information.py` | [Calculate information value and net measurement benefit from finite losses, probabilities, and observation models](skills/optimization-modeling-experiments/references/decision-information.md) |

Exit code `2` means invalid input. In the first four tools, `1` indicates a failed candidate, failed execution outcomes, or required review; the information evaluator does not use `1`. Code `0` means the tool completed its check or calculation; read the output fields for the conclusion. These tools do not replace a solver, independently verify business semantics or probability sources, or certify global optimality.

## Documentation

- [Skill instructions](skills/optimization-modeling-experiments/SKILL.md)
- [Modeling, solving, experiments, and decision references](skills/optimization-modeling-experiments/references)
- [Configuration and report templates](skills/optimization-modeling-experiments/assets)
- [Contribution guide](CONTRIBUTING.md)

## Development and testing

Tests require PyYAML. Install modeling libraries and solvers as needed for actual solving tasks.

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
```

An optional CI configuration is provided in [ci/tests.yml](ci/tests.yml). To enable it, copy it to `.github/workflows/tests.yml` and commit with credentials that permit workflow writes.

## License

[MIT](LICENSE)
