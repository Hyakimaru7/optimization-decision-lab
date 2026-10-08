# Operational validation and rolling planning

**English** | [简体中文](zh-CN/operational-validation.md)

Use for execution, dynamic states, replay, simulation, and continuing replanning. A single mathematical solve does not require every step.

## Three levels of evidence

1. Mathematical: original objectives, constraints, domains, and applicable optimality evidence.
2. Process: actual timing, shared resources, physical states, recourse, and failures.
3. Decision: user goals, execution costs, stability, preferences, and actual outcomes.

Report these separately. Integer orders do not ensure feasible machine schedules; static energy balance does not ensure instantaneous power/SOC feasibility. Identify omitted critical mechanisms and minimal additional checks.

## States and time

Define time steps, timestamps/timezones, initial/terminal states, and start/end conventions. For example `I_(t+1)=I_t+arrivals_t+completed_t-actual_shipments_t`.

Lead times apply to arrivals/completion; procurement is not immediately usable. Shared equipment, people, and places must not conflict over relevant periods. Map event simulation to optimization periods; discretization may hide brief conflicts.

Explain terminal inventory/state/value assumptions. A truncated horizon can encourage depletion or hoarding; test sensitivity to horizon and terminal treatment.

## From variables to actions

Export entity IDs, actions, quantities, start/end, prerequisites, and states. Revalidate the recovered plan after rounding times/batches, sorting, or manual edits.

Separate executed, committed, and adjustable actions; respect frozen commitments. For unstable plans consider change counts/magnitudes, cancellation fees, and stability objectives, explaining tradeoffs.

Compare the current policy, candidate, incremental benefit, switching cost, and invalidation conditions. Revalidate fallback plans in the state where used; the old plan may also be infeasible.

Computing, replaying, or generating a plan does not itself authorize orders, equipment control, or operational writes. Deliver a reviewable table and follow actual user authorization for external actions.

## Replay and simulation

Fix visible information, initial state, shared events, and rules. Check simulator conservation, boundaries, and hand-computed steps before evaluation. With real data, validate simulator error and applicability. Reusing the same simplification in optimizer and simulator can conceal failures; check critical rules independently.

Evaluate full costs: decisions, inventory/waiting, delays/shortage, recovery, switching, and terminal states. Do not use realized future demand to plan and compare it to forecast-only baselines.

Replay supports identifiable historical mechanisms. If policies affect demand/behavior, static replay is insufficient for causal gains. Distinguish simulation, historical, and field-pilot evidence.

## Rolling planning

When needed: obtain actual state and then-visible forecast; freeze commitments; solve a window; validate; propose/submit its currently executable part; observe and update.

Submission may mean simulator actions or reviewable proposals, not automatic real operations. Specify task-specific periods/events such as forecast shifts, breakdowns, violation risk, and changed commitments. Avoid universal trigger thresholds.

Assess step budgets, no-solution/timeout behavior, freshness, switching frequency, and cumulative service costs. A time-limited feasible candidate is only useful within actual execution rules; never adopt a hard-infeasible one automatically.

## Explanation

Where applicable report binding rules, marginal changes, and alternatives. Use secondary objectives to select less disruptive or easier actions among tied/near-tied optima; state allowed primary-objective degradation.

Guarantees attach to models, snapshots, uncertainty sets, and time spans. Recheck in new states rather than reusing old optimality claims.

## Execution feedback for model correction

Align decision-time information, suggested/actual actions, human edits, and outcomes. Separate input forecast errors, mechanism discrepancy, execution deviation, and external events: reduced capacity and omitted processing time require different fixes.

Do not classify every human edit as inefficiency. Inspect unrecorded qualifications, maintenance, commitments, or preferences; do not turn a single edit into a universal rule. Restore hard feasibility first, while treating ordinary preferences as possible secondary objectives.

Choose one decision-relevant discrepancy, propose a falsifiable correction and minimal test, retain the old model, and compare full costs/service/violations under equal information and execution rules. Fit parameters appropriately and validate on independent frozen periods. Process changes and selection bias can prevent causal identification through replay.

Authorized field pilots need execution scope, comparison, and stopping criteria. Separate suggested from realized gains using actual actions and predefined metrics. Unexecuted suggestions have no realized benefit evidence. If real operations/permissions are missing, deliver verified proposals and precise gaps without inventing field data.
