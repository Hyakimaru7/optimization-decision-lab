#!/usr/bin/env python3
"""Find missing declared requirements, stale evidence and untested validators."""
import sys
from decision_support_common import obj, label, labels, cli


def audit(data):
    """Check declared traceability; do not infer or prove business semantics."""
    obj(data, ("model_revision", "model_elements", "validators", "requirements", "tests"), "input")
    revision = label(data["model_revision"], "model_revision")
    elements = set(labels(data["model_elements"], "model_elements"))
    validators = set(labels(data["validators"], "validators"))
    if not isinstance(data["tests"], list) or not isinstance(data["requirements"], list) or not data["requirements"]:
        raise ValueError("requirements must be nonempty and tests must be an array")
    tests = {}
    for test in data["tests"]:
        obj(test, ("id", "requirement_id", "requirement_revision", "model_revision", "validator_id", "result", "evidence"), "test")
        for key in ("id", "requirement_id", "requirement_revision", "model_revision", "validator_id", "evidence"):
            label(test[key], f"test.{key}")
        if test["result"] not in ("passed", "failed", "not_run"):
            raise ValueError("test.result must be passed, failed or not_run")
        if test["id"] in tests:
            raise ValueError("duplicate test id")
        tests[test["id"]] = test
    records = []
    req_ids = set()
    used_tests = set()
    for req in data["requirements"]:
        obj(req, ("id", "text", "kind", "source", "revision", "model_elements", "validator_ids", "test_ids", "semantic_review"), "requirement")
        for key in ("id", "text", "source", "revision"):
            label(req[key], f"requirement.{key}")
        if req["id"] in req_ids:
            raise ValueError("duplicate requirement id")
        req_ids.add(req["id"])
        if req["kind"] not in ("hard", "soft"):
            raise ValueError("kind must be hard or soft")
        mapped = labels(req["model_elements"], "requirement.model_elements")
        vids = labels(req["validator_ids"], "validator_ids")
        tids = labels(req["test_ids"], "test_ids")
        semantic = obj(req["semantic_review"], ("status", "evidence"), "semantic_review")
        if semantic["status"] not in ("confirmed", "pending"):
            raise ValueError("semantic_review.status must be confirmed or pending")
        label(semantic["evidence"], "semantic_review.evidence")
        issues = []
        if not mapped:
            issues.append("not_mapped_to_model")
        if set(mapped) - elements:
            issues.append("unknown_model_elements")
        if semantic["status"] != "confirmed":
            issues.append("semantics_not_reviewed")
        if req["kind"] == "hard" and not vids:
            issues.append("no_independent_validator")
        if set(vids) - validators:
            issues.append("unknown_validators")
        covered = set()
        for tid in tids:
            used_tests.add(tid)
            test = tests.get(tid)
            if test is None:
                issues.append(f"missing_test:{tid}")
                continue
            if test["requirement_id"] != req["id"] or test["validator_id"] not in vids:
                issues.append(f"test_link_mismatch:{tid}")
                continue
            fresh = test["model_revision"] == revision and test["requirement_revision"] == req["revision"]
            if not fresh:
                issues.append(f"stale_test:{tid}")
            if test["result"] != "passed":
                issues.append(f"test_not_passed:{tid}")
            if fresh and test["result"] == "passed":
                covered.add(test["validator_id"])
        for vid in set(vids) - covered:
            issues.append(f"validator_without_current_passing_test:{vid}")
        records.append({"id": req["id"], "kind": req["kind"], "issues": sorted(set(issues)), "coverage_record_consistent": not issues})
    orphan = sorted(set(tests) - used_tests)
    hard_failed = [r["id"] for r in records if r["kind"] == "hard" and r["issues"]]
    warnings = [r["id"] for r in records if r["kind"] == "soft" and r["issues"]]
    return {"status": "review_required" if hard_failed else "declared_contract_consistent",
            "hard_requirements_with_issues": hard_failed, "soft_requirements_with_issues": warnings,
            "requirements": records, "unlinked_tests": orphan,
            "semantic_truth_verified": False, "evidence_contents_verified": False,
            "scope": "declared records only; not an automated discovery of hidden requirements"}


if __name__ == "__main__":
    sys.exit(cli(audit, lambda r: r["status"] == "declared_contract_consistent"))
