#!/usr/bin/env python3
"""Keep company/product navigation and footer consistent in public static HTML."""
from pathlib import Path
from fnmatch import fnmatch
import argparse,json,re
from site_chrome import apply_chrome,ROOT

def public_pages():
    policy=json.loads((ROOT/'data/search-policy.json').read_text())
    for path in sorted(ROOT.rglob('*.html')):
        relative=path.relative_to(ROOT)
        if any(part.startswith('.') for part in relative.parts) or any(fnmatch(relative.as_posix(),p) for p in policy['internalPaths']):continue
        source=path.read_text()
        if re.search(r'http-equiv=["\']refresh',source,re.I):continue
        match=re.search(r'<link\b[^>]*rel="canonical"[^>]*href="https://lcbridge.app([^"]+)"',source)
        if match:yield path,match[1],source

def run(write=False):
    stale=[]
    for file,path,source in public_pages():
        result=apply_chrome(source,path)
        if result!=source:
            stale.append(str(file.relative_to(ROOT)))
            if write:file.write_text(result)
    print(json.dumps({'updated' if write else 'stale':len(stale),'pages':stale if not write else []},indent=2))
    return 0 if write or not stale else 1
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args();raise SystemExit(run(args.write))
