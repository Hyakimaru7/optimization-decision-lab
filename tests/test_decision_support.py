import copy
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'skills/optimization-modeling-experiments'
sys.path.insert(0, str(ROOT / 'scripts'))
from assess_plan_validity import assess
from audit_requirement_contract import audit
from evaluate_information import evaluate


def asset(name):
    return json.loads((ROOT / 'assets' / name).read_text())


def plan():
    return asset('plan-validity-example.json')


class PlanTests(unittest.TestCase):
    def test_buffered_and_nominal_optimal_plan(self):
        d=plan(); before=copy.deepcopy(d); r=assess(d)
        self.assertEqual(d,before)
        self.assertEqual(r['status'],'within_declared_envelope')
        self.assertEqual(r['max_radius'],1)
        self.assertEqual(r['objective_original'],990)
        self.assertFalse(r['optimality_certified'])
        d['model']['solution']=[8,8]; r=assess(d)
        self.assertEqual(r['max_radius'],0)
        self.assertFalse(r['feasible_at_target'])

    def test_boundaries_and_monotonicity(self):
        statuses=[]
        for rho in [0,.1,.9,1,1.01,2]:
            d=plan(); d['target_radius']=rho; statuses.append(assess(d)['feasible_at_target'])
        self.assertEqual(statuses,[True,True,True,True,False,False])

    def test_negative_variables_and_simultaneous_box_corners(self):
        d=plan()
        d['model']={'objective':{'sense':'min','coefficients':[0,0]},'inequalities':{'A':[[2,-1]],'b':[5]},'equalities':{'A':[],'b':[]},'bounds':[[None,None],[None,None]],'solution':[-2,3]}
        d['uncertainty']={'inequalities':{'coefficient_absolute':[[.2,.3]],'rhs_absolute':[.5]},'equalities':{'coefficient_absolute':[],'rhs_absolute':[]},'bounds':[[0,0],[0,0]]}
        r=assess(d); self.assertAlmostEqual(r['max_radius'],12/1.8)
        corner_residuals=[(2+s1*.2)*-2+(-1+s2*.3)*3-(5+sb*.5) for s1,s2,sb in itertools.product((-1,1),repeat=3)]
        self.assertAlmostEqual(r['rows'][0]['worst_residual_at_target'],max(corner_residuals))

    def test_equality_uses_both_signs(self):
        for rhs in (5,7):
            d=plan(); d['model']['equalities']={'A':[[0,1]],'b':[rhs]}
            d['uncertainty']['equalities']={'coefficient_absolute':[[0,0]],'rhs_absolute':[1]}
            d['tolerances']['atol']=2
            r=assess(d); eq=[x for x in r['rows'] if x['id']=='equalities[0]'][0]
            self.assertEqual(eq['max_radius'],2-abs(7-rhs))

    def test_lower_and_upper_bounds_adverse_directions(self):
        d=plan(); d['uncertainty']['bounds']=[[2,2],[1,1]]
        r=assess(d); rows={x['id']:x for x in r['rows']}
        self.assertEqual(rows['bounds[0].lower']['max_radius'],4)
        self.assertEqual(rows['bounds[0].upper']['max_radius'],2)

    def test_zero_uncertainty_is_scoped_unbounded(self):
        d=plan(); d['uncertainty']['inequalities']['rhs_absolute']=[0,0,0]
        r=assess(d); self.assertTrue(r['unbounded_in_declared_box']); self.assertIsNone(r['max_radius'])

    def test_bad_nominal_and_integer_candidate_no_radius(self):
        for x in ([12,20],[8.1,7]):
            d=plan(); d['model']['solution']=x; r=assess(d)
            self.assertFalse(r['nominal_feasible']); self.assertIsNone(r['max_radius'])
            self.assertFalse(r['unbounded_in_declared_box'])

    def test_stale_context_and_expiry_review_even_if_math_passes(self):
        for key in ['model_revision','data_revision','context_revision']:
            d=plan(); d['current'][key]='changed'; r=assess(d)
            self.assertTrue(r['feasible_at_target']); self.assertIn(key+'_changed',r['review_reasons'])
        d=plan(); d['current']['as_of']=d['artifact']['expires_at']
        self.assertIn('expired',assess(d)['review_reasons'])
        d=plan(); d['current']['as_of']='2026-10-08T08:00:00+08:00'
        self.assertIn('generated_in_future',assess(d)['review_reasons'])

    def test_invalid_uncertainty_timestamps_and_shape(self):
        cases=[]
        d=plan(); d['uncertainty']['inequalities']['rhs_absolute'][0]=-1; cases.append(d)
        d=plan(); d['uncertainty']['inequalities']['coefficient_absolute'].pop(); cases.append(d)
        d=plan(); d['model']['bounds'][0][1]=None; d['uncertainty']['bounds'][0][1]=1; cases.append(d)
        d=plan(); d['current']['as_of']='2026-10-08T10:00:00'; cases.append(d)
        d=plan(); d['artifact']['expires_at']=d['artifact']['generated_at']; cases.append(d)
        d=plan(); d['target_radius']=True; cases.append(d)
        d=plan(); d['model']['solution']=None; cases.append(d)
        for d in cases:
            with self.subTest(d=d),self.assertRaises(ValueError): assess(d)

    def test_unit_scaling_preserves_radius_with_zero_tolerance(self):
        d=plan(); r=assess(d)
        d['model']['inequalities']['A'][0]=[v*60 for v in d['model']['inequalities']['A'][0]]
        d['model']['inequalities']['b'][0]*=60; d['uncertainty']['inequalities']['rhs_absolute'][0]*=60
        self.assertEqual(assess(d)['max_radius'],r['max_radius'])


