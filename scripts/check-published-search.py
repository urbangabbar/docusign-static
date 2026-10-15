#!/usr/bin/env python3
"""Ensure Jekyll publishes the generated discovery files but not private sources."""
import json
from fnmatch import fnmatch
from pathlib import Path
import sys
from check_brand_separation import scan as scan_brand_separation

root = Path(__file__).resolve().parents[1]
site = Path(sys.argv[1])
brand_check = scan_brand_separation(site, root, published=True)
if brand_check['errors']:
    raise SystemExit('\n'.join(brand_check['errors']))
for name in ('sitemap.xml', 'image-sitemap.xml', 'llms.txt', 'robots.txt', 'search-manifest.json'):
    if (site / name).read_bytes() != (root / name).read_bytes():
        raise SystemExit(f'Published discovery file differs: {name}')
for name in ('AGENTS.md', 'HANDOFF.md', 'HIGHLEVEL_DEVELOPMENT.md', 'data', 'scripts', 'skills', 'brand', 'blog-drafts', 'output', 'docs'):
    if (site / name).exists():
        raise SystemExit(f'Private source unexpectedly published: {name}')
policy = json.loads((root / 'data/search-policy.json').read_text())
for path in site.rglob('*'):
    relative = path.relative_to(site).as_posix()
    if path.is_file() and relative != '404.html' and any(fnmatch(relative, pattern) for pattern in policy['internalPaths']):
        raise SystemExit(f'Internal policy path unexpectedly published: {relative}')
manifest = json.loads((site / 'search-manifest.json').read_text())
for page in manifest['pages']:
    relative = page['url'].removeprefix(manifest['baseUrl']).lstrip('/')
    path = site / (relative + 'index.html' if page['url'].endswith('/') else relative + '.html')
    if not path.is_file():
        raise SystemExit(f'Public page omitted from build: {page["url"]}')
print(f'Published all {len(manifest["pages"])} public pages; private sources excluded.')
