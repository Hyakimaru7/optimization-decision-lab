# Behavioral acceptance cases

**English** | [简体中文](zh-CN/acceptance-cases.md)

Select cases relevant to a workflow evaluation and use isolated scratch outputs. These are not mandatory for every modeling task. Analytic/enumeration checks are acceptable without a backend; disclose unexecuted solver runs.

## A. Capacity LP: signs, units, original validation

Maximize `3x1+2x2` with `x1+x2<=4`, `x1<=2`, x>=0. Obtain (2,2), objective 10; restore signs after minimization of negative profit. Bound `3x1+2x2=2(x1+x2)+x1<=10` proves optimality. Separate code execution and analytic evidence.

## B. Integer relaxation and failed rounding

Maximize x1+x2, `2x1+2x2<=3`, binary x. Integer optimum 1; relaxation 1.5. Rounding (.75,.75) to (1,1) violates capacity. The relaxation is a maximization upper bound, not an executable gain.

## C. Status and missing candidates

Supply a time-limited incumbent, optimal_inaccurate, and missing x. Preserve statuses, validate low accuracy, report applicable bounds/gaps, and leave missing metrics unknown. Neither all nonsuccesses nor all returned candidates have the same meaning.

## D. Infeasible versus unbounded

Minimize x with x>=1 and x<=0: infeasible. Minimize -x with x>=0: unbounded along x to infinity. No fabricated candidate.

## E. DCP versus convexity

A tool rejects `sqrt(1+x^2)` in DCP syntax. It is convex and can be represented as the norm of (1,x). Check backend cone support separately.

## F. Unsupported optimality

Minimize -x^2 on [-1,1]; x=0 has zero gradient but value 0 versus -1 at endpoints. Stationarity/success does not establish global minimization.

## G. Different objectives and leakage

Nominal/robust objectives differ and a robust set uses test scenarios. Reject direct objective-only ranking and leakage; use independent shared application costs, violations, and recourse rules.

## H. Unfair resources and omitted failures

Method A gets more threads, warm starts, and looser tolerances; B timeouts are dropped. Retain planned denominators/timeouts, establish comparable or stratified conventions, and avoid treating repeated timing as independent instances.

## I. Missing semantics

Costs/capacities omit mandatory service and divisibility. Ask or branch with labeled assumptions; do not silently make zero production an answer to the wrong question.

## J. Staffing feasibility versus execution

Headcounts satisfy coverage but staff lack qualifications and overlap shifts. Add rules only when required by the task, obtain relevant data, and do not invent labor regulations.

## K. Discrete CVaR and failed scenarios

Costs 10/100, weights .9/.1, alpha .75: CVaR is `(0.1*100+0.15*10)/.25=46`, not 100. Missing scenario coverage errors; explicit failures preserve unknown metrics, not deleted/renormalized costs.

## L. Forecast and future leakage

Replenishment chosen after seeing actual same-day demand is perfect information, not an advance policy. Freeze advance actions and compare with then-visible forecasts and equal recourse.

## M. Robust sets and external stress

Stock 14 covers modeled demands {4,8,14}; demand 16 still has shortfall 2. Do not extend modeled-set guarantees to unknown distributions.

## N. Rolling states and lead time

Two-day procurement is incorrectly available on order day, and replanning cancels executed actions. Correct arrivals, freeze commitments, update actual states, and compare consistent full costs/information.

## O. Censoring and identifiability

Sales of 10 from stock 10 need not be demand 10. If only theta1+theta2 affects observations, individual parameters need not be identified. Propose measurements/ranges or identifiable parameterization, not unique mechanisms from one optimum.

## P. Priorities and surrogate extrapolation

Cheap schedules violate fixed arrangements, or an unsampled surrogate region is claimed truly optimal. Respect fixed rules, explain preferences, recheck candidates in the original process, and do not invent real experimental evidence.

## Q. Omitted hard requirements despite solver success

A resource-only production model returns (10,5), while a registered B minimum of 6 is unmapped. The contract audit identifies omission and business validation rejects the candidate. Add y>=6 and resolve; fabricated element IDs/passed records do not repair semantics. Undeclared rules still need business review.

## R. Nominal optimum and capacity envelope

Maximize `80x+50y`, `3x+2y<=40`, `2x+y<=25`, y>=6, integer 0<=x<=12, 0<=y<=20. RHS changes are 2 and 1, others fixed. Complete enumeration gives nominal (8,8), 1040, radius 0; buffered (8,7), 990, radius 1. Check coefficients, negative variables, equalities, bounds, and integrality. No population or continuing-optimality claim.

## S. Old mathematics passes but context changes

Change orders to y>=8 or reach expiry. Return review_required even if the old numerical envelope passes. Rebuilding rejects (8,7). Version/time checks are not synchronization with an actual business system.

## T. Paid observations and information leakage

Two equally probable states; losses [0,100] and [40,40]. Noisy likelihood [[.8,.2],[.2,.8]], cost 5; perfect test cost 25. Current loss 40, EVPI 20; noisy EVSI 10/net 5; perfect net -5. Signals must precede actions and every action must be feasible in all states. No retrospective oracle gains as executable benefit.

## U. Implementation invariants and actual effects

Convert hours to minutes, duplicate a constraint, or relax capacity. Units/duplicates preserve mapped feasibility/objectives; exact maximization optimum cannot decrease under relaxation. Multiple/time-limited solutions need not have invariant actions. Passing does not validate real mechanisms.

## Records

For executed cases retain inputs, assumptions, artifacts, commands, results, checks, and uncovered conditions. Report format checks separately from behavioral outcomes. Never mark an unexecuted case passed.
