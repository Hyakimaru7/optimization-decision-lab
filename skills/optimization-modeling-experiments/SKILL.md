---
name: optimization-modeling-experiments
description: "Turn production, daily planning, and research problems into executable optimization decisions and reproducible experiments. Use for optimization modeling, business-rule coverage, data review, solution validation, uncertainty and policy comparison, existing-plan validity, rolling planning, information value, and research hypotheses; not for unrelated software performance tuning."
metadata:
  version: "3.0.0"
---

# Optimization Modeling and Experimental Validation

**English** | [简体中文](SKILL.zh-CN.md)

Turn the user's problem into decisions with clear semantics, consistent mathematics, executable actions, and checkable evidence. Evaluate the problem formulation, numerical solution, and application outcome separately. Develop theory when it is needed for correct modeling, method applicability, or interpretation. Respond in the user's requested language.

## Scope and defaults

Handle LP, QP, convex conic optimization, continuous nonlinear optimization, MILP, MIQP, constraint programming, and nonconvex models requiring special treatment. Respect the structure of stochastic, robust, bilevel, dynamic, multiobjective, and expensive black-box problems; do not transfer ordinary convex guarantees indiscriminately.

Identify the request: clarify requirements, formulate, audit, implement and solve, compare policies or methods, reproduce, explore research, or plan during operation. Use the smallest sufficient model for a simple problem. Do not enable risk, simulation, or statistics by default. A request for a complete experiment requires execution, not just a plan.

Reuse the project's language, dependencies, notation, and directory conventions. Without an existing stack, consider Python and open tools suited to the model. Check installed modeling packages, actual solver backends, and licenses. This skill requires no fixed solver, commercial license, or network connection.

Ask only for missing information that changes the model meaning or prevents execution, such as objective direction, integrality, or whether a hard constraint may be violated. Continue independent work. Label provisional assumptions and explain their impact; explicitly identify synthetic data.

## Read only relevant resources

