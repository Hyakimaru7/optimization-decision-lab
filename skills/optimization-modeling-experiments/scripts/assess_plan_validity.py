#!/usr/bin/env python3
"""Check fixed linear plans under explicit box perturbations and snapshot expiry."""
from datetime import datetime
import math
import sys
from check_linear_solution import check_candidate, group, vector, number
from decision_support_common import obj, label, nonnegative, total, cli


def timestamp(value, name):
    label(value, name)
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{name} must be ISO 8601") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(f"{name} must include a timezone")
    return result


def assess(data):
    """Assess a supplied fixed plan, not its optimality or unmodeled mechanisms."""
    obj(data, ("model", "uncertainty", "target_radius", "tolerances", "artifact", "current"), "input")
    t = obj(data["tolerances"], ("atol", "rtol", "integer_tol"), "tolerances")
    nominal = check_candidate(data["model"], **t)
    if not nominal["has_solution"]:
        raise ValueError("a fixed solution is required")
    model = data["model"]
    x = vector(model["solution"], len(model["objective"]["coefficients"]), "solution")
    n = len(x)
    rho = nonnegative(data["target_radius"], "target_radius")
    u = obj(data["uncertainty"], ("inequalities", "equalities", "bounds"), "uncertainty")
    records = []

    def record(identifier, residual, growth, threshold):
        if not all(math.isfinite(v) for v in (residual, growth, threshold)):
            raise ValueError("nonfinite arithmetic; rescale inputs")
        margin = threshold - residual
        limit = margin / growth if margin >= 0 and growth > 0 else None
        if limit is not None and not math.isfinite(limit):
            raise ValueError("nonfinite radius; rescale uncertainty")
        worst = total((residual, rho * growth))
        records.append({"id": identifier, "nominal_residual": residual,
                        "adverse_growth_per_radius": growth, "threshold": threshold,
                        "worst_residual_at_target": worst, "passed_at_target": worst <= threshold,
                        "max_radius": limit, "unbounded_in_declared_box": margin >= 0 and growth == 0})

    nominal_rows = {r["id"]: r for r in nominal["constraints"]}
    for kind in ("inequalities", "equalities"):
        matrix, rhs, scales = group(model.get(kind, {"A": [], "b": []}), n, kind)
        ug = obj(u[kind], ("coefficient_absolute", "rhs_absolute"), f"uncertainty.{kind}")
        raw = ug["coefficient_absolute"]
        if not isinstance(raw, list) or len(raw) != len(matrix):
            raise ValueError(f"uncertainty.{kind} coefficient row count mismatch")
        delta = [vector(row, n, "coefficient_absolute") for row in raw]
        db = vector(ug["rhs_absolute"], len(matrix), "rhs_absolute")
        if any(v < 0 for row in delta for v in row) or any(v < 0 for v in db):
            raise ValueError("uncertainty must be nonnegative")
        for i, (row, bdelta) in enumerate(zip(delta, db)):
            identifier = f"{kind}[{i}]"
            nr = nominal_rows[identifier]
            r = nr["signed_residual"]
            record(identifier, abs(r) if kind == "equalities" else r,
                   total([abs(v) * d for v, d in zip(x, row)] + [bdelta]), nr["threshold"])
    ub = u["bounds"]
    if not isinstance(ub, list) or len(ub) != n:
        raise ValueError("uncertainty.bounds must have one pair per variable")
    for i, (pair, delta) in enumerate(zip(model["bounds"], ub)):
        ds = vector(delta, 2, "uncertainty.bounds")
        if any(d < 0 for d in ds):
            raise ValueError("bound uncertainty must be nonnegative")
        for side, value, d in zip(("lower", "upper"), pair, ds):
            if value is None:
                if d != 0:
                    raise ValueError("absent bounds must have zero uncertainty")
                continue
            value = number(value, "bound")
            residual = value - x[i] if side == "lower" else x[i] - value
            record(f"bounds[{i}].{side}", residual, d, nominal["bounds"][i]["threshold"])

    a = obj(data["artifact"], ("model_revision", "data_revision", "context_revision", "generated_at", "expires_at"), "artifact")
    c = obj(data["current"], ("model_revision", "data_revision", "context_revision", "as_of"), "current")
    reasons = []
    for key in ("model_revision", "data_revision", "context_revision"):
        if label(a[key], key) != label(c[key], key):
            reasons.append(f"{key}_changed")
    generated = timestamp(a["generated_at"], "generated_at")
    expiry = timestamp(a["expires_at"], "expires_at")
    as_of = timestamp(c["as_of"], "as_of")
    if expiry <= generated:
        raise ValueError("expires_at must be later than generated_at")
    if as_of < generated:
        reasons.append("generated_in_future")
    if as_of >= expiry:
        reasons.append("expired")
    feasible = nominal["all_passed"] and all(r["passed_at_target"] for r in records)
    limits = [r for r in records if r["max_radius"] is not None]
    radius = min(r["max_radius"] for r in limits) if nominal["all_passed"] and limits else None
    if not nominal["all_passed"]:
        reasons.append("nominal_candidate_infeasible")
    elif not feasible:
        reasons.append("target_outside_validity_envelope")
    return {"status": "review_required" if reasons else "within_declared_envelope",
            "nominal_feasible": nominal["all_passed"], "feasible_at_target": feasible,
            "target_radius": rho, "max_radius": radius,
            "unbounded_in_declared_box": nominal["all_passed"] and not limits,
            "limiting_rows": [r["id"] for r in limits if r["max_radius"] == radius],
            "review_reasons": reasons, "rows": records,
            "objective_original": nominal["objective_original"], "optimality_certified": False,
            "scope": "fixed candidate; independent simultaneous box changes; stated numerical tolerances; no execution authorization"}


if __name__ == "__main__":
    sys.exit(cli(assess, lambda r: r["status"] == "within_declared_envelope"))
