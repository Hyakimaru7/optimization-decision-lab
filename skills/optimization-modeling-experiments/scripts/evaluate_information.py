#!/usr/bin/env python3
"""Compare finite decision losses and noisy measurements by expected decision value."""
import sys
from check_linear_solution import vector
from decision_support_common import obj, label, labels, nonnegative, total, cli


def probabilities(raw, n, name):
    values = vector(raw, n, name)
    if any(v < 0 for v in values) or abs(total(values) - 1) > 1e-9:
        raise ValueError(f"{name} must be nonnegative and sum to one")
    s = total(values)
    return [p / s for p in values]


def evaluate(data):
    """Compute EVPI, EVSI and minimax regret on a supplied complete loss table."""
    obj(data, ("distribution_kind", "loss_unit", "actions_feasible_in_all_states", "states", "probabilities", "actions", "losses", "experiments"), "input")
    if data["distribution_kind"] not in ("hypothetical", "empirical", "calibrated"):
        raise ValueError("invalid distribution_kind")
    label(data["loss_unit"], "loss_unit")
    if data["actions_feasible_in_all_states"] is not True:
        raise ValueError("all listed actions must be feasible in all states; redesign infeasible actions or model recourse explicitly")
    states = labels(data["states"], "states", True)
    actions = labels(data["actions"], "actions", True)
    p = probabilities(data["probabilities"], len(states), "probabilities")
    raw_losses = data["losses"]
    if not isinstance(raw_losses, list) or len(raw_losses) != len(actions):
        raise ValueError("losses must have one row per action")
    losses = [vector(row, len(states), "losses") for row in raw_losses]
    expected = [total(c * q for c, q in zip(row, p)) for row in losses]
    base_index = min(range(len(actions)), key=lambda i: expected[i])
    base = expected[base_index]
    state_best = [min(row[j] for row in losses) for j in range(len(states))]
    perfect = total(c * q for c, q in zip(state_best, p))
    regrets = [max(total((row[j], -state_best[j])) for j in range(len(states))) for row in losses]
    regret_index = min(range(len(actions)), key=lambda i: regrets[i])
    if not isinstance(data["experiments"], list):
        raise ValueError("experiments must be an array")
    ids = set()
    records = []
    for experiment in data["experiments"]:
        obj(experiment, ("id", "signals", "likelihood", "cost", "available_before_decision"), "experiment")
        eid = label(experiment["id"], "experiment.id")
        if eid in ids:
            raise ValueError("duplicate experiment id")
        ids.add(eid)
        if experiment["available_before_decision"] is not True:
            raise ValueError("experiment signals must be available before the decision")
        signals = labels(experiment["signals"], "signals", True)
        raw = experiment["likelihood"]
        if not isinstance(raw, list) or len(raw) != len(states):
            raise ValueError("likelihood must have one row per state")
        likelihood = [probabilities(row, len(signals), "likelihood row") for row in raw]
        cost = nonnegative(experiment["cost"], "experiment.cost")
        contributions = []
        policy = []
        for k, signal in enumerate(signals):
            mass = total(p[j] * likelihood[j][k] for j in range(len(states)))
            joint_losses = [total(p[j] * likelihood[j][k] * row[j] for j in range(len(states))) for row in losses]
            chosen = min(range(len(actions)), key=lambda i: joint_losses[i]) if mass > 0 else None
            contributions.append(joint_losses[chosen] if chosen is not None else 0)
            policy.append({"signal": signal, "probability": mass,
                           "action": actions[chosen] if chosen is not None else None})
        informed = total(contributions)
        gross = total((base, -informed))
        net = total((gross, -cost))
        records.append({"id": eid, "expected_loss_after_observation": informed,
                        "evsi_gross": gross, "experiment_cost": cost, "net_value": net,
                        "worthwhile_under_given_table": net > 0, "signal_policy": policy})
    best = min(records, key=lambda r: r["expected_loss_after_observation"] + r["experiment_cost"]) if records else None
    return {"status": "evaluated", "distribution_kind": data["distribution_kind"], "loss_unit": data["loss_unit"],
            "baseline_action": actions[base_index], "baseline_expected_loss": base,
            "expected_loss_with_perfect_information": perfect, "evpi": total((base, -perfect)),
            "actions": [{"id": a, "expected_loss": e, "worst_regret_over_declared_states": r} for a, e, r in zip(actions, expected, regrets)],
            "minimax_regret_action": actions[regret_index], "experiments": records,
            "selected_experiment": best["id"] if best and best["net_value"] > 0 else None,
            "calibration_verified": False, "population_guarantee": False,
            "scope": "finite supplied actions/states, risk-neutral loss; perfect information is an idealized bound; minimax includes zero-probability declared states"}


if __name__ == "__main__":
    sys.exit(cli(evaluate, lambda r: True))
