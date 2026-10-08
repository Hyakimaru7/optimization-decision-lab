# Measurements and experiments that change decisions

**English** | [简体中文](zh-CN/decision-information.md)

Use for missing parameters, measurement purchases, distinguishing experiments, or stopping data collection. Information gain and prediction accuracy are not automatically decision benefits.

## Timing and assumptions

List actions, unknown states, same-unit losses, current information, observation mechanisms, measurement cost/delay, and deadlines. Distinguish future randomness from currently unknown parameters. Observations must arrive early enough to change actions; fixed commitments cannot receive retrospective selection gains.

Use expected information value with credible probabilities/losses; otherwise use ranges, action-switch boundaries, scenario regret, or minimal distinguishing experiments. Arbitrary weights do not establish guaranteed payback, and maximum parameter variance does not determine measurement priority.

## Finite-table evaluation

From the skill directory:

```bash
python3 scripts/evaluate_information.py assets/information-example.json
```

All actions must be feasible in every listed state. Otherwise model explicitly feasible recourse policies/costs or use a suitable two-stage formulation. The script requires `actions_feasible_in_all_states:true`, a caller declaration requiring independent checking. Large finite penalties cannot absorb inviolable constraints.

For losses L(a,theta) and probabilities p(theta):

- Current optimum `C0=min_a sum_theta p(theta)*L(a,theta)`.
- Perfect-information loss `CPI=sum_theta p(theta)*min_a L(a,theta)`; `EVPI=C0-CPI`. This idealized bound uses the same action set and is not a purchasable observation automatically.
- Experiment e produces signals z with q(z|theta,e). Optimal observed loss `Ce=sum_z min_a sum_theta p(theta)*q(z|theta,e)*L(a,theta)`.
- `EVSI=C0-Ce`; net value subtracts experiment cost. Under this complete risk-neutral table, `0<=EVSI<=EVPI`, up to arithmetic error.
- Action worst regret is `max_theta[L(a,theta)-min_b L(b,theta)]`. Minimizing it is minimax regret over declared states, distinct from minimizing worst loss and not a guarantee beyond the set.

Required top level: `distribution_kind` (`hypothetical/empirical/calibrated`), `loss_unit`, the feasibility declaration, nonempty unique `states`, matching `probabilities`, nonempty unique `actions`, action-row/state-column `losses`, and `experiments`. Finite numbers, including negative losses; probabilities nonnegative and sum to 1 within 1e-9 roundoff.

Experiments contain `id,signals,likelihood,cost,available_before_decision`; likelihood is state-row/signal-column, each row sums to 1. Costs are nonnegative in loss units; timing declaration is true. Zero-probability signals have no selected action. Expected losses ignore zero-weight states; minimax regret includes all declared states. Ties choose the first input action without claiming uniqueness.

The script does not fit likelihoods, generate data, or verify calibration. Exit 0 means evaluated, 2 invalid. Check real gains/probabilities/discrepancy with data; `calibration_verified` and `population_guarantee` are always false. Combining experiments requires joint/sequential modeling; their individual EVSIs are not additive.

## Practical and scientific use

Specify the action measurement can change, then choose a timely experiment distinguishing relevant states. Record policies, measurement cost/delay/quality, and consistent realized losses. Begin with small/ shadow replay; actual pilots require user authorization.

Without a defensible application loss, propose a falsifiable distinguishing experiment: where competing mechanisms predict differently, what is observed, noise, and results rejecting each mechanism. Structural nonidentifiability requires changed design; repeating identical experiments cannot create missing identifying information.

A justified EVPI can bound further information spending for the same decision/actions/horizon. If even the cheapest information exceeds it, stopping may be reasonable within that scope. This cannot stop research seeking new actions/mechanisms or long-term scientific knowledge.