class ContractTests(unittest.TestCase):
    def test_declared_consistency_is_not_semantic_certification(self):
        r=audit(asset('requirement-contract-example.json'))
        self.assertEqual(r['status'],'declared_contract_consistent')
        self.assertFalse(r['semantic_truth_verified']); self.assertFalse(r['evidence_contents_verified'])

    def test_omitted_requirement_mapping_and_stale_tests(self):
        d=asset('requirement-contract-example.json'); d['requirements'][0]['model_elements']=[]
        self.assertIn('not_mapped_to_model',audit(d)['requirements'][0]['issues'])
        d=asset('requirement-contract-example.json'); d['model_revision']='new'
        self.assertEqual(audit(d)['status'],'review_required')

    def test_failed_pending_unknown_and_incorrect_link(self):
        cases=[]
        d=asset('requirement-contract-example.json'); d['tests'][0]['result']='failed'; cases.append(d)
        d=asset('requirement-contract-example.json'); d['requirements'][0]['semantic_review']['status']='pending'; cases.append(d)
        d=asset('requirement-contract-example.json'); d['requirements'][0]['model_elements']=['unknown']; cases.append(d)
        d=asset('requirement-contract-example.json'); d['tests'][0]['requirement_id']='other'; cases.append(d)
        d=asset('requirement-contract-example.json'); d['requirements'][0]['validator_ids']=[]; cases.append(d)
        for d in cases: self.assertEqual(audit(d)['status'],'review_required')

    def test_soft_warning_separate_from_hard(self):
        d=asset('requirement-contract-example.json'); d['requirements'][0]['kind']='soft'; d['requirements'][0]['model_elements']=[]
        r=audit(d); self.assertEqual(r['status'],'declared_contract_consistent'); self.assertEqual(r['soft_requirements_with_issues'],['B_min'])

    def test_undeclared_requirements_cannot_be_discovered(self):
        d=asset('requirement-contract-example.json'); d['tests'][0]['id']='unlinked'; d['requirements'][0]['test_ids'].remove('B_bad5')
        r=audit(d); self.assertIn('unlinked',r['unlinked_tests'])
        self.assertEqual(r['status'],'declared_contract_consistent')

    def test_malformed_duplicate_and_typo(self):
        for change in ('duplicate','typo','result'):
            d=asset('requirement-contract-example.json')
            if change=='duplicate': d['requirements'].append(copy.deepcopy(d['requirements'][0]))
            if change=='typo': d['model_revison']='bad'
            if change=='result': d['tests'][0]['result']='success'
            with self.assertRaises(ValueError): audit(d)


