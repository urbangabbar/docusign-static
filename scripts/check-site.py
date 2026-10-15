#!/usr/bin/env python3
"""Validate canonical pages, local links/assets, JSON-LD and discovery files."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, unquote
from collections import Counter, deque
import json
import re
import sys
import xml.etree.ElementTree as ET
from check_brand_separation import scan as scan_brand_separation
import importlib.util

platform_spec = importlib.util.spec_from_file_location('platform_names', Path(__file__).with_name('check-platform-names.py'))
platform_names = importlib.util.module_from_spec(platform_spec)
platform_spec.loader.exec_module(platform_names)

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://lcbridge.app'
IGNORED = {'.git', '.playwright-mcp', 'output', 'scripts', 'docs', 'blog-drafts', 'Claude outputs'}


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.meta = {}
        self.canonical = []
        self.title = ''
        self.title_count = 0
        self.h1_count = 0
        self.main_count = 0
        self.ids = []
        self.links = []
        self.assets = []
        self.schemas = []
        self.images = []
        self.in_title = False
        self.in_schema = False
        self.redirect = False
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.append(a['id'])
        if tag == 'meta':
            self.meta[a.get('name', a.get('property', '')).lower()] = a.get('content', '')
            if a.get('http-equiv', '').lower() == 'refresh':
                self.redirect = True
                m = re.search(r'url=(.+)', a.get('content', ''), re.I)
                if m:
                    self.links.append(m.group(1))
        if tag == 'link':
            if a.get('rel') == 'canonical':
                self.canonical.append(a.get('href'))
            if a.get('href') and a.get('rel') in ['stylesheet', 'icon', 'apple-touch-icon', 'preload']:
                self.assets.append(a['href'])
        if tag == 'title':
            self.in_title = True
            self.title_count += 1
        if tag == 'h1':
            self.h1_count += 1
        if tag == 'main' or a.get('role') == 'main':
            self.main_count += 1
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'img':
            self.images.append(a)
            if a.get('src'):
                self.assets.append(a['src'])
            for candidate in a.get('srcset', '').split(','):
                if candidate.strip():
                    self.assets.append(candidate.strip().split()[0])
        if tag == 'source':
            for candidate in a.get('srcset', '').split(','):
                if candidate.strip():
                    self.assets.append(candidate.strip().split()[0])
        if tag == 'script':
            if a.get('src'):
                self.assets.append(a['src'])
            if a.get('type') == 'application/ld+json':
                self.in_schema = True
                self.schemas.append('')

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'script':
            self.in_schema = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_schema:
            self.schemas[-1] += data


def resolve(url):
    path = unquote(urlsplit(url).path)
    candidate = ROOT / path.lstrip('/')
    if candidate.is_file():
        return candidate
    if candidate.with_suffix('.html').is_file():
        return candidate.with_suffix('.html')
    if candidate.is_dir() and (candidate / 'index.html').is_file():
        return candidate / 'index.html'
    return None


def main():
    pages = {}
    errors = scan_brand_separation(ROOT)['errors'] + platform_names.scan(ROOT)['errors']
    notes = []
    for path in ROOT.rglob('*.html'):
        parts = path.relative_to(ROOT).parts
        if parts[0] in IGNORED or any(part in {'.git', '.playwright-mcp'} for part in parts):
            continue
        pages[path] = Page(path)
    sitemap = ET.parse(ROOT / 'sitemap.xml')
    urls = [e.text for e in sitemap.iter() if e.tag.endswith('}loc')]
    titles = Counter()
    descriptions = Counter()
    graph = {}
    for url in urls:
        path = resolve(url)
        if path not in pages:
            errors.append(f'Sitemap URL has no page: {url}')
            continue
        page = pages[path]
        if page.redirect or page.canonical != [url]:
            errors.append(f'Sitemap URL is not self-canonical: {url} -> {page.canonical}')
        if 'noindex' in page.meta.get('robots', ''):
            errors.append(f'Noindex page in sitemap: {url}')
        if page.h1_count != 1 or page.title_count != 1:
            errors.append(f'Heading/title count: {url}, H1={page.h1_count}, title={page.title_count}')
        if not page.meta.get('description'):
            errors.append(f'Missing description: {url}')
        if page.main_count != 1:
            notes.append(f'Main landmark count {page.main_count}: {url}')
        titles[' '.join(page.title.split())] += 1
        descriptions[page.meta.get('description')] += 1
        graph[url] = []
        for raw in page.schemas:
            try:
                schema = json.loads(raw)
                for node in schema.get('@graph', [schema]):
                    if node.get('@type') == 'Organization' and node.get('@id', '').endswith('#organization'):
                        if node.get('name') != 'LC Bridge' or node.get('url') != BASE + '/':
                            errors.append(f'Organization identity mismatch: {url}')
            except Exception as exc:
                errors.append(f'Invalid JSON-LD: {url}: {exc}')
        if not page.schemas:
            errors.append(f'Missing static schema: {url}')
        for link in page.links:
            full = urljoin(url, link)
            parts = urlsplit(full)
            if parts.netloc != 'lcbridge.app' or parts.scheme not in ['http', 'https']:
                continue
            target = resolve(full)
            if not target:
                errors.append(f'Broken link: {url} -> {full}')
            elif parts.fragment and target in pages and parts.fragment not in pages[target].ids:
                errors.append(f'Missing fragment: {url} -> {full}')
            dest = full.split('#')[0].split('?')[0]
            if dest in urls:
                graph[url].append(dest)
        for asset in page.assets:
            full = urljoin(url, asset)
            if urlsplit(full).netloc == 'lcbridge.app' and not resolve(full):
                errors.append(f'Missing asset: {url} -> {full}')
        for image in page.images:
            if 'alt' not in image:
                errors.append(f'Image has no alt attribute: {url} -> {image.get("src")}')
        if len(page.ids) != len(set(page.ids)):
            errors.append(f'Duplicate HTML ID: {url}')
    for title, count in titles.items():
        if count > 1:
            errors.append(f'Duplicate sitemap title ({count}): {title}')
    for desc, count in descriptions.items():
        if desc and count > 1:
            errors.append(f'Duplicate sitemap description ({count}): {desc}')
    for url in re.findall(r'\]\((https://lcbridge\.app/[^)]+)\)', (ROOT / 'llms.txt').read_text()):
        if not resolve(url):
            errors.append(f'Broken llms.txt URL: {url}')
    for product in ['docusign-integration', 'community-agents']:
        text = (ROOT / product / 'index.html').read_text()
        if re.search(r'if.*?matchMedia.*?mount\(true', text):
            errors.append(f'Autoplay mounted on initial load: {product}')
    for path in [ROOT / 'assets/analytics.js', ROOT / 'assets/analytics-config.js']:
        if not path.exists():
            errors.append(f'Missing analytics asset: {path}')
    distances = {BASE + '/': 0}
    queue = deque(distances)
    while queue:
        source = queue.popleft()
        for target in graph.get(source, []):
            if target not in distances:
                distances[target] = distances[source] + 1
                queue.append(target)
    for url in urls:
        if url not in distances:
            errors.append(f'Orphan sitemap URL: {url}')
        elif distances[url] > 3:
            notes.append(f'Deep page ({distances[url]} clicks): {url}')
    print(json.dumps({'sitemap_pages': len(urls), 'canonical_pages': len(graph),
                      'maximum_click_depth': max(distances.values()),
                      'errors': sorted(set(errors)), 'notes': sorted(set(notes))}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