- For natural-language requests, business tables, daily planning, or policy choice, read [Problem to decision](references/problem-to-decision.md).
- For formulation, reformulation, units, or constraint semantics, read [Model audit](references/model-audit.md).
- For solver selection, returned solutions, statuses, or optimality claims, read [Solver validation](references/solver-validation.md). Numerical solving must include its original-model validation procedure.
- For comparison, reproduction, sensitivity, or batch experiments, read [Experiment protocol](references/experiment-protocol.md).
- For forecast errors, unknown distributions, supply variability, or out-of-sample claims, read [Uncertainty and scenarios](references/uncertainty-and-scenarios.md).
- For executable plans, time evolution, replay, replanning, or execution feedback, read [Operational validation](references/operational-validation.md).
- For research questions, model discrepancy, identification, experimental design, or expensive black boxes, read [Research exploration](references/research-exploration.md).
- For many requirements, handoffs, repeated model edits, or omitted critical rules, read [Requirement contracts](references/requirement-contract.md). Optionally use the [contract auditor](scripts/audit_requirement_contract.py); it checks declared links and evidence records, not natural-language equivalence.
- To reuse a plan, evaluate buffers, or review input changes, read [Plan validity](references/plan-validity.md). Use the [validity assessor](scripts/assess_plan_validity.py) for fixed linear plans. Model, data, or context revisions require review; the tool does not authorize execution.
- To choose between measurement and immediate action, read [Decision information](references/decision-information.md). Use the [information evaluator](scripts/evaluate_information.py) for complete finite loss tables. Do not invent probabilities, measurement accuracy, or benefits.
- When asked to assess this skill or workflow, read [Acceptance cases](references/acceptance-cases.md). Do not run every case by default.
- For a new complete experiment, adapt the [configuration](assets/experiment-config.json) and [report template](assets/research-report-template.md). The configuration is a project convention, not a solver-native input.
- To independently check an LP/MILP candidate, use the [linear checker](scripts/check_linear_solution.py). See [its schema and limits](references/solver-validation.md#linear-solution-checker). It checks feasibility and objectives, not optimality.
- To compare costs, shortfalls, and tail risks on shared scenarios, use the [scenario evaluator](scripts/evaluate_scenarios.py). See [its schema](references/uncertainty-and-scenarios.md#scenario-evaluator). It summarizes supplied outcomes, not simulations or calibrated probabilities.
- Adapt the [decision brief](assets/decision-brief-template.md) or [research hypothesis record](assets/research-hypothesis-template.md) when useful; do not create every template automatically.

## 1. Establish the question and evidence

From the description, formulas, data, and code, identify the objective, decisions, decision times, parameters and uncertainties, data sources, evaluation criteria, and resource budget.

Establish who decides what and when, what is then known, how the plan is executed, and what counts as success. Separate the actual goal from its computable proxy. Record important omitted mechanisms, user-specified nonnegotiable requirements, and the current policy. Solver output alone does not establish that the real question was answered.

Review data granularity, time windows, units, keys and joins, missingness and duplication, truncation or censoring, forecast bias, identifiability, and availability at the decision time. If data cannot support a detailed model, choose an interpretable simplification and explain the missing information and its value.

Link research hypotheses to model changes, observable metrics, and experiments. For example, test whether robust constraints reduce out-of-sample violations and quantify their extra cost. Keep modeling quality, solution quality, and application effectiveness separate.

Distinguish facts, user requirements, added assumptions, and untested conjectures. Verify methods, theorems, and recent claims against original papers or official documentation, with traceable sources. Never fabricate citations, runs, results, or novelty.

## 2. Build a checkable model

Provide the elements the problem needs:

- Sets, indices, decisions, parameters, dimensions, units, domains, and sources.
- The original objective direction, meaning of each term, and normalization.
- Each constraint class, interpretation, index scope, and boundary cases.
- Assumptions, their basis, effect, and planned validation.

Use a common representation where helpful, without forcing a rewrite:

\[
\operatorname{min/max}_x f(x;\theta),\qquad
g_i(x;\theta)\le0,\quad h_j(x;\theta)=0,\quad x\in\mathcal X.
\]

Check units, indices, objective direction, domains, boundaries, feasibility, and boundedness. State missing existence or uniqueness conditions; convexity alone is insufficient. Check initial/terminal states and recurrences in time models, and information availability and nonanticipativity in stochastic models.

Separate hard requirements, soft requirements, and preferences. Explain weights and scales. For user priorities, consider lexicographic or epsilon-constraint formulations rather than silently substituting a weighted sum.

For production, scheduling, routing, budgeting, daily planning, or research allocation, inspect relevant startup and batch costs, minimum demand, time windows, switching, shared resources, qualifications, reachability, and service rules. Domain patterns reveal possible omissions; they do not authorize new requirements. Trace each constraint to a requirement or labeled assumption.

For important rules, preserve source, formula/code, independent validation, and a rejected counterexample. Prevent both model and checker from omitting the same rule. Solver success cannot compensate for an unmapped or untested requirement. A short table is sufficient for simple problems.

## 3. Classify and reformulate

Assess variable domains, smoothness, convexity, separability, sparsity, quadratic/conic/logical structure, and expected size. Justify property claims; failure of a tool's DCP rules does not prove nonconvexity.

For each reformulation, state the original and transformed expressions, conditions, equivalence/relaxation/approximation, variable recovery, and objective mapping.

Check valid Big-M bounds, rounding, denominator signs in fractional transformations, product linearization, epigraphs for absolute values/maxima, penalties, and smoothing. Do not claim equivalence without support.

For nonconvex, MINLP, or bilevel problems, state local/global boundaries. Before replacing an inner problem by KKT conditions, check applicability and overall equivalence.

## 4. Choose tools and implement

Choose by structure, size, sparsity, available dependencies, licenses, and required guarantees. Examples:

| Model | Possible entry point | Key boundary |
| --- | --- | --- |
| LP / MILP | SciPy's HiGHS interfaces or an existing modeling system | Preserve status, incumbents, valid bounds, and gap |
| Discrete scheduling / logic | OR-Tools CP-SAT or an existing CP system | Check integer encoding/scaling; feasible is not optimal |
| Convex QP / conic | CVXPY with an installed compatible solver | Check cone support and numerical accuracy |
| Smooth constrained nonlinear | SciPy or an existing NLP system | Generally local guarantees |
| Nonconvex mixed integer | An appropriate MINLP/global solver | Separate local results, global bounds, and time limits |
| Large structured models | Decomposition, proximal, or domain methods | Validate subproblems and stopping criteria |

Do not equate a modeling package with a working backend. Consult current official documentation when capabilities matter; record actual runtime versions.

Separate loading, modeling, solving, and verification. Keep independent original-objective and constraint functions rather than relying solely on transformed solver objects. Prefer sparse representations at scale and report variable, constraint, and nonzero counts.

Expose instances, model/solver parameters, tolerances, seeds, threads, limits, and output paths. Provide executable entry points and precise dependency records. Run a minimal instance before scaling.

Estimate growth, memory, and budgets before expanding. Enumeration is for appropriately small cases and checking. For larger problems, consider aggregation, sparsity, decomposition, heuristics, or early stopping, with quality evidence and losses. A usable time-limited incumbent can have value; unlimited retries are not diagnosis.

## 5. Validate solutions and claims

First inspect whether a solution exists, its shape and finite values, raw status, and termination reason. Without a usable solution, do not invent objectives or residuals.

Recompute the original objective, constraint residuals, bounds, and integrality after recovering variables, signs, scales, and constants. Preserve absolute residuals and scales; explain tolerances and units.

Report solver claims, independent original-model validation, and applicable optimality evidence separately. Use suitable gradient/proximal/KKT measures or valid bounds. Feasibility does not establish optimality.

For nonconvex problems, stationarity, agreement across initializations, and a better objective do not certify global optimality. A time-limited MIP incumbent with an open bound remains informative, but is not proven optimal.

For execution, additionally check the business/physical process: scheduling conflicts, lead times, inventory, shared resources, recovery, switching, and relevant preferences. Simulation/replay reveal issues in represented mechanisms, not every real mechanism. Provide executable decision tables, justified buffers, and alternatives.

Specify bound direction, source, original-objective mapping, and gap definition. Without a valid bound, report unknown; label differences from numerical references as reference differences. Diagnose negative gaps without silently clipping or dropping them.

Diagnose low accuracy, numerical failures, infeasibility, or unboundedness using [Solver validation](references/solver-validation.md). Log retries and changes to constraints, scale, tolerances, or solver. Do not soften hard requirements without authorization.

Distinguish fixed-plan feasibility under input changes, reoptimized sensitivity, decision change, and actual failure. Record model/data/context revisions, validity periods, committed actions, and review events. Check hard feasibility first; consider benefit bounds, switching costs, and compute costs before reoptimizing. Small changes alone are not evidence.

## 6. Design and execute experiments

A complete experiment specifies main metrics, baselines, instance generation/splits, sizes, parameter changes, repetitions, tuning, and resource budgets. Include a runnable starting configuration and its scope.

Without a budget, begin with a small smoke check and estimate batch costs. Distinguish exploratory findings from predefined comparisons; do not select favorable instances or stopping rules after seeing results.

Choose baselines answering the question: original models, simple policies, relaxations, mature solvers, or established methods. Across models, compute shared application metrics rather than comparing differently defined objectives alone.

Use comparable instances and resources. Define initialization, tuning, preprocessing, compilation, warm starts, and timing. Pair random comparisons by instance/scenario where possible. Deterministic repetitions mainly measure timing variation.

Select ablations, sensitivity, interactions, scale studies, and out-of-sample evaluation as relevant. For inference, define independent units, pairing, and uncertainty sources; repeated timing of one instance is not additional independent instance data.

For suspected implementation bugs, test justified invariants under renaming, variable permutation, positive unit scaling, redundant constraints, and constraint relaxation. Relaxing constraints cannot reduce a proven maximization optimum. Multiple optima, time limits, and tolerances can change actions or incumbent ordering; test appropriate invariants.

Separate fitting/training, tuning, frozen-policy evaluation, and stress tests. Unknown probabilities must not be presented as empirical distributions. Compare consistent end-to-end costs, recovery rules, means, service, tails, and hard violations. Limit unsupported generalization to conditional scenario findings.

For rolling planning, separate advance decisions from observed-state recourse and freeze executed/committed actions. Update actual states. Compare baselines under the same information and forecast rules; prevent future leakage in replay.

With insufficient data, identify unknowns that could change actions and the smallest measurement or distinguishing experiment available before the decision. Compute information value only with defensible loss/observation models. Information gain, prediction accuracy, and decision benefit are different objectives. Without credible probabilities, use bounds, counterexamples, and scenario regret.

Save all planned attempts, including failure, timeout, and no solution. Distinguish normal infeasible scenarios from technical failures. Do not assign zero cost or zero gap to failed runs. Report valid counts, failures, and denominators.

## 7. Deliver and finish

Deliver files needed for this task, not empty boilerplate. A full experiment usually includes:

- Model/assumptions and data provenance/processing.
- Executable code, configuration, actual environment, and reproduction commands.
- Planned runs, raw records, solutions/logs or traceable paths.
- Original-model validation, summaries/figures, conclusions, and applicability.

For actual decisions, include effective times, input snapshots, execution meaning, benefits relative to the current policy, switching costs, and invalidation conditions. For research, include falsifiable hypotheses, nearest baselines, minimal distinguishing experiments, and evidence gaps. Record novelty-search scope; absence from a search is not proof of novelty.

Follow workspace conventions, separating scratch files and deliverables. Every reported number must trace to execution records. Keep synthetic and real evidence distinct.

Before completing a solving/experimental task, confirm that minimal instances ran and were checked, requested experiments ran or precise environment blockers are disclosed, claims match statuses/residuals/bounds, and reproduction works. Deliver completed work and exact missing pieces when blocked; never claim unexecuted work ran.

Lead the final report with results and evidence, then files, commands, and material limitations. Finite experiments do not prove universal optimality, convergence, novelty, or out-of-sample benefit.
