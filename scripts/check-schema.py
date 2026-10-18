#!/usr/bin/env python3
"""Audit all public pages; optionally validate against official Schema.org terms."""
from pathlib import Path
from collections import Counter
import argparse,json
from schema_validation import check, parse_graph, vocabulary_errors

ROOT = Path(__file__).resolve().parents[1]

def scan(root=ROOT, vocabulary=None):
    root = Path(root)
    manifest = json.loads((root / 'search-manifest.json').read_text())
    pages = []
    types = Counter()
    for page in manifest['pages']:
        rel = page['url'].removeprefix(manifest['baseUrl'] + '/')
        source = (root / (rel + 'index.html' if page['url'].endswith('/') else rel + '.html')).read_text()
        result = check(source, page['url'])
        try:
            graph = parse_graph(source)
            types.update(n['@type'] for n in graph)
            if vocabulary:
                result['errors'] += vocabulary_errors(graph, vocabulary)
        except (ValueError, KeyError):
            pass
        pages.append({'url': page['url'], **result})
    return {'pagesChecked': len(pages), 'types': dict(types),
            'errors': [{'url': p['url'], 'issue': e} for p in pages for e in p['errors']],
            'notes': [{'url': p['url'], 'note': e} for p in pages for e in p['notes']], 'pages': pages}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vocabulary', type=Path)
    p.add_argument('--report', type=Path)
    args = p.parse_args()
    result = scan(vocabulary=json.loads(args.vocabulary.read_text()) if args.vocabulary else None)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'pages'}, indent=2))
    raise SystemExit(bool(result['errors']))
