# Worked examples

**English** | [简体中文](EXAMPLES.zh-CN.md) · [README](../README.md)

Run `python3 examples/run_demo.py` from the repository root. It writes actual JSON outputs to `results/demo/`; `--output results/another-run` selects a separate directory. The demo uses complete enumeration and the bundled tools, with no external solver.

## 1. An omitted delivery rule

Produce integer quantities x,y of products A,B:

\[
\max\ 80x+50y,\quad 3x+2y\le40,\quad 2x+y\le25,\quad
0\le x\le12,\quad0\le y\le20.
\]

The business order also requires `y>=6`. A resource-only model returns `(10,5)` and profit 1050 but violates this order. The requirement manifest can flag a declared rule with no model mapping, while the independent order validator rejects y=5. After adding `[0,-1]*[x,y]<=-6`, the nominal optimum is `(8,8)`, profit 1040.

For each model all 13*21=273 candidates are considered, with an independent calculation from resource/quantity rules compared to matrix checks. Complete enumeration supplies optimality evidence only for this small bounded domain. A consistent manifest alone does not prove that code implements business semantics.

## 2. A buffered fixed plan

Declare machine-capacity change up to 2 hours and material-capacity change up to 1 unit, holding coefficients, orders, and variable bounds fixed. Requiring feasibility at the simultaneous adverse corner gives capacities 38 and 24. Its optimum is `(8,7)`, profit 990, consuming machine 38 and material 23.

For machine capacity, nominal slack is 2 and adverse growth per radius is 2, so the maximum radius is 1. Material slack is 2 and growth 1, giving radius 2; global radius is 1. The original optimum `(8,8)` consumes all 40 machine hours, so its machine radius is zero.

The profit sacrifice is 50, about 4.81% of corrected nominal profit. This buys feasibility within the declared set, not guaranteed higher realized profits. The plan may be conservative when changes are correlated; no unknown-distribution probability guarantee is implied.

If the order changes to y>=8, the old matrix still passes for `(8,7)`. A changed context revision returns review_required; reconstructing the new rule then rejects the candidate. Time/revision input is caller-supplied, not automatic synchronization or monitoring.

## 3. Is a noisy preproduction test worth paying for?

This is a separate synthetic process-choice problem. Both actions are feasible in both states. Losses use yuan:

| Action | Normal material (p=.5) | Difficult material (p=.5) | Expected loss |
| --- | ---: | ---: | ---: |
| Standard process | 0 | 100 | 50 |
| Careful process | 40 | 40 | 40 |

Without measurement, select careful processing with loss 40. Perfect information selects standard for normal material and careful for difficult material, loss 20: EVPI=20.

A test before action has likelihood matrix `[[.8,.2],[.2,.8]]`: state rows and normal/difficult signal columns. Either signal has probability .5. For the normal signal, posterior expected standard loss is 20, so choose standard. For the difficult signal, choose careful with loss 40. Overall loss is .5*20+.5*40=30: EVSI=10.

The noisy test costs 5, giving net value 5. A perfect test costing 25 gives net value -5. The evaluator chooses the noisy test under this supplied finite risk-neutral table. Probabilities and measurement accuracy are hypothetical, not calibrated measurements or guaranteed payback.

## Output files

| File inside the selected output directory | Contents |
| --- | --- |
| production-comparison.json | Enumerated optima, counts, buffer cost, redundant-row/unit-change checks |
| order-test-evidence.json | Actual bad-case and boundary order-validator executions |
| contract-input.json / contract-reports.json | Declared mappings and missing/corrected audit results |
| plan-input.json / plan-reports.json | Nominal/buffered envelopes, context change, rebuilt-order rejection |
| information-input.json / information-report.json | Hypothetical loss/observation table and calculated values |

Modify inputs for your own problem while retaining actual units, rules, decision timing, snapshots, and evidence. Larger models require an appropriate solver; extending brute-force enumeration is not a scaling strategy. Tests check code and synthetic invariants, not independent agent behavior or real industrial outcomes.
