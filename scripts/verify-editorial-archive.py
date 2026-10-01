"""Verify the 2026-10-02 archive and built site's internal destinations.

Run after Hugo: python scripts/verify-editorial-archive.py [public-directory]
Checks original bytes, withdrawn URLs/RSS/sitemap, links, assets, and HTML anchors.
"""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urljoin, urlsplit


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])


def verify(root, public):
    manifest = json.loads((root / 'archive/manifest.json').read_text(encoding='utf-8'))
    errors = []
    xml = '\n'.join(p.read_text(encoding='utf-8') for p in public.rglob('*.xml'))
    for item in manifest['withdrawn']:
        archived = root / item['archive_path']
        if hashlib.sha256(archived.read_bytes()).hexdigest() != item['sha256']:
            errors.append(f'Archive changed: {item["slug"]}')
        if (root / item['original_path']).exists():
            errors.append(f'Withdrawn source reappeared: {item["slug"]}')
        if (public / 'posts' / item['slug']).exists() or item['url'] in xml:
            errors.append(f'Withdrawn URL still published: {item["url"]}')
    if (public / 'archive').exists():
        errors.append('Archive itself was published')
    for kind in ('일일보고서', '주간레시피'):
        if (public / 'categories' / kind).exists():
            errors.append(f'Empty retired category still published: {kind}')
    pages = {p.resolve(): Page(p.read_text(encoding='utf-8')) for p in public.rglob('*.html')}
    checked = 0
    for path, page in pages.items():
        rel = path.relative_to(public).as_posix()
        origin = '/' + (rel[:-10] if rel.endswith('index.html') else rel)
        for link in page.links:
            url = urlsplit(urljoin('https://yieldrecipe.com' + origin, link))
            if url.scheme not in ('https', 'http') or url.netloc != 'yieldrecipe.com':
                continue
            target = (public / unquote(url.path).lstrip('/')).resolve()
            try:
                target.relative_to(public)
            except ValueError:
                errors.append(f'Path escapes output: {rel}: {link}')
                continue
            if target.is_dir():
                target /= 'index.html'
            checked += 1
            if not target.is_file():
                errors.append(f'Missing target: {rel}: {link}')
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f'Missing anchor: {rel}: {link}')
    if errors:
        raise SystemExit('\n'.join(sorted(set(errors))))
    print(f'PASS: {len(manifest["withdrawn"])} archived originals; {len(pages)} HTML pages; {checked} internal destinations')


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    public = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root / 'public'
    if not (public / 'index.html').is_file():
        raise SystemExit('Build the site first; output index.html is missing')
    verify(root, public)
