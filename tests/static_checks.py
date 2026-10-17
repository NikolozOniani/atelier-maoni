"""Repository checks. Run from any working directory with Python 3."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import importlib.util
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
checks = 0


def check(condition, message):
    global checks
    assert condition, message
    checks += 1


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


pages = [ROOT / lang / page / 'index.html' for lang in ['ka', 'en'] for page in ['', 'work', 'contact']]
for path in pages:
    text = path.read_text()
    parsed = Page()
    parsed.feed(text)
    ids = [attrs['id'] for _, attrs in parsed.tags if 'id' in attrs]
    check(len(ids) == len(set(ids)), f'Duplicate HTML IDs: {path}')
    check(sum(tag == 'h1' for tag, _ in parsed.tags) == 1, f'Heading hierarchy: {path}')
    check(f'<html lang="{path.relative_to(ROOT).parts[0]}">' in text, f'Language: {path}')
    check('Atelier_Maoni_pics' not in text and '_studio/review' not in text, f'Internal source reference: {path}')
    check('tel:+995592120806' in text, f'Telephone: {path}')
    for tag, attrs in parsed.tags:
        if tag == 'img':
            check('alt' in attrs, f'Missing alt: {path}')
        for key in ['src', 'href']:
            target = attrs.get(key, '')
            if not target or urlsplit(target).scheme or target.startswith('#'):
                continue
            relative = unquote(urlsplit(target).path)
            check(not relative.startswith('/'), f'Root-absolute path breaks project hosting: {path}: {target}')
            resolved = (path.parent / relative).resolve()
            check(resolved.is_relative_to(ROOT) and resolved.exists(), f'Broken local path: {path}: {target}')
            if urlsplit(target).fragment and resolved.is_dir():
                check(f'id="{urlsplit(target).fragment}"' in (resolved/'index.html').read_text(), f'Broken anchor: {target}')
        for item in attrs.get('srcset', '').split(','):
            if item.strip():
                relative = item.strip().split()[0]
                check((path.parent / relative).resolve().is_file(), f'Broken responsive image: {relative}')

inventory = json.loads((ROOT/'_studio/data/photo-inventory.json').read_text())
check(len(inventory) == 34, 'Expected the complete original archive')
for image in inventory:
    check(hashlib.sha256((ROOT/image['path']).read_bytes()).hexdigest() == image['sha256'], f'Original changed: {image["path"]}')
    check(bool(image['description']) and image['opened'], f'Incomplete inventory: {image["path"]}')
check(len(set(row['sha256'] for row in inventory)) == 34, 'Unexpected exact duplicates')
projects = json.loads((ROOT/'_studio/data/portfolio.json').read_text())
check(len(projects) == 14 and sum(p['featured'] for p in projects) == 6, 'Curation counts')
excluded_minors = {16,17,19,21,24,26,27,28,29,30,31,32}
check(not excluded_minors.intersection(n for p in projects for n in p['images']), 'Minor portrait selected')
check(not (ROOT/'.nojekyll').exists(), '.nojekyll bypasses archive exclusions')
config = (ROOT/'_config.yml').read_text()
for name in ['Atelier_Maoni_pics','_studio','tests','PHOTO-SELECTION.md','MISSING-INFORMATION.md']:
    check(f'  - {name}\n' in config, f'Missing deployment exclusion: {name}')
ET.parse(ROOT/'sitemap.xml')
check('Disallow:' not in (ROOT/'robots.txt').read_text(), 'Crawlers blocked')

# Exercise URL-dependent metadata without inventing or writing production URLs.
spec = importlib.util.spec_from_file_location('render', ROOT/'_studio/render.py')
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)
render.BASE = 'https://example.invalid/atelier-maoni'
meta = render.metadata('../../', 'en', 'work', render.COPY['en'])
check('rel="canonical" href="https://example.invalid/atelier-maoni/en/work/"' in meta, 'Canonical generation')
check('content="https://example.invalid/atelier-maoni/assets/images/' in meta, 'OG image generation')
check('hreflang="ka" href="https://example.invalid/atelier-maoni/ka/work/"' in meta, 'Alternate URL generation')
before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in pages}
render.BASE = render.SITE['siteUrl'].rstrip('/')
render.render()
check(all(hashlib.sha256(p.read_bytes()).hexdigest() == digest for p,digest in before.items()), 'Rendering is not repeatable')
print(f'PASS: {checks} static checks; all 34 originals unchanged; 6 localized pages; repeatable rendering.')
