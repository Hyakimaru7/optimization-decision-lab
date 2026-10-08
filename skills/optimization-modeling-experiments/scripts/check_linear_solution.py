#!/usr/bin/env python3
"""Independently check an LP/MILP candidate. This does not solve the model."""

import argparse
import json
import math
import sys
from pathlib import Path


def number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    try:
        result = float(value)
    except (ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    return result


def vector(values, size, name):
    if not isinstance(values, list) or len(values) != size:
        raise ValueError(f"{name} must contain {size} entries")
    return [number(v, f"{name}[{i}]") for i, v in enumerate(values)]


def reject_unknown(data, allowed, name):
    unknown = set(data) - set(allowed)
    if unknown:
        raise ValueError(f"{name} has unsupported fields: {sorted(unknown)}")


def group(data, n, name):
    if not isinstance(data, dict):
        raise ValueError(f"{name} must be an object")
    reject_unknown(data, ("A", "b", "scales"), name)
    rows = data.get("A")
    if not isinstance(rows, list):
        raise ValueError(f"{name}.A must be an array")
    matrix = [vector(row, n, f"{name}.A[{i}]") for i, row in enumerate(rows)]
    rhs = vector(data.get("b"), len(rows), f"{name}.b")
    scales = vector(data.get("scales", [max(1.0, abs(b)) for b in rhs]),
                    len(rows), f"{name}.scales")
    if any(s <= 0 for s in scales):
        raise ValueError(f"{name}.scales must be positive")
    return matrix, rhs, scales


def dot(a, b):
    value = math.fsum(ai * bi for ai, bi in zip(a, b))
    if not math.isfinite(value):
        raise ValueError("nonfinite dot product; rescale the model")
    return value


def check_candidate(data, atol=1e-6, rtol=1e-6, integer_tol=1e-6):
    atol = number(atol, "atol")
    rtol = number(rtol, "rtol")
    integer_tol = number(integer_tol, "integer_tol")
    if min(atol, rtol, integer_tol) < 0:
        raise ValueError("tolerances must be nonnegative")
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    reject_unknown(data, ("objective", "inequalities", "equalities", "bounds",
                          "integer_indices", "solution"), "input")
    objective = data.get("objective")
    if not isinstance(objective, dict) or objective.get("sense") not in ("min", "max"):
        raise ValueError("objective must declare sense min or max")
    reject_unknown(objective, ("sense", "coefficients", "constant"), "objective")
    raw_c = objective.get("coefficients")
    if not isinstance(raw_c, list) or not raw_c:
        raise ValueError("objective.coefficients must be a nonempty array")
    n = len(raw_c)
    c = vector(raw_c, n, "objective.coefficients")
    constant = number(objective.get("constant", 0), "objective.constant")
    groups = {name: group(data.get(name, {"A": [], "b": []}), n, name)
              for name in ("inequalities", "equalities")}
    raw_bounds = data.get("bounds")
    if not isinstance(raw_bounds, list) or len(raw_bounds) != n:
        raise ValueError("bounds must explicitly contain one pair per variable")
    bounds = []
    for i, pair in enumerate(raw_bounds):
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError(f"bounds[{i}] must be [lower, upper]")
        lo, hi = [None if v is None else number(v, f"bounds[{i}]") for v in pair]
        if lo is not None and hi is not None and lo > hi:
            raise ValueError(f"bounds[{i}] has lower greater than upper")
        bounds.append((lo, hi))
    indices = data.get("integer_indices", [])
    if not isinstance(indices, list) or any(
        isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < n for i in indices
    ):
        raise ValueError("integer_indices must be valid zero-based integer indices")
    if len(indices) != len(set(indices)):
        raise ValueError("integer_indices must be unique")
    if "solution" not in data:
        raise ValueError("solution must be supplied; use null when unavailable")
    if data["solution"] is None:
        return {"status": "no_solution", "objective_original": None,
                "has_solution": False, "constraints": None,
                "bounds": None, "integers": None, "all_passed": None,
                "optimality_certified": False}
    x = vector(data["solution"], n, "solution")
    records = []
    for kind, (matrix, rhs, scales) in groups.items():
        for i, (row, b, scale) in enumerate(zip(matrix, rhs, scales)):
            residual = dot(row, x) - b
            if not math.isfinite(residual):
                raise ValueError("nonfinite constraint residual; rescale the model")
            violation = max(residual, 0.0) if kind == "inequalities" else abs(residual)
            threshold = atol + rtol * scale
            if not math.isfinite(threshold):
                raise ValueError("nonfinite tolerance threshold")
            normalized = violation / scale
            if not math.isfinite(normalized):
                raise ValueError("nonfinite normalized violation; use meaningful scales")
            records.append({"id": f"{kind}[{i}]", "signed_residual": residual,
                            "violation": violation, "scale": scale,
                            "normalized_violation": normalized,
                            "threshold": threshold, "passed": violation <= threshold})
    bound_records = []
    for i, (lo, hi) in enumerate(bounds):
        scale = max([1.0] + [abs(v) for v in (lo, hi) if v is not None])
        violation = max([0.0] + ([lo - x[i]] if lo is not None else [])
                        + ([x[i] - hi] if hi is not None else []))
        threshold = atol + rtol * scale
        if not math.isfinite(violation) or not math.isfinite(threshold):
            raise ValueError("nonfinite bound residual or threshold; rescale the model")
        bound_records.append({"id": f"bounds[{i}]", "violation": violation,
                              "scale": scale, "threshold": threshold,
                              "normalized_violation": violation / scale,
                              "passed": violation <= threshold})
    integer_records = [{"id": f"integer[{i}]", "violation": abs(x[i] - round(x[i])),
                        "threshold": integer_tol,
                        "passed": abs(x[i] - round(x[i])) <= integer_tol} for i in indices]
    value = dot(c, x) + constant
    if not math.isfinite(value):
        raise ValueError("nonfinite objective; rescale the model")
    passed = all(r["passed"] for r in records + bound_records + integer_records)
    return {"status": "candidate_feasible" if passed else "candidate_infeasible",
            "has_solution": True, "objective_sense": objective["sense"],
            "objective_original": value, "constraints": records,
            "bounds": bound_records, "integers": integer_records,
            "all_passed": passed, "optimality_certified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--atol", type=float, default=1e-6)
    parser.add_argument("--rtol", type=float, default=1e-6)
    parser.add_argument("--integer-tol", type=float, default=1e-6)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = check_candidate(data, args.atol, args.rtol, args.integer_tol)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
        return 0 if result.get("all_passed") is True else 1
    except (OSError, ValueError, OverflowError, TypeError) as error:
        print(json.dumps({"status": "invalid_input", "error": str(error)},
                         ensure_ascii=False, allow_nan=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
