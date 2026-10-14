"""Export inspectable synthetic samples; never call models or manufacture results."""
from pathlib import Path
from .fixtures import make_cases
from .run import dump

ROOT=Path(__file__).resolve().parent

def main():
    for c in make_cases():
        if c['instance']!=0:continue
        folder=ROOT/'samples'/c['id'];folder.mkdir(parents=True,exist_ok=True)
        for name,text in c['bundle'].items():(folder/name).write_bytes((text.rstrip()+'\n').encode('utf-8'))
        (folder/'trusted-task.txt').write_bytes(('\n'.join(x['id']+': '+x['text'] for x in c['task'])+'\n').encode('utf-8'))
    dump(ROOT/'preparation.json',{'status':'PREPARED_NOT_MEASURED','authored_cases':48,'repeats':2,
       'factorial_arms':['Mixed-Flat','Mixed-Graph','Isolated-Flat','Isolated-Graph'],
       'strong_baseline':'TaskRuntime','planned_method_trajectories':480,
       'unshared_logical_role_use_upper_bound':672,'model':'gpt-6-luna','cumulative_budget_usd':20,
       'prior_usage_estimate_usd':1.257365875,'preparation_model_calls':0,
       'warning':'No sample has yet been shown to fool a model. Stub/reference checks are not empirical outcomes.'})
    print('Exported 24 inspectable sample bundles (first instance); zero model calls.')

if __name__=='__main__':main()
