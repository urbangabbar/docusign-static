#!/usr/bin/env python3
"""Local preview with GitHub Pages-style extensionless .html resolution."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path):
        actual = Path(super().translate_path(path))
        if not actual.exists() and actual.with_suffix('.html').is_file():
            actual = actual.with_suffix('.html')
        return str(actual)

    def do_GET(self):
        requested = unquote(urlsplit(self.path).path)
        parts = [part for part in requested.split('/') if part]
        if parts and (parts[0] in ['.git', '.claude', '.agents', 'output', 'scripts', 'docs', 'blog-drafts', 'Claude outputs']
                      or '.git' in parts):
            self.send_error(404)
            return
        return super().do_GET()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    print(f'Preview at http://127.0.0.1:{args.port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
