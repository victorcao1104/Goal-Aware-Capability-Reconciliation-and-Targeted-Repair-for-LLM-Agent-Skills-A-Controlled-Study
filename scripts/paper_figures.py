"""Typesetting pass: same frozen metrics, legends outside plotted bars."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    root=Path(__file__).resolve().parent.parent
    rows=json.loads((root/'results/summary/summary.json').read_text())['metrics']
    rows={(r['campaign'],r['mode'],r['method']):r for r in rows}
    out=root/'paper/figures'
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'ps.fonttype':42})
    methods=['B0','B1','B2','B2P','B2R','B3','B4','B5']
    def vals(mode,names,key):
        return [rows[('formal-v1',mode,n)][key] if rows[('formal-v1',mode,n)][key] is not None else np.nan for n in names]
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.7),sharey=True)
    x=np.arange(len(methods))
    for ax,mode,title in zip(axes,('agent','scripted'),('Live Luna plans','Deterministic stress replay')):
        ax.bar(x-.18,vals(mode,methods,'asr'),.36,color='#bb5544',label='Attack success')
        ax.bar(x+.18,vals(mode,methods,'tsr'),.36,color='#367b98',label='Task success')
        for i,n in enumerate(methods):
            if any(rows[('formal-v1',mode,n)][k] is None for k in ('asr','tsr')):
                ax.text(i,.04,'N/A',rotation=90,ha='center',fontsize=7)
        ax.set_xticks(x,methods,rotation=35)
        ax.set_ylim(0,1.05)
        ax.set_yticks([0,.25,.5,.75,1])
        ax.set_title(title)
        ax.grid(axis='y',alpha=.22)
        ax.set_axisbelow(True)
        ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('Observed proportion')
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.5,1.05))
    fig.tight_layout(rect=(0,0,1,.9))
    for extension in ('pdf','png'):
        fig.savefig(out/('security-utility.'+extension),bbox_inches='tight',dpi=220)
    plt.close(fig)
    methods=['B5','NO_TASK','NO_FLOW','NO_REPAIR','PLAN_ONLY','SCOPE_INSPIRED']
    fig,ax=plt.subplots(figsize=(3.45,2.9))
    x=np.arange(len(methods))
    ax.barh(x-.17,vals('scripted',methods,'asr'),.34,color='#bb5544',label='Attack success')
    ax.barh(x+.17,vals('scripted',methods,'joint_repair_success'),.34,color='#367b98',label='Joint success')
    ax.set_yticks(x,['Full','No task','No source flow','No repair','Advice only','Scope inspired'])
    ax.invert_yaxis()
    ax.set_xlim(0,1.05)
    ax.set_xticks([0,.5,1])
    ax.spines[['top','right']].set_visible(False)
    for i,n in enumerate(methods):
        if any(rows[('formal-v1','scripted',n)][k] is None for k in ('asr','joint_repair_success')):
            ax.text(.04,i,'N/A',fontsize=7)
    ax.set_xlabel('Observed proportion; stress replay only',fontsize=8)
    ax.legend(loc='lower left',bbox_to_anchor=(-.65,1.02),ncol=2,frameon=False,fontsize=7)
    fig.tight_layout()
    for extension in ('pdf','png'):
        fig.savefig(out/('ablations.'+extension),bbox_inches='tight',dpi=220)
    plt.close(fig)


if __name__=='__main__':
    main()
