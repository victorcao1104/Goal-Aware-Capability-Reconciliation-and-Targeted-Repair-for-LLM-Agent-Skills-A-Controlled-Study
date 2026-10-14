"""Derived v7 reports and scientific figures; never changes frozen measurements."""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
from research_v7.api import ROOT,OUT
from research_v7.model import ARMS,SETTINGS
from research_v7.run import collect
from research_v7.fixtures import cases
from research_v7.engine import analyze
REPORT=ROOT/'research_v7/report'
METHODS=(*ARMS,'DeterministicFlat','DeterministicGraph')
LABELS=('Full flat + prose','Full flat clean','Full graph clean','Sliced flat clean','Sliced graph clean','Deterministic flat','Deterministic graph')
def encode(v):return json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
def load():
    s,rows,records=collect()
    if s!=json.loads((OUT/'summary.json').read_text(encoding='utf-8')):raise RuntimeError('Summary mismatch')
    return s,rows,records
def diagnostics(s,rows,records):
    result={}
    by_case={c['id']:c for c in cases()}
    field_reporting={}
    for setting in SETTINGS:
        for method in METHODS:
            rs=[r for r in rows if r['setting']==setting and r['method']==method]
            buckets=Counter()
            for r in rs:
                z=r['score']
                if r['policy_status']!='ok' or r.get('audit_status','ok')!='ok':kind='request_failure'
                elif z['joint']:kind='optimal_success' if z['optimal_joint'] else 'nonminimal_success'
                elif r.get('proposal',{}).get('decision')=='deny':kind='denied'
                elif not z['valid'] or not z.get('proposal_shape_valid',True):kind='invalid_proposal'
                elif not z['goal']:kind='required_output_lost'
                elif not z['permitted']:kind='contract_rejection'
                elif z['unsafe_execution']:kind='unsafe_activation'
                else:kind='other'
                buckets[kind]+=1
            result[setting+'/'+method]=dict(buckets)
            if method in ARMS:
                counts=Counter()
                for r in rs:
                    c=by_case[r['case_id']];states=analyze(c)['states'];prediction=r['proposal'].get('rows_at_sinks',{})
                    if r['audit_status']!='ok':continue
                    if {k:sorted(v) for k,v in prediction.items()}=={k:sorted(v) for k,v in c['required'].items()}:
                        counts['matches_required_output_field_set']+=1
                    if any(any(states[sink].get(f,{}).get('class')=='aggregate' for f in fs) for sink,fs in prediction.items()):
                        counts['reports_aggregate_as_row_field']+=1
                    if any(any(meta['class']=='rows' and f not in prediction.get(sink,[]) for f,meta in states[sink].items()) for sink in c['sinks']):
                        counts['omits_actual_row_field']+=1
                field_reporting[setting+'/'+method]=dict(counts)
    deterministic_equal=True
    for c in {r['case_id'] for r in rows}:
        for setting in SETTINGS:
            for repeat in (0,1):
                pair={r['method']:r for r in rows if r['case_id']==c and r['setting']==setting and r['repeat']==repeat and r['method'].startswith('Deterministic')}
                f,g=pair['DeterministicFlat'],pair['DeterministicGraph']
                deterministic_equal &= f['score']==g['score'] and f['repair']['edits']==g['repair']['edits'] and f['repair']['count']==g['repair']['count']
    success_examples=[r for r in rows if r['variant']=='unsafe' and r['method'] in ARMS and r['score']['joint']]
    nonminimal=[r for r in success_examples if not r['score']['optimal_joint']]
    source=json.loads((OUT/'execution.json').read_text(encoding='utf-8'))
    return dict(failure_buckets=result,deterministic_outcomes_and_edits_equal=bool(deterministic_equal),
                field_reporting=field_reporting,
                provider_models=dict(Counter(q['model'] for q in records.values())),
                source=source,example_nonminimal=nonminimal[0] if nonminimal else None,
                example_optimal=next((r for r in success_examples if r['score']['optimal_joint']),None),
                cost_allocation_sum=sum(g['allocated_physical_usd'] for g in s['per_arm']))
