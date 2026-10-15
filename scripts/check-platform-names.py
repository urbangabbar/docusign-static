#!/usr/bin/env python3
"""Keep platform-name coverage and referenced-image discovery consistent."""
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
IMAGE_NS = 'http://www.google.com/schemas/sitemap-image/1.1'


class Context(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.capture = False
        self.blocks = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'p' and 'lcb-platform-context' in a.get('class', '').split():
            self.capture = True
            self.blocks.append('')
            if 'hidden' in a or a.get('aria-hidden') == 'true':
                self.blocks[-1] = 'HIDDEN '

    def handle_endtag(self, tag):
        if tag == 'p':
            self.capture = False

    def handle_data(self, data):
        if self.capture:
            self.blocks[-1] += data


def scan(root=ROOT):
    root = Path(root)
    manifest = json.loads((root / 'search-manifest.json').read_text())
    base = manifest['baseUrl']
    aliases = json.loads((root / 'data/product-facts.json').read_text())['platform']
    errors = []
    expected_images = {}
    for page in manifest['pages']:
        relative = page['url'].removeprefix(base).lstrip('/')
        path = root / (relative + 'index.html' if page['url'].endswith('/') else relative + '.html')
        source = path.read_text()
        context = Context(source).blocks
        if len(context) != 1 or context[0].startswith('HIDDEN ') or not all(re.search(r'\b' + term + r'\b', context[0]) for term in ['GoHighLevel', 'GHL', 'HighLevel']):
            errors.append(f'Missing visible platform-name context: {page["url"]}')
        if 'GoHighLevel' not in page['title'] or 'GoHighLevel' not in page['description']:
            errors.append(f'Primary platform name missing from metadata: {page["url"]}')
        graphs = []
        for raw in re.findall(r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', source, re.S):
            data = json.loads(raw)
            graphs.extend(data.get('@graph', [data]))
        platform = next((n for n in graphs if n.get('@id') == base + '/#gohighlevel-platform'), {})
        if platform.get('name') != aliases['name'] or platform.get('alternateName') != aliases['alternateName']:
            errors.append(f'Platform entity aliases differ from reviewed facts: {page["url"]}')
        webpage = next((n for n in graphs if n.get('@id') == page['url'] + '#webpage'), {})
        if webpage.get('about') != {'@id': platform.get('@id')}:
            errors.append(f'Page does not reference the platform entity: {page["url"]}')
        org = next((n for n in graphs if n.get('@id') == base + '/#organization'), {})
        if set(org.get('alternateName', [])) & {aliases['name'], *aliases['alternateName']}:
            errors.append(f'Platform aliases incorrectly assigned to LC Bridge: {page["url"]}')
        if page.get('images'):
            expected_images[page['url']] = set(page['images'])
    actual_images = {}
    for node in ET.parse(root / 'image-sitemap.xml').getroot().findall(f'{{{NS}}}url'):
        url = node.findtext(f'{{{NS}}}loc')
        actual_images[url] = {n.text for n in node.findall(f'{{{IMAGE_NS}}}image/{{{IMAGE_NS}}}loc')}
    if actual_images != expected_images:
        errors.append('Image sitemap does not match the public pages’ referenced images')
    for images in actual_images.values():
        for image in images:
            if not image.startswith(base + '/') or not (root / image.removeprefix(base + '/')).is_file():
                errors.append(f'Image sitemap references a missing/local-external image: {image}')
    return {'pagesChecked': len(manifest['pages']),
            'uniqueImages': len(set().union(*actual_images.values())) if actual_images else 0,
            'errors': errors}


if __name__ == '__main__':
    result = scan()
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['errors']))
