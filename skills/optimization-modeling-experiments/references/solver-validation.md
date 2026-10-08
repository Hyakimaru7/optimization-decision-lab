# Solver selection and original-model validation

**English** | [简体中文](zh-CN/solver-validation.md)

## Availability and statuses

Check installed backends and model support; in CVXPY use `installed_solvers()`. A modeling package is not every backend. Read version-specific status definitions and preserve raw status, message, precision, and configuration.

| Status/observation | Reportable statement | Check |
| --- | --- | --- |
| optimal / success | Successful termination under solver criteria | Original feasibility, applicable guarantees, tolerances, bounds |
| optimal_inaccurate or similar | Solver-reported low accuracy | Research requirements, residuals, necessary cross-checks |
| Time/iteration limit | Stopped within budget | Candidate and valid bounds; not proven optimal |
| infeasible | Solver-reported infeasibility | Model, scale, accuracy, available certificate |
| unbounded | Solver-reported unboundedness | Omissions, bounds, direction/certificate |
| infeasible_or_unbounded | Ambiguous diagnosis | Follow backend documentation |
| Exception/NaN/missing result | Technical failure or no usable result | Preserve cause; no invented objectives/residuals |

Local NLP success does not imply global optimality. Interpret the backend and original problem together.

## Independent checking

1. Check presence, shape, domain, and finite values. Use null/unknown without a solution, not zero.
2. Recover original variables, objective direction, scales, and constants; recompute the objective.
3. Compute original residuals, including variable bounds and integrality represented as attributes.
4. Compare with the solver claim and preserve violated constraint IDs.
5. Assess applicable optimality evidence and limit the conclusion.

For inequalities g_i(x)<=0 and equalities h_j(x)=0, use `v_i=max(g_i(x),0)` and `e_j=abs(h_j(x))`. For finite bounds use `max(l_k-x_k,x_k-u_k,0)` with absent bounds excluded; integrality deviation is `abs(x_k-round(x_k))`. Rounding here measures deviation; an actually rounded candidate needs full rechecking.

Different-unit residuals are not one physical quantity. Use predefined positive scales s_i and `violation_i <= atol_i + rtol_i*s_i`; explain scales and units. Keep absolute and normalized values. Do not widen tolerances according to observed violations. Use separate integer tolerance.

## Bounds and gaps

After mapping to the original objective, L is a valid lower bound on the optimum and U a valid upper bound. A feasible minimization candidate supplies U, a maximization candidate L; the other side needs valid dual, relaxation, or global-solver evidence.

With finite, justified sides, one reporting convention is `gap_abs=U-L`, `gap_rel=(U-L)/max(1,abs(U),abs(L))`. The reference scale 1 is in reporting objective units; change/document it when changing units/scales. Preserve the solver's separate gap and definition; this convention may differ from backend stopping criteria.

Without a valid side, gap is unknown. Local solutions, best multistart values, and numerical references do not become valid dual bounds automatically. Tolerance-feasible candidates are numerical evidence, not exact certificates. State finite-precision bound provenance.

If U<L, retain raw values and diagnose sign mappings, constants, rounding, precision, or invalid bounds. Label even small conflicts rather than silently clipping them.

## KKT and local measures

For suitable differentiable minimization with Lagrangian `f+sum(lambda_i*g_i)+sum(nu_j*h_j)`, record stationarity, primal feasibility, nonnegative inequality multipliers, and complementarity `abs(lambda_i*g_i)`. Define signs explicitly for maximization.

Check variable-bound multipliers and signs. Missing multipliers mean incomplete KKT evidence. Use subgradient/proximal measures for nonsmooth/composite problems. Explain constraint qualifications and convexity for necessary/sufficient claims; local measures do not certify nonconvex global optima.

## Diagnosis and retries

Use evidence to inspect data/indices, scaling, bounds, redundant/conflicting rules, logs, and available IIS/certificates. Auxiliary slack models can localize violations if scales are explained; they do not replace the original model.

As a starting convention, allow at most two justified numerical retries for the same instance; user budgets/plans may change this. Without new diagnosis, stop that attempt and continue independent work. Model/semantic changes are separate configurations and must not overwrite failures.

## Linear solution checker

`scripts/check_linear_solution.py` uses only Python's standard library. Example:

```json
{
  "objective": {"sense": "max", "coefficients": [3, 2], "constant": 0},
  "inequalities": {"A": [[1, 1], [1, 0]], "b": [4, 2]},
  "equalities": {"A": [], "b": []},
  "bounds": [[0, null], [0, null]],
  "integer_indices": [],
  "solution": [2, 2]
}
```

Rows represent Ax<=b or Ax=b. Negate greater-than rows consistently. Bounds are explicit for every variable; null means absent. Integer indices are zero-based; binary variables need integrality plus [0,1] bounds. `solution:null` returns `no_solution` with unknown objective.

Each group optionally provides positive `scales` matching rows. Defaults are max(1,abs(b_i)); bound scales use finite bounds and are at least 1. These defaults assume sensible numerical units; explicitly supply scales and explain the unit of 1 otherwise.

From the skill directory:

```bash
python3 scripts/check_linear_solution.py candidate.json --atol 1e-6 --rtol 1e-6 --integer-tol 1e-6
```

JSON output contains the original objective, per-row residual/violation, scales, thresholds, pass flags, and integer deviations. Exit 0 means tolerance-feasible, 1 means failed/no solution, 2 means invalid input with a structured message.

Unsupported: nonlinear, semicontinuous/semiinteger, conic, strict inequalities, and implicit logic. Check these separately in the original model. The script reads no solver status and supplies no dual bound/optimality proof. Floating-point/tolerance checks are not exact mathematical feasibility.

## Official sources

- [CVXPY DCP](https://www.cvxpy.org/tutorial/dcp/index.html), [statuses](https://www.cvxpy.org/tutorial/intro/index.html), [solvers](https://www.cvxpy.org/tutorial/solvers/index.html).
- [SciPy linprog](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html), [milp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html), [minimize](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html).
- [OR-Tools CP-SAT](https://developers.google.com/optimization/cp/cp_solver): verify integer encoding and exact rational scaling; arbitrary rounding can change the problem. Feasible differs from optimal. The linear checker cannot verify unexpanded interval/nonoverlap logic.

Use documentation matching the installed backend version.
