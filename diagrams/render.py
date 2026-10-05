# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6", "playwright>=1.40"]
# ///
"""Render the diagrams in this folder to PNGs in diagrams/png/.

  departments.yaml  -> one workflow diagram per department
  html/*.html       -> standalone figures (screenshot of the #card element)
  overview.dot      -> the architecture diagram (needs Graphviz)

Usage (from the repo root):
    uv run diagrams/render.py                    # everything
    uv run diagrams/render.py writing media      # only these departments
    uv run diagrams/render.py roles-vs-tasks     # only this html figure
    uv run diagrams/render.py --keep-html        # also keep generated department HTML

First run only: install the headless browser Playwright uses:
    uv run --with playwright playwright install chromium

The overview diagram (overview.dot) needs Graphviz (`brew install graphviz`).
It's skipped with a note if `dot` isn't installed.
"""
from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DATA = HERE / "departments.yaml"
PAGES = HERE / "html"
OUT = HERE / "png"
WIDTH = 720  # CSS px; rendered at 2x for sharp text on Medium and GitHub

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#fff;font-family:Inter,-apple-system,"SF Pro Text","Segoe UI",system-ui,sans-serif;color:#0f172a}
.card{width:%(w)spx;padding:34px 34px 26px;background:#fff}
.head{border-left:8px solid var(--c);padding:2px 0 2px 16px;margin-bottom:16px}
.title{font-size:31px;font-weight:700;letter-spacing:-.01em;color:var(--c)}
.meta{overflow-wrap:anywhere;font-size:16px;color:#475569;margin-top:4px;font-family:ui-monospace,"SF Mono",Menlo,"DejaVu Sans Mono",monospace}
.start{font-size:18px;color:#334155;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:10px 14px;margin:0 0 18px}
ol{list-style:none;margin:0;padding:0;position:relative}
ol::before{content:"";position:absolute;left:23px;top:18px;bottom:18px;width:3px;background:var(--c);opacity:.35;border-radius:2px}
li{position:relative;display:flex;gap:16px;align-items:flex-start;margin:0 0 12px}
.num{flex:0 0 48px;height:48px;border-radius:50%%;background:var(--c);color:#fff;font-weight:700;font-size:21px;display:flex;align-items:center;justify-content:center;position:relative;z-index:1;border:3px solid var(--c)}
.box{flex:1;background:var(--tint);border:2px solid color-mix(in srgb,var(--c) 35%%,white);border-radius:12px;padding:10px 16px 11px}
.name{font-size:23px;font-weight:650;display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px}
.desc{font-size:18.5px;line-height:1.38;color:#334155;margin-top:3px}
.tag{font-size:14.5px;font-weight:550;color:#334155;background:#fff;border:1.5px solid #cbd5e1;border-radius:999px;padding:2px 10px}
li.planned .num{background:#fff;color:var(--c);border-style:dashed}
li.planned .box{background:#fff;border-style:dashed;border-color:#94a3b8}
.status-tag{font-size:13px;font-weight:650;border:1px solid #94a3b8;border-radius:5px;padding:2px 7px;background:#fff;color:#475569}.status-tag.verified{border-color:#16a34a;color:#166534;background:#f0fdf4}
li.requires-approval .num{background:#f59e0b;border-color:#f59e0b}
li.requires-approval .box{background:#fffbeb;border-color:#f59e0b}
li.requires-approval .tag{border-color:#f59e0b;color:#92400e;background:#fef3c7}
li.approval{margin:2px 0 14px 64px;display:block}
.gr{font-size:17.5px;line-height:1.4;color:#78350f;background:#fef3c7;border:2px solid #f59e0b;border-radius:10px;padding:9px 14px}
.gr b{color:#92400e}
li.outcomes{display:block;margin:0}
.oc-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin:2px 0 14px 64px}
.oc{border:2px solid color-mix(in srgb,var(--c) 45%%,white);background:#fff;border-radius:10px;padding:8px 12px;font-size:18px;font-weight:600}
.oc span{display:block;font-weight:400;font-size:15.5px;color:#475569;margin-top:2px}
.oc.wide{grid-column:1 / -1}
.carries{margin-top:16px;border-top:1px solid #e2e8f0;padding-top:14px;font-size:16px;color:#475569}
.carries b{display:block;font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:#64748b;margin-bottom:8px}
.chip{display:inline-block;font-size:16.5px;color:#0f172a;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:999px;padding:3px 12px;margin:0 6px 7px 0}
.extra{font-size:17px;color:#334155;margin-top:6px}
.legend{margin-top:12px;font-size:14.5px;color:#64748b;display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center}
.lg{display:inline-flex;align-items:center;gap:7px}
.sw{width:22px;height:14px;border-radius:4px;display:inline-block}
""" % {"w": WIDTH}

VALID_STATUS = {"planned", "configured", "verified"}


def esc(value) -> str:
    return html.escape(str(value))


def validate(key: str, d: dict) -> None:
    for field in ("title", "color", "tint", "meta", "start", "stages", "carries", "capability_status"):
        if field not in d:
            sys.exit(f"departments.yaml: '{key}' is missing '{field}'")
    if d["capability_status"] not in VALID_STATUS:
        sys.exit(f"departments.yaml: {key} has invalid department capability status")
    for i, s in enumerate(d["stages"], 1):
        if "approval" in s:
            continue
        if "name" not in s:
            sys.exit(f"departments.yaml: '{key}' stage #{i} needs 'name' (or 'approval')")
        status = s.get("capability_status")
        if not isinstance(s.get("approval_required"), bool):
            sys.exit(f"departments.yaml: {key} stage #{i} needs boolean approval_required")
        if status == "verified" and not s.get("evidence"):
            sys.exit(f"departments.yaml: {key} stage #{i} needs evidence before Verified")
        if status not in VALID_STATUS:
            sys.exit(f"departments.yaml: '{key}' stage '{s['name']}' has status '{status}'; "
                     f"use one of {sorted(VALID_STATUS)}")


def build_html(d: dict) -> str:
    rows, n = [], 0
    for s in d["stages"]:
        if "approval" in s:
            rows.append(f'<li class="approval"><div class="gr"><b>My approval.</b> {esc(s["approval"])}</div></li>')
            continue
        n += 1
        status = s.get("capability_status")
        cls = status + (" requires-approval" if s["approval_required"] else "")
        status_badge = f'<span class="status-tag {status}">{status.title()}</span>'
        approval_badge = '<span class="tag">Owner approval</span>' if s["approval_required"] else ""
        tag = f'<span class="tag">{esc(s["tag"])}</span>' if s.get("tag") else ""
        desc = f'<div class="desc">{esc(s["desc"])}</div>' if s.get("desc") else ""
        rows.append(f'<li class="{cls}"><div class="num">{n}</div><div class="box">'
                    f'<div class="name">{esc(s["name"])}{status_badge}{tag}{approval_badge}</div>{desc}</div></li>')

    if d.get("outcomes"):
        boxes = []
        for i, o in enumerate(d["outcomes"]):
            wide = " wide" if i == 0 and o.get("note") else ""
            note = f'<span>{esc(o["note"])}</span>' if o.get("note") else ""
            boxes.append(f'<div class="oc{wide}">{esc(o["name"])}{note}</div>')
        rows.append(f'<li class="outcomes"><div class="oc-grid">{"".join(boxes)}</div></li>')

    chips = "".join(f'<span class="chip">{esc(c)}</span>' for c in d["carries"])
    extra = f'<div class="extra">{esc(d["extra"])}</div>' if d.get("extra") else ""

    legend = [
        '<span class="lg">Planned: not implemented or verified</span>',
        '<span class="lg">Configured: setup exists</span>',
        '<span class="lg">Verified: recorded live evidence</span>',
        '<span class="lg"><span class="sw" style="background:#fef3c7;border:2px solid #f59e0b"></span>Amber: owner approval required</span>',
    ]

    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'<div class="card" id="card" style="--c:{d["color"]};--tint:{d["tint"]}">'
            f'<div class="head"><div class="title">{esc(d["title"])}</div><div class="meta">{esc(d["meta"])}<br>Department capability: {d["capability_status"].title()}</div></div>'
            f'<div class="start">{esc(d["start"])}</div>'
            f'<ol>{"".join(rows)}</ol>'
            f'<div class="carries"><b>The card carries</b>{chips}{extra}</div>'
            f'<div class="legend">{"".join(legend)}</div>'
            f'</div></body></html>')


def render_departments(selected: list[str], keep_html: bool) -> None:
    from playwright.sync_api import Error as PlaywrightError, sync_playwright

    data = yaml.safe_load(DATA.read_text())["departments"]
    pages = {p.stem: p for p in sorted(PAGES.glob("*.html"))} if PAGES.exists() else {}
    unknown = [k for k in selected if k not in data and k not in pages]
    if unknown:
        sys.exit(f"Unknown diagram(s): {', '.join(unknown)}. "
                 f"Known: {', '.join([*data, *pages])}")
    keys = [k for k in selected if k in data] if selected else list(data)
    page_keys = [k for k in selected if k in pages] if selected else list(pages)
    for k in keys:
        validate(k, data[k])

    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except PlaywrightError as error:
            sys.exit("Browser rendering could not launch Chromium: " + str(error) + "\n"
                     "If the browser is absent, install it with official Playwright. "
                     "If browser processes are restricted, use --engine graphviz.")
        page = browser.new_page(viewport={"width": WIDTH + 40, "height": 900}, device_scale_factor=2)
        for k in keys:
            page.set_content(build_html(data[k]))
            page.wait_for_timeout(100)
            out = OUT / f"{k}.png"
            page.locator("#card").screenshot(path=str(out))
            if keep_html:
                (OUT / f"{k}.html").write_text(build_html(data[k]))
            print(f"wrote {out.relative_to(HERE.parent)}")
        for k in page_keys:
            page.goto(pages[k].as_uri())
            page.wait_for_timeout(100)
            out = OUT / f"{k}.png"
            page.locator("#card").screenshot(path=str(out))
            print(f"wrote {out.relative_to(HERE.parent)}")
        browser.close()


def render_overview() -> None:
    src = HERE / "overview.dot"
    if not src.exists():
        return
    if not shutil.which("dot"):
        print("skipped overview.png: Graphviz isn't installed (brew install graphviz)")
        return
    out = OUT / "overview.png"
    OUT.mkdir(exist_ok=True)
    subprocess.run(["dot", "-Tpng", "-Gdpi=150", str(src), "-o", str(out)], check=True)
    print(f"wrote {out.relative_to(HERE.parent)}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Render department workflow diagrams.")
    ap.add_argument("departments", nargs="*",
                    help="department keys from departments.yaml or html/ figure names (default: all)")
    ap.add_argument("--engine", choices=("browser", "graphviz", "cards"), default="browser", help="browser HTML, original-style SVG cards, or Graphviz")
    ap.add_argument("--keep-html", action="store_true", help="also write the generated HTML next to each PNG")
    args = ap.parse_args()
    if args.engine in ("graphviz", "cards"):
        data = yaml.safe_load(DATA.read_text())["departments"]
        for key in args.departments or list(data):
            if key in data:
                validate(key, data[key])
        if args.engine == "cards":
            from card_render import render
        else:
            from graphviz_render import render
        render(args.departments)
    else:
        render_departments(args.departments, args.keep_html)
    if not args.departments:
        render_overview()


if __name__ == "__main__":
    main()
