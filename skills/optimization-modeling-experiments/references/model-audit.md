# Model audit and reformulation

**English** | [简体中文](zh-CN/model-audit.md)

Read relevant sections when formulating, auditing, or reformulating models.

## Semantics, data, boundaries

Map actual requirements to formulas, code locations, and independent validators. Distinguish decisions from known parameters: future random demand is not a known deterministic input. Scenario decisions must respect information available when made.

Check consistent indices, omitted/duplicate/invalid combinations, units of quantities/times/costs/probabilities, scales of squared/absolute losses, and domains of capacities, demands, probabilities, covariances, and distances. Record missing/outlier treatment without silently changing raw data. Interpret boundary variables, empty sets, zero capacity/demand, initial/terminal states, and extreme parameters.

Declare real/nonnegative/integer/binary domains and bounds. Do not omit free variables because a solver defaults to nonnegative values, or fail to verify implicit variable attributes.

## Feasibility, boundedness, existence

Use easy necessary conditions, feasible constructions, and small instances. Passing a necessary condition is not sufficiency.

A continuous objective on a nonempty compact feasible set attains an optimum. A nonempty closed set and appropriate coercivity on that set can also suffice. State the conditions; a finite lower bound alone does not ensure attainment. Strict convexity gives uniqueness under suitable conditions including a convex feasible set, but existence is still needed.

Distinguish infeasibility from unboundedness. Investigate feasible improving directions where appropriate. Local solver failure does not prove either.

## Convexity and problem classes

Convex minimization requires a convex objective, convex inequality functions, affine equalities, and a convex domain; maximization uses a concave objective. Integer domains are nonconvex even when their continuous relaxation is convex.

Check the symmetric part and positive semidefiniteness of quadratic forms. Explain numerical uncertainty near zero eigenvalues. Convex-function equalities generally are not convex constraints. DCP is a recognition system, not a complete test of all convex expressions.

## Common transformations

| Transformation | Check | Required explanation |
| --- | --- | --- |
| Epigraph variable t>=f(x) | Objective direction/monotonicity in t and other t constraints | Why the bound becomes tight |
| Absolute value/maximum auxiliaries | Whether their upper bound is minimized | Epigraphs cannot freely replace equalities or nonconvex lower bounds |
| Big-M / indicator | Valid bounds and logical directions | Small M can remove feasible points; large M harms relaxation/numerics |
| Binary-continuous products | Valid continuous bounds | Full linearization and recovery |
| McCormick envelope | Bounded rectangular domain | Generally a relaxation, not the product equality |
| Fractional substitutions | Denominator sign/zeros and invertibility | Transformed domain, objective, recovery |
| Integer relaxation | Original and relaxed domains | Rounding requires repair and rechecking |
| Penalties/soft constraints | Original hard rules, penalty, scale | Equivalence is conditional; violations need task authorization |
| Smoothing/discretization | Parameters, approximation, grid | Assess bias and accuracy/grid sensitivity |

For minimization with the same objective, enlarging the feasible set gives a lower bound; restricting it can give an upper bound through a feasible candidate. Reverse directions for maximization. Objective changes require their own mapping; set inclusion alone is insufficient.

## Multiple objectives, stochastic and robust models

Explain weighted objective units, normalization, and preferences. Weighted sums generally miss some Pareto points with nonconvex objective images. Explain epsilon thresholds and feasibility for epsilon-constraint methods.

Scenario probabilities must be nonnegative and normalized; log any modification. Separate expectations, risk, chance constraints, and worst-case goals. Finite-scenario feasibility does not ensure population chance constraints.

Specify robust uncertainty sets, information structure, dualization conditions, and conservatism. Scenario approximations need not be equivalent to guarantees over an entire set.

Separate training, tuning, and evaluation. Do not fit normalization, demand distributions, or uncertainty sets on test data.

Before reducing bilevel models, check inner optimality characterizations, constraint qualifications, strong duality, and solution selection. Local KKT conditions cannot generally replace global inner optimality.

## Audit output

Identify location, affected claim, evidence, and smallest correction. Separate definite errors, missing conditions, and semantics requiring clarification. Preserve traceability between original and corrected models.
