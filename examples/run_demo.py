#!/usr/bin/env python3
"""Reproduce synthetic v3 checks with exhaustive finite-domain production models."""
import argparse
import copy
import json
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent.parent/'results/demo')
    parser.add_argument('--skill',type=Path,default=Path(__file__).resolve().parent.parent/'skills/optimization-modeling-experiments')
    args=parser.parse_args()
    sys.path.insert(0,str(args.skill.resolve()/'scripts'))
    from assess_plan_validity import assess
    from audit_requirement_contract import audit
    from evaluate_information import evaluate
    from check_linear_solution import check_candidate

    def load(name):
        return json.loads((args.skill/'assets'/name).read_text(encoding='utf-8'))

    target=Path(args.output).resolve()
    target.mkdir(parents=True,exist_ok=True)

    def save(name,value):
        (target/name).write_text(json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')

    plan=load('plan-validity-example.json')
    corrected=copy.deepcopy(plan['model'])
    omitted=copy.deepcopy(corrected)
    omitted['inequalities']['A'].pop(); omitted['inequalities']['b'].pop()
    robust=copy.deepcopy(corrected)
    robust['inequalities']['b'][:2]=[38,24]

    # Exhaustive enumeration proves optimality only in this bounded integer domain.
    def solve(model):
        best=None; feasible=0
        for x in range(13):
            for y in range(21):
                candidate=copy.deepcopy(model); candidate['solution']=[x,y]
                # Independent domain rule calculation, separate from matrix checker.
                valid=(3*x+2*y <= model['inequalities']['b'][0] and
                       2*x+y <= model['inequalities']['b'][1] and
                       (len(model['inequalities']['A'])==2 or y>=6))
                checked=check_candidate(candidate,0,0,0)
                assert checked['all_passed']==valid
                if valid:
                    feasible+=1
                    value=80*x+50*y
                    if best is None or value>best['profit']:
                        best={'solution':[x,y],'profit':value}
        return {'best':best,'candidates_checked':273,'feasible_candidates':feasible,
                'proof_scope':'complete bounded integer enumeration; synthetic model'}

    solutions={'omitted_order':solve(omitted),'corrected_order':solve(corrected),'buffered_resources':solve(robust)}
    assert solutions['omitted_order']['best']=={'solution':[10,5],'profit':1050}
    assert solutions['corrected_order']['best']=={'solution':[8,8],'profit':1040}
    assert solutions['buffered_resources']['best']=={'solution':[8,7],'profit':990}
    witness=solutions['omitted_order']['best']['solution']
    assert witness[1]<6
    corrected['solution']=witness
    assert not check_candidate(corrected,0,0,0)['all_passed']

    # Mathematical invariants of the small exact optimization models.
    duplicate=copy.deepcopy(robust)
    duplicate['inequalities']['A'].append([3,2]); duplicate['inequalities']['b'].append(38)
    assert solve(duplicate)['best']==solutions['buffered_resources']['best']
    scaled=copy.deepcopy(robust)
    scaled['inequalities']['A'][0]=[180,120]; scaled['inequalities']['b'][0]=2280
    # Verify transformed candidates directly; original independent validator uses hours.
    for x in range(13):
        for y in range(21):
            for m in (robust,scaled): m['solution']=[x,y]
            assert check_candidate(robust,0,0,0)['all_passed']==check_candidate(scaled,0,0,0)['all_passed']

    plan['model']['solution']=solutions['buffered_resources']['best']['solution']
    buffered_report=assess(plan)
    nominal_plan=copy.deepcopy(plan); nominal_plan['model']['solution']=solutions['corrected_order']['best']['solution']
    nominal_report=assess(nominal_plan)
    changed=copy.deepcopy(plan); changed['current']['context_revision']='synthetic-new-order-B-at-least-8'
    changed_report=assess(changed)
    changed_model=copy.deepcopy(plan['model']); changed_model['inequalities']['b'][2]=-8
    changed_model_check=check_candidate(changed_model,0,0,0)
    assert buffered_report['max_radius']==1 and nominal_report['max_radius']==0
    assert changed_report['feasible_at_target'] and changed_report['status']=='review_required'
    assert not changed_model_check['all_passed']
    save('plan-input.json',plan)
    save('plan-reports.json',{'buffered':buffered_report,'nominal_optimum':nominal_report,'changed_order_context':changed_report,'rebuilt_for_changed_order':changed_model_check})

    contract=load('requirement-contract-example.json')
    def check_B_order(y): return y>=6
    executions=[{'id':'B_bad5','input_y':5,'expected':False,'actual':check_B_order(5)},
                {'id':'B_boundary6','input_y':6,'expected':True,'actual':check_B_order(6)}]
    for record in executions:
        assert record['expected']==record['actual']
    save('order-test-evidence.json',executions)
    for test in contract['tests']:
        test['evidence']='order-test-evidence.json:'+test['id']
        test['result']='passed'
    contract['requirements'][0]['semantic_review']['evidence']='run_demo.py: corrected inequality [0,-1]*[x,y]<=-6 and independent y>=6'
    missing=copy.deepcopy(contract); missing['requirements'][0]['model_elements']=[]
    save('contract-input.json',contract)
    save('contract-reports.json',{'missing_model_mapping':audit(missing),'corrected':audit(contract)})

    information=load('information-example.json')
    info_report=evaluate(information)
    assert info_report['evpi']==20
    assert abs(info_report['experiments'][0]['net_value']-5)<1e-12
    save('information-input.json',information)
    save('information-report.json',info_report)
    save('production-comparison.json',{'source_kind':'synthetic','solutions':solutions,
         'omitted_optimum_rejected_by_order_rule':True,
         'buffer_profit_sacrifice':1040-990,
         'buffered_capacities':{'machine_hours':38,'material_units':24},
         'metamorphic_checks':{'duplicate_resource_row':'passed','hours_to_minutes':'passed'}})
    print(json.dumps({'status':'passed','results_directory':str(target),
                      'nominal_profit':1040,'buffered_profit':990,'measurement_net_value':5},ensure_ascii=False))


if __name__=='__main__': main()
