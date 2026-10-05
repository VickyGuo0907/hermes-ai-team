"""Editable, exact SVG tool map. Official icons are embedded without recoloring."""
from pathlib import Path
from html import escape
import base64,subprocess
ROOT=Path(__file__).resolve().parent
parts=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1440" height="2050" viewBox="0 0 1440 2050"><rect width="1440" height="2050" fill="white"/><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="5" orient="auto"><path d="M1 1 L7 5 L1 9" fill="none" stroke="#64748b" stroke-width="2"/></marker></defs>']
def text(x,y,s,size=24,color='#475569',weight=400):
 parts.append(f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(s)}</text>')
def box(x,y,w,h,color='#cbd5e1',fill='#f8fafc',dash=False):
 parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{fill}" stroke="{color}" stroke-width="3"'+(' stroke-dasharray="11 8"' if dash else '')+'/>')
def icon(k,x,y,size=48):
 p=next(iter((ROOT/'logos').glob(k+'.png')),None) or next(iter((ROOT/'logos').glob(k+'.svg')),None)
 if p:
  mime='image/svg+xml' if p.suffix=='.svg' else 'image/png';b=base64.b64encode(p.read_bytes()).decode()
  parts.append(f'<image x="{x}" y="{y}" width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet" xlink:href="data:{mime};base64,{b}"/>')
def brand(k,x,y,name,detail=None):
 icon(k,x,y-33,44);text(x+58,y,name,28,'#0f172a',700)
 if detail:text(x+58,y+34,detail,21)
def arrow(y1,y2,dash=False):
 parts.append(f'<path d="M720 {y1} L720 {y2}" stroke="#64748b" stroke-width="3" fill="none" marker-end="url(#arrow)"'+(' stroke-dasharray="9 7"' if dash else '')+'/>')
text(60,78,'My AI team: the tools and the workflow',46,'#0f172a',700)
text(60,119,'A practical setup on my Mac — with explicit handoffs and durable project context.',26)
text(60,176,'1  WHERE I WORK AND CHECK IN',23,'#64748b',700)
box(60,197,425,151);brand('hermes',82,244,'Hermes Agent desktop');text(82,284,'Profiles and boards at my desk',23);text(82,318,'Desktop access is in use',21)
box(507,197,425,151);brand('discord',529,244,'Discord');brand('slack',529,304,'Slack');text(725,303,'Gateway connected',20)
box(954,197,426,151);brand('openai',976,244,'ChatGPT');text(976,285,'Discussion and article editing',23);text(976,318,'Manual workspace, no auto handoff',20)
parts.append('<path d="M719 357 L719 386" stroke="#64748b" stroke-width="3" fill="none" marker-end="url(#arrow)"/>')
text(60,420,'2  HERMES AGENT COORDINATES THE WORK',23,'#64748b',700)
box(60,442,1320,282,'#93b4fb','#eff6ff');brand('hermes',85,492,'Hermes Agent · gateway, profiles, Kanban')
text(85,534,'Development  /  Writing  /  Media  /  Dream Department (discovery-dept)',26,'#2563eb',700)
brand('openai',85,594,'Codex','Development planning; local fallback')
brand('lmstudio',753,594,'LM Studio','Local server: 127.0.0.1:1234/v1')
brand('qwen',753,675,'Qwen','Local drafting, media briefs, idea capture')
text(85,673,'Discord idea read + capture demonstrated',23)
text(85,704,'A coordinator model is separate from a coding worker.',21)
arrow(734,766)
text(60,800,'3  TWO COMPLEMENTARY RECORDS',23,'#64748b',700)
box(60,820,649,179,'#94a3b8','#f1f5f9');text(86,865,'Hermes Agent Kanban',30,'#0f172a',700);text(86,908,'Task status, owner, blocker and next action',24);text(86,945,'Links to approved documents and evidence',24);text(86,979,'One work record; separate project boards',21)
box(731,820,649,179,'#c4a1f5','#faf5ff');brand('obsidian',755,867,'Obsidian · project vaults');text(755,909,'Requirements, plans and decision history',24);text(755,946,'Discussion notes and approved specifications',23);text(755,980,'Manual document handoff; auto sync unverified',21)
arrow(1009,1040,True)
box(60,1070,1320,83,'#f59e0b','#fffbeb');text(87,1118,'MY APPROVAL',27,'#b45309',700);text(321,1118,'Approve the scope and exact artifacts before dispatch or publication.',25)
text(60,1203,'4  EXECUTION OPTIONS — HERMES AGENT DISPATCH IS PLANNED',23,'#64748b',700)
box(60,1224,1320,291,'#94a3b8','#ffffff',True)
brand('orca',88,1277,'Orca + Orca Mobile');text(560,1277,'Remote access works; task-to-worker binding is pending.',24)
box(88,1318,394,146,'#cbd5e1','#f8fafc');brand('claude-app',108,1369,'Claude Code');text(108,1411,'Complex feature implementation',22);text(108,1444,'One writer per branch / worktree',21)
box(503,1318,394,146,'#cbd5e1','#f8fafc');brand('openai',523,1369,'Codex');text(523,1411,'Build or separate verification',22);text(523,1444,'Test the submitted commit',21)
box(918,1318,434,146,'#cbd5e1','#f8fafc');brand('opencode',938,1369,'OpenCode');text(938,1411,'Optional local worker via LM Studio',22);text(938,1444,'Provider / permissions trial pending',21)
text(88,1495,'Git branch → frozen commit → separate verification → my merge / release decision',23)

text(60,1601,'5  CONTENT DESTINATIONS — AUTOMATED PUBLISHING IS PLANNED',23,'#64748b',700)
box(60,1621,1320,219,'#94a3b8','#ffffff',True)
brand('medium',88,1677,'Medium');brand('substack',525,1677,'Substack');brand('x',995,1677,'X')
text(88,1723,'Articles',23);text(525,1723,'Articles and newsletters',23);text(995,1723,'Short posts',23)
text(88,1773,'Video / short-video production tools: still to choose and connect.',25)
text(88,1810,'The Medium draft is edited manually; no department publishes automatically.',23)
box(60,1880,42,24,'#94a3b8','#f8fafc');text(117,1900,'Solid: current tool or configured service',22)
box(720,1880,42,24,'#94a3b8','#fff',True);text(777,1900,'Dashed: planned integration',22)
text(60,1944,'Tool availability does not mean every connection or workflow has passed an end-to-end test.',22)
text(60,1983,'Logos / app icons belong to their respective owners. No endorsement is implied.',20)
text(60,2015,'Setup snapshot: October 2026 · Obsidian is durable context, not automatic model memory.',20)
parts.append('</svg>');out=ROOT/'png/AI_Team_Tools_Architecture.svg';out.write_text('\n'.join(parts));subprocess.run(['rsvg-convert','-o',str(out.with_suffix('.png')),str(out)],check=True)
print(out.with_suffix('.png'))
