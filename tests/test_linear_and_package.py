import copy
import importlib.util
import itertools
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1] / "skills/optimization-modeling-experiments"
SCRIPT = ROOT / "scripts/check_linear_solution.py"
spec = importlib.util.spec_from_file_location("linear_checker", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def lp(x=(2, 2)):
    return {"objective": {"sense": "max", "coefficients": [3, 2], "constant": 0},
            "inequalities": {"A": [[1, 1], [1, 0]], "b": [4, 2]},
            "equalities": {"A": [], "b": []}, "bounds": [[0, None], [0, None]],
            "integer_indices": [], "solution": list(x) if x is not None else None}


class CandidateChecks(unittest.TestCase):
    def test_lp_objective_and_feasibility(self):
        r = checker.check_candidate(lp())
        self.assertTrue(r["all_passed"])
        self.assertEqual(r["objective_original"], 10)
        self.assertFalse(r["optimality_certified"])

    def test_feasible_nonoptimal_not_certified(self):
        r = checker.check_candidate(lp((0, 0)))
        self.assertTrue(r["all_passed"])
        self.assertFalse(r["optimality_certified"])

    def test_lp_vertices_match_analytic_bound(self):
        vertices = [(0, 0), (2, 0), (2, 2), (0, 4)]
        records = [checker.check_candidate(lp(x)) for x in vertices]
        self.assertTrue(all(r["all_passed"] for r in records))
        self.assertEqual(max(r["objective_original"] for r in records), 10)
        for x1, x2 in vertices:
            self.assertLessEqual(2 * (x1 + x2) + x1, 10)

    def test_negative_variable_bound(self):
        r = checker.check_candidate(lp((-1, 0)))
        self.assertFalse(r["all_passed"])
        self.assertEqual(r["bounds"][0]["violation"], 1)

    def test_inequality_violation(self):
        r = checker.check_candidate(lp((3, 2)))
        self.assertFalse(r["all_passed"])
        self.assertEqual(r["constraints"][0]["violation"], 1)

    def test_equality_not_one_sided(self):
        for x in ((0, 0), (2, 2)):
            model = lp(x)
            model["equalities"] = {"A": [[1, 1]], "b": [3]}
            self.assertFalse(checker.check_candidate(model)["all_passed"])

    def test_milp_enumeration_and_relaxation(self):
        model = lp()
        model["objective"]["coefficients"] = [1, 1]
        model["inequalities"] = {"A": [[2, 2]], "b": [3]}
        model["bounds"] = [[0, 1], [0, 1]]
        model["integer_indices"] = [0, 1]
        feasible = []
        for x in itertools.product((0, 1), repeat=2):
            model["solution"] = list(x)
            r = checker.check_candidate(model)
            if r["all_passed"]:
                feasible.append(r["objective_original"])
        self.assertEqual(max(feasible), 1)
        model["solution"] = [0.75, 0.75]
        before = copy.deepcopy(model)
        self.assertFalse(checker.check_candidate(model)["all_passed"])
        self.assertEqual(model, before)
        model["integer_indices"] = []
        r = checker.check_candidate(model)
        self.assertTrue(r["all_passed"])
        self.assertEqual(r["objective_original"], 1.5)
        model["solution"] = [1, 1]
        self.assertFalse(checker.check_candidate(model)["all_passed"])

    def test_objective_constant_and_sense_preserved(self):
        model = lp()
        model["objective"] = {"sense": "min", "coefficients": [-3, -2], "constant": 7}
        self.assertEqual(checker.check_candidate(model)["objective_original"], -3)

    def test_no_solution_has_unknown_metrics(self):
        r = checker.check_candidate(lp(None))
        self.assertIsNone(r["objective_original"])
        self.assertIsNone(r["all_passed"])
        self.assertEqual(r["status"], "no_solution")

    def test_explicit_scale_and_tolerance(self):
        model = lp((2.00001, 2))
        model["inequalities"]["scales"] = [1, 1]
        self.assertFalse(checker.check_candidate(model, atol=1e-8, rtol=0)["all_passed"])
        self.assertTrue(checker.check_candidate(model, atol=1e-4, rtol=0)["all_passed"])

    def test_invalid_domain_and_data_rejected(self):
        bad = []
        model = lp(); model["solution"] = [float("nan"), 2]; bad.append(model)
        model = lp(); model["solution"] = [True, 2]; bad.append(model)
        model = lp(); model["solution"] = [2]; bad.append(model)
        model = lp(); model["bounds"][0] = [3, 2]; bad.append(model)
        model = lp(); del model["bounds"]; bad.append(model)
        model = lp(); model["integer_indices"] = [0, 0]; bad.append(model)
        model = lp(); model["integer_indices"] = [True]; bad.append(model)
        model = lp(); model["inequalities"]["scales"] = [0, 1]; bad.append(model)
        model = lp(); model["integer_indexs"] = [0]; bad.append(model)
        for model in bad:
            with self.subTest(model=model):
                with self.assertRaises(ValueError):
                    checker.check_candidate(model)
        with self.assertRaises(ValueError):
            checker.check_candidate(lp(), atol=-1)

    def test_infeasible_lp(self):
        for x in (0, 0.5, 1):
            model = {"objective": {"sense": "min", "coefficients": [1]},
                     "bounds": [[None, None]], "solution": [x],
                     "inequalities": {"A": [[-1], [1]], "b": [-1, 0]}}
            self.assertFalse(checker.check_candidate(model)["all_passed"])

    def test_cli_exit_codes_and_json(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "model.json"
            for data, code in ((lp(), 0), (lp((3, 2)), 1), (lp(None), 1), ({}, 2)):
                path.write_text(json.dumps(data), encoding="utf-8")
                result = subprocess.run([sys.executable, str(SCRIPT), str(path)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertIn("status", json.loads(result.stdout))


class PackageChecks(unittest.TestCase):
    def test_metadata_and_resource_links(self):
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        front = yaml.safe_load(content.split("---", 2)[1])
        self.assertEqual(front["name"], ROOT.name)
        self.assertTrue(front["description"])
        ui = yaml.safe_load((ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))
        self.assertIn("$" + ROOT.name, ui["interface"]["default_prompt"])
        for md in ROOT.rglob("*.md"):
            text = md.read_text(encoding="utf-8")
            self.assertNotIn("[TODO", text)
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if not link.startswith(("https://", "http://", "#")):
                    path = link.split("#", 1)[0]
                    self.assertTrue((md.parent / path).is_file(), (md, link))

    def test_experiment_configuration_consistency(self):
        data = json.loads((ROOT / "assets/experiment-config.json").read_text())
        self.assertEqual(data["mode"], "smoke")
        self.assertGreaterEqual(data["budget"]["total_seconds"],
                                data["budget"]["per_run_seconds"])
        self.assertTrue(data["protocol"]["save_all_attempts"])
        self.assertTrue(data["output"]["save_logs"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
