# Requirement contracts and counterexamples

**English** | [简体中文](zh-CN/requirement-contract.md)

Use for easily omitted order rules, reformulation, handoffs, or important decisions. Check whether the real question is represented before celebrating solver success. Simple tasks need only a table and counterexamples.

## Semantics before records

Record source/revision, requirement, hard/soft type, formula, code location, independent business validation, and counterexamples. Compute validators from original entities such as orders/timing/resources, not just regenerated matrices.

“Deliver at least 6 units of B” means `y>=6`; `(10,5)` must be rejected. If model and validator both omit that limit, both may report success. A suggestion to deliver more is not automatically a hard lower bound.

Reasoning cannot turn unknown rules into confirmed facts. Provide conditional plans and gaps when critical requirements are unconfirmed. Manifests cannot discover all undeclared rules; trace actual execution through orders, materials, equipment, time, and roles where needed.

## Executable audit

From the skill directory:

```bash
python3 scripts/audit_requirement_contract.py assets/requirement-contract-example.json
```

All fields are required; unknown fields are rejected:

- `model_revision`: acceptance snapshot revision, preferably a content hash covering model, validation code, and relevant test inputs. Versioning only formulation code misses changed data/validators. String provenance is not verified.
- `model_elements`, `validators`: unique current model-element and independent-validator IDs.
- Nonempty `requirements`: each has `id,text,kind,source,revision,model_elements,validator_ids,test_ids,semantic_review`.
- Kind is `hard/soft`. Semantic review contains `status:"confirmed"/"pending"` and nonempty `evidence`, supplied after actual review, not by this script's semantic judgment.
- `tests`: each has `id,requirement_id,requirement_revision,model_revision,validator_id,result,evidence`; result is `passed/failed/not_run`. Versions match the model and linked requirement.

Hard rules require existing model mappings, recorded semantic confirmation, existing independent validators, and at least one current passing test for each validator. Test business semantics/boundaries, not just absence of exceptions. Soft-rule issues and unlinked tests are separate.

The script reads records without running tests, opening evidence files, or verifying truth. Callers must run tests and retain actual evidence. Never fill in passed to conceal unexecuted work. The supplied manifest is synthetic demonstration metadata and must be replaced.

Exit 0 means declared hard-rule records are consistent (inspect soft warnings); 1 means hard rules need review; 2 means invalid input. Outputs always set `semantic_truth_verified:false` and `evidence_contents_verified:false`.

## Changes and infeasibility

Rerun affected checks after changed requirements/models. An IIS is irreducible, generally not minimum cardinality, and not all independent conflicts. On interrupted computation, also check whether irreducibility was reached. Map conflicts to business sources; inspect data, units, and duplication before repair. See [computeIIS documentation](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html#Model.computeIIS).

Repair criteria such as number of changed rules, amount changed, and operational cost can yield different plans. Monetary penalties cannot replace nonnegotiable rules. Experiment on a copy; loosening tolerance, softening hard rules, or deleting orders is not default repair.
