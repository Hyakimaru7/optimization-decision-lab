# From a practical problem to a decision

**English** | [简体中文](zh-CN/problem-to-decision.md)

Use for natural-language requirements, business tables, daily planning, and policy selection. Apply relevant checks; domain patterns are not mandatory questionnaires.

## Decision brief

Identify decision makers, controllable actions, decision/execution times, available information, objectives, hard requirements/preferences, current rules, resources, and acceptable latency. Clarify whether nonservice, delay, overtime, outsourcing, or other recourse is allowed.

Translate “best,” “cheap,” “fair,” and “robust” into testable definitions. A cost objective does not automatically represent comfort, service, stability, or fairness. Present representative feasible tradeoffs for conflicting goals; weights/priorities come from users or labeled assumptions, not universal preference claims.

Separate model optimality, implementability, and willingness to execute. Explain comparison to current practice, active constraints, improvement costs, assumptions, and alternatives. Use rules or analytic calculations for simple problems; justify what a more complex model adds.

## Data readiness

Check units, entity/time granularity, keys, joins, and decision cutoffs. Establish join cardinality before aggregating; duplicate joins must not double-count costs, inventory, or hours.

Distinguish missing, zero, not applicable, and unobservable. Missing capacity is neither zero nor infinity. Record filtering, outliers, and imputation. Use ranges/scenarios for critical missing inputs instead of false precision.

Check demand censoring from stockouts: sales need not equal demand. Determine whether times, costs, and equipment states reflect previous policy selection; resulting bias can impair extrapolation.

Predictors need inputs available at each decision, training cutoffs, and error structure. Assess downstream costs/violations as well as prediction errors; higher accuracy alone does not establish better decisions.

## Domain patterns for finding omissions

| Context | Decisions/goals | Potentially relevant omissions | Useful acceptance metrics |
| --- | --- | --- | --- |
| Production/inventory | Batches, procurement, replenishment; cost/service | Startup, switching, minimum batches, lead times, inventory, commitments | Executable orders, shortage/delay, inventory, full cost |
| Staff/task scheduling | People/equipment and periods | Qualifications, availability, rest, precedence, nonoverlap | Coverage, conflicts, preferences, changes |
| Routing/travel | Routes, assignment, departures | Windows, handling, capacities, reachability, variable travel time | Arrival, lateness, distance, operating cost |
| Energy/equipment | Load, storage, on/off states | Power versus energy, efficiency, ramping, SOC, terminal state | Dynamic balance, peaks, full cost, feasible state |
| Daily/family resources | Time/budget allocation | Fixed arrangements, travel, energy, priorities, stability | Feasible schedules, preferences, budget, adjustment cost |
| Research/experiments | Samples, instruments, conditions | Resolution, noise, identifiability, batches, experimental cost | Information value, error, distinguishability, budget |

These are modeling prompts, not new policies or laws. Verify the provenance, applicability, and version of external requirements; never invent rules from a domain name. Retrieve external data/docs only when needed.

## Cost and benefit conventions

Separate incremental decision costs from fixed/sunk costs. Define procurement, inventory, shortage, recovery, startup, energy, travel, and switching terms. Avoid counting staged expenses twice. Keep fitted and reported units consistent.

Objective constants do not affect ranking within one model but matter for cross-model total costs, benefit reporting, and relative gaps. Restore them; do not manufacture improvements by rescaling different objectives.

Subtract implementation/switching costs and specify the comparison horizon. Interpret shadow prices only within the model, local perturbation ranges, and applicable duality conditions. Integer jumps, large expansion, and structural changes require reoptimization rather than unrestricted multiplier extrapolation.

## Delivering with insufficient data

State the smallest model supported, unidentified parameters, their effects, and the most valuable missing data. Label assumed ranges/scenarios. Branch or ask when different meanings change the plan.

Adapt the [decision brief](../assets/decision-brief-template.md).

## Sources

- [OR-Tools employee scheduling](https://developers.google.com/optimization/scheduling/employee_scheduling).
- [Smart Predict, then Optimize](https://arxiv.org/abs/1710.08005): prediction error differs from decision loss; verify assumptions before using particular methods/guarantees.
