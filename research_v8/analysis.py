"""Predeclared paired mean differences with task-family cluster resampling."""
import random
def cluster_interval(values):
    rng=random.Random(7648)
    samples=sorted(sum(rng.choice(values) for _ in values)/len(values) for _ in range(5000))
    return dict(mean=sum(values)/len(values),low=samples[124],high=samples[4874],families=len(values))
def contrasts(rows):
    output=[]
    for cohort in ('oracle','extracted'):
        for setting in ('mini','luna_none','luna_low'):
            for baseline in ('Fixed','LLM','Monotone','Provenance','SingleWitness'):
                for metric in ('safe_feasible','valid_narrowing'):
                    choose=lambda r:r['cohort']==cohort and r['setting']==setting and r['event']!='trusted_cancel' and (metric!='valid_narrowing' or r['event']=='valid_narrow')
                    left={(r['task'],r['repeat'],r['event']):r for r in rows if choose(r) and r['method']==baseline}
                    right={(r['task'],r['repeat'],r['event']):r for r in rows if choose(r) and r['method']=='TaskPreserving'}
                    if not left:continue
                    if left.keys()!=right.keys():raise RuntimeError('Unmatched analysis rows')
                    families=sorted({k[0] for k in left});effects=[]
                    for family in families:
                        keys=[k for k in left if k[0]==family]
                        effects.append(sum(int(right[k]['score'][metric])-int(left[k]['score'][metric]) for k in keys)/len(keys))
                    output.append(dict(cohort=cohort,setting=setting,left=baseline,right='TaskPreserving',metric=metric,
                        family_effects=dict(zip(families,effects)),**cluster_interval(effects)))
    return output

