"""Original rounded-card visual style, rendered as SVG/PNG without a browser.

Requires PyYAML and rsvg-convert (librsvg). The SVG files remain editable.
"""
from pathlib import Path
import html
import re
import shutil
import subprocess
import yaml

HERE = Path(__file__).resolve().parent
OUT = HERE / 'png'

def width(text, size, bold=False):
    # Conservative Arial advances for wrapping; allow extra breathing room.
    return sum((.28 if c in ' il.,:;!\'|()' else .85 if c in 'MW@%' else
                .64 if c.isupper() else .56) * size for c in text) * (1.03 if bold else 1)

def pale(color):
    return '#' + ''.join(f'{round(int(color[i:i+2],16)*.35+255*.65):02x}' for i in (1,3,5))

def wrap(text, max_width, size, bold=False):
    lines = []; line = ''
    for word in str(text).split():
        candidate = (line + ' ' + word).strip()
        if line and width(candidate, size, bold) > max_width:
            lines.append(line); line = word
        else: line = candidate
    if line: lines.append(line)
    return lines

class Figure:
    def __init__(self): self.parts = []
    def rect(self, x,y,w,h,fill='#fff',stroke='#e2e8f0',radius=12,dash=False,sw=2):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')
    def text(self, x,y,text,size=18,color='#334155',bold=False,anchor='start'):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{html.escape(str(text))}</text>')
    def lines(self,x,y,text,max_width,size=18,color='#334155',bold=False):
        lines=wrap(text,max_width,size,bold)
        for i,line in enumerate(lines): self.text(x,y+i*size*1.4,line,size,color,bold)
        return len(lines)*size*1.4
    def pill(self,x,y,text,size=14.5,fill='#fff',stroke='#cbd5e1',color='#334155',bold=False):
        w=width(text,size,bold)+22
        self.rect(x,y,w,26,fill,stroke,13,sw=1)
        self.text(x+11,y+18,text,size,color,bold)
        return w
    def pills(self,x,y,items,max_width,size=14.5):
        start=x
        for text,fill,stroke,color,bold in items:
            w=width(text,size,bold)+22
            if x>start and x+w>start+max_width: x=start;y+=33
            x+=self.pill(x,y,text,size,fill,stroke,color,bold)+7
        return y+26
    def save(self,name,height):
        OUT.mkdir(exist_ok=True)
        svg=OUT/(name+'.svg')
        svg.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="{height}" viewBox="0 0 720 {height}" font-family="Arial, Helvetica, sans-serif"><rect width="100%" height="100%" fill="white"/>'+''.join(self.parts)+'</svg>')
        subprocess.run(['rsvg-convert','--zoom','2',str(svg),'-o',str(OUT/(name+'.png'))],check=True)
        print('wrote diagrams/png/'+name+'.png (original card style)')

def item(text,fill='#fff',stroke='#cbd5e1',color='#334155',bold=False):
    return text,fill,stroke,color,bold

def department(key,d):
    f=Figure(); c=d['color']; tint=d['tint']
    f.text(58,64,d['title'],31,c,True)
    y=88
    y+=f.lines(58,y,d['meta'],616,16,'#475569')
    f.text(58,y+3,'Department capability: '+d['capability_status'].title(),14,'#64748b');y+=24
    f.rect(34,34,8,y-34,c,c,0,sw=0)
    start_h=len(wrap(d['start'],622,18))*25.2+24
    f.rect(34,y+12,652,start_h,'#f8fafc','#e2e8f0',10,sw=1)
    f.lines(48,y+37,d['start'],622,18)
    y+=start_h+32
    timeline_start=y+24; circles=[];n=0
    for s in d['stages']:
        if 'approval' in s:
            h=len(wrap('My approval. '+s['approval'],554,17.5))*24.5+24
            f.rect(98,y,588,h,'#fef3c7','#f59e0b',10)
            f.lines(112,y+27,'My approval. '+s['approval'],554,17.5,'#92400e')
            y+=h+14;continue
        n+=1;planned=s['capability_status']=='planned';approval=s['approval_required']
        box_color='#f59e0b' if approval else '#94a3b8' if planned else pale(c)
        fill='#fffbeb' if approval else '#fff' if planned else tint
        start_index=len(f.parts)
        f.text(114,y+30,s['name'],23,'#0f172a',True)
        tags=[item(s['capability_status'].title(),stroke='#94a3b8')]
        if s.get('tag'):tags.append(item(s['tag']))
        if approval:tags.append(item('Owner approval','#fef3c7','#f59e0b','#92400e',True))
        tx=114+width(s['name'],23,True)+12
        if tx+width(tags[0][0],14.5)+22>670:tx=114;ty=y+44
        else:ty=y+8
        end=f.pills(tx,ty,tags,670-tx)
        desc_y=max(y+56,end+24)
        desc_h=f.lines(114,desc_y,s.get('desc',''),556,18.5)
        h=max(80,desc_y-y+desc_h-18.5+15)
        content=f.parts[start_index:];del f.parts[start_index:]
        f.rect(98,y,588,h,fill,box_color,12,planned)
        f.parts.extend(content)
        circles.append((y+24,n,planned,approval));y+=h+14
    if circles:
        f.parts.insert(0,f'<path d="M58 {timeline_start} V{circles[-1][0]+24}" stroke="{c}" opacity=".35" stroke-width="3"/>')
    for cy,n,planned,approval in circles:
        color='#f59e0b' if approval else c
        f.parts.append(f'<circle cx="58" cy="{cy}" r="23" fill="{color if approval or not planned else "white"}" stroke="{color}" stroke-width="3"'+(' stroke-dasharray="6 4"' if planned else '')+'/>')
        f.text(58,cy+7,n,21,'white' if approval or not planned else c,True,'middle')
    if d.get('outcomes'):
        for i,o in enumerate(d['outcomes']):
            if i==0:
                note_h=len(wrap(o.get('note',''),560,15.5))*21.7
                f.rect(98,y,588,49+note_h,'#fff',c,10)
                f.text(111,y+26,o['name'],18,c,True)
                f.lines(111,y+49,o.get('note',''),560,15.5,'#475569');y+=61+note_h
            else:
                x=98+(i-1)*200
                f.rect(x,y,188,58,'#fff',c,10)
                f.lines(x+12,y+25,o['name'],164,16,'#334155',True)
        y+=72
    f.parts.append(f'<path d="M34 {y} H686" stroke="#e2e8f0"/>');y+=29
    f.text(34,y,'THE CARD CARRIES',15,'#64748b',True);y+=13
    y=f.pills(34,y,[item(x,'#f1f5f9','#e2e8f0','#0f172a') for x in d['carries']],652,16.5)+15
    if d.get('extra'):y+=f.lines(34,y+15,d['extra'],652,17)+10
    y+=f.lines(34,y+16,'Planned: not implemented or verified · Configured: setup exists',652,14.5,'#64748b')
    y+=f.lines(34,y+16,'Verified: recorded live evidence · Amber: owner approval required',652,14.5,'#64748b')
    f.save(key,int(y+35))

