# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Offline source checks only; never invokes Hermes Agent, models, or a gateway."""
from pathlib import Path
import ast
import importlib.util
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]

def main():
    for source in ROOT.rglob('*.yaml'): yaml.safe_load(source.read_text())
    for source in ROOT.rglob('*.py'): ast.parse(source.read_text())
    spec = importlib.util.spec_from_file_location('diagram_renderer', ROOT/'diagrams/render.py')
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    data = yaml.safe_load((ROOT/'diagrams/departments.yaml').read_text())['departments']
    for key, department in data.items():
        renderer.validate(key, department)
        rendered = renderer.build_html(department)
        for stage in department['stages']:
            if 'approval' in stage: continue
            assert stage['capability_status'].title() in rendered
        assert 'owner approval required' in rendered
    for profile in (ROOT/'departments').glob('*/config.example.yaml'):
        cfg = yaml.safe_load(profile.read_text())
        assert cfg['kanban']['dispatch_in_gateway'] is False
        assert cfg['kanban']['dispatch_profiles'] == []
        if profile.parent.name != 'development': assert cfg['fallback_providers'] == []
    gateway = yaml.safe_load((ROOT/'gateway/config.example.yaml').read_text())
    assert gateway['kanban']['dispatch_in_gateway'] is False
    assert len(gateway['gateway']['profile_routes']) == 2
    for f in [ROOT/'README.md',ROOT/'article/hermes-ai-departments.md']:
        text = f.read_text()
        assert not re.search(r'\bHermes\b(?! Agent)',text)
        assert 'Screenshot to add' not in text
        assert 'installer ready' not in text.lower()
    article = (ROOT/'article/hermes-ai-departments.md').read_text()
    for target in re.findall(r'!\[[^\n]*\]\(([^)]+)\)', article):
        assert (ROOT/'article'/target).is_file()
    assert 'executor_implemented: false' in (ROOT/'workflow/stage-policy.yaml').read_text()
    print('PASS: YAML, Python syntax, diagram statuses, approval labels, model policy, routing structure, article references and scope boundaries.')

if __name__ == '__main__': main()
