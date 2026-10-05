#!/usr/bin/env python3
"""Render this kit's Markdown article as self-contained HTML, using only the standard library."""
from pathlib import Path
import base64
import html
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'article/hermes-ai-departments.md'
OUT = ROOT / 'article/Hermes_Agent_Workforce_Article.html'

def inline(s):
    s = html.escape(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'\[([^\]]+)\]\((\.{1,2}/[^\s)]+)\)', r'\1 (in the source package)', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', s)
    return s.replace('\\[', '[').replace('\\]', ']')

def build():
    lines = SOURCE.read_text().splitlines()
    out = []
    i = 0
    while i < len(lines):
        s = lines[i]
        if not s.strip(): i += 1; continue
        if s.startswith('    ') or s.startswith('```'):
            fenced = s.startswith('```')
            chunk = []
            if fenced: i += 1
            while i < len(lines):
                line = lines[i]
                if fenced and line.startswith('```'): i += 1; break
                if not fenced and line and not line.startswith('    '): break
                chunk.append(line if fenced else line[4:])
                i += 1
            out.append('<pre><code>' + html.escape('\n'.join(chunk).rstrip()) + '</code></pre>')
            continue
        image = re.fullmatch(r'!\[(.*)\]\(([^)]+)\)', s)
        if image:
            path = (SOURCE.parent / image[2]).resolve()
            if not path.is_relative_to(ROOT.resolve()): raise ValueError('Image must belong to the kit')
            data = base64.b64encode(path.read_bytes()).decode()
            out.append('<figure><img alt="'+html.escape(image[1],quote=True)+'" src="data:image/png;base64,'+data+'"></figure>')
            i += 1; continue
        heading = re.match(r'^(#{1,6}) (.*)$', s)
        if heading:
            level = len(heading[1]); out.append(f'<h{level}>'+inline(heading[2])+f'</h{level}>')
            i += 1; continue
        if s == '---': out.append('<hr>'); i += 1; continue
        if s.startswith('> '):
            chunk = []
            while i < len(lines) and lines[i].startswith('> '): chunk.append(lines[i][2:]); i += 1
            out.append('<blockquote>'+inline(' '.join(chunk))+'</blockquote>'); continue
        if s.startswith('- '):
            chunk = []
            while i < len(lines) and lines[i].startswith('- '): chunk.append(lines[i][2:]); i += 1
            out.append('<ul>'+''.join('<li>'+inline(c)+'</li>' for c in chunk)+'</ul>'); continue
        chunk = [s]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^(?:#|```|!\[|> |\- |    )',lines[i]):
            chunk.append(lines[i]); i += 1
        out.append('<p>'+inline(' '.join(chunk))+'</p>')
    css = '''body{margin:0;background:#f5f7fa;color:#182230;font:17px/1.65 system-ui,-apple-system,sans-serif}main{max-width:960px;margin:30px auto;padding:45px;background:white}h1{font-size:36px;line-height:1.2}h2{font-size:26px;line-height:1.3;margin-top:40px}h3{font-size:21px}a{color:#155eaa}pre{background:#f0f4f8;padding:18px;border-radius:8px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px;line-height:1.5}code{font-family:ui-monospace,SFMono-Regular,monospace}p code,li code{background:#f0f4f8;font-size:.9em}figure{margin:25px 0}img{max-width:100%;height:auto;display:block}blockquote{margin:22px 0;border-left:3px solid #7c9bbd;padding:10px 18px;background:#f7f9fc}li{margin-bottom:6px}hr{border:0;border-top:1px solid #dce3eb;margin:35px 0}@media(max-width:700px){main{margin:0;padding:22px}h1{font-size:29px}}@media print{body{background:white}main{margin:0;padding:0}h2,h3{break-after:avoid}figure,pre{break-inside:avoid}}'''
    page = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Building My Own AI Team with Hermes Agent</title><style>'+css+'</style></head><body><main>'+''.join(out)+'</main></body></html>'
    OUT.write_text(page)
    print('Wrote '+str(OUT.relative_to(ROOT)))

if __name__ == '__main__': build()
