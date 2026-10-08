# Validity envelope for a fixed plan

**English** | [简体中文](zh-CN/plan-validity.md)

Use before execution, after input changes, during handoffs, or when comparing buffers. This assesses whether original actions still satisfy declared constraints, distinct from reoptimization or LP optimal-basis sensitivity.

## Supported calculation

From the skill directory:

```bash
python3 scripts/assess_plan_validity.py assets/plan-validity-example.json
```

The script checks fixed LP/MILP candidates: linear inequalities/equalities, bounds, and original integrality. Parameter changes do not alter integrality. Unsupported: changed variable domains, nonlinear/logic rules, correlated sets, and observation-dependent recourse. Use appropriate original-business checks/methods/simulation for other structures.

For `a_i*x<=b_i`, coefficient absolute changes d_ij and RHS changes e_i define an independent simultaneous box:

`worst_residual_i(rho)=a_i*x-b_i+rho*(sum_j(abs(x_j)*d_ij)+e_i)`.

This is the box worst residual for fixed x. Equalities use `abs(a_i*x-b_i)+rho*growth`; lower bounds increase adversely and upper bounds decrease. Row radii are `(threshold-nominal_residual)/growth`, with the global minimum. This envelope may conservatively cover correlated real changes; it is not a probability interval.

No radius is returned for a nominally invalid candidate. A passing zero-growth row imposes no limit within the declared box. With all growth zero, `max_radius:null` and `unbounded_in_declared_box:true` do not mean indefinite real-world validity. Equalities are often fragile to independent changes; replacing them with inequalities cannot conceal that.

Checks are floating point with explicit tolerances, not exact rational or interval proofs. Scales remain fixed at nominal values; perturbations do not silently widen tolerance. Zero tolerance can express physical hard limits but cannot remove floating-point arithmetic error. Use exact/reliable interval tools when strict certification is required.

## Input contract

All top-level fields are required and unknown fields rejected:

- `model`: [linear checker input](solver-validation.md#linear-solution-checker), including a real `solution`.
- `uncertainty.inequalities` and `.equalities`: each has `coefficient_absolute` matrix and `rhs_absolute` array matching model rows/dimensions. Write empty arrays for zero rows. Values are nonnegative.
- `uncertainty.bounds`: per-variable `[lower_absolute,upper_absolute]`; absent bounds require zero changes.
- `target_radius`: nonnegative multiplier; 1 is the full declared set. Changes need data/engineering ranges or labeled assumptions; nothing is fitted automatically.
- `tolerances`: nonnegative `atol,rtol,integer_tol`. Use model row `scales` for differing units, with justification.
- `artifact`: `model_revision,data_revision,context_revision,generated_at,expires_at`.
- `current`: the same revisions plus `as_of`. ISO 8601 timestamps have timezones; expiry exceeds generation. Business sets the validity period, not a universal hour count.

Zero change means held fixed, not unknown error. Objectives, domain/rule changes, and omitted mechanisms are outside the box guarantee. Context revisions should cover relevant orders, qualifications, locations, and commitments. Callers generate authentic hashes/snapshots.

Any revision mismatch, expiry, future generation, nominal invalidity, or envelope exceedance returns `review_required`. Even a passing numerical envelope requires review after changed revisions: reconstruct current rules/commitments and issue a new record. This does not prove the new model infeasible. The tool compares supplied strings/times only; it does not access operations, verify hash provenance, reoptimize, or execute.

Exit 0 means consistent current snapshot and declared envelope; 1 review required; 2 invalid input. Preserve rows and reasons. Optimality is always uncertified; exit 0 is not business execution authorization.

## Whether to replan

Restore hard feasibility before cost tradeoffs. With a still-feasible plan, compare replacement benefit, cancellation/switching, and computation. Valid bounds can sometimes stop unnecessary solving.

For maximization, let current feasible value be L and a current valid upper bound U. If every acceptable replacement costs at least K to switch and `U-L<=K`, no replacement has strictly positive net gain under these assumptions. Bounds must belong to current models/data and the same benefit convention. Typical costs are not valid lower bounds. For minimization use current cost minus a valid lower bound. Neither proves the current plan optimal automatically.