def roles():
    source=(HERE/'html/roles-vs-tasks.html').read_text();f=Figure()
    f.text(34,64,'Roles vs. tasks',31,'#0f172a',True)
    y=86+f.lines(34,86,'Same lifecycle. The work record preserves context; specialist sessions handle execution.',652,18,'#475569')+24
    begin=len(f.parts);top=y
    f.text(54,y+32,'ROLE-BASED COORDINATION',15,'#475569',True);y+=50
    labels=['Business analyst','Architect','Developer','QA','Release manager']
    for i,label in enumerate(labels):
        x=54+i*126;f.rect(x,y,94,70,'#fff','#cbd5e1',10)
        lines=wrap(label,84,17,True)
        for j,line in enumerate(lines):f.text(x+47,y+34-(len(lines)-1)*10+j*21,line,17,'#0f172a',True,'middle')
        if i<4:f.text(x+109,y+43,'→',24,'#94a3b8',True,'middle')
    y+=91
    y+=f.lines(54,y,'An illustrative role arrangement. Roles carry expertise and accountability; the lifecycle itself does not prescribe these five roles.',612,17.5)
    y+=15;contents=f.parts[begin:];del f.parts[begin:]
    f.rect(34,top,652,y-top,'#f8fafc','#e2e8f0',14);f.parts.extend(contents);y+=24
    begin=len(f.parts);top=y
    y+=32
    y+=f.lines(54,y,'TASK-CENTERED COORDINATION AND SPECIALIST EXECUTION',612,15,'#1d4ed8',True)+9
    f.rect(54,y,612,87,'#fff','#2563eb',12)
    f.text(70,y+29,'One authoritative record links the artifacts',19,'#0f172a',True)
    f.pills(70,y+42,[item(x,'#f1f5f9','#e2e8f0') for x in ['requirements','decisions','checks','next action']],578,15.5)
    y+=101
    rows=re.findall(r'<div class="t([^\"]*)"><div class="n">([^<]+)</div><div class="c">(.*?)</div></div>',source,re.S)
    for classes,name,contents in rows:
        tags=re.findall(r'<span class="p([^\"]*)">(.*?)</span>',contents,re.S)
        start=len(f.parts);f.text(68,y+28,name,19,'#0f172a',True)
        pills=[]
        for cls,text in tags:
            if 'm' in cls:
                pills.append(item(html.unescape(text),'#fef3c7' if 'gate' in classes else '#eff6ff','#f59e0b' if 'gate' in classes else '#93c5fd','#92400e' if 'gate' in classes else '#1e3a8a'))
            elif 'i' in cls:pills.append(item(html.unescape(text),'#f5f3ff','#a78bfa','#4c1d95',True))
            else:pills.append(item(html.unescape(text)))
        end=f.pills(180,y+10,pills,472,15);h=end-y+12
        contents=f.parts[start:];del f.parts[start:]
        gate='gate' in classes
        f.rect(54,y,612,h,'#fffbeb' if gate else '#fff','#f59e0b' if gate else '#94a3b8' if 'planned' in classes else '#bfdbfe',10,'planned' in classes)
        f.parts.extend(contents);y+=h+9
    y+=9;contents=f.parts[begin:];del f.parts[begin:]
    f.rect(34,top,652,y-top,'#eff6ff','#bfdbfe',14);f.parts.extend(contents)
    y+=30
    y+=f.lines(34,y,'Worker routing and access enforcement are planned. A fresh session alone does not guarantee independent judgment.',652,17.5)+15
    y=f.pills(34,y,[item('Model or worker','#eff6ff','#93c5fd'),item('Intended access'),item('Separate assessment','#f5f3ff','#a78bfa'),item('Dashed: planned'),item('Amber: my approval','#fef3c7','#f59e0b','#92400e')],652,14.5)
    f.save('roles-vs-tasks',int(y+30))

def render(selected):
    if not shutil.which('rsvg-convert'):raise RuntimeError('Install librsvg for --engine cards')
    data=yaml.safe_load((HERE/'departments.yaml').read_text())['departments']
    for key in selected or list(data)+['roles-vs-tasks']:
        if key in data:department(key,data[key])
        elif key=='roles-vs-tasks':roles()
        else:raise ValueError('Unknown diagram '+key)
