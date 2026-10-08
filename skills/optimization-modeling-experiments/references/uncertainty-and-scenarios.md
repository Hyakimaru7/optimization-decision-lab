# Uncertainty, service, and scenario evaluation

**English** | [简体中文](zh-CN/uncertainty-and-scenarios.md)

Read when uncertain demand, time, cost, or supply affects decisions, or out-of-sample benefits are claimed. Do not introduce complex stochastic models automatically.

## Sources of uncertainty

Separate estimable randomness, parameter estimation, structural discrepancy, extreme stress, and unknown probabilities. Preserve temporal/spatial/entity dependencies; independent sampling can create impossible combinations.

Record forecast/scenario/set provenance, training cutoffs, units, and calibration. Without distribution support, use intervals and explicit conditional scenarios. Equal or expert weights are not measured distributions.

## Modeling routes

| Route | Consider when | Boundary to explain |
| --- | --- | --- |
| Nominal deterministic | Small error impact or a baseline | No automatic feasibility under variability |
| Expected/scenario two-stage | Usable scenarios/weights and recourse | Advance decisions, later observations, limited and charged recourse |
| Chance constraints | User permits probabilistic service violations | Joint versus individual probabilities, calibration, sample guarantees |
| Robust | Requirements over an explicit uncertainty set | Set-relative guarantee, unknown outside, conservatism costs |
| Distributionally robust | Calibratable distribution ambiguity | Set/radius provenance and guarantee conditions; not automatically reliable |
| Risk objectives/constraints | High losses matter beyond averages | Shared loss, level, weight, service meaning |

Do not observe the future and reselect an advance action while calling it executable. Scenario trees need nonanticipativity; recourse uses only information visible then. Label perfect-information oracles as idealized bounds/diagnostics.

## Shared metrics

On identical evaluation scenarios and cost/recourse rules, report relevant expected costs, shortfalls, hard violations, and tail risk. Shortage penalties do not authorize hard violations.

Separate shortage-free probability, demand-volume-weighted fill, maximum shortfall, and group/time service. A mean of ratios differs from a ratio of totals; good aggregate service need not satisfy every group.

For losses l_s with probabilities p_s:

\[
\operatorname{CVaR}_{\alpha}(l)=\min_{\eta}\left[\eta+\frac{1}{1-\alpha}\sum_s p_s(l_s-\eta)_+\right],\quad 0\le\alpha<1.
\]

Weights are nonnegative and sum to one. CVaR measures upper-tail losses, not a confidence interval. Split probability mass at a discrete tail boundary; do not simply average observations above VaR. Simulated losses produce model/distribution-conditional risk.

Explain alpha, lambda, units, and preferences for `E[l]+lambda*CVaR`; this changes the objective without automatically guaranteeing service. Finite training/evaluation scenarios do not certify population tails.

## Evaluation and stress

Separate fitting/training, tuning, and evaluation by decision time. Freeze policies; using test results to change them starts a new tuning cycle requiring fresh independent evaluation.

Replay can lack outcomes for unused actions or suffer selection bias. Describe identification limits; simulated comparisons do not directly prove real causal gains.

Report stress scenarios separately with design rationale: demand peaks, supply delay, failures, shifts. Uncalibrated extremes should not silently enter expectations. Passing a finite list is not a universal robust certificate.

Report samples, independent units, and pairing. No observed rare event does not establish zero probability. Artificial scenario weights are not IID samples; scenario count alone does not justify confidence intervals.

## Scenario evaluator

`scripts/evaluate_scenarios.py` uses the standard library to summarize supplied outcomes on shared scenarios: weighted costs, CVaR, service, and hard-violation probabilities. It does not solve, simulate, fit probabilities, or certify population reliability.

```json
{
  "distribution_kind": "hypothetical", "cost_unit": "yuan", "demand_unit": "units", "alpha": 0.9,
  "scenarios": [
    {"id": "low", "probability": 0.25, "demand": 4},
    {"id": "mid", "probability": 0.5, "demand": 8},
    {"id": "high", "probability": 0.25, "demand": 14}
  ],
  "policies": [{"id": "stock-8", "outcomes": [
    {"scenario_id": "low", "status": "ok", "total_cost": 20, "shortfall": 0, "hard_violation": false},
    {"scenario_id": "mid", "status": "ok", "total_cost": 16, "shortfall": 0, "hard_violation": false},
    {"scenario_id": "high", "status": "ok", "total_cost": 46, "shortfall": 6, "hard_violation": false}
  ]}]
}
```

Declare `hypothetical`, `empirical`, or `calibrated`; the tool does not verify that declaration. Each policy covers every scenario exactly once. Probabilities must be nonnegative and sum to 1 within 1e-9; only roundoff normalization is allowed. Missing/failed scenarios cannot be silently dropped.

`shortfall` is within [0,demand] in demand units; `hard_violation` is explicitly Boolean. Failure uses `status:"failed"` and a nonempty `error` without invented metrics. Complete cost/service/risk metrics then become unknown, with failure count/probability retained. Zero-probability scenarios remain traceable; even their failures mark evaluation incomplete.

Alpha defaults to 0.9 and lies in [0,1). `shortfall_tolerance` defaults to zero and affects only the reported shortage event, not quantities or hard rules. Negative costs are allowed, consistently interpreted as losses to minimize.

From the skill directory run `python3 scripts/evaluate_scenarios.py assets/scenario-example.json`. Exit 0 means complete evaluation, 1 means failures and unknown metrics, 2 means invalid input. Complete does not mean hard-feasible: inspect violations. No intervals, significance, or real probabilities are inferred.

The [synthetic inventory example](../assets/scenario-example.json) uses q=0,...,15 and `l(q,d)=2q+(q-d)_+ +5(d-q)_+`. On demands {4,8,14} with weights {.25,.5,.25}, mean cost chooses q=8, mean plus CVaR_0.9 chooses q=12, and minimum expected cost while covering modeled demands chooses q=14. Freeze these and evaluate {6,10,16} using the same hypothetical weights. Service shortage is distinct from physical q-domain feasibility; this is not a demand forecast or population guarantee.

## Sources

- [Rockafellar and Uryasev: CVaR optimization](https://sites.math.washington.edu/~rtr/papers/rtr179-CVaR1.pdf).
- [CVaR for general loss distributions](https://sites.math.washington.edu/~rtr/papers/rtr187-CVaR2.pdf).
