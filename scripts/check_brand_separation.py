#!/usr/bin/env python3
"""Fail publication on cross-brand references or unreviewed public media."""
import argparse
import hashlib
import html
import json
from fnmatch import fnmatch
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(r'g[\W_]*o[\W_]*c[\W_]*s[\W_]*m|g[\W_]*o[\W_]*v[\W_]*p[\W_]*r[\W_]*e[\W_]*n[\W_]*e[\W_]*u[\W_]*r[\W_]*s', re.I)
MEDIA = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.ico', '.pdf', '.mp4', '.webm', '.mov', '.mp3', '.wav', '.m4a', '.ogg', '.woff', '.woff2', '.ttf', '.otf', '.eot'}


def has_forbidden_reference(text):
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m[1], 16)), text)
    for _ in range(2):
        text = html.unescape(unquote(text))
    return bool(FORBIDDEN.search(text) or FORBIDDEN.search(re.sub(r'<[^>]*>', '', text)))


def public_files(root, policy_root=None, published=False):
    if published:
        return sorted(p for p in root.rglob('*') if p.is_file())
    policy_root = policy_root or root
    policy = json.loads((policy_root / 'data/search-policy.json').read_text())
    config = (policy_root / '_config.yml').read_text()
    excludes = [s.strip().rstrip('/') for s in re.findall(r'^\s+-\s+([^\n#]+)', config, re.M)]
    def public(path):
        relative = path.relative_to(root).as_posix()
        if any(part.startswith('.') for part in path.relative_to(root).parts):
            return False
        if any(fnmatch(relative, pattern) for pattern in policy['internalPaths'] if pattern != '404.html'):
            return False
        return not any(relative == p or relative.startswith(p + '/') or fnmatch(relative, p) for p in excludes)
    return sorted(p for p in root.rglob('*') if p.is_file() and public(p))


def scan(root=ROOT, policy_root=None, published=False):
    root = Path(root)
    policy_root = Path(policy_root or root)
    approval_path = policy_root / 'data/approved-public-media.json'
    approved = json.loads(approval_path.read_text())['sha256'] if approval_path.exists() else {}
    errors = []
    files = public_files(root, policy_root, published)
    for path in files:
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        if has_forbidden_reference(relative) or has_forbidden_reference(data.decode('utf-8', errors='ignore')):
            errors.append(f'Forbidden public brand reference: {relative}')
        if path.suffix.lower() in MEDIA:
            if approved.get(relative) != hashlib.sha256(data).hexdigest():
                errors.append(f'Public media requires brand review before approval: {relative}')
        else:
            try:
                data.decode('utf-8')
            except UnicodeDecodeError:
                errors.append(f'Unrecognized public binary requires review: {relative}')
    return {'filesScanned': len(files), 'mediaScanned': sum(p.suffix.lower() in MEDIA for p in files), 'errors': errors}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--published', type=Path)
    args = parser.parse_args()
    result = scan(args.published or args.root, args.root, bool(args.published))
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['errors']))
