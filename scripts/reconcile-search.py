#!/usr/bin/env python3
"""Maintain a private Google submission queue from the deployed public manifest.

This prepares work and records confirmed UI outcomes; it does NOT submit to Google.
GSC Wizard and the signed-in Search Console UI perform the actual external actions.
"""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def reconcile(state, manifest):
    entries = state.setdefault('urls', {})
    current = {p['url']: p for p in manifest['pages']}
    for url, page in current.items():
        entry = entries.setdefault(url, {})
        if entry.get('contentHash') != page['contentHash']:
            entry.update(contentHash=page['contentHash'], status='pending', reason='New or changed public page')
            entry.pop('requestedAt', None)
        entry['title'] = page['title']
    for url, entry in entries.items():
        if url not in current:
            entry['status'] = 'retired'
    state['manifest'] = manifest
    state['lastReconciledAt'] = datetime.now(timezone.utc).isoformat()
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--live', action='store_true', help='Read deployed manifest; use after publication')
    parser.add_argument('--record', help='Exact public URL whose Google UI outcome was verified')
    parser.add_argument('--status', choices=['accepted', 'quota', 'blocked'])
    parser.add_argument('--detail', default='')
    args = parser.parse_args()
    private = args.root / 'output/search-maintenance'
    private.mkdir(parents=True, exist_ok=True)
    path = private / 'state.json'
    state = json.loads(path.read_text()) if path.exists() else {'version': 1, 'urls': {}}
    if args.live:
        with urlopen(Request('https://lcbridge.app/search-manifest.json',
                             headers={'User-Agent': 'LCBridge-Search-Maintenance', 'Cache-Control': 'no-cache'}), timeout=30) as r:
            manifest = json.load(r)
    else:
        manifest = json.loads((args.root / 'search-manifest.json').read_text())
    if manifest.get('baseUrl') != 'https://lcbridge.app':
        raise SystemExit('Unexpected manifest host')
    state = reconcile(state, manifest)
    if args.record:
        if not args.status or args.record not in {p['url'] for p in manifest['pages']}:
            raise SystemExit('A confirmed status and current public URL are required')
        entry = state['urls'][args.record]
        now = datetime.now(timezone.utc)
        if args.status == 'quota':
            state['submissionRetryAfter'] = (now + timedelta(hours=24)).isoformat()
            entry['status'] = 'pending'
        else:
            entry['status'] = args.status
        entry['detail'] = args.detail
        entry['lastAttemptAt'] = now.isoformat()
        if args.status == 'accepted':
            entry['requestedAt'] = now.isoformat()
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    pending = [u for u, e in state['urls'].items() if e['status'] == 'pending']
    accepted = [u for u, e in state['urls'].items() if e['status'] == 'accepted']
    print(json.dumps({'publicPages': len(manifest['pages']), 'acceptedRequests': len(accepted),
                      'pendingRequests': pending, 'submissionRetryAfter': state.get('submissionRetryAfter'),
                      'stateFile': str(path)}, indent=2))


if __name__ == '__main__':
    main()
