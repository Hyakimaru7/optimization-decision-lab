# Contributing

**English** | [简体中文](CONTRIBUTING.zh-CN.md)

Describe the modeling/decision failure a change addresses, affected assumptions, and observable expected behavior. Supply minimal reproducible inputs and actual outputs for numerical bugs. Synthetic inputs are welcome and should be labeled.

Keep [English](skills/optimization-modeling-experiments/SKILL.md) and [Chinese](skills/optimization-modeling-experiments/SKILL.zh-CN.md) instructions consistent. Update matching references and README pages when capabilities, schemas, limitations, or commands change. Keep numerical script logic shared between languages.

Use the smallest sufficient change. Preserve failed-run evidence, original objectives, hard requirements, and honest guarantee boundaries. Do not introduce mandatory solver dependencies into standard-library utilities.

Before a pull request, run from the repository root:

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 examples/run_demo.py
```

Explain changes, executed checks, results, and remaining limits. New numerical logic needs meaningful boundary/invariant tests. Do not add organizational rules from one example or claim real production gains from synthetic data. Submit contributions under the repository's [MIT license](LICENSE).
