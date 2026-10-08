#!/usr/bin/env python3
"""Evaluate supplied policy outcomes on shared scenarios; no optimization or probability fitting."""
import argparse
import json
import math
from pathlib import Path
import sys


def num(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    try:
        result = float(value)
    except (ValueError, OverflowError) as error:
        raise ValueError(f"{label} must be a finite number") from error
    if not math.isfinite(result):
        raise ValueError(f"{label} must be a finite number")
    return result


def object_fields(value, allowed, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    unknown = set(value) - set(allowed)
    if unknown:
        raise ValueError(f"{label} has unsupported fields: {sorted(unknown)}")


def identifier(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def finite_sum(values, label):
    try:
        value = math.fsum(values)
    except (ValueError, OverflowError) as error:
        raise ValueError(f"{label} overflow; rescale values") from error
    if not math.isfinite(value):
        raise ValueError(f"{label} is nonfinite; rescale values")
    return value


def weighted_cvar(costs, probabilities, alpha):
    """Upper-tail mean with probability mass split at a discrete quantile."""
    if len(costs) != len(probabilities) or not costs:
        raise ValueError("costs and probabilities must have equal positive length")
    alpha = num(alpha, "alpha")
    if not 0 <= alpha < 1:
        raise ValueError("alpha must be in [0, 1)")
    pairs = [(num(c, "cost"), num(p, "probability")) for c, p in zip(costs, probabilities)]
    if any(p < 0 for _, p in pairs):
        raise ValueError("probabilities must be nonnegative")
    total = finite_sum((p for _, p in pairs), "probability total")
    if abs(total - 1) > 1e-9 or total <= 0:
        raise ValueError("probabilities must sum to 1 within 1e-9")
    tail = 1.0 - alpha
    remaining = tail
    terms = []
    for cost, p in sorted(pairs, reverse=True):
        mass = min(remaining, p / total)
        if mass > 0:
            # Divide first: prevents underflow of cost * very small tail mass.
            terms.append(cost * (mass / tail))
            remaining = max(0.0, remaining - mass)
        if remaining == 0:
            break
    if remaining > 1e-12 * tail:
        raise ValueError("insufficient probability mass for CVaR")
    return finite_sum(terms, "CVaR")


def evaluate(data):
    object_fields(data, ("distribution_kind", "cost_unit", "demand_unit", "alpha",
                        "shortfall_tolerance", "scenarios", "policies", "baseline_policy_id"), "input")
    kind = data.get("distribution_kind")
    if kind not in ("hypothetical", "empirical", "calibrated"):
        raise ValueError("distribution_kind must be hypothetical, empirical, or calibrated")
    cost_unit = identifier(data.get("cost_unit"), "cost_unit")
    demand_unit = identifier(data.get("demand_unit"), "demand_unit")
    alpha = num(data.get("alpha", 0.9), "alpha")
    tolerance = num(data.get("shortfall_tolerance", 0), "shortfall_tolerance")
    if not 0 <= alpha < 1 or tolerance < 0:
        raise ValueError("alpha must be in [0,1), shortfall_tolerance nonnegative")
    raw_scenarios = data.get("scenarios")
    if not isinstance(raw_scenarios, list) or not raw_scenarios:
        raise ValueError("scenarios must be a nonempty array")
    scenarios = {}
    for entry in raw_scenarios:
        object_fields(entry, ("id", "probability", "demand"), "scenario")
        sid = identifier(entry.get("id"), "scenario.id")
        if sid in scenarios:
            raise ValueError(f"duplicate scenario: {sid}")
        probability = num(entry.get("probability"), "scenario.probability")
        demand = num(entry.get("demand"), "scenario.demand")
        if probability < 0 or demand < 0:
            raise ValueError("probability and demand must be nonnegative")
        scenarios[sid] = {"probability": probability, "demand": demand}
    total = finite_sum((s["probability"] for s in scenarios.values()), "probability total")
    if abs(total - 1) > 1e-9 or total <= 0:
        raise ValueError("probabilities must sum to 1 within 1e-9; do not silently normalize")
    for scenario in scenarios.values():
        scenario["probability"] /= total
    expected_demand = finite_sum((s["probability"] * s["demand"] for s in scenarios.values()),
                                "expected demand")
    policies = data.get("policies")
    if not isinstance(policies, list) or not policies:
        raise ValueError("policies must be a nonempty array")
    reports = {}
    for policy in policies:
        object_fields(policy, ("id", "outcomes"), "policy")
        pid = identifier(policy.get("id"), "policy.id")
        if pid in reports:
            raise ValueError(f"duplicate policy: {pid}")
        outcomes = policy.get("outcomes")
        if not isinstance(outcomes, list):
            raise ValueError("policy.outcomes must be an array")
        by_id, failures = {}, []
        for outcome in outcomes:
            object_fields(outcome, ("scenario_id", "status", "total_cost", "shortfall",
                                   "hard_violation", "error"), "outcome")
            sid = identifier(outcome.get("scenario_id"), "outcome.scenario_id")
            if sid not in scenarios or sid in by_id:
                raise ValueError(f"unknown or duplicate outcome scenario: {sid}")
            status = outcome.get("status")
            if status == "failed":
                identifier(outcome.get("error"), "failed outcome.error")
                if any(key in outcome for key in ("total_cost", "shortfall", "hard_violation")):
                    raise ValueError("failed outcomes must not supply fabricated metrics")
                failures.append({"scenario_id": sid, "error": outcome["error"]})
                by_id[sid] = {"status": status}
            elif status == "ok":
                if "error" in outcome:
                    raise ValueError("successful outcome must not contain error")
                cost = num(outcome.get("total_cost"), "outcome.total_cost")
                shortfall = num(outcome.get("shortfall"), "outcome.shortfall")
                if not 0 <= shortfall <= scenarios[sid]["demand"]:
                    raise ValueError("shortfall must be between zero and scenario demand")
                if not isinstance(outcome.get("hard_violation"), bool):
                    raise ValueError("hard_violation must be an explicit boolean")
                by_id[sid] = {"status": status, "total_cost": cost, "shortfall": shortfall,
                              "hard_violation": outcome["hard_violation"]}
            else:
                raise ValueError("outcome status must be ok or failed")
        if set(by_id) != set(scenarios):
            raise ValueError(f"policy {pid} lacks complete shared scenario coverage")
        report = {"id": pid, "status": "incomplete" if failures else "complete",
                  "scenario_count": len(scenarios), "failed_count": len(failures),
                  "failure_probability": finite_sum((scenarios[f["scenario_id"]]["probability"]
                                                     for f in failures), "failure probability"),
                  "failures": failures, "metrics": None,
                  "all_listed_hard_constraints_satisfied": None}
        if not failures:
            ids = list(scenarios)
            probabilities = [scenarios[s]["probability"] for s in ids]
            costs = [by_id[s]["total_cost"] for s in ids]
            shortfalls = [by_id[s]["shortfall"] for s in ids]
            expected_cost = finite_sum((p * c for p, c in zip(probabilities, costs)), "expected cost")
            expected_shortfall = finite_sum((p * s for p, s in zip(probabilities, shortfalls)),
                                            "expected shortfall")
            report["metrics"] = {
                "expected_cost": expected_cost,
                "cvar_cost": weighted_cvar(costs, probabilities, alpha),
                "worst_cost_positive_probability": max(c for c, p in zip(costs, probabilities) if p > 0),
                "expected_shortfall": expected_shortfall,
                "service_shortfall_probability": finite_sum((p for p, s in zip(probabilities, shortfalls)
                                                             if s > tolerance), "shortfall probability"),
                "volume_weighted_fill_rate": 1 - expected_shortfall / expected_demand if expected_demand > 0 else None,
                "hard_violation_probability": finite_sum((scenarios[s]["probability"] for s in ids
                                                          if by_id[s]["hard_violation"]), "violation probability")
            }
            report["all_listed_hard_constraints_satisfied"] = all(not by_id[s]["hard_violation"] for s in ids)
        reports[pid] = report
    comparisons = []
    baseline = data.get("baseline_policy_id")
    if baseline is not None:
        identifier(baseline, "baseline_policy_id")
        if baseline not in reports:
            raise ValueError("baseline_policy_id must identify a supplied policy")
        for pid, report in reports.items():
            if pid != baseline:
                difference = None
                if report["metrics"] is not None and reports[baseline]["metrics"] is not None:
                    difference = num(report["metrics"]["expected_cost"] -
                                     reports[baseline]["metrics"]["expected_cost"], "cost difference")
                comparisons.append({"policy_id": pid, "baseline_policy_id": baseline,
                                    "expected_cost_difference_policy_minus_baseline": difference})
    return {"distribution_kind_as_declared": kind, "distribution_calibration_verified": False,
            "cost_unit": cost_unit, "demand_unit": demand_unit, "alpha": alpha,
            "probability_sum_before_roundoff_normalization": total,
            "expected_demand": expected_demand, "policies": list(reports.values()),
            "comparisons": comparisons,
            "all_evaluations_complete": all(p["status"] == "complete" for p in reports.values()),
            "population_guarantee": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        report = evaluate(json.loads(args.input.read_text(encoding="utf-8")))
        print(json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2))
        return 0 if report["all_evaluations_complete"] else 1
    except (OSError, ValueError, OverflowError, TypeError) as error:
        print(json.dumps({"status": "invalid_input", "error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
