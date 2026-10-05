"""Browser-free rendering of the same diagram data; no models, gateway or network."""
from pathlib import Path
import html
import re
import shutil
import subprocess
import textwrap
import yaml

HERE = Path(__file__).resolve().parent
OUT = HERE/'png'

def wrap(value, width=66):
    return '<BR ALIGN="LEFT"/>'.join(html.escape(s) for s in textwrap.wrap(str(value),width=width))

def table(title, desc='', note='', width=650):
    rows = ['<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="19"><B>'+wrap(title,52)+'</B></FONT></TD></TR>']
    if desc: rows.append('<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="15">'+wrap(desc)+'</FONT></TD></TR>')
    if note: rows.append('<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="13" COLOR="#475569">'+wrap(note)+'</FONT></TD></TR>')
    return '<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="8" WIDTH="'+str(width)+'">'+''.join(rows)+'</TABLE>'

def node(key, title, desc='', note='', color='#94a3b8', fill='#ffffff', planned=False):
    style = 'rounded,filled,dashed' if planned else 'rounded,filled'
    return key+' [shape=box,style="'+style+'",color="'+color+'",fillcolor="'+fill+'",label=<'+table(title,desc,note)+'>];'

def base():
    return ['digraph G {','graph [rankdir=TB,bgcolor="white",pad="0.3",ranksep="0.20",nodesep="0.3",fontname="Helvetica"];',
            'node [fontname="Helvetica",penwidth=1.8,margin="0.02"];','edge [color="#94a3b8",arrowsize=0.55];']

def emit(name, lines):
    dot = OUT/(name+'.dot'); dot.write_text('\n'.join(lines+['}']))
    subprocess.run(['dot','-Tpng','-Gdpi=150',str(dot),'-o',str(OUT/(name+'.png'))],check=True)
    print('wrote diagrams/png/'+name+'.png (Graphviz)')

def department(key,d):
    lines=base()
    lines.append(node('title',d['title'],d['meta'],'Department capability: '+d['capability_status'].title(),color=d['color'],fill=d['tint'],planned=d['capability_status']=='planned'))
    lines.append(node('start','Starting point',d['start']))
    lines.append('title->start [style=invis];')
    prev='start';number=0
    for i,s in enumerate(d['stages']):
        name='stage'+str(i)
        if 'approval' in s:
            lines.append(node(name,'Owner approval required',s['approval'],'Operating policy; executor enforcement is planned',color='#f59e0b',fill='#fffbeb'))
        else:
            number+=1;status=s['capability_status']
            approval=s['approval_required'];color='#f59e0b' if approval else d['color']
            fill='#fffbeb' if approval else '#ffffff' if status=='planned' else d['tint']
            notes=[status.title()]
            if s.get('tag'): notes.append(s['tag'])
            if approval:notes.append('Owner approval required')
            lines.append(node(name,str(number)+'  '+s['name'],s.get('desc',''),' · '.join(notes),color=color,fill=fill,planned=status=='planned'))
        lines.append(prev+'->'+name+';');prev=name
    if d.get('outcomes'):
        desc='; '.join(o['name']+(': '+o['note'] if o.get('note') else '') for o in d['outcomes'])
        lines.append(node('outcomes','Decision outcomes',desc,color=d['color'],fill=d['tint']))
        lines.append(prev+'->outcomes;');prev='outcomes'
    lines.append(node('record','The work record links',', '.join(d['carries']),d.get('extra','')))
    lines.append(prev+'->record [style=invis];')
    lines.append(node('legend','Capability and approval are separate','Planned: not implemented or verified. Configured: setup exists. Verified: recorded live evidence. Amber: owner approval required.'))
    lines.append('record->legend [style=invis];')
    emit(key,lines)

def roles():
    source=(HERE/'html/roles-vs-tasks.html').read_text()
    lines=base()
    lines.append(node('title','Roles vs. tasks','Same lifecycle. The work record preserves context; specialist sessions handle execution.'))
    roles=[html.unescape(re.sub('<[^>]+>','',x)) for x in re.findall(r'<div class="r">(.*?)</div>',source,re.S)]
    lines.append(node('roles','Role-based coordination',' → '.join(roles),'Illustrative responsibilities; the lifecycle does not prescribe these five roles.'))
    lines.append('title->roles [style=invis];')
    lines.append(node('context','Task-centered coordination','One authoritative record links requirements, decisions, checks, artifacts and next action.'))
    lines.append('roles->context [style=invis];')
    prev='context'
    rows=re.findall(r'<div class="t([^\"]*)"><div class="n">([^<]+)</div><div class="c">(.*?)</div></div>',source,re.S)
    for i,(classes,name,contents) in enumerate(rows):
        tags=[html.unescape(re.sub('<[^>]+>','',t)) for t in re.findall(r'<span class="p[^\"]*">(.*?)</span>',contents,re.S)]
        planned='planned' in classes;approval='gate' in classes
        key='task'+str(i)
        lines.append(node(key,name,'; '.join(tags),('Planned' if planned else 'Configured')+(' · owner approval required' if approval else ''),color='#f59e0b' if approval else '#3b82f6',fill='#fffbeb' if approval else '#eff6ff',planned=planned))
        lines.append(prev+'->'+key+';');prev=key
    lines.append(node('legend','Intended access and separate assessment','Worker routing and access enforcement are planned. A fresh session alone does not guarantee independent judgment. Amber: artifact-specific owner approval.'))
    lines.append(prev+'->legend [style=invis];')
    emit('roles-vs-tasks',lines)

def render(selected):
    if not shutil.which('dot'):raise RuntimeError('Graphviz is required for --engine graphviz')
    OUT.mkdir(exist_ok=True)
    data=yaml.safe_load((HERE/'departments.yaml').read_text())['departments']
    for key in selected or list(data)+['roles-vs-tasks']:
        if key in data:department(key,data[key])
        elif key=='roles-vs-tasks':roles()
        else:raise ValueError('Graphviz cannot render unknown figure '+key)
