#!/usr/bin/env python3
"""Generate discovery files from every public HTML page, never a hand-kept URL list."""
import argparse
from collections import deque
from datetime import datetime, timezone
from fnmatch import fnmatch
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MARKER = '\n## Complete public page directory\n'
NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
IMAGE_NS = 'http://www.google.com/schemas/sitemap-image/1.1'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.title = ''
        self.in_title = False
        self.description = ''
        self.canonicals = []
        self.robots = []
        self.links = []
        self.images = []
        self.refresh = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title':
            self.in_title = True
        if tag == 'link' and 'canonical' in a.get('rel', '').lower().split():
            self.canonicals.append(a.get('href', ''))
        if tag == 'meta':
            name = a.get('name', '').lower()
            if name in ('robots', 'googlebot'):
                self.robots.append(a.get('content', '').lower())
            if name == 'description':
                self.description = a.get('content', '')
            if a.get('http-equiv', '').lower() == 'refresh':
                self.refresh = a.get('content', '')
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'img' and a.get('src'):
            self.images.append(a['src'])
        if tag in ('img', 'source'):
            for candidate in a.get('srcset', '').split(','):
                if candidate.strip():
                    self.images.append(candidate.strip().split()[0])
        if tag == 'video' and a.get('poster'):
            self.images.append(a['poster'])
        if tag == 'meta' and a.get('property', a.get('name')) in ('og:image', 'twitter:image'):
            self.images.append(a.get('content', ''))

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, text):
        if self.in_title:
            self.title += text


def route(path):
    """Match GitHub Pages directory indexes and extensionless flat HTML files."""
    return '/' + (path[:-10] if Path(path).name == 'index.html' else path[:-5])


def last_changed(root, path):
    result = subprocess.run(['git', 'log', '-1', '--format=%cI', '--', path],
                            cwd=root, capture_output=True, text=True)
    return result.stdout.strip()[:10] or datetime.now(timezone.utc).date().isoformat()


def inventory(root, policy):
    base = policy['baseUrl']
    pages, redirects, errors = {}, [], []
    previous_path = root / 'search-manifest.json'
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else {}
    prior = {p['url']: p for p in previous.get('pages', [])}
    today = datetime.now(timezone.utc).date().isoformat()
    for path in sorted(root.rglob('*.html')):
        relative = path.relative_to(root).as_posix()
        if any(fnmatch(relative, pattern) for pattern in policy['internalPaths']):
            continue
        source = path.read_text()
        page = Page(source)
        url = base + route(relative)
        if page.refresh is not None:
            match = re.fullmatch(r'\s*0\s*;\s*url\s*=\s*(.+?)\s*', page.refresh, re.I)
            if not match:
                errors.append(f'Redirect must be immediate: {relative}')
                continue
            target = urljoin(url, match.group(1).strip('"\''))
            if page.canonicals != [target]:
                errors.append(f'Redirect/canonical disagreement: {relative}')
            redirects.append({'from': url, 'to': target})
            continue
        if page.canonicals != [url]:
            errors.append(f'Public page requires self-canonical {url}: {relative}')
        if any(re.search(r'\b(noindex|none)\b', rule) for rule in page.robots):
            errors.append(f'Public page unexpectedly noindex: {relative}; classify internal explicitly if intended')
        if not page.title.strip() or not page.description.strip():
            errors.append(f'Public page missing title/description: {relative}')
        digest = sha256(source.encode()).hexdigest()
        old = prior.get(url)
        lastmod = (old['lastmod'] if old and old['contentHash'] == digest
                   else today if old else last_changed(root, relative))
        images = []
        for raw in page.images:
            absolute = urljoin(url, raw)
            parts = urlsplit(absolute)
            clean = parts._replace(query='', fragment='').geturl()
            local = root / parts.path.lstrip('/')
            if parts.netloc == urlsplit(base).netloc and any(fnmatch(parts.path.lstrip('/'), pattern) for pattern in policy['internalPaths']):
                errors.append(f'Public page references an internal image: {relative} -> {clean}')
                continue
            if parts.netloc == urlsplit(base).netloc and local.is_file() and local.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.avif'):
                images.append(clean)
        pages[url] = {'url': url, 'title': ' '.join(page.title.split()),
                      'description': ' '.join(page.description.split()),
                      'contentHash': digest, 'lastmod': lastmod,
                      'images': sorted(set(images)), '_links': page.links}
    graph = {}
    for url, page in pages.items():
        graph[url] = []
        for link in page['_links']:
            parts = urlsplit(urljoin(url, link))
            target = parts._replace(query='', fragment='').geturl()
            if target in pages:
                graph[url].append(target)
    reachable = {base + '/'}
    queue = deque(reachable)
    while queue:
        for target in graph.get(queue.popleft(), []):
            if target not in reachable:
                reachable.add(target)
                queue.append(target)
    for url in pages:
        if url not in reachable:
            errors.append(f'Public page is orphaned; link it from a public hub: {url}')
    for redirect in redirects:
        if redirect['to'] not in pages:
            errors.append(f'Redirect targets missing/internal/redirect page: {redirect}')
    removed = sorted(set(prior) - set(pages))
    for url in removed:
        # A deleted page is valid. A changed path with a replacement needs a redirect.
        errors.append(f'Previously public URL removed: {url}; add a redirect or acknowledge in data/search-removals.json')
    acknowledgements_path = root / 'data/search-removals.json'
    acknowledgements = json.loads(acknowledgements_path.read_text()) if acknowledgements_path.exists() else {}
    new_redirects = {p['from']: p['to'] for p in redirects}
    errors = [e for e in errors if not any(e.startswith(f'Previously public URL removed: {u};')
              and (u in new_redirects or acknowledgements.get(u)) for u in removed)]
    # Keep removal decisions explicit and available to the GSC reconciliation workflow.
    manifest = {'version': 1, 'baseUrl': base,
                'pages': [{k: v for k, v in p.items() if not k.startswith('_')}
                          for p in pages.values()],
                'redirects': redirects,
                'retiredUrls': acknowledgements}
    return manifest, errors


