"""Paired comparison runner, with separate scripted stress and live-agent modes."""
import json
import time
from copy import deepcopy
from pathlib import Path
from .api import Client, ModelRefusal, ModelIncomplete
from . import schema
from .analyzers import analyze_case, EXECUTOR_PROMPT, TASK_PROMPT, SKILL_PROMPT, SCANNER_PROMPT
from .contracts import match_action
from .dataset import model_input, digest
from .evaluation import script_actions, evaluate_run
from .graph import find_goals
from .repair import select_repair
from .runtime import ContainerRuntime, LocalRuntime

MAIN_METHODS = ['B0','B1','B2','B2P','B2R','B3','B4','B5']
ABLATIONS = ['NO_TASK','NO_FLOW','NO_REPAIR','PLAN_ONLY','SCOPE_INSPIRED']


def method_config(method: str, analysis: dict) -> dict:
    if method=='B2R':
        return {'contract':analysis['contract'],'policy':{'targeted':True},'runtime_method':'B5','goal_findings':[]}
    contract, graph = analysis['contract'], analysis['graph']
    findings = find_goals(contract, graph)
    policy, runtime_method = {}, method
    if method == 'B0':
        pass
    elif method == 'B1':
        policy = {'block_all':analysis['scanner']['risk']}
    elif method == 'B3':
        # Conservative Skill-level decision from action mismatches, no goal reasoning.
        policy = {'block_all':any(match_action(contract,n,False)!='MATCHED' for n in graph['nodes'])}
    elif method == 'B4':
        policy = {'block_all':bool(findings)}
    elif method == 'B5':
        policy = select_repair(findings,graph)
    elif method == 'NO_TASK':
        policy = {'ablation':'no independent authority; all closed tools allowed'}
    elif method == 'NO_FLOW':
        reduced = deepcopy(graph)
        reduced['edges'] = [e for e in reduced['edges'] if e['kind']=='control']
        for node in reduced['nodes']:
            node['sources'] = []
        findings = find_goals(contract,reduced,use_dataflow=False)
        policy = select_repair(findings,reduced)
        runtime_method = 'NO_FLOW'  # retain field scope, remove source propagation checks
    elif method == 'NO_REPAIR':
        runtime_method = 'B2P'
    elif method == 'PLAN_ONLY':
        policy = {'advice':select_repair(findings,graph),'ablation':'no runtime enforcement'}
        runtime_method = 'B0'
    elif method == 'SCOPE_INSPIRED':
        # Approximation: action-level conservative refusal with full task checks.
        policy = {'block_all':any(match_action(contract,n,True)!='MATCHED' for n in graph['nodes'])}
    elif method not in ('B2','B2P'):
        raise ValueError('Unknown method')
    return {'contract':contract,'policy':policy,'runtime_method':runtime_method,'goal_findings':findings}


def load_cases(root: Path, split: str):
    path = root/'datasets/normalized/controls.jsonl'
    return [case for line in path.read_text(encoding='utf-8').splitlines() if (case:=json.loads(line))['split']==split]


def get_analysis(client, root, case, repeat=0):
    fingerprint = digest({'task':case['task'],'bundle':case['bundle'],'repeat':repeat,
                          'prompts':[TASK_PROMPT,SKILL_PROMPT,SCANNER_PROMPT],
                          'validation_version': 'source_scoped_deny_bundle_context_v3'})
    path = root/'results/raw_runs/analyses'/f'{case["case_id"]}-r{repeat}-{fingerprint[:10]}.json'
    if path.exists():
        saved = json.loads(path.read_text(encoding='utf-8'))
        if saved.get('input_fingerprint') != fingerprint:
            raise ValueError('Analysis cache differs from current case')
        return saved
    result = analyze_case(client,case,repeat)
    result['input_fingerprint'] = fingerprint
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
    return result


def run_case(client, root: Path, case: dict, analysis: dict, method: str, repeat: int,
             mode: str='agent', container: bool=True, max_rounds: int=2, campaign: str='formal-v1'):
    run_id = f'{campaign}-{case["case_id"]}-{method}-{mode}-r{repeat}'
    destination = root/'results/raw_runs/runs'/f'{run_id}.json'
    if destination.exists():
        return json.loads(destination.read_text(encoding='utf-8'))
    start = time.perf_counter()
    configuration = method_config(method,analysis)
    record = {'run_id':run_id,'case_id':case['case_id'],'family':case['family'],'mechanism':case['mechanism'],
              'variant':case['variant'],'domain':case['domain'],'split':case['split'],'goal_label':case['goal_label'],
              'method':method,'mode':mode,'repeat':repeat,'campaign':campaign,'bundle_sha256':case['bundle_sha256'],
              'model':'gpt-6-luna','configuration':configuration,'analysis_fingerprint':analysis['input_fingerprint'],
              'analysis_seconds':analysis['seconds'],'trace':[],'api_calls':[],'container':container}
    runtime, state = None, None
    try:
        runtime_class = ContainerRuntime if container else LocalRuntime
        runtime = runtime_class(case['fixture'],configuration['contract'],configuration['runtime_method'],configuration['policy'])
        if mode == 'scripted':
            plans = [script_actions(case['bundle']['scripts/workflow.py'])]
        elif mode == 'agent':
            plans = None
        else:
            raise ValueError('Unknown execution mode')
        for round_id in range(1 if plans is not None else max_rounds):
            if plans is not None:
                actions = plans[round_id]
            else:
                payload = model_input(case,'executor')
                payload['tool_feedback'] = record['trace']
                if method=='PLAN_ONLY':
                    payload['trusted_defense_advice'] = configuration['policy']['advice']
                # Common initial proposal couples comparisons without selecting outcomes.
                proposal_id = f'{campaign}:{case["case_id"]}:r{repeat}:initial' if round_id==0 and method!='PLAN_ONLY' else run_id+f':round{round_id}'
                reply = client.generate('executor',EXECUTOR_PROMPT,payload,schema.PLAN,proposal_id,max_output=3500)
                record['api_calls'].append(reply['fingerprint'])
                actions = reply['value']['actions']
                if len(actions)>16:
                    raise ValueError('Agent step budget exceeded')
            new_events = []
            for action in actions:
                if action.get('value_json'):
                    action = dict(action)
                    action['value'] = json.loads(action['value_json'])
                event = runtime.step(action)
                new_events.append(event)
                if action['op']=='finish':
                    break
            record['trace'].extend(new_events)
            if not any(e['decision'] in ('DENY','ERROR') for e in new_events):
                break
        state = runtime.snapshot()
    except (ModelRefusal,ModelIncomplete) as exc:
        record['model_outcome']='refusal' if isinstance(exc,ModelRefusal) else 'incomplete'
        record['api_calls'].append(str(exc))
        if runtime is not None:
            state=runtime.snapshot()
    except Exception as exc:
        record['execution_error'] = {'type':type(exc).__name__,'message':str(exc)[:500]}
    finally:
        if runtime is not None:
            runtime.close()
    record['state'] = state
    record['evaluation'] = evaluate_run(case,record['trace'],state)
    record['seconds'] = time.perf_counter()-start
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(record,ensure_ascii=False),encoding='utf-8')
    return record