def table(s,setting):
    def get(m,v):return next(g for g in s['groups'] if g['setting']==setting and g['method']==m and g['variant']==v)
    lines=['| Method | Safe task completion | Unsafe: safe completion | Unsafe: minimum edits | Safe utility | Authorized utility | Row classification |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for m in METHODS:
        a,u,cl,au=[get(m,v) for v in ('all','unsafe','safe','authorized')]
        cls=str(a['raw_class_correct'])+'/24' if m in ARMS else 'deterministic'
        lines.append(f"| {m} | {a['joint']}/24 | {u['joint']}/8 | {u['optimal_joint']}/8 | {cl['joint']}/8 | {au['joint']}/8 | {cls} |")
    return '\n'.join(lines)
def case_study(rows):
    def row(case,repeat,setting,method):
        return next(r for r in rows if (r['case_id'],r['repeat'],r['setting'],r['method'])==(case,repeat,setting,method))
    def show(r):
        link='../results/requests/'+r['components'][1]+'.json'
        return f"**{r['case_id']}, repeat {r['repeat']}, {r['setting']}, {r['method']}** — [retained response]({link})\n\n"+'\n'.join([
            '    '+line for line in encode(dict(proposal=r['proposal'],score=r['score'])).splitlines()])
    f=row('mobility-unsafe',0,'luna_low','FullFlatClean')
    g=row('mobility-unsafe',0,'luna_low','FullGraphClean')
    harm=row('mobility-authorized',1,'luna_low','FullGraphClean')
    safe=row('mobility-safe',0,'mini','FullGraphClean')
    unsafe=row('mobility-unsafe',0,'mini','FullGraphClean')
    return """# V7 evidence-linked case study

These examples were selected after measurement to explain observed mechanisms, not to estimate frequencies. The complete frozen denominators remain in the results.

## Shared-prefix repair
On the same unsafe program, Luna low with full flat input used four merge projections; full graph input selected two shared-prefix projections. Both preserved all four aggregate outputs. This is one case of better repair placement, not overall graph superiority.

"""+show(f)+'\n\n'+show(g)+"""

## Correct tracking, wrong necessity decision
On a truly authorized counterpart, the full graph auditor correctly listed all original row fields but removed them anyway. The task explicitly required those rows; concrete goal equality failed, so the proposal was not activated. The matching full-flat job succeeded. This isolates a task interpretation/over-repair failure even when provenance reporting is correct.

"""+show(harm)+"""

## Interface mismatch and a separate unsafe allow
In the safe Mini example, the prose correctly calls f02/f12 aggregates, but rows_at_sinks contains those same aggregate IDs. Thus strict row-field accuracy fails despite an appropriate allow decision. On the unsafe counterpart, the response also omits the actual f01/f11 row branches and allows the program. The verifier prevents activation. These cases must not be combined into a claim that every field-reporting failure is a semantic flow failure, nor that every successful guard means a correct LLM audit.

"""+show(safe)+'\n\n'+show(unsafe)+'\n'
def documents(s,rows,records,d):
    prep=json.loads((OUT/'preparation.json').read_text(encoding='utf-8'))
    tables='\n\n'.join('### '+setting+'\n\n'+table(s,setting) for setting in SETTINGS)
    pairlines=['| Setting | Contrast (right minus left) | Right-only success | Left-only success |','|---|---|---:|---:|']
    for p in s['paired']:
        if p['metric']=='joint':
            pairlines.append(f"| {p['setting']} | {p['right']} − {p['left']} | {p['right_only']} | {p['left_only']} |")
    pairs='\n'.join(pairlines)
    costs=['| Setting | Method | Logical component uses | Unique request references* | Allocated USD | Mean audit input tokens |',
           '|---|---|---:|---:|---:|---:|']
    for p in s['per_arm']:
        n=p['unique_audit_requests'];mean=p['audit_input_tokens']/n if n else 0
        costs.append(f"| {p['setting']} | {p['method']} | {p['logical_component_calls']} | {p['unique_component_requests']} | {p['allocated_physical_usd']:.8f} | {mean:.1f} |")
    cost_table='\n'.join(costs)
    counters=['| Case | All / sliced nodes | Flat slice query | Graph build + query | Minimum edits | Candidate checks |',
              '|---|---:|---:|---:|---:|---:|']
    for c in prep['certificates']:
        counters.append(f"| {c['case_id']} | {c['nodes']} / {c['slice_nodes']} | {c['flat_slice_work']['query_visits']} | {c['graph_slice_work']['index_build_units']} + {c['graph_slice_work']['query_visits']} | {c['minimum']['count']} | {c['minimum']['checks']} |")
    counter_table='\n'.join(counters)
    auth='\n'.join(f"- {k}: exact eight-decision vector {v['exact']}/{v['n']}; excess-grant jobs {v['excess_jobs']}; missing-grant jobs {v['missing_jobs']}." for k,v in s['authority'].items())
    errors='\n'.join(f"- {k}: {encode(v).strip().replace(chr(10),' ')}" for k,v in d['failure_buckets'].items())
    money=f"This version: USD{s['incremental_usd']:.9f}; cumulative conservative ledger: USD{s['cumulative_usd']:.9f} / USD20."
    evidence=f"{s['physical_requests']} physical requests; {s['rows']} method outcomes; {s['logical_component_uses']} logical component uses. Statuses: {s['statuses']}."
    actual_en="""The complete-input graph arm did not improve safe completion: Mini 15/24 versus flat 16/24, Luna none 13/24 versus 15/24, and Luna low 23/24 versus 24/24. Sliced graph versus sliced flat was 16/24 versus 16/24, 15/24 versus 16/24, and 23/24 versus 24/24.

There is a narrower repair-placement signal: on the eight unsafe trials, full-graph minimum-edit success rose from 0 to 2 for Luna none and from 6 to 7 for Luna low. It was not consistent across inputs: slicing reversed the Luna-none ordering (graph 1/8, flat 3/8). Mini found no successful two-edit repair in any arm. These are small correlated samples, not proof of a general graph benefit.

Luna low correctly reported every original row field in all five arms (24/24 each), yet graph variants unnecessarily removed explicitly required rows in one authorized trial each. Correct provenance therefore did not ensure correct task interpretation. Deterministic graph and flat tied exactly, reaching 22/24, 16/24 and 24/24 under the three generated contracts; remaining failures were restrictive authority contracts, not unsolved repairs.

Removing raw prose changed full-flat safe completion from 15 to 16 for Mini, 13 to 15 for Luna none, and 24 to 24 for Luna low. The isolated authority generated zero excess-grant jobs in this v7 corpus, so this experiment does not reproduce v6b's mixed-authority contamination result. It tests audit exposure under an already separated authority channel.

Sliced flat input used about 24.9% fewer audit input tokens than full flat. Explicit edges increased full-context input tokens by about 23.6%. These measured context effects are distinct from a claim that graph reasoning is uniquely better. All methods had zero unauthorized activated executions because the verifier blocked incompatible proposals; this does not mean the model audits were all correct."""
    actual_zh="""完整输入下，图方法的安全完成率没有超过无图：Mini为15/24对16/24，Luna none为13/24对15/24，Luna low为23/24对24/24。裁剪后也没有整体优势。

但出现了更窄的信号：危险样本的两处最优修复，Luna none完整图为2/8、完整无图为0/8；Luna low为7/8对6/8。不过裁剪后Luna none反而是图1/8、无图3/8，不能宣称稳定优势。Mini所有方法均未完成两处最优修复。

Luna low五个方法都能准确报告原始记录字段（各24/24），但两个图方法各误删了一次用户明确要求上传的记录。这说明“追踪正确”不等于“知道该不该修改”。确定性图与顺序基线完全相同；分别达到22/24、16/24、24/24，其余失败来自权限合同过度限制。

去掉原始Skill文本后，完整无图的安全完成数由Mini的15变16、Luna none的13变15、Luna low仍为24。改善有限，且本轮独立合同没有出现新增越权授权，不能把它写成再次证明混合权限生成器被攻击。

裁剪让无图审查输入token减少约24.9%；额外显式图边使完整输入增加约23.6%。这些是可测量的工程取舍。所有方法实际越权激活均为0，是验证器拦截的结果，不能据此说模型审查全都正确。"""
    en=f"""# Verified field-flow repair: v7 measured supplement

## Design and scope
The frozen experiment separates four mechanisms: raw Skill prose exclusion, backward relevance slicing, explicit dependency edges, and deterministic verified repair. Two sources each split into two required destinations. A local fix at every sink needs four projections; correctly placed shared-prefix cuts need two. Aggregation changes content class while retaining source lineage. Serialization changes neither content class nor authority.

The graph and nongraph arms receive the same records and trusted semantics. A graph adds only adjacency. Both deterministic solvers have the same search space, goal checker and candidate-policy gate. There is no oracle repair or true policy substituted for a generated contract. True task labels are used for scoring and synthetic complexity certificates only.

Four synthetic contexts, three variants, two repeats and three model settings yield 72 jobs. Each job has five model arms and two deterministic baselines. All model proposals have one call, the same 2400 output-token ceiling and the same per-setting cost envelope. Job/arm order was seeded before measurement. Independent authority receives no Skill prose or action list. All Clean audit arms exclude Skill prose.

## Results
{actual_en}

Safe task completion requires an activated, contract-permitted execution that preserves every required concrete output and causes no unauthorized row submission. Blocking is not task completion. Minimum-edit success additionally requires two edits for unsafe inputs or zero for controls. Row classification concerns the original program, before repair.

{tables}

{evidence}

{auth}

### Paired contrasts
{pairs}

Each comparison has 24 paired uses per setting, but only four context templates. Repeats and variants are correlated. These are descriptive discordances; no statistical equivalence or general superiority is inferred. Classification contrasts and edit histograms are retained in summary.json.

### Deterministic controls and full work accounting
Identical flat/graph repair choices and scored outcomes across all jobs: **{d['deterministic_outcomes_and_edits_equal']}**.

{counter_table}

Query visits alone exclude construction. Graph build counts nodes plus edges; index entries are operation/memory-entry proxies, not measured time or byte memory. Every candidate check uses the same independent concrete interpreter plus sequential symbolic verifier. Full candidate concrete and symbolic node evaluations are retained in each repair.work record, including partially executed invalid candidates. These shared checks must be included in any end-to-end comparison. No graph runtime speedup is claimed.

## Cost and reproduction
{money}

{cost_table}

*Unique component request sets overlap across methods. Each physical cost is divided equally across all recorded component uses, including deterministic baselines. Allocations sum to USD{d['cost_allocation_sum']:.9f}. Unsafe/safe authority requests coincide within a repeat; separate repeats never share requests. The reported logical unshared costs support standalone-arm comparisons. Token counts are provider usage, not cost-envelope reservations.

Run from repository root after installing requirements.lock:

    python -m unittest discover -s tests_v7
    python -m research_v7.reproduce
    python -m scripts.report_v7 --verify

Offline replay reconstructs fixtures, certificates, every request identity, output parse, outcome, aggregate and evidence hash without a key. Measurement source commit: {d['source']['source_commit']}. Prior studies remain unchanged.

## Failure decomposition
{errors}

proposal_safe and goal in raw rows describe the proposed field projection under true-task scoring, even when the model chose deny. They must not be interpreted as executed success; joint, activated and unsafe_execution are the execution metrics.

Strict row-field accuracy combines dataflow understanding with output-interface compliance. Mini sometimes returned required aggregate fields in rows_at_sinks while describing them as aggregates in its prose; this is a reporting mismatch, not evidence that every such case involved wrong flow reasoning. The diagnostics separately count aggregate fields reported as rows, omitted actual row fields and lists matching the required-output schema. None of these post-hoc diagnostics changes the frozen primary score. See the evidence-linked case study.

## Interpretation and limitations
Report graph-edge effects only from FullFlatClean versus FullGraphClean and SliceFlatClean versus SliceGraphClean. Report prose exclusion from FullFlatRaw versus FullFlatClean. FullFlatClean versus SliceFlatClean isolates removal of irrelevant records; this is not uniquely graph-based because a reverse sequential scan computes exactly the same slice.

The deterministic baseline establishes what a trusted closed interpreter and repair search can do. Its success is not evidence of graph-specific intelligence. Differences in model completion and minimum-edit selection are separate findings. A four-edit safe repair is useful but fails the minimum-edit endpoint. A zero-leak gate that blocks everything also fails utility.

These inputs are already complete declared IR, not arbitrary Skill code. Hidden actions, dynamic control flow, external tool semantics, races, extraction mistakes and production enforcement are outside scope. The four contexts share one topology family; there are no independent human labels or real deployments. All variants are disclosed, including controls and failures. No outcome-dependent sample selection occurred.

The authority interface supplies opaque sink IDs and a task referring to their corresponding destinations, without a source-to-destination binding table. Permissions are uniform across all four sinks in this corpus, but the interface does not test precise resource binding and may contribute to conservative interpretation. Observed under-grant counts are mismatches to the authored task contract, not a demonstrated causal diagnosis of the model.

## Relation to prior systems
Task-only authority overlaps with [Progent](https://arxiv.org/html/2504.11703v3), and executable provenance/enforcement overlaps with [CaMeL](https://arxiv.org/html/2503.18813v2). [ActionGuard](https://arxiv.org/html/2609.39450) motivates exclusion of raw Skill prose from a reviewer, while [ActGov](https://arxiv.org/html/2609.24446) already separates bounded semantic extraction from deterministic governance. [SkillScope](https://arxiv.org/html/2605.05868v3) already studies skill graphs and localized repair. These are related mechanisms, not full systems reimplemented by this benchmark.

The defensible contribution is a controlled decomposition with an equally capable nongraph baseline, concrete utility verification and multi-site minimum-edit certificates. Do not claim invention of task isolation, information-flow tracking, graph repair or deterministic enforcement. A larger independent workflow corpus and arbitrary-code extraction study are needed before a deployment claim.
"""
    zh=f"""# V7：字段级数据流、相关性裁剪与可验证修复

这轮把“图”拆成可以单独检验的机制：隔离原始 Skill 文本、移除无关步骤、显式提供依赖边，以及用确定性执行验证修复。所有结果均来自冻结后的完整实验，没有按结果删样本。

## 设计升级
两个独立数据源各自分叉到两个出口，共四个出口。每个出口都必须保留对应汇总值。逐个出口删原始记录需要四处修改；找对共享上游位置只需两处；删掉汇总所需输入则任务失败。保留数据来源不等于仍包含原始记录，真实聚合和仅做序列化被明确区分。

无图方法拥有相同的完整事实、工具语义、修改位置、验证器、调用次数和输出上限。裁剪同样可以通过反向顺序扫描得到，不能把裁剪收益全部归给图。图的增量贡献只看有边/无边的匹配对照。

## 实测结果
{actual_zh}

各模型每种方法共24次，危险、安全、真实授权各8次。“安全完成”要求通过候选权限合同、保留全部输出，并且没有违背真实任务的上传；单纯阻断不算成功。“最少修改”要求危险样本两处，正常对照零处。

{tables}

{evidence}

权限合同的八个布尔决策正确性：

{auth}

## 配对差异
右侧独有成功与左侧独有成功分别列出，不只看总分：

{pairs}

样本只有四个合成模板，重复运行不是新的独立任务；不能把相同分数写成已经证明两者等效，也不能将小幅差异直接推广。

Mini的严格字段报告分数还混入接口理解问题：它有时把需要输出的汇总字段填进“原始记录字段”列表，理由中却正确称其为汇总。因此不能把低分全部解释成数据流推理失败。诊断文件分别记录这些可观测错误模式，未修改正式评分。

## 图的计算价值如何解释
顺序与图基线在全部任务上选择相同修复且得分相同：**{d['deterministic_outcomes_and_edits_equal']}**。图可能少访问节点，但建图需要额外工作。所有候选修复都经过相同的具体执行和符号检查，相关成本已完整记录，未只展示图遍历次数。

{counter_table}

这里是操作计数和索引条目数，不是运行时间或字节内存测量，因此不声称图加速。更多工程价值可能来自重复查询、增量更新或解释接口，这轮没有测试这些能力。

## 论文应怎样定位
贡献应聚焦于：把授权来源、字段内容、相关性裁剪和修复验证分开比较；使用能力相同的无图基线；区分“阻断泄露”“保持任务”和“最少修改”。图是否提高模型成绩，以本轮匹配结果为准。

独立任务授权、数据来源追踪、图辅助修复及确定性门控都有现有工作，不能分别宣称首创。参考 Progent、CaMeL、ActionGuard、ActGov 和 SkillScope 的关系说明见英文报告。我们不是这些完整系统的复现，不能把局部对照写成击败它们。

局限：输入已经是完整的声明式操作，不是对任意 Skill 代码的可靠提取；工具语义可信；没有动态分支、隐藏操作、真实网络执行、独立人工标注或真实部署评估。四个场景共享一种拓扑家族。当前结论必须限制在这些条件内。

权限生成器只看到不透明出口ID及任务，没有单独的来源—目的地绑定表。本轮四个出口的权限要求相同，仍可评分，但它不检验精细资源绑定，也不能排除接口信息不足影响保守拒绝。

## 费用与复现
本轮保守计费 **USD{s['incremental_usd']:.9f}**；历史累计 **USD{s['cumulative_usd']:.9f} / USD20**。

复现无需模型密钥。安装固定依赖后运行 research_v7.reproduce 与 scripts.report_v7 --verify，即可核对全部请求、评分、汇总和证据哈希。原始论文与旧实验保持原样，本报告是新版本补充材料。
"""
    return {'findings.md':en,'findings.zh.md':zh,'diagnostics.json':encode(d),'case-study.md':case_study(rows)}
def figures(s):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({'font.size':9,'font.family':'DejaVu Sans','pdf.fonttype':42})
    fig,axes=plt.subplots(2,3,figsize=(14,7),layout='constrained')
    colors=['#989898','#3e729d','#e5a241','#4a9981','#ba6666','#56724b','#77618f']
    for col,setting in enumerate(SETTINGS):
        for row,(variant,metric,denom,title) in enumerate([('all','joint',24,'Safe task completion /24'),('unsafe','optimal_joint',8,'Minimum-edit safe repair /8')]):
            vals=[next(g for g in s['groups'] if g['setting']==setting and g['variant']==variant and g['method']==m)[metric] for m in METHODS]
            ax=axes[row,col];ax.barh(range(7),vals,color=colors)
            ax.set_yticks(range(7),LABELS if col==0 else ['']*7);ax.invert_yaxis()
            ax.set_xlim(0,denom+1);ax.set_xticks(range(0,denom+1,4 if denom==24 else 2))
            ax.set_title(setting+'\n'+title);ax.grid(axis='x',alpha=.2)
            for y,v in enumerate(vals):ax.text(v+.15,y,str(v),va='center',fontsize=8)
    for ext in ('png','pdf'):
        kw={'dpi':180} if ext=='png' else {'metadata':{'CreationDate':None,'ModDate':None}}
        fig.savefig(REPORT/('outcomes.'+ext),**kw)
    plt.close(fig)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--verify',action='store_true');args=ap.parse_args()
    s,rows,records=load();d=diagnostics(s,rows,records);docs=documents(s,rows,records,d)
    REPORT.mkdir(parents=True,exist_ok=True)
    if not args.verify:
        for name,content in docs.items():(REPORT/name).write_text(content,encoding='utf-8',newline='\n')
        figures(s)
        paths=[REPORT/name for name in docs]+[REPORT/'outcomes.png',REPORT/'outcomes.pdf',Path(__file__)]
        manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        (REPORT/'manifest.json').write_text(encode(manifest),encoding='utf-8',newline='\n')
    else:
        for name,content in docs.items():
            if (REPORT/name).read_text(encoding='utf-8')!=content:raise RuntimeError('Report mismatch '+name)
        manifest=json.loads((REPORT/'manifest.json').read_text(encoding='utf-8'))
        for name,digest in manifest.items():
            if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('Report hash mismatch '+name)
    print('Verified reports' if args.verify else 'Generated reports and figures')
if __name__=='__main__':main()