def generated(root, policy, manifest):
    base = policy['baseUrl']
    ET.register_namespace('', NS)
    xml = ET.Element(f'{{{NS}}}urlset')
    for page in manifest['pages']:
        node = ET.SubElement(xml, f'{{{NS}}}url')
        ET.SubElement(node, f'{{{NS}}}loc').text = page['url']
        ET.SubElement(node, f'{{{NS}}}lastmod').text = page['lastmod']
    ET.indent(xml, space='  ')
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(xml, encoding='unicode') + '\n'
    ET.register_namespace('image', IMAGE_NS)
    image_xml = ET.Element(f'{{{NS}}}urlset')
    for page in manifest['pages']:
        if not page.get('images'):
            continue
        node = ET.SubElement(image_xml, f'{{{NS}}}url')
        ET.SubElement(node, f'{{{NS}}}loc').text = page['url']
        for image in page['images']:
            image_node = ET.SubElement(node, f'{{{IMAGE_NS}}}image')
            ET.SubElement(image_node, f'{{{IMAGE_NS}}}loc').text = image
    ET.indent(image_xml, space='  ')
    image_sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(image_xml, encoding='unicode') + '\n'
    robots = '# Generated by scripts/sync-search.py. Public pages are crawlable.\nUser-agent: *\nAllow: /\n'
    for bot in policy['aiCrawlers']:
        robots += f'\nUser-agent: {bot}\nAllow: /\n'
    robots += f'\nSitemap: {base}/sitemap.xml\n'
    robots += f'Sitemap: {base}/image-sitemap.xml\n'
    # Retain reviewed product facts; replace old generated directory and prune obsolete local links.
    llms = (root / 'llms.txt').read_text().split(MARKER)[0].rstrip()
    valid = {p['url'] for p in manifest['pages']}
    redirects = {p['from']: p['to'] for p in manifest['redirects']}
    lines = []
    for line in llms.splitlines():
        for old, new in redirects.items():
            line = line.replace('](' + old + ')', '](' + new + ')')
        local = re.findall(r'\]\((' + re.escape(base) + r'/[^)]*)\)', line)
        if any(u.split('#')[0] not in valid and u != base + '/sitemap.xml' for u in local):
            continue
        lines.append(line)
    llms = '\n'.join(lines).rstrip() + MARKER + '\n'
    for page in manifest['pages']:
        label = page['title'].replace('[', '').replace(']', '')
        llms += f'- [{label}]({page["url"]}): {page["description"]}\n'
    config_path = root / '_config.yml'
    config = config_path.read_text() if config_path.exists() else 'exclude:\n'
    header = re.search(r'^exclude:[ \t]*(?:#[^\n]*)?$', config, re.M)
    if not header:
        raise ValueError('_config.yml requires an exclude block list for private publishing rules')
    existing_excludes = {s.strip() for s in re.findall(r'^\s+-\s+([^\n#]+)', config, re.M)}
    for pattern in policy['internalPaths']:
        if pattern in ('404.html', '.*'):
            continue
        exclusion = pattern[:-1] if pattern.endswith('/*') else pattern
        if exclusion not in existing_excludes:
            config = config[:header.end()] + '\n  - ' + exclusion + config[header.end():]
    return {'sitemap.xml': sitemap, 'image-sitemap.xml': image_sitemap,
            'robots.txt': robots, 'llms.txt': llms, '_config.yml': config,
            'search-manifest.json': json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'}


def run(root, write=False):
    policy = json.loads((root / 'data/search-policy.json').read_text())
    manifest, errors = inventory(root, policy)
    if errors:
        print(json.dumps({'errors': errors}, indent=2))
        return 1
    outputs = generated(root, policy, manifest)
    stale = [name for name, text in outputs.items()
             if not (root / name).exists() or (root / name).read_text() != text]
    if write:
        for name in stale:
            (root / name).write_text(outputs[name])
    print(json.dumps({'publicPages': len(manifest['pages']), 'redirects': len(manifest['redirects']),
                      'updated' if write else 'stale': stale, 'errors': []}, indent=2))
    return 0 if write or not stale else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    sys.exit(run(args.root, args.write))
