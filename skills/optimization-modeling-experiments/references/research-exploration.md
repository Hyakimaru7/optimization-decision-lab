# Optimization modeling for research exploration

**English** | [简体中文](zh-CN/research-exploration.md)

Use for research questions, discrepancy, identification, simulation optimization, experimental conditions, and expensive black boxes. Select relevant branches; do not force every experiment into a paper project.

## Falsifiable hypotheses

Link phenomenon/bottleneck, nearest baseline, changed assumption/mechanism, observable main metric, minimal distinguishing experiment, and supporting/refuting outcomes. Complexity, added modules, or improvement over a weak baseline do not automatically establish a contribution.

Separate modeling, algorithmic, experimental, and application contributions and their evidence. Search original papers and author code, recording date, keywords, scope, and nearest work. Failure to find a match is not proof of novelty.

Negative findings and conditional boundaries can answer the question. Record changes to definitions, tuning, and assumptions; do not relabel exploratory additions as predefined validation. Adapt the [hypothesis record](../assets/research-hypothesis-template.md).

## Mechanisms and data

Separate domain/physical mechanisms from empirical proxies. Estimated objectives/constraints contain error; optimization may exploit inaccurate proxy regions. Examine domain of validity and sample support.

Good loss fits do not establish identifiability. Check parameter combinations with identical outputs, bounds/regularization, and identifying data. Report within identifiable scope; one optimum does not confirm a mechanism.

Use independent fitting/calibration validation and define correlation, batches, noise, and repeated-measure levels. Optimized parameters answer the fitted-loss problem, not causality.

## Simulation and expensive black boxes

Record call costs, noise, domains, failure meanings, and total budget. Assess derivatives, surrogate models, Bayesian optimization, experimental design, or derivative-free methods by context; none is universally best.

Cache executed calls with full input/code revisions. Failure is not an excellent objective. Define seed/repetition levels for stochastic simulation. Compare methods under equal calls/time, tuning, and initial designs.

Surrogates select evaluations within defined applicability. Check final candidates in the original simulator/observations; surrogate feasibility is not real feasibility. Respect inviolable experimental constraints during sampling rather than relying on penalties.

## Choosing the next experiment

Distinguish better operating conditions, parameter identification, competing hypotheses, and prediction accuracy; their optimization goals differ.

Consider measurement resolution, batches, repeats, instrument availability, resources, and allowable conditions. Information matrices, expected information gain, and surrogate uncertainty are candidate criteria, with explicit noise, priors/current estimates, and identifiability conditions. Maximizing information alone does not establish discovery.

Provide candidates, hypotheses distinguished, required resources, and branches after outcomes. Real experiments require reviewable plans/evidence and actual user authorization for execution.

## Evidence and conclusions

When relevant compare simpler models, established methods, the proposal, ablations, discrepancy, and out-of-sample performance under the same application/full-cost definitions.

Label proof, numerical evidence, proxy simulation, actual observation, and conjecture separately. Experimental gains do not imply universal theory. Report failure conditions, not only best instances.

When data cannot distinguish explanations, identify missing observations, identification, or scale; greater complexity is not certainty. Prioritize the next work reducing critical scientific/decision uncertainty.
