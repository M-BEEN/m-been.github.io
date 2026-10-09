"""Check the learning publication boundary and inspect the built output.

This validates structure and reproducible examples, not originality or AdSense eligibility.
"""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.h1 = 0
        self.meta = {}
        self.scripts = []
        self.canonical = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'h1': self.h1 += 1
        if tag == 'meta': self.meta[a.get('name', '')] = a.get('content', '')
        if tag == 'script' and a.get('src'): self.scripts.append(a['src'])
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a.get('href')


def verify(public):
    errors = []
    config = tomllib.loads((ROOT/'hugo.toml').read_text(encoding='utf-8'))
    for section, allowed in [('posts', {'worked-example', 'source-audit'}), ('tools', {'calculator'})]:
        for p in (ROOT/'content'/section).rglob('*.md'):
            if p.name == '_index.md': continue
            text = p.read_text(encoding='utf-8')
            # Date reports use JSON front matter; reject them before inspecting YAML fields.
            if not text.startswith('---\n'):
                errors.append(f'{p.name}: only editorial learning content may publish here')
                continue
            fm = text.split('---', 2)[1]
            kind = re.search(r'^content_kind: "([^"]+)"$', fm, re.M)
            if not kind or kind.group(1) not in allowed:
                errors.append(f'{p.name}: missing learning content kind')
            if re.search(r'^is(report|weekly|technical):\s*true', fm, re.M | re.I):
                errors.append(f'{p.name}: automated market-report publishing is outside this site scope')
            for field in ('description', 'date', 'evidence_label'):
                if not re.search(rf'^{field}:\s*\S+', fm, re.M): errors.append(f'{p.name}: missing {field}')
    for item in json.loads((ROOT/'archive/revisions/2026-10-09/manifest.json').read_text(encoding='utf-8')):
        if hashlib.sha256((ROOT/item['archive']).read_bytes()).hexdigest() != item['sha256']:
            errors.append(f'Revision original modified: {item["archive"]}')
    required = ['index.html', 'learn/index.html', 'about/index.html', 'contact/index.html',
        'editorial-policy/index.html', 'privacy/index.html', 'research-methods/index.html',
        'tools/compound/index.html', 'tools/costs/index.html', 'tools/position/index.html']
    for relative in required:
        if not (public/relative).is_file(): errors.append(f'Missing page: {relative}')
    pages = list(public.rglob('*.html'))
    for path in pages:
        html = path.read_text(encoding='utf-8')
        if re.fullmatch(r'google[0-9a-f]+\.html', path.name) and html.strip() == f'google-site-verification: {path.name}':
            continue  # Google's unchanged ownership-verification file is not a content page.
        d = Document(html)
        if d.h1 != 1: errors.append(f'{path.relative_to(public)}: expected one main heading, got {d.h1}')
        if not d.meta.get('description'): errors.append(f'{path.name}: missing description')
        if d.meta.get('google-adsense-account') != config['params']['adsenseClient']:
            errors.append(f'{path.name}: verification identity changed')
        if not d.canonical or not d.canonical.startswith(config['baseURL']):
            errors.append(f'{path.name}: incorrect canonical origin')
        ad_scripts = [src for src in d.scripts if 'googlesyndication' in src]
        if not config['params'].get('adsenseEnabled') and ad_scripts:
            errors.append(f'{path.name}: unexpected ad request before serving is enabled')
        if not str(path.relative_to(public)).replace('\\','/').startswith('posts/') and ad_scripts:
            errors.append(f'{path.name}: advertisements on a utility/navigation page')
    pubid = config['params']['adsenseClient'].removeprefix('ca-')
    if f'google.com, {pubid}, DIRECT, f08c47fec0942fa0' not in (public/'ads.txt').read_text():
        errors.append('ads.txt publisher differs from verification metadata')
    # Inspect the rendered prose against hand-calculated fixture values, not just the module.
    examples = {
        'posts/note-prior-day-surge/index.html': ['95,507.96', '−4.4920'],
        'posts/note-overnight-retract/index.html': ['1,349,253', '1,105,116', '244,137'],
        'tools/costs/index.html': ['1,349,253', '244,137'],
        'posts/guide-stop-loss-design/index.html': ['98,800', '193,800'],
    }
    for path, values in examples.items():
        text = (public/path).read_text(encoding='utf-8')
        for value in values:
            if value not in text: errors.append(f'{path}: expected worked-example value {value}')
    if errors: raise SystemExit('\n'.join(errors))
    print(f'PASS: learning publication boundary, revision hashes, {len(pages)} page structures, ad verification, worked-example values')


if __name__ == '__main__':
    verify(Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'public')
