# Optimization experiment protocol

**English** | [简体中文](zh-CN/experiment-protocol.md)

## Question and budget

Tie each experiment to a question: costs under equal service, relaxation error by size, robust out-of-sample violations, or solver sensitivity to sparsity.

Record main metrics, baselines, factors, instances, independent units, tuning, stopping rules, precision, and resource budgets beforehand. Label additions made after seeing results as exploratory.

A starting configuration can use one checkable instance, one smoke solve, a 60-second limit, and a fixed data seed. This validates the pipeline, not stable performance superiority. Without a batch budget, measure this start and estimate expansion; with an agreed budget, complete the planned experiment. A tolerance of 1e-6 is a starting suggestion only; adapt to units, scale, requirements, and backend capabilities, recording parameter mappings.

## Data and instances

For real data record provenance, access/license conditions, version, read time, hashes, missingness, and filters. For synthetic data record distributions, parameters, generator revision, and seed; synthetic performance is not real-world performance.

Share instances across methods. Separate training/tuning/evaluation of scenarios, forecasts, and uncertainty sets. Prevent future leakage in time series.

Separate randomness of instance generation, algorithms, and runtime timing. Record seeds/repetition levels. Seeds alone do not ensure bitwise reproducibility: backends, versions, threads, and hardware matter.

## Comparison conventions

- Solver comparisons use the same original model and comparable quality goals; nominal tolerances need not imply equal residuals.
- Model comparisons preserve their separate objectives and shared application metrics, domains, scales, and service requirements.
- Relaxation/integer comparisons explain bound direction, recovery, and original integrality; relaxation values are not better executable plans automatically.
- Use comparable tuning budgets; tune on separate data and disclose defaults versus tuned results.
- State threads, time limits, warm starts, preprocessing, compilation, and model-build timing. Report cold and warm starts separately.
- Separate build/transform, solve, verify, and end-to-end times; backend solve_time is not total time.
- When relevant define memory measurement, iterations, nodes, oracle, and communication counts; unlike counts cannot be pooled.

## Minimal validation

Use a small analytic/enumerable/trusted-cross-check instance and relevant failure/boundary cases. Passing is not universal correctness, but should cover semantics that change the conclusion.

Check smooth derivatives with finite differences/directional derivatives; ordinary gradient errors are unsuitable at nonsmooth points. Balance truncation and roundoff. Two agreeing solvers are not exact proof. Select relevant infeasible, unbounded, zero-capacity, rounding, open-gap, and missing-solution cases.

## Experiment types

| Type | Purpose | Conditions |
| --- | --- | --- |
| Main comparison | Test the hypothesis | Shared instances, predefined quality |
| Ablation | Identify a mechanism | Hold other factors; explain domain changes |
| Sensitivity | Parameter stability | Justified ranges; single factors miss interactions |
| Scaling | Runtime/memory growth | Record sparsity, structure, and timeouts |
| Out-of-sample | Generalization/robustness | Independent scenarios and identical execution/recourse |

Distinguish objective stability from decision stability under jumps or multiple optima. Different optimal vectors need not indicate a bug.

## Raw records

Prefer JSONL, one uniquely identified run/attempt per line, linked to its planned unit. Useful fields:

| Fields | Meaning |
| --- | --- |
| experiment_id, run_id, attempt, instance_id | Experiment and attempt identity |
| model_id, method, solver, solver_version | Formulation/backend identity |
| data_hash, code_revision, config_path | Traceability |
| instance_seed, algorithm_seed, repeat | Randomness levels; null if inapplicable |
| n_variables, n_constraints, n_nonzeros | Defined problem sizes |
| status_raw, termination_reason, has_solution | Original termination information |
| objective_original, objective_solver | Objective mapping |
| lower_bound_original, upper_bound_original, bound_source | Bounds/evidence; null if unknown |
| gap_abs, gap_rel, solver_gap | Separate reporting/backend gaps |
| feasibility_by_class, integer_violation | Residuals, units, scales, thresholds |
| optimality_measure, validation_outcome | Evidence and independent checks |
| build_seconds, solve_wall_seconds, verify_seconds, total_seconds | Defined timing boundaries |
| solution_path, log_path, error | Artifacts and failure cause |

Generate useful fields but retain identity, status, solution presence, validation, and timing conventions. JSON contains no NaN/Infinity; use null and preserve error causes.

Maintain planned-unit denominators, not success-only counts. Keep every retry and predefine aggregation; do not silently pick the fastest/best attempt.

## Summaries and figures

Count quality-passing, feasible-only, low-accuracy, limited, normal infeasible/unbounded, technical failure, and unexecuted units. Report valid metric counts.

Use paired comparisons on random instances; define resampling units/independence for intervals. Repeated deterministic timing does not increase independent instance count. Use statistics only when relevant and justified; explain multiple comparisons.

Time limits censor convergence times. Report unfinished counts or predefined penalties with formulas, not success-only speed claims. Label units, scales, uncertainty, valid counts, and limits. Log axes must not silently drop zero/negative values; short plot segments do not prove convergence rates.

## Reproduction

Record OS, CPU/GPU, memory, threads, language, dependencies, and actual solver versions. Preserve recoverable code via commits/diffs or file hashes.

Provide runnable data preparation, single-instance, batch, validation, and summary entry points (possibly one parameterized script). Do not overwrite raw data. Resume by run identity and report state/configuration conflicts.

Adapt the [report](../assets/research-report-template.md). Downgrade unsupported claims; planned work is not an executed result.