class InformationTests(unittest.TestCase):
    def test_noisy_and_perfect_measurement_costs(self):
        r=evaluate(asset('information-example.json'))
        self.assertEqual(r['baseline_action'],'careful_process'); self.assertEqual(r['baseline_expected_loss'],40)
        self.assertEqual(r['evpi'],20)
        self.assertAlmostEqual(r['experiments'][0]['evsi_gross'],10)
        self.assertAlmostEqual(r['experiments'][0]['net_value'],5)
        self.assertEqual(r['experiments'][1]['net_value'],-5)
        self.assertEqual(r['selected_experiment'],'noisy_preproduction_test')
        self.assertFalse(r['population_guarantee'])

    def test_uninformative_and_zero_probability_signals(self):
        d=asset('information-example.json'); e=d['experiments'][0]
        e['signals'].append('impossible'); e['likelihood']=[[.5,.5,0],[.5,.5,0]]
        r=evaluate(d)['experiments'][0]
        self.assertAlmostEqual(r['evsi_gross'],0); self.assertIsNone(r['signal_policy'][2]['action'])

    def test_value_bounds_for_random_tables(self):
        rng=random.Random(142)
        for _ in range(100):
            d=asset('information-example.json'); d['losses']=[[rng.uniform(-100,100) for _ in range(2)] for _ in range(2)]
            t=rng.random(); d['probabilities']=[t,1-t]
            s=rng.random(); q=rng.random(); d['experiments'][0]['likelihood']=[[s,1-s],[q,1-q]]
            r=evaluate(d)
            for e in r['experiments']:
                self.assertGreaterEqual(e['evsi_gross'],-1e-10); self.assertLessEqual(e['evsi_gross'],r['evpi']+1e-10)

    def test_translation_and_action_dominance(self):
        d=asset('information-example.json'); r=evaluate(d)
        d['losses']=[[x+1000 for x in row] for row in d['losses']]
        self.assertAlmostEqual(evaluate(d)['evpi'],r['evpi'])
        d['losses']=[[1,1],[2,2]]
        self.assertEqual(evaluate(d)['evpi'],0)

    def test_zero_weight_state_still_in_minimax_regret(self):
        d=asset('information-example.json'); d['probabilities']=[1,0]
        r=evaluate(d); self.assertEqual(r['baseline_action'],'standard_process')
        self.assertEqual(r['minimax_regret_action'],'careful_process')

    def test_invalid_probabilities_feasibility_and_future_information(self):
        cases=[]
        d=asset('information-example.json'); d['probabilities']=[.5,.6]; cases.append(d)
        d=asset('information-example.json'); d['actions_feasible_in_all_states']=False; cases.append(d)
        d=asset('information-example.json'); d['experiments'][0]['available_before_decision']=False; cases.append(d)
        d=asset('information-example.json'); d['experiments'][0]['likelihood'][0]=[.5,.6]; cases.append(d)
        d=asset('information-example.json'); d['losses'][0][0]=float('inf'); cases.append(d)
        d=asset('information-example.json'); d['experiments'][0]['cost']=-1; cases.append(d)
        for d in cases:
            with self.subTest(d=d),self.assertRaises(ValueError): evaluate(d)


class CLITests(unittest.TestCase):
    def test_all_cli_codes_and_json(self):
        contract=asset('requirement-contract-example.json'); contract['requirements'][0]['model_elements']=[]
        p=plan(); p['model']['solution']=[8,8]
        cases=[('assess_plan_validity.py',plan(),0),('assess_plan_validity.py',p,1),('audit_requirement_contract.py',asset('requirement-contract-example.json'),0),('audit_requirement_contract.py',contract,1),('evaluate_information.py',asset('information-example.json'),0)]
        cases += [(name,{},2) for name in ('assess_plan_validity.py','audit_requirement_contract.py','evaluate_information.py')]
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'input.json'
            for script,d,code in cases:
                path.write_text(json.dumps(d))
                result=subprocess.run([sys.executable,str(ROOT/'scripts'/script),str(path)],capture_output=True,text=True)
                self.assertEqual(result.returncode,code,result.stderr); self.assertIn('status',json.loads(result.stdout))


if __name__=='__main__': unittest.main(verbosity=2)
