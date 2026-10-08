import copy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1] / "skills/optimization-modeling-experiments"
SCRIPT = ROOT / "scripts/evaluate_scenarios.py"
spec = importlib.util.spec_from_file_location("scenario_evaluator", SCRIPT)
evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)


def data():
    return {"distribution_kind": "hypothetical", "cost_unit": "yuan", "demand_unit": "units",
            "alpha": 0.75,
            "scenarios": [{"id": "a", "probability": 0.9, "demand": 10},
                          {"id": "b", "probability": 0.1, "demand": 20}],
            "policies": [{"id": "p", "outcomes": [
                {"scenario_id": "a", "status": "ok", "total_cost": 10,
                 "shortfall": 0, "hard_violation": False},
                {"scenario_id": "b", "status": "ok", "total_cost": 100,
                 "shortfall": 10, "hard_violation": False}]}]}


class ScenarioChecks(unittest.TestCase):
    def test_discrete_fractional_tail(self):
        self.assertAlmostEqual(evaluator.weighted_cvar([10, 100], [0.9, 0.1], .75), 46)

    def test_alpha_zero_mean_high_alpha_and_negative_costs(self):
        self.assertAlmostEqual(evaluator.weighted_cvar([10, 100], [.9, .1], 0), 19)
        self.assertAlmostEqual(evaluator.weighted_cvar([10, 100], [.9, .1], 1-1e-16), 100)
        self.assertAlmostEqual(evaluator.weighted_cvar([-10, -1], [.9, .1], .9), -1)

    def test_translation_and_tail_monotonicity(self):
        for alpha in (0, .25, .75, .9, .99):
            a = evaluator.weighted_cvar([2, 10, 50], [.4, .5, .1], alpha)
            b = evaluator.weighted_cvar([9, 17, 57], [.4, .5, .1], alpha)
            self.assertAlmostEqual(b - a, 7)
        risks = [evaluator.weighted_cvar([2, 10, 50], [.4, .5, .1], a)
                 for a in (0, .25, .75, .9, .99)]
        self.assertTrue(all(b >= a - 1e-10 for a, b in zip(risks, risks[1:])))

    def test_zero_probability_excluded_from_risk(self):
        self.assertAlmostEqual(evaluator.weighted_cvar([10, 100000], [1, 0], .9), 10)

    def test_mean_fill_probability_and_scope(self):
        r = evaluator.evaluate(data())
        m = r["policies"][0]["metrics"]
        self.assertAlmostEqual(m["expected_cost"], 19)
        self.assertAlmostEqual(m["expected_shortfall"], 1)
        self.assertAlmostEqual(m["volume_weighted_fill_rate"], 10/11)
        self.assertAlmostEqual(m["service_shortfall_probability"], .1)
        self.assertFalse(r["population_guarantee"])
        self.assertFalse(r["distribution_calibration_verified"])

    def test_failure_keeps_metrics_unknown(self):
        d = data()
        d["policies"][0]["outcomes"][1] = {"scenario_id": "b", "status": "failed", "error": "timeout"}
        r = evaluator.evaluate(d)
        self.assertFalse(r["all_evaluations_complete"])
        self.assertIsNone(r["policies"][0]["metrics"])
        self.assertAlmostEqual(r["policies"][0]["failure_probability"], .1)

    def test_zero_demand_ratio_unknown(self):
        d = data()
        for s in d["scenarios"]: s["demand"] = 0
        for o in d["policies"][0]["outcomes"]: o["shortfall"] = 0
        self.assertIsNone(evaluator.evaluate(d)["policies"][0]["metrics"]["volume_weighted_fill_rate"])

    def test_hard_violation_reported_not_hidden_by_service(self):
        d = data()
        d["policies"][0]["outcomes"][0]["hard_violation"] = True
        r = evaluator.evaluate(d)
        self.assertTrue(r["all_evaluations_complete"])
        self.assertFalse(r["policies"][0]["all_listed_hard_constraints_satisfied"])
        self.assertAlmostEqual(r["policies"][0]["metrics"]["hard_violation_probability"], .9)

    def test_paired_expected_cost_comparison(self):
        d = data()
        p = copy.deepcopy(d["policies"][0]); p["id"] = "q"
        for o in p["outcomes"]: o["total_cost"] += 2
        d["policies"].append(p); d["baseline_policy_id"] = "p"
        r = evaluator.evaluate(d)
        self.assertAlmostEqual(r["comparisons"][0]["expected_cost_difference_policy_minus_baseline"], 2)

    def test_missing_duplicate_unknown_scenarios_rejected(self):
        variants = []
        d=data(); d["policies"][0]["outcomes"].pop(); variants.append(d)
        d=data(); d["policies"][0]["outcomes"].append(copy.deepcopy(d["policies"][0]["outcomes"][0])); variants.append(d)
        d=data(); d["policies"][0]["outcomes"][0]["scenario_id"]="unknown"; variants.append(d)
        d=data(); d["scenarios"].append(copy.deepcopy(d["scenarios"][0])); variants.append(d)
        for d in variants:
            with self.subTest(d=d), self.assertRaises(ValueError): evaluator.evaluate(d)

    def test_probabilities_do_not_silently_normalize(self):
        for value in (-.1, 0, 2, float("nan"), True):
            d=data(); d["scenarios"][0]["probability"]=value
            with self.subTest(value=value), self.assertRaises(ValueError): evaluator.evaluate(d)
        d=data(); d["scenarios"][0]["probability"] += 1e-11
        self.assertTrue(evaluator.evaluate(d)["all_evaluations_complete"])

    def test_invalid_metrics_alpha_and_fields_rejected(self):
        variants=[]
        d=data(); d["alpha"]=1; variants.append(d)
        d=data(); d["policies"][0]["outcomes"][0]["shortfall"]=11; variants.append(d)
        d=data(); del d["policies"][0]["outcomes"][0]["hard_violation"]; variants.append(d)
        d=data(); d["policies"][0]["outcomes"][0]["total_cost"]=float("inf"); variants.append(d)
        d=data(); d["shortfal_tolerance"]=1; variants.append(d)
        d=data(); d["policies"][0]["outcomes"][0] = {"scenario_id":"a", "status":"failed", "error":"bad", "total_cost":0}; variants.append(d)
        for d in variants:
            with self.subTest(d=d), self.assertRaises(ValueError): evaluator.evaluate(d)

    def test_cli_status_codes_and_valid_json(self):
        failed=data(); failed["policies"][0]["outcomes"][0]={"scenario_id":"a","status":"failed","error":"timeout"}
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"input.json"
            for d, expected in ((data(),0),(failed,1),({},2)):
                p.write_text(json.dumps(d))
                result=subprocess.run([sys.executable,str(SCRIPT),str(p)],text=True,capture_output=True)
                self.assertEqual(result.returncode,expected,result.stderr)
                self.assertIsInstance(json.loads(result.stdout),dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)
